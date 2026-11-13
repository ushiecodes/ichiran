import interview


def test_read_single_handles_skip_tldr_rtfm_and_required_answers(monkeypatch):
    responses = iter(["", "SKIP"])
    monkeypatch.setattr("builtins.input", lambda *_: next(responses))

    assert interview._read_single("q1") == interview.GENERIC_ANSWERS["q1"]

    responses = iter(["", "required answer"])
    monkeypatch.setattr("builtins.input", lambda *_: next(responses))
    assert interview._read_single("q1", required=True) == "required answer"

    responses = iter(["RTFM", "answer"])
    monkeypatch.setattr("builtins.input", lambda *_: next(responses))
    monkeypatch.setattr(interview, "print_info", lambda _: None)
    assert interview._read_single("q1") == "answer"

    responses = iter(["TLDR"])
    monkeypatch.setattr("builtins.input", lambda *_: next(responses))
    assert interview._read_single("q1") == interview.GENERIC_ANSWERS["q1"]

    help_shown = []
    responses = iter(["RTFM", "answer"])
    monkeypatch.setattr("builtins.input", lambda *_: next(responses))
    monkeypatch.setattr(interview, "print_rtfm", help_shown.append)
    assert interview._read_single("q1", rtfm="help") == "answer"
    assert help_shown == ["help"]

    responses = iter(["SKIP", "required answer"])
    monkeypatch.setattr("builtins.input", lambda *_: next(responses))
    assert interview._read_single("q1", required=True) == "required answer"


def test_read_multiline_handles_content_and_special_commands(monkeypatch):
    responses = iter(["first line", "second line", "END"])
    monkeypatch.setattr("builtins.input", lambda: next(responses))
    assert interview._read_multiline("q2") == "first line\nsecond line"

    responses = iter(["RTFM", "notes", "END"])
    shown = []
    monkeypatch.setattr("builtins.input", lambda: next(responses))
    monkeypatch.setattr(interview, "print_rtfm", shown.append)
    assert interview._read_multiline("q2", rtfm="help") == "notes"
    assert shown == ["help"]

    responses = iter(["SKIP"])
    monkeypatch.setattr("builtins.input", lambda: next(responses))
    assert interview._read_multiline("q2") == interview.SKIP_KEYWORD

    responses = iter(["TLDR"])
    monkeypatch.setattr("builtins.input", lambda: next(responses))
    assert interview._read_multiline("q2") == interview.GENERIC_ANSWERS["q2"]

    responses = iter(["SKIP", "required answer", "END"])
    monkeypatch.setattr("builtins.input", lambda: next(responses))
    assert interview._read_multiline("q2", required=True) == "required answer"

    responses = iter(["END", "answer", "END"])
    monkeypatch.setattr("builtins.input", lambda: next(responses))
    assert interview._read_multiline("q2", required=True) == "answer"

    responses = iter(["RTFM", "answer", "END"])
    monkeypatch.setattr("builtins.input", lambda: next(responses))
    monkeypatch.setattr(interview, "print_info", lambda _: None)
    assert interview._read_multiline("q2") == "answer"

    responses = iter(["QUIT"])
    monkeypatch.setattr("builtins.input", lambda: next(responses))
    assert interview._read_multiline("q2") == interview.QUIT_KEYWORD


def test_quit_confirmation_and_question_runner(monkeypatch):
    responses = iter(["QUIT", "N", "answer"])
    monkeypatch.setattr("builtins.input", lambda *_: next(responses))
    questions = [
        {
            "key": "q1",
            "text": "Question",
            "hints": [],
            "multiline": False,
            "required": False,
        }
    ]

    assert interview._run_questions(questions, {}) == {"q1": "answer"}

    responses = iter(["QUIT", "Y"])
    monkeypatch.setattr("builtins.input", lambda *_: next(responses))
    assert interview._run_questions(questions, {}) is interview.QUIT_SENTINEL


def test_question_runner_records_skip_flags_and_generic_answers(monkeypatch):
    questions = [
        {
            "key": "q21",
            "text": "Audit?",
            "hints": [],
            "multiline": False,
            "required": False,
            "skippable_flag": "q21_skipped",
        }
    ]
    monkeypatch.setattr("builtins.input", lambda *_: "SKIP")
    answers = {}
    assert interview._run_questions(questions, answers) is answers
    assert answers == {"q21_skipped": True}

    monkeypatch.setattr(
        interview, "_read_single", lambda *args, **kwargs: interview.GENERIC_ANSWERS["q21"]
    )
    answers = {}
    interview._run_questions(questions, answers)
    assert answers == {
        "q21": interview.GENERIC_ANSWERS["q21"],
        "q21_skipped": True,
    }


def test_layer_parser_and_interview_completion(monkeypatch):
    assert interview._parse_layer_intent("more") == ["layer2", "layer3"]
    assert interview._parse_layer_intent("usage and deployment") == [
        "layer2",
        "layer3",
    ]
    assert interview._parse_layer_intent("something else") == []

    monkeypatch.setattr(interview, "run_phase_one", lambda answers: answers)
    monkeypatch.setattr(interview, "_ask_layer_prompt", lambda: "done")
    assert interview.run_interview() == {}


def test_interview_returns_none_when_user_confirms_quit(monkeypatch):
    monkeypatch.setattr(interview, "run_phase_one", lambda _: interview.QUIT_SENTINEL)

    assert interview.run_interview() is None


def test_interview_runs_both_optional_layers(monkeypatch):
    monkeypatch.setattr(interview, "run_phase_one", lambda answers: answers)
    monkeypatch.setattr(interview, "_ask_layer_prompt", lambda: "more")
    monkeypatch.setattr(interview, "run_phase_two", lambda answers: answers)
    monkeypatch.setattr(interview, "run_phase_three", lambda answers: answers)

    assert interview.run_interview() == {}


def test_interview_clarifies_unclear_layer_choice(monkeypatch):
    answers = {"q1": "summary"}
    monkeypatch.setattr(interview, "run_phase_one", lambda _: answers)
    monkeypatch.setattr(interview, "_ask_layer_prompt", lambda: "unclear")
    monkeypatch.setattr(interview.console, "input", lambda _: "no thanks")

    assert interview.run_interview() is answers


def test_interview_can_add_layer_three_after_layer_two(monkeypatch):
    answers = {}
    prompts = iter(["layer 2", "layer 3"])
    monkeypatch.setattr(interview, "run_phase_one", lambda _: answers)
    monkeypatch.setattr(interview, "_ask_layer_prompt", lambda: next(prompts))
    monkeypatch.setattr(interview, "run_phase_two", lambda result: result)
    monkeypatch.setattr(interview, "run_phase_three", lambda result: result)

    assert interview.run_interview() is answers


def test_phase_runners_collect_all_question_groups(monkeypatch):
    monkeypatch.setattr(
        interview, "_read_single", lambda key, **kwargs: f"answer-{key}"
    )
    monkeypatch.setattr(
        interview, "_read_multiline", lambda key, **kwargs: f"answer-{key}"
    )

    phase_one = {}
    assert interview.run_phase_one(phase_one) is phase_one
    assert {f"q{index}" for index in range(1, 6)} <= phase_one.keys()

    phase_two = {}
    assert interview.run_phase_two(phase_two) is phase_two
    assert {f"q{index}" for index in range(6, 17)} <= phase_two.keys()

    phase_three = {}
    assert interview.run_phase_three(phase_three) is phase_three
    assert {f"q{index}" for index in range(17, 31)} <= phase_three.keys()
    assert phase_three["q21_skipped"] is False


def test_phase_runners_propagate_confirmed_quit(monkeypatch):
    monkeypatch.setattr(
        interview, "_run_questions", lambda *_: interview.QUIT_SENTINEL
    )
    assert interview.run_phase_one({}) is interview.QUIT_SENTINEL
    assert interview.run_phase_two({}) is interview.QUIT_SENTINEL
    assert interview.run_phase_three({}) is interview.QUIT_SENTINEL


def test_layer_prompt_normalizes_console_input(monkeypatch):
    monkeypatch.setattr(interview, "print_layer_prompt", lambda: None)
    monkeypatch.setattr(interview.console, "input", lambda _: "  MORE  ")

    assert interview._ask_layer_prompt() == "more"


def test_interview_completes_after_layer_two_or_cancels_layer_three(monkeypatch):
    answers = {}
    prompts = iter(["layer 2", "done"])
    monkeypatch.setattr(interview, "run_phase_one", lambda _: answers)
    monkeypatch.setattr(interview, "_ask_layer_prompt", lambda: next(prompts))
    monkeypatch.setattr(interview, "run_phase_two", lambda result: result)

    assert interview.run_interview() is answers

    monkeypatch.setattr(interview, "_ask_layer_prompt", lambda: "layer 3")
    monkeypatch.setattr(
        interview, "run_phase_three", lambda _: interview.QUIT_SENTINEL
    )
    assert interview.run_interview() is None


def test_optional_phase_quit_cancels_interview(monkeypatch):
    monkeypatch.setattr(interview, "run_phase_one", lambda answers: answers)
    monkeypatch.setattr(interview, "_ask_layer_prompt", lambda: "layer 2")
    monkeypatch.setattr(
        interview, "run_phase_two", lambda _: interview.QUIT_SENTINEL
    )

    assert interview.run_interview() is None


def test_format_answers_uses_labels_and_omits_missing_answers():
    formatted = interview.format_answers({"q1": "Project summary"})

    assert "Q1. Project description" in formatted
    assert "Project summary" in formatted
    assert "Q2. Full tech stack" not in formatted
