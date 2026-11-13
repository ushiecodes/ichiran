import importlib
import json
from pathlib import Path

import config


def test_default_config_path_uses_home_directory(monkeypatch, tmp_path):
    original_config_dir = config.CONFIG_DIR
    original_config_file = config.CONFIG_FILE
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    importlib.reload(config)

    assert config.CONFIG_DIR == tmp_path / ".config" / "ichiran"
    assert config.CONFIG_FILE == config.CONFIG_DIR / "config.json"
    config.CONFIG_DIR = original_config_dir
    config.CONFIG_FILE = original_config_file


def set_config_paths(monkeypatch, tmp_path):
    config_dir = tmp_path / "config"
    config_file = config_dir / "config.json"
    monkeypatch.setattr(config, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(config, "CONFIG_FILE", config_file)
    return config_dir, config_file


def test_save_and_load_api_key(monkeypatch, tmp_path):
    config_dir, config_file = set_config_paths(monkeypatch, tmp_path)

    config.save_api_key("secret")

    assert config_dir.is_dir()
    assert json.loads(config_file.read_text(encoding="utf-8")) == {
        "api_key": "secret"
    }
    assert config.load_api_key() == "secret"


def test_load_api_key_falls_back_to_environment(monkeypatch, tmp_path):
    set_config_paths(monkeypatch, tmp_path)
    monkeypatch.setenv("API_KEY", "environment-secret")

    assert config.load_api_key() == "environment-secret"


def test_saved_api_key_takes_precedence_over_environment(monkeypatch, tmp_path):
    _, config_file = set_config_paths(monkeypatch, tmp_path)
    config_file.parent.mkdir()
    config_file.write_text('{"api_key": "saved"}', encoding="utf-8")
    monkeypatch.setenv("API_KEY", "environment")

    assert config.load_api_key() == "saved"


def test_prompt_for_api_key_saves_stripped_input(monkeypatch, tmp_path):
    set_config_paths(monkeypatch, tmp_path)
    monkeypatch.setattr("builtins.input", lambda _: "  entered-key  ")

    assert config.prompt_for_api_key() == "entered-key"
    assert config.load_api_key() == "entered-key"


def test_get_api_key_returns_existing_key_without_prompt(monkeypatch):
    monkeypatch.setattr(config, "load_api_key", lambda: "existing")
    monkeypatch.setattr(
        config, "prompt_for_api_key", lambda: (_ for _ in ()).throw(AssertionError())
    )

    assert config.get_api_key() == "existing"


def test_get_api_key_prompts_when_key_is_missing(monkeypatch):
    monkeypatch.setattr(config, "load_api_key", lambda: None)
    monkeypatch.setattr(config, "prompt_for_api_key", lambda: "entered")

    assert config.get_api_key() == "entered"


def test_reset_removes_saved_key(monkeypatch, tmp_path):
    _, config_file = set_config_paths(monkeypatch, tmp_path)
    config_file.parent.mkdir()
    config_file.write_text('{"api_key": "saved"}', encoding="utf-8")
    messages = []
    monkeypatch.setattr(config, "print_success", messages.append)

    config.reset_api_key()

    assert not config_file.exists()
    assert messages == ["API key removed."]


def test_reset_reports_missing_saved_key(monkeypatch, tmp_path):
    set_config_paths(monkeypatch, tmp_path)
    messages = []
    monkeypatch.setattr(config, "print_info", messages.append)

    config.reset_api_key()

    assert messages == ["No saved API key was found."]
