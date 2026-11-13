# Software Quality Assurance (SQA) Plan

**Project:** Ichiran 0.1.0  
**Quality owners:** Hruday (CLI/configuration/UI/test specification), Utkarsh Kamat (scanner/Gemini/writer/integration specification)

## 1. Quality objectives

1. Install the CLI from declared project metadata and invoke its console entry point.
2. Keep automated tests deterministic and safe: no real Gemini requests, no real home-directory writes, no unattended input.
3. Meet or exceed 85% measured line coverage for application modules.
4. Preserve explicit failure behavior for remote API failures and README write choices.
5. Keep requirements, modules, and tests traceable in the [RTM](03_Traceability_Matrix.md).

## 2. Assurance activities

| Activity | Method | Completion evidence |
|---|---|---|
| Requirements review | Cross-check SRS against current CLI and module behavior. | SRS and RTM reviewed together. |
| Design review | Review module boundaries, data flow, external Gemini boundary, and error handling. | SDD diagrams and interface table. |
| Static quality | Run Ruff as a development tool and review diagnostics before release. | `uv run ruff check .` passed on the completed source and tests. |
| Unit/integration tests | Run the documented Pytest command, with the coverage threshold enabled. | Pytest summary and coverage table. |
| Packaging check | Install the editable project with the test extra and exercise the console script. | Packaging verification record in `docs/08_Packaging_Installation_Verification.md`. |
| Security handling | Check secret exclusions, mocked API boundary, and config storage limitations. | Scanner/config tests and security notes in the user manual. |

## 3. Defect management

Record each defect with a reproducible command or input, expected behavior, actual behavior, severity, owner, and linked requirement/test. Fixes should add or update a focused regression test. Do not mark a defect resolved solely because the CLI exits successfully.

## 4. Review and release criteria

- No known failing focused test.
- Coverage command passes with at least 85%.
- `ichiran --version` and `ichiran --reset` work without entering the interactive interview.
- Packaging installs the flat modules and command script.
- Documentation describes tested behavior and labels simulation or unverified deployment claims.
- No API key, `.env.local`, generated virtual environment, or machine-specific credential file enters version control.

## 5. Responsibilities

- **Utkarsh Kamat:** scanner, prompt/generation, writer, integration evidence, SRS/SDD and integration report.
- **Hruday:** CLI, config, interview/display, test specification and user manual.
- **Joint:** requirements review, end-to-end mocked test, RTM review, final presentation, and release approval.

Ownership describes planned academic responsibility, not proof of historical contribution; the repository contains no verified per-student commit history for this assignment.
