# Git Collaboration Strategy and Illustrative Contribution Log

## 1. Branching model

The following is a **proposed collaboration workflow**, not a claim that these branches have been created or protected:

- `main`: stable reviewed release branch; protect it from direct pushes when repository settings permit.
- `dev`: integration branch for completed, reviewed features.
- `feature/cli-interview-config`: Hruday's CLI, interview, display, and configuration work.
- `feature/scanner-gemini-writer`: Utkarsh Kamat's scanner, Gemini, prompt, and writer work.
- `test/pytest-suite`: joint test and integration work.

Open pull requests from feature branches to `dev`; run tests and review the traceability impact before merging. Promote a validated release from `dev` to `main`.

## 2. Responsibility split

| Contributor | Planned core ownership | Planned SDLC ownership |
|---|---|---|
| Utkarsh Kamat | `gemini.py`, `prompt.py`, `scanner.py`, `writer.py` | SRS, SDD, integration testing report |
| Hruday | `cli.py`, `config.py`, `display.py`, `interview.py` | SQA plan, test plan/cases, user manual, RTM |
| Joint | End-to-end and packaging tests | Test integration, review, presentation and viva |

This allocation is a plan for equal academic participation; it is not verified by Git author metadata.

## 3. Simulated chronological commit-message exercise

**Important:** The entries below are illustrative project-work messages requested for an academic presentation. They are not actual commits, do not have commit hashes, and must not be presented as repository history or used as authorship evidence. The repository history was inspected separately and currently has only the pre-existing `source code` commit.

| # | Illustrative author | Conventional commit message |
|---:|---|---|
| 1 | Utkarsh Kamat `<work.utkarshkamat@gmail.com>` | `feat(scanner): add allowlisted project file discovery` |
| 2 | Hruday `<hruday@example.com>` | `feat(cli): add command-line entry point and argument parsing` |
| 3 | Utkarsh Kamat `<work.utkarshkamat@gmail.com>` | `feat(scanner): honor ignore rules and skip binary files` |
| 4 | Hruday `<hruday@example.com>` | `feat(config): persist Gemini API key in user config` |
| 5 | Utkarsh Kamat `<work.utkarshkamat@gmail.com>` | `feat(prompt): define README generation instructions` |
| 6 | Hruday `<hruday@example.com>` | `feat(display): render Rich banner and workflow panels` |
| 7 | Utkarsh Kamat `<work.utkarshkamat@gmail.com>` | `feat(gemini): assemble codebase context for generation` |
| 8 | Hruday `<hruday@example.com>` | `feat(interview): add initial project questionnaire` |
| 9 | Utkarsh Kamat `<work.utkarshkamat@gmail.com>` | `fix(scanner): prioritize manifests within context budget` |
| 10 | Hruday `<hruday@example.com>` | `feat(interview): support skip help and quit controls` |
| 11 | Utkarsh Kamat `<work.utkarshkamat@gmail.com>` | `feat(gemini): retry rate-limited requests with backoff` |
| 12 | Hruday `<hruday@example.com>` | `feat(interview): add optional documentation depth layers` |
| 13 | Utkarsh Kamat `<work.utkarshkamat@gmail.com>` | `feat(writer): handle README creation and collisions` |
| 14 | Hruday `<hruday@example.com>` | `fix(config): preserve environment key fallback` |
| 15 | Utkarsh Kamat `<work.utkarshkamat@gmail.com>` | `fix(scanner): enforce exact formatted context character limit` |
| 16 | Hruday `<hruday@example.com>` | `feat(cli): add version and credential reset flags` |
| 17 | Utkarsh Kamat `<work.utkarshkamat@gmail.com>` | `test(scanner): cover ignore binary and size filtering` |
| 18 | Hruday `<hruday@example.com>` | `test(interview): cover multiline input and sentinels` |
| 19 | Utkarsh Kamat `<work.utkarshkamat@gmail.com>` | `test(gemini): mock rate limits and client failures` |
| 20 | Hruday `<hruday@example.com>` | `test(config): isolate key storage in temporary directories` |
| 21 | Utkarsh Kamat `<work.utkarshkamat@gmail.com>` | `test(writer): verify overwrite append and cancel behavior` |
| 22 | Hruday `<hruday@example.com>` | `test(cli): exercise flags and cancelled interview flow` |
| 23 | Utkarsh Kamat `<work.utkarshkamat@gmail.com>` | `docs(sdlc): specify requirements and component architecture` |
| 24 | Hruday `<hruday@example.com>` | `docs(quality): add test plan traceability and user manual` |
| 25 | Utkarsh Kamat `<work.utkarshkamat@gmail.com>` | `test(integration): verify mocked generation pipeline` |
| 26 | Hruday `<hruday@example.com>` | `docs(presentation): add V-model slides and viva questions` |

For genuine contribution evidence, create branches and commits only as each student performs and reviews the described work; do not backdate or attribute commits to another person.
