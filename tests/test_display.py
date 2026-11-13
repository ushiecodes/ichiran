from io import StringIO

from rich.console import Console

import display


def capture_console(monkeypatch):
    output = StringIO()
    monkeypatch.setattr(
        display, "console", Console(file=output, force_terminal=False, width=120)
    )
    return output


def test_banner_and_info_panel_render(monkeypatch):
    output = capture_console(monkeypatch)

    display.print_banner()
    display.print_info_box(cwd="C:\\project", api_key_loaded=False)

    rendered = output.getvalue()
    assert "AI-powered README generator" in rendered
    assert "C:\\project" in rendered
    assert "No API key found" in rendered


def test_info_panel_reports_loaded_key(monkeypatch):
    output = capture_console(monkeypatch)

    display.print_info_box(cwd="C:\\project", api_key_loaded=True)

    assert "API key loaded" in output.getvalue()


def test_display_helpers_and_question_render(monkeypatch):
    output = capture_console(monkeypatch)

    display.print_phase_controls("Phase 1")
    display.print_question("Question?", ["Hint"])
    display.print_rtfm("Help text")
    display.print_layer_prompt()
    display.print_success("Done")
    display.print_warning("Careful")
    display.print_error("Failed")
    display.print_info("Details")
    display.print_audit_report(["finding one", "finding two"])

    rendered = output.getvalue()
    for expected in ("Phase 1", "Question?", "Hint", "Help text", "Done", "finding two"):
        assert expected in rendered
