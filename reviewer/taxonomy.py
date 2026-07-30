from typing import Literal


Severity = Literal[
    "low",
    "medium",
    "high",
    "critical",
]

IssueCategory = Literal[
    "security",
    "bug",
    "performance",
    "maintainability",
]

IssueRule = Literal[
    "sql_injection",
    "shell_injection",
    "path_traversal",
    "mutable_default_argument",
]


VALID_SEVERITIES: set[str] = {
    "low",
    "medium",
    "high",
    "critical",
}

VALID_CATEGORIES: set[str] = {
    "security",
    "bug",
    "performance",
    "maintainability",
}

VALID_RULES: set[str] = {
    "sql_injection",
    "shell_injection",
    "path_traversal",
    "mutable_default_argument",
}