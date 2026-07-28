


def build_review_prompt(code: str) -> str:
    return f"""
Review this Python code.

Report only definite, meaningful issues directly supported by the code.

Do not:
- invent missing requirements
- treat design alternatives as bugs
- report hypothetical performance problems
- mention type hints or docstrings unless they cause a concrete issue

If there are no meaningful issues, respond with exactly:

No meaningful issues found.

Python code:
{code}
"""
