# System Integration Testing Report

**System under test:** Ichiran CLI 0.1.0  
**Environment:** Windows, Python 3.12.12  
**Execution:** Pytest, local temporary directories, fake Gemini client  
**External API calls:** None

## 1. Integration scope

The primary path exercises CLI orchestration, interview answers, Gemini prompt assembly, scanner output, mocked external generation, Markdown cleanup, and README writing. The API client is replaced with an in-memory fake that checks the user answer appears in the prompt and returns a deterministic Markdown response.

## 2. Integration case

| Case | Expected result | Observed result |
|---|---|---|
| `test_cli_to_readme_pipeline_with_mocked_gemini` | CLI invokes generation with interview answers; fake response is cleaned and written as README.md. | Passed; resulting file contains `# Test README`; no live service or interactive input. |
| `test_generate_readme_uses_client_and_scanned_context` | Gemini boundary receives configured key, formatted answers, and scanner context. | Passed with a fake client. |
| Scanner-to-prompt tests | Ignore filters and context budget apply before model call. | Passed in scanner unit tests. |
| Writer collision tests | Existing output is overwritten/appended/cancelled only per user choice. | Passed in writer unit tests. |

## 3. V-Model test relationship

The component data flow (scanner and interview → prompt assembly/Gemini → writer) is validated by the mocked integration case. Unit tests cover each module boundary; CLI tests cover end-user flags and cancellation. The test traceability table is in the [RTM](03_Traceability_Matrix.md).

## 4. Result

The recorded complete suite passed **54 tests** and reached **96% line coverage**, exceeding the 85% project gate. Pytest was run with coverage fail-under enabled. No live Gemini calls were made. See the [test plan and report](04_Test_Plan_and_Report.md) for the exact command and test partition.

## 5. Limitations

This is a local deterministic integration test, not a live-service certification. It does not measure remote latency, API quota behavior, or the factual quality of Gemini-generated content. Linux and macOS runs remain to be collected.
