import gemini


class RateLimitError(Exception):
    pass


def test_rate_limit_retries_with_exponential_backoff(monkeypatch):
    attempts = []
    waits = []

    def generate_content(**_):
        attempts.append(1)
        if len(attempts) < 3:
            raise RateLimitError("429 RESOURCE_EXHAUSTED")
        return type("Response", (), {"text": "# Generated"})()

    client = type(
        "Client",
        (),
        {
            "models": type(
                "Models", (), {"generate_content": staticmethod(generate_content)}
            )()
        },
    )()
    monkeypatch.setattr(gemini, "ClientError", RateLimitError)
    monkeypatch.setattr(gemini.time, "sleep", waits.append)
    monkeypatch.setattr(gemini, "print_warning", lambda _: None)

    assert gemini._call_with_retry(client, "prompt") == "# Generated"
    assert len(attempts) == 3
    assert waits == [2, 4]


def test_rate_limit_exhaustion_raises_actionable_runtime_error(monkeypatch):
    waits = []

    def generate_content(**_):
        raise RateLimitError("429 RESOURCE_EXHAUSTED")

    client = type(
        "Client",
        (),
        {
            "models": type(
                "Models", (), {"generate_content": staticmethod(generate_content)}
            )()
        },
    )()
    monkeypatch.setattr(gemini, "ClientError", RateLimitError)
    monkeypatch.setattr(gemini.time, "sleep", waits.append)
    monkeypatch.setattr(gemini, "print_warning", lambda _: None)

    try:
        gemini._call_with_retry(client, "prompt")
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

    client = type(
        "Client",
        (),
        {
            "models": type(
                "Models", (), {"generate_content": staticmethod(generate_content)}
            )()
        },
    )()
    monkeypatch.setattr(gemini, "ClientError", RateLimitError)

    try:
        gemini._call_with_retry(client, "prompt")
    except RateLimitError as error:
        assert "400" in str(error)
    else:
        raise AssertionError("Expected non-rate-limit ClientError to propagate")
    assert len(attempts) == 1


def test_generate_readme_uses_client_and_scanned_context(monkeypatch):
    captured = {}

    class FakeModels:
        def generate_content(self, **kwargs):
            captured.update(kwargs)
            return type("Response", (), {"text": "# README"})()

    class FakeClient:
        def __init__(self, api_key):
            captured["api_key"] = api_key
            self.models = FakeModels()

    monkeypatch.setattr(gemini.genai, "Client", FakeClient)
    monkeypatch.setattr(gemini, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(gemini, "scan_codebase", lambda root: {"tree": [], "files": {}})
    monkeypatch.setattr(gemini, "format_codebase_for_prompt", lambda _: "code")
    monkeypatch.setattr(gemini, "format_answers", lambda _: "answers")
    monkeypatch.setattr(gemini, "print_info", lambda _: None)

    assert gemini.generate_readme({"q1": "project"}) == "# README"
    assert captured["api_key"] == "test-key"
    assert "answers" in captured["contents"]
    assert "code" in captured["contents"]
