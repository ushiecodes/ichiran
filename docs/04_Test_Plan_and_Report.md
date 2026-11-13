# Test Plan and Pytest Test Case Specification

**Method:** V-Model verification and validation  
**Test framework:** Pytest with pytest-cov and pytest-mock declared in the `test` extra.

## 1. Verification strategy

| V-Model design level | Corresponding test level | Verification |
|---|---|---|
| Business/user needs | Acceptance | CLI paths and mocked full generation pipeline. |
| System requirements | System | CLI, interview flow, scanner, collision handling, and output behavior. |
| Architecture | Integration | Scanner/context, answer formatting, Gemini client, and writer integration with a fake client. |
| Module design | Unit | Config, display, interview parsing, scanner, writer, and retry tests. |

## 2. Test safety and isolation

- Tests replace `genai.Client`; no test calls Google Gemini or needs a valid API key.
- Tests patch `builtins.input` or Rich console input; they never wait for an evaluator's terminal.
- Config tests mock `Path.home()` when checking its default path and redirect config constants to `tmp_path` for file operations; no test writes to the real home config file.
- Scanner and writer tests operate only in pytest temporary directories.
- Backoff tests patch `time.sleep`; they do not wait in real time.

## 3. Test case inventory

| Test file | Coverage |
|---|---|
| `tests/test_cli.py` | Installed-version output, fallback, reset-only behavior, normal orchestration, and interview cancellation. |
| `tests/test_config.py` | Config save/load, environment fallback, precedence, input prompt, key reset, and absent-key behavior. |
| `tests/test_display.py` | Banner, information panel, phase controls, question/help rendering, and status helpers. |
| `tests/test_interview.py` | Single-line and multiline controls, required answers, quit confirmation, optional layers, cancellation, and formatting. |
| `tests/test_scanner.py` | Whitelist, binary and secret exclusions, `.gitignore`, priority ordering, file-size and context limits, and read errors. |
| `tests/test_writer.py` | New output, fence cleanup, overwrite, append, cancel, and invalid collision input. |
| `tests/test_gemini.py` | 429 retry/backoff, retry exhaustion, non-429 propagation, and prompt construction with a fake client. |
| `tests/test_integration.py` | CLI-to-README flow with a mocked Gemini response. |
| `tests/test_packaging.py` | Authors, command script, and optional test dependency metadata. |

## 4. Execution and result

Run the test suite with coverage enforcement:

```powershell
uv sync --extra test
uv run pytest -q --cov=cli --cov=config --cov=display --cov=gemini --cov=interview --cov=prompt --cov=scanner --cov=writer --cov-report=term-missing --cov-fail-under=85
```

**Recorded verification:** 54 tests passed in 5.05 seconds; aggregate source coverage was **96%**, above the 85% threshold. The run used Python 3.12.12 on Windows and passed the `--cov-fail-under=85` gate. The suite did not make real API calls.

| Module | Line coverage |
|---|---:|
| `cli.py` | 97% |
| `config.py` | 100% |
| `display.py` | 100% |
| `gemini.py` | 100% |
| `interview.py` | 93% |
| `prompt.py` | 100% |
| `scanner.py` | 99% |
| `writer.py` | 100% |
| **Total** | **96%** |

## 5. Known limits

- This report records a local Windows run; Linux and macOS still require execution in those environments.
- Coverage measures executed source lines; it does not prove that Gemini-generated prose is factually correct.
- The scanner excludes named categories, but cannot detect every secret embedded in an otherwise eligible text file.
- API availability, quotas, and remote response quality remain outside the local test boundary.
