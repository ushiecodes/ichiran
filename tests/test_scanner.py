from pathlib import Path

import scanner


def test_scan_applies_whitelist_binary_and_ignore_rules(project_dir):
    (project_dir / "image.png").write_bytes(b"not source")
    (project_dir / "data.txt").write_bytes(b"text\x00with binary marker")
    (project_dir / ".env.local").write_text("API_KEY=secret", encoding="utf-8")
    nested = project_dir / "ignored-dir"
    nested.mkdir()
    (nested / "hidden.py").write_text("print('hidden')", encoding="utf-8")
    (project_dir / ".gitignore").write_text(
        "ignored.txt\nignored-dir/\n", encoding="utf-8"
    )

    result = scanner.scan_codebase(str(project_dir))

    assert "main.py" in result["files"]
    assert "ignored.txt" not in result["files"]
    assert "image.png" not in result["files"]
    assert "data.txt" not in result["files"]
    assert ".env.local" not in result["files"]
    assert not any("ignored-dir" in path for path in result["tree"])


def test_scan_records_tree_for_unsupported_text_suffix(project_dir):
    (project_dir / "notes.bin").write_text("plain text but not whitelisted", encoding="utf-8")

    result = scanner.scan_codebase(str(project_dir))

    assert "notes.bin" in result["tree"]
    assert "notes.bin" not in result["files"]


def test_scan_marks_oversized_file(monkeypatch, project_dir):
    (project_dir / "large.py").write_text("12345", encoding="utf-8")
    monkeypatch.setattr(scanner, "MAX_FILE_SIZE_KB", 0)

    result = scanner.scan_codebase(str(project_dir))

    assert result["files"]["large.py"] == "[SKIPPED: Exceeds 0KB limit]"

    (project_dir / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    result = scanner.scan_codebase(str(project_dir))
    assert result["files"]["pyproject.toml"] == "[SKIPPED: Exceeds 0KB limit]"


def test_gitignore_patterns_match_nested_windows_paths(project_dir):
    nested = project_dir / "build" / "generated"
    nested.mkdir(parents=True)
    ignored_file = nested / "artifact.py"
    ignored_file.write_text("ignored", encoding="utf-8")
    (project_dir / ".gitignore").write_text("build/\n", encoding="utf-8")

    result = scanner.scan_codebase(str(project_dir))

    assert not any(path.startswith("build/") for path in result["tree"])


def test_priority_files_are_included_before_other_files(project_dir):
    (project_dir / "z_extra.txt").write_text("extra", encoding="utf-8")
    (project_dir / "pyproject.toml").write_text("[project]\n", encoding="utf-8")

    result = scanner.scan_codebase(str(project_dir))

    assert list(result["files"]).index("pyproject.toml") < list(result["files"]).index(
        "z_extra.txt"
    )


def test_format_codebase_preserves_sections_and_caps_characters(monkeypatch):
    monkeypatch.setattr(scanner, "MAX_TOTAL_CHARS", 180)
    result = scanner.format_codebase_for_prompt(
        {"tree": ["main.py"], "files": {"main.py": "x" * 1000}}
    )

    assert len(result) <= 180
    assert "=== PROJECT FILE TREE ===" in result
    assert "=== FILE CONTENTS ===" in result
    assert "TRUNCATED AT BUDGET LIMIT" in result


def test_format_codebase_caps_oversized_file_tree(monkeypatch):
    monkeypatch.setattr(scanner, "MAX_TOTAL_CHARS", 60)
    result = scanner.format_codebase_for_prompt(
        {"tree": [f"file-{index}.py" for index in range(100)], "files": {}}
    )

    assert len(result) <= 60


def test_binary_read_error_is_treated_as_binary(monkeypatch, tmp_path):
    source = tmp_path / "source.py"

    class Unreadable:
        def __enter__(self):
            raise OSError("permission denied")

        def __exit__(self, *_):
            return False

    monkeypatch.setattr(Path, "open", lambda *args, **kwargs: Unreadable())

    assert scanner.is_binary_file(source)


def test_scan_marks_file_unreadable_after_binary_check(monkeypatch, project_dir):
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("permission denied")),
    )

    result = scanner.scan_codebase(str(project_dir))

    assert result["files"]["main.py"] == "[unreadable]"
