from ichiran import gemini


class RateLimitError(Exception):
    pass


def _client_with(generate_content):
    """Build a fake client whose models.generate_content is the given function."""
    models = type("Models", (), {"generate_content": staticmethod(generate_content)})()
    return type("Client", (), {"models": models})()


def test_rate_limit_retries_with_exponential_backoff(monkeypatch):
    attempts = []
    waits = []

    def generate_content(**_):
        attempts.append(1)
        if len(attempts) < 3:
            raise RateLimitError("429 RESOURCE_EXHAUSTED")
        return type("Response", (), {"text": "# Generated"})()

    monkeypatch.setattr(gemini, "ClientError", RateLimitError)
    monkeypatch.setattr(gemini.time, "sleep", waits.append)
    monkeypatch.setattr(gemini, "print_warning", lambda _: None)

    result = gemini._call_with_retry(_client_with(generate_content), "test-model", "prompt")

    assert result == "# Generated"
    assert len(attempts) == 3
    assert waits == [2, 4]


def test_rate_limit_exhaustion_raises_actionable_runtime_error(monkeypatch):
    waits = []

    def generate_content(**_):
        raise RateLimitError("429 RESOURCE_EXHAUSTED")

    monkeypatch.setattr(gemini, "ClientError", RateLimitError)
    monkeypatch.setattr(gemini.time, "sleep", waits.append)
    monkeypatch.setattr(gemini, "print_warning", lambda _: None)

    try:
        gemini._call_with_retry(_client_with(generate_content), "test-model", "prompt")
    except RuntimeError as error:
        assert "after all retries" in str(error)
    else:
        raise AssertionError("Expected exhausted retries to raise RuntimeError")
    assert waits == [2, 4]


def test_non_rate_limit_client_error_is_not_retried(monkeypatch):
    attempts = []

    def generate_content(**_):
        attempts.append(1)
        raise RateLimitError("400 INVALID_ARGUMENT")

    monkeypatch.setattr(gemini, "ClientError", RateLimitError)

    try:
        gemini._call_with_retry(_client_with(generate_content), "test-model", "prompt")
    except RateLimitError as error:
        assert "400" in str(error)
    else:
        raise AssertionError("Expected non-rate-limit ClientError to propagate")
    assert len(attempts) == 1


def test_server_error_is_retried_then_raises_friendly_message(monkeypatch):
    attempts = []
    waits = []

    class TransientError(Exception):
        pass

    def generate_content(**_):
        attempts.append(1)
        raise TransientError("503 UNAVAILABLE")

    monkeypatch.setattr(gemini, "ServerError", TransientError)
    monkeypatch.setattr(gemini.time, "sleep", waits.append)
    monkeypatch.setattr(gemini, "print_warning", lambda _: None)

    try:
        gemini._call_with_retry(_client_with(generate_content), "test-model", "prompt")
    except RuntimeError as error:
        assert "overloaded" in str(error)
    else:
        raise AssertionError("Expected exhausted server retries to raise RuntimeError")
    assert len(attempts) == 3
    assert waits == [2, 4]


def test_resolve_model_uses_env_override_without_listing(monkeypatch):
    monkeypatch.setenv("ICHIRAN_MODEL", "my-model")

    assert gemini._resolve_model(object()) == "my-model"


def test_resolve_model_picks_first_preferred_model_available(monkeypatch):
    from types import SimpleNamespace as NS

    monkeypatch.delenv("ICHIRAN_MODEL", raising=False)

    class Models:
        def list(self):
            return [
                NS(name="models/gemini-2.5-flash-lite", supported_actions=["generateContent"]),
                NS(name="models/embedding-001", supported_actions=["embedContent"]),
            ]

    client = type("Client", (), {"models": Models()})()

    assert gemini._resolve_model(client) == "gemini-2.5-flash-lite"


def test_generate_readme_uses_client_and_scanned_context(monkeypatch, tmp_path):
    captured = {}

    class FakeModels:
        def generate_content(self, **kwargs):
            captured.update(kwargs)
            return type("Response", (), {"text": "# README"})()

    class FakeClient:
        def __init__(self, api_key):
            captured["api_key"] = api_key
            self.models = FakeModels()

    monkeypatch.setenv("ICHIRAN_MODEL", "test-model")
    monkeypatch.setattr(gemini, "SESSION_FILE", tmp_path / "session.json")
    monkeypatch.setattr(gemini.genai, "Client", FakeClient)
    monkeypatch.setattr(gemini, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(gemini, "scan_codebase", lambda root: {"tree": [], "files": {}})
    monkeypatch.setattr(gemini, "format_codebase_for_prompt", lambda _: "code")
    monkeypatch.setattr(gemini, "format_answers", lambda _: "answers")
    monkeypatch.setattr(gemini, "print_info", lambda _: None)

    assert gemini.generate_readme({"q1": "project"}) == "# README"
    assert captured["api_key"] == "test-key"
    assert captured["model"] == "test-model"
    assert "answers" in captured["contents"]
    assert "code" in captured["contents"]
    assert (tmp_path / "session.json").exists()
