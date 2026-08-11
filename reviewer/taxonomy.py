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
    "long_function",
    "duplicate_code",
    "list_membership_in_loop",
    "string_concatenation_in_loop",
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
    "long_function",
    "duplicate_code",
    "list_membership_in_loop",
    "string_concatenation_in_loop",
}

RULE_SEVERITY = {
    "duplicate_code": "medium",
    "list_membership_in_loop": "medium",
    "long_function": "low",
    "mutable_default_argument": "medium",
    "path_traversal": "high",
    "shell_injection": "critical",
    "sql_injection": "critical",
    "string_concatenation_in_loop": "low",
}
