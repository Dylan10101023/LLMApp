MAX_INPUT_CHARS = 2000  # simple guardrail


def is_input_too_long(user_input: str) -> bool:
    return len(user_input) > MAX_INPUT_CHARS


def check_prompt_injection(user_input: str):
    """
    Very basic injection check.
    Returns (flag: bool, reason: str | None)
    """
    lower = user_input.lower()

    patterns = [
        "ignore previous instructions",
        "ignore all previous instructions",
        "act as system",
        "you are now system",
        "forget the system prompt",
        "change your rules",
    ]

    for p in patterns:
        if p in lower:
            return True, f"Detected suspicious pattern: '{p}'"

    return False, None