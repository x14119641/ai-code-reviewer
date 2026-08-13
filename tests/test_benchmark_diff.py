from reviewer.benchmark_diff import build_benchmark_diff


def test_build_benchmark_diff_contains_changed_lines() ->None:
    before_source = """\
def find_users(users: dict[str, int]) -> None:
    pass
"""

    after_source = """\
def find_users(users: list[str]) -> None:
    pass
"""

    diff = build_benchmark_diff(
        before_source, after_source, path="example.py"
    )
    
    assert "-def find_users(users: dict[str, int]) -> None:" in diff
    assert "+def find_users(users: list[str]) -> None:" in diff
    
    
def test_build_benchmark_diff_uses_git_style_file_headers() -> None:
    before_source = "value = 1\n"
    after_source = "value = 2\n"

    diff = build_benchmark_diff(
        before_source,
        after_source,
        path="example.py",
    )

    assert "--- a/example.py" in diff
    assert "+++ b/example.py" in diff


def test_build_benchmark_diff_returns_empty_string_when_sources_are_identical() -> None:
    source = "value = 1\n"

    diff = build_benchmark_diff(
        source,
        source,
        path="example.py",
    )

    assert diff == ""