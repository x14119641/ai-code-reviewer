# Results

The evaluation system has grown incrementally as the reviewer, taxonomy, prompt strategy, and supported review modes have evolved.

The project now maintains two distinct evaluation tracks:

* **Full-file review benchmarks**, currently containing 65 cases.
* **Git-diff review benchmarks**, currently containing an initial 11-case suite.

These suites measure different behaviors and should not be compared directly.

The full-file suite evaluates whether the reviewer can identify issues in complete Python source files.

The diff suite evaluates whether the reviewer can identify issues introduced or worsened by a change while avoiding findings that were already present before the diff.

Results from different stages should not always be compared directly because the benchmark suites, prompts, generation settings, taxonomy, and severity evaluation strategy have evolved over time.

---

## Full-File Review Results

### Initial Model Comparison

The following results were produced during the initial **v1 model comparison** using the original 35-case benchmark suite.

These experiments were performed before deterministic generation settings and rule-based severity normalization were introduced.

```text
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━┳━━━━┳━━━━━━━━┳━━━━━━━━┓
┃ Model                 ┃ Prompt ┃ Accuracy ┃ Severity ┃ Passed ┃ FP ┃ FN ┃ Errors ┃   Time ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━╇━━━━╇━━━━━━━━╇━━━━━━━━┩
│ qwen3.5:9b            │ v1     │    91.4% │    68.4% │     32 │  2 │  1 │      0 │  90.4s │
│ qwen2.5-coder:7b      │ v1     │    82.9% │    73.7% │     29 │  5 │  1 │      0 │  48.9s │
│ qwen2.5-coder:14b     │ v1     │    80.0% │    56.2% │     28 │  3 │  4 │      0 │  71.8s │
│ gemma3:12b            │ v1     │    77.1% │    64.7% │     27 │  5 │  2 │      0 │ 115.2s │
│ deepseek-coder-v2:16b │ v1     │    65.7% │    50.0% │     23 │ 10 │  2 │      0 │ 157.7s │
│ llama3.1:8b           │ v1     │    51.4% │    50.0% │     18 │ 11 │  0 │      0 │  73.7s │
└───────────────────────┴────────┴──────────┴──────────┴────────┴────┴────┴────────┴────────┘
```

These results remain useful as an early model comparison, but they should not be directly compared with newer controlled prompt experiments.

The evaluation setup has since changed in two important ways:

* Generation uses `temperature=0` and a fixed seed (`42`) to reduce run-to-run variation.
* Severity is derived deterministically from the detected rule instead of trusting the LLM's severity prediction.

### Controlled Prompt Evaluation

Prompt optimization initially used Qwen 3.5 9B against the same 35-case benchmark suite with controlled generation settings.

| Prompt | Accuracy | Passed | False Positives | False Negatives |
| ------ | -------: | -----: | --------------: | --------------: |
| v1     |    85.7% |  30/35 |               4 |               1 |
| v2     |    88.6% |  31/35 |               3 |               1 |
| v3     |    88.6% |  31/35 |               3 |               1 |
| v4     |    91.4% |  32/35 |               2 |               1 |

These experiments showed that making **rule-specific detection boundaries explicit** was more effective than adding increasingly general instructions intended to suppress false positives.

Prompt v4 became the stable prompt for the original taxonomy.

### Benchmark Expansion

After the initial prompt experiments, the full-file benchmark suite was expanded incrementally from **35 to 65 cases**.

New cases were added in small groups containing positive, negative, and boundary examples rather than only straightforward detections.

The expanded suite tests rules including:

| Category        | Rules                                                   |
| --------------- | ------------------------------------------------------- |
| Bug             | Mutable default argument, Unreachable code              |
| Security        | SQL injection, Shell injection, Path traversal          |
| Performance     | List membership in loops, String concatenation in loops |
| Maintainability | Duplicate code, Long function                           |

The expanded suite also includes safe cases designed specifically to measure false positives, such as:

* `None` used safely instead of a mutable default
* Tuple, set, and dictionary membership boundaries
* Parameterized SQL queries
* Allowlisted commands and paths
* `join()` and `StringIO` instead of repeated string concatenation
* Shared helper functions instead of duplicated logic
* Valid control flow that remains reachable

### Current v5 Result

Prompt v5 was created from v4 to introduce the new `unreachable_code` bug rule while keeping previous prompt versions frozen for reproducibility.

The current Qwen 3.5 9B result on the **65-case full-file benchmark suite** is:

```text
Model              qwen3.5:9b
Prompt             v5
Benchmarks         65
Passed             60
Failed              5
Accuracy           92.3%
Severity accuracy 100.0%
Execution time    145.7s
```

All five newly introduced `unreachable_code` benchmarks passed.

The remaining failures are:

#### False positives

```text
benchmarks/bug/mutable_default_argument/none_default_safe.py
benchmarks/performance/list_membership_in_loop/tuple_membership_in_loop_safe.py
```

`none_default_safe.py` is incorrectly classified as `mutable_default_argument` even though the default value is `None` and the mutable object is created inside the function.

`tuple_membership_in_loop_safe.py` is incorrectly classified as `list_membership_in_loop`. The project taxonomy intentionally defines this rule specifically for lists, so tuple membership is considered safe for this benchmark even though tuple membership itself is linear.

#### False negatives

```text
benchmarks/maintainability/long_function/long_function.py
benchmarks/maintainability/long_function/multi_responsibility_function.py
benchmarks/security/path_traversal/user_absolute_path.py
```

The two `long_function` cases indicate that maintainability detection remains the clearest weak area in the current full-file prompt.

`user_absolute_path.py` is particularly interesting because it passed under v4 but failed under v5, making it a prompt regression.

### v4 → v5 Regression Analysis

Aggregate accuracy alone does not show how individual benchmark behavior changes between prompt versions.

The `compare-runs` command performs benchmark-level regression analysis:

```bash
uv run python main.py compare-runs \
    results/v4/qwen3.5-9b-seed42-block5.json \
    results/v5/qwen3.5-9b-seed42-block5.json
```

Current comparison:

```text
Old: v4 / qwen3.5:9b — 53/60 (88.3%)
New: v5 / qwen3.5:9b — 60/65 (92.3%)

Comparable: 60 | Fixed: 3 | Regressed: 1 | Still failing: 4 | Added: 5 | Removed: 0
```

The three fixed cases are:

```text
benchmarks/maintainability/duplicate_code/shared_helper_safe.py
benchmarks/maintainability/duplicate_code/shared_validation_helper_safe.py
benchmarks/performance/list_membership_in_loop/dict_key_membership_safe.py
```

The regression is:

```text
benchmarks/security/path_traversal/user_absolute_path.py
```

The cases still failing across both runs are:

```text
benchmarks/bug/mutable_default_argument/none_default_safe.py
benchmarks/maintainability/long_function/long_function.py
benchmarks/maintainability/long_function/multi_responsibility_function.py
benchmarks/performance/list_membership_in_loop/tuple_membership_in_loop_safe.py
```

Five new `unreachable_code` benchmarks were added between the two runs, and all five pass under v5.

This comparison demonstrates an important property of prompt engineering: **changing one part of a prompt can affect apparently unrelated rules**.

Although v5 improves performance across the original 60 comparable benchmarks, it also introduces a path-traversal regression.

---

## Git Diff Review

The reviewer now supports reviewing local Git diffs using the current contents of changed Python files as additional context.

A raw diff alone may not contain enough information to determine the behavior of unchanged lines affected by a change.

For example, changing a function parameter from:

```python
users: dict[str, int]
```

to:

```python
users: list[str]
```

can make an unchanged membership check:

```python
if username in users:
```

significantly more expensive.

The diff reviewer therefore receives two complementary inputs:

```text
Git diff
   +
Current changed-file source
   ↓
Diff-specific prompt
   ↓
Structured CodeReview
```

The diff identifies what changed, while the current source provides enough surrounding context to reason about the behavior of the resulting code.

The intended behavior differs from full-file review in one important way:

> A diff reviewer should report issues introduced or worsened by the change, not every issue visible in the current source.

This change-attribution requirement motivated the creation of a dedicated diff benchmark suite.

---

## Diff Benchmarking

Diff review now has its own benchmark format, runner, CLI command, rendering, failure handling, and result export.

The diff benchmark suite is independent from the 65-case full-file suite.

A diff benchmark contains:

```text
benchmark_case/
├── before.py
├── after.py
└── benchmark.json
```

`before.py` represents the source before the change.

`after.py` represents the source after the change.

The benchmark infrastructure generates the corresponding unified diff and supplies both that diff and the current `after.py` source to the reviewer.

`benchmark.json` describes the expected issues introduced by the change.

Example:

```json
{
  "name": "Dict to list introduces membership in loop",
  "before_path": "before.py",
  "after_path": "after.py",
  "expected_issues": [
    {
      "severity": "medium",
      "rule": "list_membership_in_loop",
      "category": "performance",
      "explanation": "Changing the lookup collection from a dict to a list introduces linear membership checks inside the loop."
    }
  ]
}
```

The same benchmark evaluator used by full-file review is reused for diff review.

This allows both review modes to share evaluation semantics for:

* Rule matching
* Category matching
* Severity matching
* False positives
* False negatives
* Overall pass/fail behavior

Diff benchmark runs are represented using the same `BenchmarkRun` result structure and can be serialized using the existing benchmark result pipeline.

### Diff Benchmark CLI

The full diff suite can be run with:

```bash
uv run python main.py benchmark-diff \
    diff_benchmarks \
    --model qwen3.5:9b \
    --prompt-version v9
```

Individual rule families can also be evaluated:

```bash
uv run python main.py benchmark-diff \
    diff_benchmarks/security/sql_injection \
    --model qwen3.5:9b \
    --prompt-version v9
```

Diff benchmark results can be exported:

```bash
uv run python main.py benchmark-diff \
    diff_benchmarks \
    --model qwen3.5:9b \
    --prompt-version v9 \
    --output qwen3.5-9b.json
```

Relative diff output filenames are stored separately from full-file results:

```text
results/
├── v1/
├── v2/
├── ...
└── diff/
    ├── v9/
    │   └── qwen3.5-9b.json
    └── v10/
        └── qwen3.5-9b.json
```

This prevents full-file and diff benchmark results from being accidentally mixed even though they share the same serialization and evaluation infrastructure.

---

## Initial Diff Benchmark Suite

The first systematic diff-review suite contains **11 benchmark cases**.

It currently covers five rules:

| Category    | Rule                     |  Cases |
| ----------- | ------------------------ | -----: |
| Bug         | Mutable default argument |      2 |
| Bug         | Unreachable code         |      2 |
| Performance | List membership in loops |      3 |
| Security    | SQL injection            |      2 |
| Security    | Shell injection          |      2 |
| **Total**   |                          | **11** |

The suite deliberately includes both newly introduced issues and attribution boundaries.

### List Membership in Loops

The initial performance cases test three distinct situations.

#### Introduced issue

```text
dict → list
```

The collection type changes from dictionary to list while an existing membership check remains unchanged.

The diff introduces a performance regression and should produce:

```text
list_membership_in_loop
```

#### Safe change

```text
dict → dict
```

Only a local variable is renamed. Dictionary membership remains efficient.

Expected result:

```text
no issues
```

#### Pre-existing issue

List membership inside the loop already exists before the diff.

The diff only performs a local rename.

Expected result:

```text
no issues
```

This third case specifically tests whether the model can distinguish an issue visible in the current code from an issue introduced by the change.

### Unreachable Code

The positive case introduces an unconditional `raise` before an existing `return`, making that return unreachable.

The boundary case already contains the unreachable return before the diff and changes only an unrelated error message.

The reviewer should detect the first case and ignore the second.

### Mutable Default Argument

The positive case changes:

```python
items: list[str] | None = None
```

to:

```python
items: list[str] = []
```

This introduces a mutable default argument and should be reported.

The boundary case already contains the mutable default before the diff and changes only local variable names.

The reviewer should therefore return no issues for the boundary case.

### SQL Injection

The positive case changes a parameterized query into an interpolated SQL string.

The diff therefore introduces `sql_injection`.

The boundary case already contains the vulnerable interpolated query before the diff and changes only an audit message.

The existing vulnerability should not be reported because it was not introduced by the change.

### Shell Injection

The positive case changes a safe argument-list subprocess call into an interpolated command executed with `shell=True`.

The diff therefore introduces `shell_injection`.

The boundary case already contains the unsafe shell command before the diff and changes only an informational message.

Again, the existing vulnerability should not be reported.

---

## Initial Diff Review Baseline

The first complete diff benchmark baseline was produced using:

```text
Model   qwen3.5:9b
Prompt  v9
Cases   11
```

Result:

```text
Benchmarks        11
Passed             8
Failed             3
Errors             0
False positives    3
False negatives    0
Accuracy          72.7%
Severity          5/5 (100.0%)
Duration          32.94s
```

The five positive introduced-issue cases all passed.

The model successfully detected:

```text
mutable_default_argument
unreachable_code
list_membership_in_loop
sql_injection
shell_injection
```

All five detections matched the expected normalized severity.

There were no false negatives.

### Diff Attribution Failures

All three failures were false positives involving **pre-existing issues**.

The failing cases were:

```text
diff_benchmarks/bug/mutable_default_argument/preexisting_mutable_default_safe
diff_benchmarks/security/shell_injection/preexisting_shell_injection_safe
diff_benchmarks/security/sql_injection/preexisting_sql_injection_safe
```

In each case:

1. The problem already existed in `before.py`.
2. The diff made an unrelated change.
3. The problem remained visible in `after.py`.
4. The model reported the existing problem anyway.

For example, the SQL injection boundary contains the vulnerable query both before and after the change:

```python
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)
```

The actual diff only changes:

```diff
- audit_message = "User lookup completed"
+ audit_message = f"User lookup completed for {username}"
```

The correct diff-review result is therefore:

```text
no issues
```

Prompt v9 instead reports `sql_injection`.

A similar pattern occurs for the pre-existing mutable default and shell injection cases.

### Successful Attribution Cases

The attribution problem is not universal.

Prompt v9 correctly ignored pre-existing issues in:

```text
diff_benchmarks/performance/list_membership_in_loop/preexisting_list_issue_safe
diff_benchmarks/bug/unreachable_code/preexisting_unreachable_safe
```

This distinction is important.

The baseline does not indicate that the reviewer completely ignores the diff and simply reviews the current file.

Instead, it suggests that attribution becomes less reliable for some highly salient issues.

Current behavior can therefore be summarized as:

```text
Introduced issues
    5/5 detected

Pre-existing boundary issues
    list_membership_in_loop    PASS
    unreachable_code           PASS
    mutable_default_argument   FAIL
    sql_injection              FAIL
    shell_injection            FAIL
```

This established change attribution as the primary target for the next diff prompt experiment.

---

## v10 Diff Attribution Experiment

Prompt v10 was created to test whether stronger and more explicit before/after attribution instructions could reduce the three false positives found under v9.

The benchmark suite remained frozen at the same **11 cases** so that any behavior change could be attributed to the prompt rather than changes in the evaluation dataset.

The final v10 experiment used explicit before/after classification:

```text
BEFORE safe   → AFTER unsafe       → report
BEFORE unsafe → AFTER worse        → report
BEFORE unsafe → AFTER same unsafe  → do not report
BEFORE safe   → AFTER safe         → do not report
```

The goal was to force the model to distinguish issue recognition from change attribution before producing a finding.

The final Qwen 3.5 9B result was:

```text
Model            qwen3.5:9b
Prompt           v10
Benchmarks       11
Passed            8
Failed            3
Errors            0
False positives   3
False negatives   0
Accuracy         72.73%
Severity          5/5 (100.00%)
Duration         36.18s
```

### v9 → v10 Comparison

| Prompt | Passed | Accuracy | False Positives | False Negatives |   Severity |
| ------ | -----: | -------: | --------------: | --------------: | ---------: |
| v9     |   8/11 |    72.7% |               3 |               0 | 5/5 (100%) |
| v10    |   8/11 |    72.7% |               3 |               0 | 5/5 (100%) |

The stronger attribution instructions produced **no improvement in aggregate accuracy** and did not change which benchmarks failed.

The same three pre-existing issues remained false positives:

```text
mutable_default_argument
shell_injection
sql_injection
```

The introduced versions of those rules continued to pass, as did the introduced `unreachable_code` and `list_membership_in_loop` cases.

The final behavior therefore remained:

```text
Introduced issues
    5/5 detected

Pre-existing boundary issues
    list_membership_in_loop    PASS
    unreachable_code           PASS
    mutable_default_argument   FAIL
    sql_injection              FAIL
    shell_injection            FAIL
```

### Experiment Conclusion

The v10 result provides evidence that the three attribution failures are not easily corrected by simply making the general change-attribution instructions stronger.

The model already has enough information in these small benchmark diffs to observe that the vulnerable construct existed before the unrelated change.

Despite increasingly explicit before/after instructions, Qwen 3.5 9B continued to report the same highly visible pre-existing patterns.

This suggests that, for the current model and benchmark cases, issue recognition can dominate change attribution for some rules.

The result also reinforces an observation already seen during full-file prompt development:

> More explicit general instructions do not necessarily improve model behavior.

Prompt changes should therefore continue to be evaluated empirically rather than assuming that stronger wording produces stronger compliance.

Prompt v10 does **not** replace v9 as the diff-review baseline because it provides no measurable improvement.

The current diff baseline remains:

```text
Prompt v9
8/11
72.7% accuracy
3 false positives
0 false negatives
```

Rather than continuing to optimize the prompt against the same three cases, the next step is to expand the diff benchmark suite.

A larger suite will show whether the attribution failures are:

* specific to a few highly salient rules,
* systematic across other rule families,
* or representative of a broader limitation in the current diff-review strategy.

Only after broader benchmark coverage should larger prompt or context-architecture changes be considered.

---

## Diff Prompt Evolution

Git-diff review uses a separate prompt from full-file review.

The diff prompt receives:

* The Git diff
* The current contents of changed Python files
* The same structured output requirements used by the rest of the reviewer

Prompt v9 remains the current baseline.

Prompt v10 tested stronger change-attribution instructions but did not improve benchmark performance.

The current prompt history is:

```text
v9
    ↓
Initial 11-case diff baseline
    ↓
8/11 — 72.7%
    ↓
Three persistent pre-existing-issue false positives
    ↓
v10 attribution experiment
    ↓
Explicit before/after classification
    ↓
8/11 — 72.7%
    ↓
No improvement over v9
```

The experiment indicates that repeatedly strengthening general attribution instructions is unlikely to be the most useful immediate direction.

The next experimental phase is therefore:

```text
Freeze v9 baseline
    ↓
Record v10 as unsuccessful attribution experiment
    ↓
Expand diff benchmark coverage
    ↓
Measure attribution behavior across more rules
    ↓
Identify systematic failure patterns
    ↓
Decide whether the next intervention should target
prompt design, context construction, or model choice
```

This keeps the evaluation process evidence-driven rather than optimizing repeatedly against three individual failures.

---

## Result Analysis

The project provides complementary ways to analyze exported benchmark results.

### Aggregate Comparison

Compare multiple benchmark runs:

```bash
uv run python main.py compare-results results/v5/
```

Results can also be grouped by rule or category:

```bash
uv run python main.py compare-results results/v5/ --by-rule
uv run python main.py compare-results results/v5/ --by-category
```

### Individual Run Analysis

Inspect the failures from one exported benchmark run:

```bash
uv run python main.py analyze-result \
    results/v5/qwen3.5-9b-seed42-block5.json
```

This surfaces:

* False positives
* False negatives
* Rule mismatches
* Category mismatches
* Severity mismatches

### Cross-Run Regression Analysis

Compare two specific runs benchmark by benchmark:

```bash
uv run python main.py compare-runs \
    results/v4/qwen3.5-9b-seed42-block5.json \
    results/v5/qwen3.5-9b-seed42-block5.json
```

This identifies:

* Fixed benchmarks
* Regressed benchmarks
* Benchmarks that remain failing
* Added benchmarks
* Removed benchmarks

Together, these tools provide three levels of experiment analysis:

```text
Aggregate comparison
        ↓
Rule / category analysis
        ↓
Individual benchmark regression analysis
```

The same evaluation and serialization foundation is now also used by diff benchmark runs, allowing diff prompt experiments to follow the same reproducible workflow.

---

## Current Observations

### Full-File Review

* Qwen 3.5 9B produced the strongest result in the initial multi-model comparison.
* Qwen 2.5 Coder 7B provided a strong speed-to-accuracy trade-off in the initial model benchmark.
* Controlled prompt iteration improved Qwen 3.5 9B from **85.7% with v1** to **91.4% with v4** on the original 35-case suite.
* Explicit rule-specific detection boundaries were more effective than generic false-positive suppression instructions.
* Expanding the suite from 35 to 65 cases exposed additional generalization and boundary failures that were not visible in the smaller suite.
* Prompt v5 reaches **92.3% accuracy on 65 benchmarks** with **100% severity accuracy**.
* The `unreachable_code` rule currently passes all five of its full-file benchmark cases.
* `long_function` remains the clearest weak rule in the current full-file prompt.
* The v4 → v5 experiment fixed three existing failures but regressed `user_absolute_path.py`.
* Aggregate accuracy should not be used alone when deciding whether a prompt revision is better.

### Git Diff Review

* Diff review now has dedicated benchmark infrastructure rather than relying on manual examples.
* The initial diff suite contains **11 cases across five rules**.
* Prompt v9 achieves **72.7% accuracy** on the initial suite.
* All **5/5 introduced-issue cases** are detected.
* Severity accuracy is **100% (5/5)** for those detections.
* There are **no false negatives** in the v9 baseline.
* All three failures are false positives involving issues that existed before the diff.
* Pre-existing list-membership and unreachable-code problems are correctly ignored.
* Pre-existing mutable-default, SQL-injection, and shell-injection problems are incorrectly reported.
* Prompt v10 tested stronger explicit before/after attribution instructions.
* v10 also achieved **72.7% accuracy with the same three false positives and no false negatives**.
* The v10 experiment therefore produced no measurable improvement over v9.
* The main measured weakness remains **change attribution**, not basic issue recognition.
* Stronger general attribution wording alone did not resolve the measured failures.
* The next step is to expand the diff benchmark suite before making larger prompt or context-architecture changes.

---

## Current Evaluation State

The project now has two complementary evaluation systems:

```text
FULL-FILE REVIEW
65-case suite
Prompt v5 baseline
92.3% accuracy
      │
      └── measures issue recognition and rule boundaries


GIT-DIFF REVIEW
11-case initial suite
Prompt v9 baseline
72.7% accuracy
      │
      ├── measures issue recognition + change attribution
      │
      └── v10 attribution experiment: no improvement
```

These should remain separate experimental tracks.

Full-file prompt improvements should be evaluated against the full-file suite.

Diff prompt improvements should be evaluated against the diff suite.

The next diff-review phase is benchmark expansion rather than continued optimization against the same three attribution failures.

This separation allows future development toward pull-request review without losing the reproducibility of the existing full-file experiments.
