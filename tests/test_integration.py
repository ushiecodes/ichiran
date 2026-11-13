import cli
import gemini


def test_cli_to_readme_pipeline_with_mocked_gemini(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["ichiran"])
    monkeypatch.setattr(cli, "print_banner", lambda: None)
    monkeypatch.setattr(cli, "load_api_key", lambda: "test-key")
    monkeypatch.setattr(cli, "print_info_box", lambda **kwargs: None)
    monkeypatch.setattr(cli, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(cli, "run_interview", lambda: {"q1": "A test project"})
    monkeypatch.setattr(cli, "print_success", lambda _: None)
    monkeypatch.setattr(gemini, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(gemini, "print_info", lambda _: None)

    class FakeModels:
        def generate_content(self, **kwargs):
            assert "A test project" in kwargs["contents"]
            return type("Response", (), {"text": "```markdown\n# Test README\n```"})()

    class FakeClient:
        def __init__(self, api_key):
            assert api_key == "test-key"
            self.models = FakeModels()

    monkeypatch.setattr(gemini.genai, "Client", FakeClient)

    cli.main()

    assert (tmp_path / "README.md").read_text(encoding="utf-8") == "# Test README"
