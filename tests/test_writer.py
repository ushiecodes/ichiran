import writer


def test_new_readme_is_written_and_markdown_wrapping_is_cleaned(tmp_path):
    writer.write_readme("```markdown\nnoise\n# Title\nBody\n```", str(tmp_path))

    assert (tmp_path / "README.md").read_text(encoding="utf-8") == "# Title\nBody"


def test_existing_readme_can_be_overwritten(monkeypatch, tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("old", encoding="utf-8")
    monkeypatch.setattr("builtins.input", lambda _: "o")

    writer.write_readme("# New", str(tmp_path))

    assert readme.read_text(encoding="utf-8") == "# New"


def test_existing_readme_can_be_appended(monkeypatch, tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("old", encoding="utf-8")
    monkeypatch.setattr("builtins.input", lambda _: "a")

    writer.write_readme("new", str(tmp_path))

    assert readme.read_text(encoding="utf-8") == "old\n\nnew"


def test_existing_readme_can_be_cancelled(monkeypatch, tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("old", encoding="utf-8")
    warnings = []
    monkeypatch.setattr("builtins.input", lambda _: "c")
    monkeypatch.setattr(writer, "print_warning", warnings.append)

    writer.write_readme("new", str(tmp_path))

    assert readme.read_text(encoding="utf-8") == "old"
    assert warnings == ["Cancelled. README.md was not modified."]


def test_invalid_collision_choice_does_not_change_readme(monkeypatch, tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("old", encoding="utf-8")
    warnings = []
    monkeypatch.setattr("builtins.input", lambda _: "x")
    monkeypatch.setattr(writer, "print_warning", warnings.append)

    writer.write_readme("new", str(tmp_path))

    assert readme.read_text(encoding="utf-8") == "old"
    assert warnings == ["Invalid choice. README.md was not modified."]


def test_clean_output_handles_plain_text_and_fence_only():
    assert writer._clean_output("  # Title\nBody  ") == "# Title\nBody"
    assert writer._clean_output("```\nprint(1)\n```") == "print(1)"
