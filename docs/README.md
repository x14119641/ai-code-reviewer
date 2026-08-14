## Diff Benchmark Suite

The diff-review benchmark suite was initially introduced with **11 cases across five rules** and was later expanded to **19 cases covering all nine rules in the current taxonomy**.

The expanded suite deliberately combines:

- issues introduced by a diff
- pre-existing issues that should not be attributed to the diff
- safe changes
- changes whose effects appear in unchanged code

The current coverage is:

| Category | Rule | Cases |
| --- | --- | ---: |
| Bug | Mutable default argument | 2 |
| Bug | Unreachable code | 2 |
| Security | SQL injection | 2 |
| Security | Shell injection | 2 |
| Security | Path traversal | 2 |
| Performance | List membership in loops | 3 |
| Performance | String concatenation in loops | 2 |
| Maintainability | Duplicate code | 2 |
| Maintainability | Long function | 2 |
| **Total** | | **19** |

This gives every rule in the current taxonomy at least one diff-review benchmark family.

### List Membership in Loops

The performance cases test three distinct situations.

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

### Path Traversal

The positive case removes filename sanitization and changes safe path construction into a direct join between an intended base directory and a user-controlled path.

This allows values such as parent-directory traversal or absolute paths to escape the intended directory.

The boundary case already contains the unsafe path construction before the diff and changes only an informational message.

Both v9 and v10 correctly detect the introduced case and ignore the pre-existing case.

### String Concatenation in Loops

The positive case changes efficient `str.join()` construction into repeated `+=` concatenation inside a loop.

The boundary case already contains repeated string concatenation before the diff and changes only unrelated reporting logic.

Both v9 and v10 correctly distinguish the introduced issue from the pre-existing one.

### Duplicate Code

The positive case introduces substantially duplicated normalization and validation logic across two functions.

The boundary case already contains the duplicated implementation before the diff and changes unrelated code.

Both v9 and v10 correctly ignore the pre-existing duplicate implementation but fail to detect the newly introduced duplication.

A diagnostic full-file review of the same resulting source also failed to report `duplicate_code`.

This suggests that the observed failure is primarily an **issue-recognition weakness**, rather than a diff-attribution failure.

### Long Function

The positive case expands a previously focused function so that it performs several responsibilities:

- input validation
- iteration and aggregation
- business-rule application
- result construction

The boundary case already contains this multi-responsibility implementation before the diff and changes only unrelated output logic.

Both v9 and v10 correctly ignore the pre-existing case but fail to report the newly introduced `long_function`.

This is consistent with the existing full-file benchmark results, where `long_function` is already one of the weakest rules.

---

## Initial Diff Review Baseline

The first complete diff benchmark baseline used the original **11-case suite**:

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

All five positive introduced-issue cases passed.

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

### Initial Attribution Failures

All three failures were false positives involving pre-existing issues:

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

The initial suite therefore identified **change attribution** as the primary weakness to investigate.

---

## v10 Diff Attribution Experiment

Prompt v10 was created to test whether stronger and more explicit before/after attribution instructions could reduce the three false positives found under v9.

The initial experiment kept the same 11-case suite frozen.

The final v10 prompt used explicit before/after classification:

```text
BEFORE safe   → AFTER unsafe       → report
BEFORE unsafe → AFTER worse        → report
BEFORE unsafe → AFTER same unsafe  → do not report
BEFORE safe   → AFTER safe         → do not report
```

On the original suite:

| Prompt | Passed | Accuracy | False Positives | False Negatives | Severity |
| --- | ---: | ---: | ---: | ---: | ---: |
| v9 | 8/11 | 72.7% | 3 | 0 | 5/5 (100%) |
| v10 | 8/11 | 72.7% | 3 | 0 | 5/5 (100%) |

The stronger attribution instructions produced no improvement.

The same three pre-existing issues remained false positives:

```text
mutable_default_argument
shell_injection
sql_injection
```

Prompt v10 therefore did not replace v9 as the baseline.

Instead of continuing to optimize against those three examples, the benchmark suite was expanded to determine whether the attribution problem generalized across the rest of the taxonomy.

---

## Expanded Diff Review Results

The suite was expanded from **11 to 19 cases**, adding coverage for:

```text
path_traversal
string_concatenation_in_loop
duplicate_code
long_function
```

This brings the diff suite to all **nine rules** currently supported by the reviewer.

Both v9 and v10 were evaluated against the complete expanded suite.

### v9 Expanded Result

```text
Model            qwen3.5:9b
Prompt           v9
Benchmarks       19
Passed           14
Failed            5
Errors            0
False positives   3
False negatives   2
Accuracy         73.68%
Severity          7/7 (100.00%)
Duration         48.52s
```

### v10 Expanded Result

```text
Model            qwen3.5:9b
Prompt           v10
Benchmarks       19
Passed           14
Failed            5
Errors            0
False positives   3
False negatives   2
Accuracy         73.68%
Severity          7/7 (100.00%)
Duration         47.42s
```

### v9 → v10 Expanded Comparison

| Prompt | Passed | Accuracy | False Positives | False Negatives | Severity |
| --- | ---: | ---: | ---: | ---: | ---: |
| v9 | 14/19 | 73.68% | 3 | 2 | 7/7 (100%) |
| v10 | 14/19 | 73.68% | 3 | 2 | 7/7 (100%) |

The two prompts produce the same benchmark outcomes across all 19 cases.

This provides stronger evidence that the additional attribution wording introduced in v10 does not materially change Qwen 3.5 9B's behavior on the current diff-review task.

---

## Expanded Failure Analysis

The expanded suite reveals **two distinct failure modes**.

### Change Attribution Failures

Three failures remain false positives where the issue existed before the diff:

```text
mutable_default_argument
sql_injection
shell_injection
```

For these rules, the model recognizes the issue correctly but incorrectly attributes it to an unrelated change.

However, attribution works correctly for the pre-existing cases involving:

```text
unreachable_code
list_membership_in_loop
path_traversal
string_concatenation_in_loop
duplicate_code
long_function
```

This means the attribution problem is **not universal**.

Current attribution behavior can be summarized as:

```text
Pre-existing issue attribution

unreachable_code                 PASS
list_membership_in_loop          PASS
path_traversal                   PASS
string_concatenation_in_loop     PASS
duplicate_code                   PASS
long_function                    PASS

mutable_default_argument         FAIL
sql_injection                    FAIL
shell_injection                  FAIL
```

The expanded suite therefore suggests that attribution weakness is concentrated around specific highly recognizable issue patterns rather than reflecting a general inability to reason about before/after changes.

### Issue Recognition Failures

The two false negatives are:

```text
duplicate_code
long_function
```

In both cases, the diff genuinely introduces the expected maintainability issue, but the model returns no issues.

Their corresponding pre-existing boundary cases pass.

This means the failure pattern is different from the three attribution false positives:

```text
duplicate_code
    introduced issue    FAIL
    pre-existing issue  PASS

long_function
    introduced issue    FAIL
    pre-existing issue  PASS
```

For `duplicate_code`, a separate full-file review of the resulting `after.py` source also returned no issues.

For `long_function`, the full-file benchmark suite already contains multiple false negatives for the same rule.

These results suggest that maintainability detection is a broader **issue-recognition weakness**, not specifically a diff-review attribution problem.

---

## Current Diff Review Behavior

Across the expanded 19-case suite, the current behavior can be summarized as:

```text
ATTRIBUTION WEAKNESS
├── mutable_default_argument
├── sql_injection
└── shell_injection

ISSUE-RECOGNITION WEAKNESS
├── duplicate_code
└── long_function

CURRENTLY PASSING
├── unreachable_code
├── list_membership_in_loop
├── string_concatenation_in_loop
└── path_traversal
```

All seven detected positive issues have the expected normalized severity:

```text
Severity accuracy: 7/7 (100%)
```

The expanded benchmark therefore changes the interpretation of the original result.

The initial 11-case suite suggested that **change attribution** was the main diff-review weakness.

The 19-case suite shows that there are at least two separate problems:

1. **Rule-specific attribution failures** for mutable defaults, SQL injection, and shell injection.
2. **Issue-recognition failures** for the two maintainability rules.

This distinction is important for future experiments because the two failure classes should not necessarily be addressed with the same prompt or architecture changes.

---

## Diff Prompt Evolution

Git-diff review uses a separate prompt from full-file review.

The diff prompt receives:

- The Git diff
- The current contents of changed Python files
- The same structured output requirements used by the rest of the reviewer

Prompt v9 remains the current baseline.

Prompt v10 tested stronger change-attribution instructions but did not improve benchmark performance.

The current experimental history is:

```text
v9
    ↓
Initial 11-case diff baseline
    ↓
8/11 — 72.7%
    ↓
Three attribution false positives
    ↓
v10 attribution experiment
    ↓
8/11 — 72.7%
    ↓
No improvement
    ↓
Expand suite across all taxonomy rules
    ↓
19 cases
    ↓
v9  = 14/19 — 73.68%
v10 = 14/19 — 73.68%
    ↓
Same five failures
```

The expanded experiment indicates that repeatedly strengthening general attribution instructions is unlikely to be the most useful immediate direction.

It also shows that not every failure is an attribution failure.

The next experimental phase should therefore distinguish between:

```text
attribution problems
        ↓
mutable_default_argument
sql_injection
shell_injection

recognition problems
        ↓
duplicate_code
long_function
```

This keeps future experiments targeted at the actual measured behavior rather than treating all diff-review failures as the same problem.

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

- False positives
- False negatives
- Rule mismatches
- Category mismatches
- Severity mismatches

### Cross-Run Regression Analysis

Compare two specific runs benchmark by benchmark:

```bash
uv run python main.py compare-runs \
    results/v4/qwen3.5-9b-seed42-block5.json \
    results/v5/qwen3.5-9b-seed42-block5.json
```

This identifies:

- Fixed benchmarks
- Regressed benchmarks
- Benchmarks that remain failing
- Added benchmarks
- Removed benchmarks

Together, these tools provide three levels of experiment analysis:

```text
Aggregate comparison
        ↓
Rule / category analysis
        ↓
Individual benchmark regression analysis
```

The same evaluation and serialization foundation is also used by diff benchmark runs, allowing diff prompt experiments to follow the same reproducible workflow.

---

## Current Observations

### Full-File Review

- Qwen 3.5 9B produced the strongest result in the initial multi-model comparison.
- Qwen 2.5 Coder 7B provided a strong speed-to-accuracy trade-off in the initial model benchmark.
- Controlled prompt iteration improved Qwen 3.5 9B from **85.7% with v1** to **91.4% with v4** on the original 35-case suite.
- Explicit rule-specific detection boundaries were more effective than generic false-positive suppression instructions.
- Expanding the suite from 35 to 65 cases exposed additional generalization and boundary failures that were not visible in the smaller suite.
- Prompt v5 reaches **92.3% accuracy on 65 benchmarks** with **100% severity accuracy**.
- The `unreachable_code` rule currently passes all five of its full-file benchmark cases.
- `long_function` remains the clearest weak rule in the current full-file prompt.
- The v4 → v5 experiment fixed three existing failures but regressed `user_absolute_path.py`.
- Aggregate accuracy should not be used alone when deciding whether a prompt revision is better.

### Git Diff Review

- Diff review now has dedicated benchmark infrastructure rather than relying on manual examples.
- The diff suite has expanded from **11 to 19 cases**.
- All **nine rules in the current taxonomy** are now represented.
- Prompt v9 achieves **73.68% accuracy (14/19)** on the expanded suite.
- Prompt v10 produces exactly the same **73.68% accuracy (14/19)**.
- Both prompts produce **3 false positives and 2 false negatives**.
- Severity accuracy is **100% (7/7)** for detected expected issues.
- The three false positives are rule-specific attribution failures involving `mutable_default_argument`, `sql_injection`, and `shell_injection`.
- Attribution succeeds for the pre-existing `unreachable_code`, `list_membership_in_loop`, `path_traversal`, `string_concatenation_in_loop`, `duplicate_code`, and `long_function` cases.
- The two false negatives are maintainability recognition failures involving `duplicate_code` and `long_function`.
- `duplicate_code` is also missed when the same resulting source is reviewed as a complete file.
- `long_function` was already a weak rule in the full-file benchmark suite.
- The expanded suite therefore exposes both **change-attribution** and **issue-recognition** weaknesses.
- Stronger general attribution wording in v10 did not improve either class of failure.
- Prompt v9 remains the diff-review baseline.

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
19-case suite
All 9 taxonomy rules represented
Prompt v9 baseline
14/19 — 73.68% accuracy
3 FP / 2 FN
100% severity accuracy on detected expected issues
      │
      ├── attribution weaknesses
      │   ├── mutable_default_argument
      │   ├── sql_injection
      │   └── shell_injection
      │
      ├── recognition weaknesses
      │   ├── duplicate_code
      │   └── long_function
      │
      └── v10 attribution experiment
          └── identical 14/19 result
```

These should remain separate experimental tracks.

Full-file prompt improvements should be evaluated against the full-file suite.

Diff prompt improvements should be evaluated against the diff suite.

The expanded diff benchmark has now established coverage across the complete current taxonomy.

The next experiments can therefore focus on the specific measured weaknesses rather than continuing to expand coverage or repeatedly strengthening general attribution wording.

This separation allows future development toward pull-request review without losing the reproducibility of the existing full-file and diff-review experiments.