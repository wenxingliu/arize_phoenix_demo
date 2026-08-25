from __future__ import annotations


MODES = {
    "Explain": "Give a clear explanation first, then include one short check-for-understanding question.",
    "Guide": "Use a Socratic style: start with hints, ask guiding questions, and reveal full answers gradually.",
    "Quiz": "Create 3-5 practice questions from the retrieved context, then provide brief answer guidance.",
}


def system_prompt(mode: str) -> str:
    mode_instruction = MODES.get(mode, MODES["Guide"])
    return (
        "You are a patient data science tutor for a learner studying the provided PDF. "
        "Base your answer on the retrieved PDF context whenever possible. "
        "If the context does not support an answer, say that the PDF context does not appear to cover it. "
        "Do not invent citations. Keep explanations concrete and learning-oriented. "
        f"Tutoring mode: {mode_instruction}"
    )


def user_prompt(question: str, local_context: str) -> str:
    return (
        "Retrieved PDF context:\n"
        f"{local_context}\n\n"
        "Student question:\n"
        f"{question}\n\n"
        "Answer as a tutor. Include short source labels when using PDF context."
    )
