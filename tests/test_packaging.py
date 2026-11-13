import tomllib
from pathlib import Path


def test_project_declares_authors_test_extra_and_cli_entry_point():
    project = tomllib.loads(
        Path("pyproject.toml").read_text(encoding="utf-8")
    )["project"]

    assert {author["name"] for author in project["authors"]} == {
        "Utkarsh Kamat",
        "Hruday",
    }
    assert project["scripts"]["ichiran"] == "cli:main"
    assert {"pytest", "pytest-cov", "pytest-mock"} <= {
        dependency.split(">")[0] for dependency in project["optional-dependencies"]["test"]
    }
