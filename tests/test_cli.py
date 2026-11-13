import cli


def test_version_flag_prints_installed_version(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["ichiran", "--version"])
    monkeypatch.setattr("importlib.metadata.version", lambda _: "9.8.7")

    cli.main()

    assert "v9.8.7" in capsys.readouterr().out


def test_version_flag_uses_fallback_when_package_metadata_is_missing(
    monkeypatch, capsys
):
    def missing_version(_):
        from importlib.metadata import PackageNotFoundError

        raise PackageNotFoundError("ichiran")

    monkeypatch.setattr("sys.argv", ["ichiran", "--version"])
    monkeypatch.setattr("importlib.metadata.version", missing_version)

    cli.main()

    assert "v0.1.0" in capsys.readouterr().out


def test_version_flag_does_not_hide_unexpected_metadata_errors(monkeypatch):
    monkeypatch.setattr("sys.argv", ["ichiran", "--version"])
    monkeypatch.setattr(
        "importlib.metadata.version",
        lambda _: (_ for _ in ()).throw(RuntimeError("metadata failure")),
    )

    try:
        cli.main()
    except RuntimeError as error:
        assert str(error) == "metadata failure"
    else:
        raise AssertionError("Unexpected metadata failures must remain visible")


def test_reset_flag_resets_key_without_starting_interview(monkeypatch):
    called = []
    monkeypatch.setattr("sys.argv", ["ichiran", "--reset"])
    monkeypatch.setattr(cli, "reset_api_key", lambda: called.append("reset"))
    monkeypatch.setattr(
        cli, "print_banner", lambda: (_ for _ in ()).throw(AssertionError())
    )

    cli.main()

    assert called == ["reset"]


def test_normal_launch_runs_interview_generation_and_writer(monkeypatch):
    calls = []
    monkeypatch.setattr("sys.argv", ["ichiran"])
    monkeypatch.setattr(cli, "print_banner", lambda: calls.append("banner"))
    monkeypatch.setattr(cli, "load_api_key", lambda: "saved")
    monkeypatch.setattr(cli, "print_info_box", lambda **kwargs: None)
    monkeypatch.setattr(cli, "get_api_key", lambda: "saved")
    monkeypatch.setattr(cli, "run_interview", lambda: {"q1": "project"})
    monkeypatch.setattr(
        cli, "generate_readme", lambda answers: calls.append(answers) or "# README"
    )
    monkeypatch.setattr(cli, "write_readme", lambda content: calls.append(content))
    monkeypatch.setattr(cli, "print_success", lambda message: calls.append(message))

    cli.main()

    assert calls == [
        "banner",
        {"q1": "project"},
        "# README",
        "Done. Your README is ready.",
    ]


def test_cancelled_interview_does_not_generate(monkeypatch):
    warnings = []
    monkeypatch.setattr("sys.argv", ["ichiran"])
    monkeypatch.setattr(cli, "print_banner", lambda: None)
    monkeypatch.setattr(cli, "load_api_key", lambda: "saved")
    monkeypatch.setattr(cli, "print_info_box", lambda **kwargs: None)
    monkeypatch.setattr(cli, "get_api_key", lambda: "saved")
    monkeypatch.setattr(cli, "run_interview", lambda: None)
    monkeypatch.setattr(
        cli, "generate_readme", lambda _: (_ for _ in ()).throw(AssertionError())
    )
    monkeypatch.setattr(cli, "print_warning", warnings.append)

    cli.main()

    assert warnings == ["Interview cancelled. No README was generated."]
