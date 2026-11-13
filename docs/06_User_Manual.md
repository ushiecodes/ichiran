# Ichiran User Manual

## 1. Purpose and prerequisites

Ichiran interviews you about a local project, scans eligible project text, asks Google Gemini to draft a README, and writes the result in the current directory. Use Python 3.12+, a terminal, network access, and a Gemini API key.

## 2. Install and launch

### Install from a package index

```powershell
python -m pip install ichiran
```

### Install this checkout for development

From the repository root:

```powershell
uv sync --extra test
uv run ichiran --version
```

For a pip editable install:

```powershell
python -m pip install -e ".[test]"
```

Run the command from the project you want to document:

```powershell
ichiran
```

## 3. API key setup and management

Ichiran checks its user config JSON first, then `API_KEY` from the process environment. If neither provides a key, it prompts and saves it. The JSON file stores the key as plaintext; rely on the current user's home-directory access controls and do not share the file.

To clear the saved key:

```powershell
ichiran --reset
```

An `.env.local` file can be read by python-dotenv during development. Do not commit it.

## 4. Interview controls

- **SKIP:** omit an optional answer so the generator may infer it from project context.
- **TLDR:** use the built-in generic answer for the current question.
- **RTFM:** show help and examples for the question.
- **QUIT:** ask for confirmation; answering Y cancels the README run, while N resumes the current question.
- **END:** finish a multiline answer.
- **done / layer 2 / layer 3 / more:** choose optional depth after the initial five-question phase.

## 5. Scanner and privacy

The scanner respects built-in exclusions and root `.gitignore` patterns, prioritizes recognized manifest/entry-point files, limits individual files, and truncates formatted context at the configured character budget. It ignores common virtual environments, build output, lock files, binaries, `.env`, and `.env.*`.

These are filters, not a secret detector. Review eligible source text before running the tool. Text selected for context is sent to Google Gemini. Do not scan code or data you are not permitted to disclose to that service.

## 6. README collision choices

If `README.md` already exists, choose:

- **O** to overwrite it.
- **A** to append generated Markdown.
- **C** to leave the existing file unchanged.

Any other input leaves the file unchanged.

## 7. Common issues

| Symptom | Action |
|---|---|
| CLI not found | Activate the environment where the package was installed, or reinstall with `python -m pip install -e ".[test]"`. |
| API key rejected | Reset the saved key with `ichiran --reset`, then enter a valid Gemini API key. |
| Rate-limit failure | Wait for quota recovery or use a key with available quota; the client retries 429 errors before raising. |
| Existing README prompt appears | Choose O, A, or C; no file changes occur for an invalid choice. |

## 8. Development and support

Run tests using the command in the [Test Plan](04_Test_Plan_and_Report.md). See the [SRS](01_SRS_Requirements_Specification.md), [SDD](02_System_Design_Document.md), and [traceability matrix](03_Traceability_Matrix.md) for technical details. Report reproducible failures with the exact command, platform, Python version, expected result, and actual result.
