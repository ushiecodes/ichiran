# Packaging and Installation Verification

## Metadata

- Distribution name: `ichiran`
- Python requirement: `>=3.12`
- Build backend: setuptools
- Console script: `ichiran = "cli:main"`
- Test extra: pytest, pytest-cov, pytest-mock
- Layout: root-level flat Python modules listed in `py-modules`

## Verification commands

The following commands are the reproducible local validation sequence:

```powershell
uv sync --extra test
uv run python -m pip install -e ".[test]"
uv run python -c "import cli, config, display, gemini, interview, prompt, scanner, writer"
uv run ichiran --version
uv build --out-dir .packaging-test
```

## Recorded outcome

- `uv sync --extra test` completed on Python 3.12.12 / Windows and installed the editable project with its declared runtime and test dependencies.
- `uv run python -m pip install -e ".[test]"` successfully installed the project in editable mode.
- Imports for all eight executable modules succeeded.
- `uv run ichiran --version` printed `ichiran v0.1.0`.
- `uv build --out-dir .packaging-test` produced both a source archive and a platform-independent wheel.
- The package metadata test checks both authors, the CLI script, and the optional test dependencies.

## Installation notes

From a checkout, the test extra can be installed with `python -m pip install -e ".[test]"`. For ordinary users, `python -m pip install ichiran` installs from a configured package index. No package-index publication claim is made by this local project verification.
