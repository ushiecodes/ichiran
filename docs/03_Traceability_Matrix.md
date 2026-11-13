# Requirements Traceability Matrix (RTM)

Each functional requirement maps to its primary source module and at least one concrete automated test.

| Requirement | Source module(s) | Verification test(s) |
|---|---|---|
| FR-1 CLI flags and executable metadata | `cli.py`, `pyproject.toml` | `test_version_flag_prints_installed_version`, `test_reset_flag_resets_key_without_starting_interview`, `test_project_declares_authors_test_extra_and_cli_entry_point` |
| FR-2 API key load, save, reset, prompt | `config.py` | `test_save_and_load_api_key`, `test_load_api_key_falls_back_to_environment`, `test_prompt_for_api_key_saves_stripped_input`, `test_reset_removes_saved_key` |
| FR-3 Three-phase progressive interview | `interview.py` | `test_layer_parser_and_interview_completion`, `test_interview_runs_both_optional_layers`, `test_interview_can_add_layer_three_after_layer_two` |
| FR-4 Interview sentinel controls and quit | `interview.py` | `test_read_single_handles_skip_tldr_rtfm_and_required_answers`, `test_read_multiline_handles_content_and_special_commands`, `test_quit_confirmation_and_question_runner` |
| FR-5 Text whitelist and `.gitignore` filtering | `scanner.py` | `test_scan_applies_whitelist_binary_and_ignore_rules`, `test_gitignore_patterns_match_nested_windows_paths` |
| FR-6 Binary, sensitive-name, and file-size checks | `scanner.py` | `test_scan_applies_whitelist_binary_and_ignore_rules`, `test_scan_marks_oversized_file`, `test_binary_read_error_is_treated_as_binary` |
| FR-7 Priority ordering and total context cap | `scanner.py` | `test_priority_files_are_included_before_other_files`, `test_format_codebase_preserves_sections_and_caps_characters`, `test_format_codebase_caps_oversized_file_tree` |
| FR-8 Gemini prompt construction | `gemini.py`, `prompt.py`, `interview.py`, `scanner.py` | `test_generate_readme_uses_client_and_scanned_context`, `test_cli_to_readme_pipeline_with_mocked_gemini` |
| FR-9 Retry 429 only and propagate other errors | `gemini.py` | `test_rate_limit_retries_with_exponential_backoff`, `test_rate_limit_exhaustion_raises_actionable_runtime_error`, `test_non_rate_limit_client_error_is_not_retried` |
| FR-10 Clean and create README | `writer.py` | `test_new_readme_is_written_and_markdown_wrapping_is_cleaned`, `test_clean_output_handles_plain_text_and_fence_only` |
| FR-11 Collision behavior | `writer.py` | `test_existing_readme_can_be_overwritten`, `test_existing_readme_can_be_appended`, `test_existing_readme_can_be_cancelled`, `test_invalid_collision_choice_does_not_change_readme` |
| FR-12 Automated, non-networked testing | `tests/` | `test_cli_to_readme_pipeline_with_mocked_gemini`, `test_generate_readme_uses_client_and_scanned_context`; test configuration paths and `builtins.input` are isolated in tests. |

## Coverage of non-functional requirements

| Requirement | Evidence |
|---|---|
| NFR-1/NFR-2 resource limits | Scanner file-size and total-character boundary tests. |
| NFR-3 platform support | Windows nested `.gitignore` path test and path normalization to POSIX form before matching. Linux/macOS execution remains a CI or evaluator validation item. |
| NFR-4 visible failures | Rate-limit exhaustion and non-rate-limit propagation tests. |
| NFR-5 secret handling | Scanner exclusion test and isolated config filesystem tests; manual review is still required for arbitrary secrets in eligible source files. |
| NFR-6 testability | Mocked API, patched input, temporary directories, packaging test, and coverage gate. |
