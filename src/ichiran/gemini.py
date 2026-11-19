import json
import os
import tempfile
import time
from pathlib import Path

from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError

from ichiran.config import get_api_key
from ichiran.display import console, print_info, print_warning
from ichiran.interview import format_answers
from ichiran.prompt import SYSTEM_PROMPT
from ichiran.scanner import format_codebase_for_prompt, scan_codebase

# Tried in order against the models the API key actually supports.
PREFERRED_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite",
    "gemini-3.1-flash-lite",
]

RETRIES = 3
SESSION_FILE = Path(tempfile.gettempdir()) / "ichiran_last_session.json"


def _status_code(error: Exception) -> int | None:
    """Return the HTTP status code of an error, from .code or from its message."""
    code = getattr(error, "code", None)
    if isinstance(code, int):
        return code
    text = str(error)
    for candidate in (404, 429):
        if str(candidate) in text:
            return candidate
    return None


def _resolve_model(client: genai.Client) -> str:
    """Return the model to use. ICHIRAN_MODEL overrides auto-detection."""
    override = os.getenv("ICHIRAN_MODEL")
    if override:
        return override

    try:
        available = set()
        for model in client.models.list():
            actions = getattr(model, "supported_actions", None) or []
            if "generateContent" in actions:
                available.add(model.name.removeprefix("models/"))
    except ClientError:
        return PREFERRED_MODELS[0]

    for name in PREFERRED_MODELS:
        if name in available:
            return name

    raise RuntimeError(
        "None of the preferred Gemini models are available for this API key. "
        "Set ICHIRAN_MODEL to a model from client.models.list() to override."
    )


def _save_session(answers: dict) -> Path:
    SESSION_FILE.write_text(json.dumps(answers, indent=2), encoding="utf-8")
    return SESSION_FILE


def _backoff(attempt: int, reason: str) -> None:
    wait = 2**attempt
    print_warning(f"{reason}. Retrying in {wait}s ({attempt}/{RETRIES})...")
    time.sleep(wait)


def generate_readme(answers: dict) -> str:
    # Save answers first, so a failed generation never loses the interview.
    saved = _save_session(answers)

    api_key = get_api_key()
    client = genai.Client(api_key=api_key)

    print_info("Scanning codebase...")
    scan_result = scan_codebase(".")
    codebase_context = format_codebase_for_prompt(scan_result)

    formatted_answers = format_answers(answers)

    full_prompt = f"""
{formatted_answers}

=== ACTUAL CODEBASE ===
{codebase_context}

Using both the interview answers AND the codebase above, generate a complete README.md following the system instructions exactly.
"""

    model = _resolve_model(client)
    print_info(f"Generating README with {model}...")

    try:
        return _call_with_retry(client, model, full_prompt)
    except RuntimeError as error:
        console.print(f"\n[bold red]✘[/bold red]  {error}")
        console.print(f"[dim]Your answers were saved to:[/dim] {saved}")
        raise


def _call_with_retry(client: genai.Client, model: str, prompt: str) -> str:
    for attempt in range(1, RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=model,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                contents=prompt,
            )
            if not response.text:
                raise RuntimeError("Gemini returned an empty response.")
            return response.text

        except ClientError as error:
            status = _status_code(error)
            if status == 404:
                raise RuntimeError(
                    f"Model '{model}' is no longer available. "
                    "Set ICHIRAN_MODEL to a current model."
                ) from error
            if status == 429:
                if attempt == RETRIES:
                    raise RuntimeError(
                        "Gemini rate limit hit after all retries. Wait for your quota to reset "
                        "or use a different API key (ichiran --reset)."
                    ) from error
                _backoff(attempt, "Rate limited")
                continue
            raise

        except ServerError as error:
            if attempt == RETRIES:
                raise RuntimeError(
                    "Gemini is overloaded or unavailable right now. Try again in a few minutes."
                ) from error
            _backoff(attempt, "Gemini is busy")

    raise RuntimeError("Unreachable: retry loop exited without a result.")
