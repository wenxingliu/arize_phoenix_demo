from tutor.prompts import system_prompt, user_prompt


def test_system_prompt_contains_tutoring_and_grounding_rules() -> None:
    prompt = system_prompt("Tutor")
    assert "data science tutor" in prompt
    assert "retrieved PDF context" in prompt
    assert "Socratic guidance" in prompt


def test_auto_tutor_prompt_contains_style_selection_rules() -> None:
    prompt = system_prompt("Tutor")
    assert "Style: Explain" in prompt
    assert "Style: Guide" in prompt
    assert "definition requests" in prompt
    assert "help me solve" in prompt


def test_quiz_prompt_remains_distinct() -> None:
    prompt = system_prompt("Quiz")
    assert "Create 3-5 practice questions" in prompt
    assert "Style: Explain" not in prompt


def test_user_prompt_includes_context_and_question() -> None:
    prompt = user_prompt("What is data science?", "[Source: page 1]\nData science text")
    assert "Retrieved PDF context" in prompt
    assert "What is data science?" in prompt
    assert "[Source: page 1]" in prompt
