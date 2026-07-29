def build_review_prompt(code: str) -> str:
    return f"""
Review this Python code.

Report only definite, meaningful issues directly supported by the code.

Do not:
- Invent missing requirements
- Report hypothetical performance problems
- Mention type hints or docstrings unless they cause a concrete issue
- Do not report stylistic preferences, refactoring opportunities, or design alternatives as bugs. 
  However, always report definite security vulnerabilities (e.g., SQL injection, command injection, path traversal, 
  hardcoded secrets, unsafe deserialization) when they are directly supported by the code.

If there are no meaningful issues, respond with exactly:

No meaningful issues found.

Python code:
{code}
"""
