import difflib

def build_benchmark_diff(
    before_source:str,
    after_source:str,
    *,
    path:str,
) -> str:
    before_lines = before_source.splitlines(keepends=True)
    after_lines = after_source.splitlines(keepends=True)
    
    diff_lines = difflib.unified_diff(
        before_lines,
        after_lines,
        fromfile=f"a/{path}",
        tofile=f"b/{path}",
        n=10,
    )
    
    return "".join(diff_lines)