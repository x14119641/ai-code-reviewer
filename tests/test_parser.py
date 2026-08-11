import pytest

from reviewer.engine import parse_review_response


def test_parse_valid_review() -> None:
    response = """
    {
      "issues": [
        {
          "severity": "critical",
          "category": "security",
          "title": "Unsafe query",
          "rule": "sql_injection",
          "explanation": "User input is inserted directly into the query.",
          "recommendation": "Use a parameterized query."
        }
      ]
    }
    """

    review = parse_review_response(response)

    assert len(review.issues) == 1
    assert review.issues[0].severity == "critical"
    assert review.issues[0].title == "Unsafe query"


def test_parse_empty_review() -> None:
    response = '{"issues": []}'

    review = parse_review_response(response)

    assert review.issues == []


def test_reject_invalid_json() -> None:
    response = '{"issues": ['

    with pytest.raises(RuntimeError, match="invalid JSON"):
        parse_review_response(response)


def test_reject_invalid_severity() -> None:
    response = """
    {
      "issues": [
        {
          "severity": "extreme",
          "rule": "sql_injection",
          "category": "security",
          "title": "Unsafe query",
          "explanation": "Problem explanation.",
          "recommendation": "Fix recommendation."
        }
      ]
    }
    """

    with pytest.raises(RuntimeError, match="invalid severity"):
        parse_review_response(response)