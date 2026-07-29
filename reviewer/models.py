from pathlib import Path
from dataclasses import dataclass
from typing import Literal

Severity = Literal["low", "medium", "high", "critical"]


@dataclass
class Issue:
    severity:Severity
    category:str
    title:str
    explanation:str
    recommendation:str

@dataclass
class ExpectedIssue:
    severity:Severity
    category:str
    explanation:str

@dataclass(frozen=True)
class ExpectedIssue:
    category: str
    severity: str
    explanation: str

@dataclass(frozen=True)
class Benchmark:
    name: str
    code_path: Path
    source_code: str
    expected_issues: tuple[ExpectedIssue, ...]

    @property
    def expects_issues(self) -> bool:
        return bool(self.expected_issues)
    
@dataclass 
class CodeReview:
    issues: list[Issue]