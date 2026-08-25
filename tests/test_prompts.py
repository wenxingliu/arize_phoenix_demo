from tutor.prompts import system_prompt, user_prompt


def test_system_prompt_contains_tutoring_and_grounding_rules() -> None:
    prompt = system_prompt("Guide")
    assert "data science tutor" in prompt
    assert "retrieved PDF context" in prompt
    assert "Socratic" in prompt


def test_user_prompt_includes_context_and_question() -> None:
    prompt = user_prompt("What is data science?", "[Source: page 1]\nData science text")
    assert "Retrieved PDF context" in prompt
    assert "What is data science?" in prompt
    assert "[Source: page 1]" in prompt
