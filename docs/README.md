## Diff Benchmark Suite

The diff-review benchmark suite was initially introduced with **11 cases across five rules** and was later expanded to **21 cases covering all nine rules in the current taxonomy**.

The expanded suite deliberately combines:

* issues introduced by a diff
* pre-existing issues that should not be attributed to the diff
* safe changes
* changes whose effects appear in unchanged code
* stronger diagnostic cases for subjective maintainability rules

The current coverage is:

| Category        | Rule                          |  Cases |
| --------------- | ----------------------------- | -----: |
| Bug             | Mutable default argument      |      2 |
| Bug             | Unreachable code              |      2 |
| Security        | SQL injection                 |      2 |
| Security        | Shell injection               |      2 |
| Security        | Path traversal                |      2 |
| Performance     | List membership in loops      |      3 |
| Performance     | String concatenation in loops |      2 |
| Maintainability | Duplicate code                |      3 |
| Maintainability | Long function                 |      3 |
| **Total**       |                               | **21** |

This gives every rule in the current taxonomy at least one diff-review benchmark family.

The additional `duplicate_code` and `long_function` cases deliberately use stronger examples to distinguish failures caused by ambiguous rule boundaries from broader issue-recognition weaknesses.

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

This case later became important when comparing v9 and v10 because v10 successfully stopped reporting the pre-existing mutable default while v9 continued to produce a false positive.

### SQL Injection

The positive case changes a parameterized query into an interpolated SQL string.

The diff therefore introduces `sql_injection`.

The boundary case already contains the vulnerable interpolated query before the diff and changes only an audit message.

The existing vulnerability should not be reported because it was not introduced by the change.

Both v9 and v10 continue to report the pre-existing SQL injection incorrectly.

### Shell Injection

The positive case changes a safe argument-list subprocess call into an interpolated command executed with `shell=True`.

The diff therefore introduces `shell_injection`.

The boundary case already contains the unsafe shell command before the diff and changes only an informational message.

Again, the existing vulnerability should not be reported.

Both v9 and v10 continue to report the pre-existing shell injection incorrectly.

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

The duplicate-code family now contains three cases.

The original positive case introduces repeated normalization and validation logic across two functions.

Both v9 and v10 fail to report this case.

The pre-existing boundary case already contains the duplicated implementation before the diff and changes unrelated code.

Both prompts correctly ignore that existing duplication.

A stronger diagnostic case was then added with more substantial repeated parsing and validation logic.

The results differ:

```text
Original positive
v9   FAIL
v10  FAIL

Strong positive
v9   PASS
v10  FAIL

Pre-existing boundary
v9   PASS
v10  PASS
```

This changes the interpretation of the original failure.

Qwen 3.5 9B is capable of recognizing sufficiently substantial duplicate code under v9, so `duplicate_code` is not simply an unsupported or universally missed rule.

Instead, detection appears **threshold-sensitive**.

The original normalization example sits close enough to the model's duplication threshold that it is not reported, while the stronger case is detected.

Prompt v10 introduces an additional regression: it suppresses the stronger duplicate-code finding that v9 detects correctly.

### Long Function

The long-function family also contains three cases.

The original positive case expands a previously focused function so that it performs several responsibilities:

* input validation
* iteration and aggregation
* business-rule application
* result construction

Both v9 and v10 fail to report it.

A stronger diagnostic case was then added containing substantially more responsibility in one function, including:

* required-field validation
* item normalization
* per-item validation
* aggregation
* discount decisions
* shipping decisions
* final result construction

Despite the stronger signal, both prompts still return no issues.

The pre-existing boundary case is correctly ignored by both prompts.

The results are:

```text
Original positive
v9   FAIL
v10  FAIL

Strong positive
v9   FAIL
v10  FAIL

Pre-existing boundary
v9   PASS
v10  PASS
```

This provides stronger evidence that `long_function` is a genuine **issue-recognition weakness**.

This is also consistent with the existing full-file benchmark results, where `long_function` is already one of the weakest rules.

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

On the original 11-case suite:

| Prompt | Passed | Accuracy | False Positives | False Negatives |   Severity |
| ------ | -----: | -------: | --------------: | --------------: | ---------: |
| v9     |   8/11 |    72.7% |               3 |               0 | 5/5 (100%) |
| v10    |   8/11 |    72.7% |               3 |               0 | 5/5 (100%) |

At this stage, the stronger attribution instructions appeared to produce no improvement.

The benchmark suite was therefore expanded rather than continuing to optimize against only those three examples.

Later diagnostic cases revealed that v10 does affect model behavior, but the effect is a trade-off rather than an overall improvement.

---

## Expanded Diff Review Results

The diff suite was first expanded to **19 cases** to cover all nine taxonomy rules.

Two additional diagnostic maintainability cases were then added:

```text
duplicate_code
    substantial duplicated parsing and validation

long_function
    substantial multi-responsibility order processing
```

The current expanded suite therefore contains **21 cases**.

Both v9 and v10 were evaluated against the complete suite.

### v9 Expanded Result

```text
Model            qwen3.5:9b
Prompt           v9
Benchmarks       21
Passed           15
Failed            6
Errors            0
False positives   3
False negatives   3
Accuracy         71.43%
Severity          8/8 (100.00%)
Duration         55.79s
```

### v10 Expanded Result

```text
Model            qwen3.5:9b
Prompt           v10
Benchmarks       21
Passed           15
Failed            6
Errors            0
False positives   2
False negatives   4
Accuracy         71.43%
Severity          7/7 (100.00%)
Duration         43.89s
```

### v9 → v10 Expanded Comparison

| Prompt | Passed | Accuracy | False Positives | False Negatives |   Severity |
| ------ | -----: | -------: | --------------: | --------------: | ---------: |
| v9     |  15/21 |   71.43% |               3 |               3 | 8/8 (100%) |
| v10    |  15/21 |   71.43% |               2 |               4 | 7/7 (100%) |

The aggregate accuracy is identical:

```text
v9  = 15/21 — 71.43%
v10 = 15/21 — 71.43%
```

However, the prompts no longer produce identical benchmark outcomes.

Prompt v10 fixes one false positive but introduces one additional false negative.

This demonstrates why aggregate accuracy alone is insufficient for evaluating prompt changes.

---

## Expanded Failure Analysis

The 21-case suite reveals several distinct behaviors.

### Attribution Failures

Under v9, the three pre-existing attribution failures are:

```text
mutable_default_argument
sql_injection
shell_injection
```

Under v10, the pre-existing mutable-default case is fixed:

```text
mutable_default_argument
v9   FAIL
v10  PASS
```

However, the two security attribution failures remain:

```text
sql_injection
v9   FAIL
v10  FAIL

shell_injection
v9   FAIL
v10  FAIL
```

Attribution succeeds under both prompts for the pre-existing cases involving:

```text
unreachable_code
list_membership_in_loop
path_traversal
string_concatenation_in_loop
duplicate_code
long_function
```

The attribution problem is therefore clearly **rule-specific rather than universal**.

### Duplicate-Code Recognition

The original duplicate-code positive remains a false negative under both prompts:

```text
v9   FAIL
v10  FAIL
```

The stronger duplicate-code diagnostic produces a different result:

```text
v9   PASS
v10  FAIL
```

The pre-existing duplicate-code boundary passes under both prompts.

This suggests that `duplicate_code` detection is threshold-sensitive under v9.

It also reveals a concrete v10 regression: stronger attribution constraints suppress a legitimate maintainability finding that v9 reports correctly.

### Long-Function Recognition

Both positive long-function cases fail under both prompts:

```text
Original positive
v9   FAIL
v10  FAIL

Strong positive
v9   FAIL
v10  FAIL
```

The pre-existing boundary passes under both.

The stronger diagnostic case makes the intended rule substantially less ambiguous, yet the model still does not report it.

This provides stronger evidence that `long_function` is a genuine recognition weakness rather than merely a borderline benchmark.

### Targeted Long-Function Investigation

After the expanded diff benchmark identified `long_function` as a consistent weakness, a targeted prompt experiment was performed before moving on to other diff-review failures.

The experiment tested progressively more explicit `long_function` guidance, including:

* a more operational definition of distinct responsibilities
* explicit responsibility signals such as validation, normalization, aggregation, business-rule decisions, calculations, and result construction
* guidance for distinguishing multiple concerns from several steps belonging to one cohesive responsibility
* a concrete positive prototype describing a multi-responsibility function

These changes did not improve detection.

On the three-case diff `long_function` family, the experimental prompt continued to produce:

```text
Original positive        FAIL — false negative
Strong positive          FAIL — false negative
Pre-existing boundary    PASS
```

The deliberately stronger positive was also reviewed as an ordinary full-file review and still produced no issue.

To determine whether this behavior was specific to the new diff benchmark, the established full-file `long_function` family was evaluated separately.

Both the existing v5 baseline and the experimental wording produced:

```text
Benchmarks       4
Passed           2
Failed           2
False positives  0
False negatives  2
Accuracy         50.00%
```

The two safe cases passed:

```text
Long but focused summary function    PASS
Small focused function               PASS
```

The two expected positive cases remained false negatives:

```text
Long function                              FAIL
Multiple responsibilities in invoice processing
                                           FAIL
```

Inspection of these benchmarks showed that the existing full-file positives have a somewhat subjective maintainability boundary.

Their validation, aggregation, business-rule application, and result construction can reasonably be interpreted as distinct responsibilities, but they can also be viewed as cohesive steps of a single operation.

This makes them less definitive than a security or correctness benchmark.

The stronger diff diagnostic was therefore useful because it deliberately combined substantially more responsibility in a single function:

```text
required-field validation
        +
item normalization
        +
per-item validation
        +
aggregation
        +
discount policy
        +
shipping policy
        +
result construction
```

The model still did not report `long_function`.

The resulting behavior can therefore be summarized as:

```text
long_function

safe / focused cases
    → correctly ignored

borderline multi-responsibility positives
    → not detected

strong multi-responsibility positive
    → still not detected
```

Increasingly explicit prompt wording did not change this behavior.

This suggests that Qwen 3.5 9B is conservative when applying the current `long_function` rule and that further prompt expansion would risk tuning specifically to the benchmark rather than improving general review quality.

Further prompt tuning for `long_function` was therefore stopped.

The experimental wording was not promoted to a new baseline.

---

## v9 → v10 Behavioral Changes

The final 21-case comparison exposes a precision/recall trade-off that was not visible in the earlier aggregate results.

### Fixed by v10

```text
Pre-existing mutable default argument
v9   false positive
v10  PASS
```

Prompt v10 therefore improves change attribution for this rule.

### Regressed in v10

```text
Strong duplicate-code positive
v9   PASS
v10  false negative
```

Prompt v10 becomes more conservative and suppresses a legitimate maintainability finding.

### Unchanged Failures

Both prompts continue to fail:

```text
Original duplicate-code positive
Original long-function positive
Strong long-function positive
Pre-existing shell injection
Pre-existing SQL injection
```

The final comparison can therefore be summarized as:

```text
v9 → v10

FIXED
└── mutable_default_argument attribution

REGRESSED
└── strong duplicate_code recognition

UNCHANGED
├── duplicate_code borderline positive
├── long_function positive
├── long_function strong positive
├── shell_injection attribution
└── sql_injection attribution
```

Prompt v10 does change model behavior, but it does not improve overall benchmark accuracy.

Instead, it trades one false positive for one false negative:

```text
v9
3 FP / 3 FN

v10
2 FP / 4 FN
```

For the current reviewer, v9 therefore remains the preferred diff-review baseline.

---

## Current Diff Review Behavior

The 21-case suite now provides a more nuanced picture than the original attribution experiment.

```text
ATTRIBUTION WEAKNESS
├── sql_injection
└── shell_injection

MUTABLE DEFAULT ATTRIBUTION
├── v9   FAIL
└── v10  PASS

THRESHOLD-SENSITIVE RECOGNITION
└── duplicate_code
    ├── normal positive: v9/v10 FAIL
    ├── strong positive: v9 PASS, v10 FAIL
    └── pre-existing:    v9/v10 PASS

CONSERVATIVE / WEAK RECOGNITION
└── long_function
    ├── normal positive: v9/v10 FAIL
    ├── strong positive: v9/v10 FAIL
    ├── pre-existing:    v9/v10 PASS
    └── targeted prompt experiment: no improvement

CURRENTLY ROBUST IN THIS SUITE
├── unreachable_code
├── list_membership_in_loop
├── string_concatenation_in_loop
└── path_traversal
```

Severity normalization remains stable.

Under v9:

```text
Severity accuracy: 8/8 (100%)
```

Under v10:

```text
Severity accuracy: 7/7 (100%)
```

The difference in denominator exists because v10 misses the strong duplicate-code finding that v9 detects.

---

## Diff Prompt Evolution

Git-diff review uses a separate prompt from full-file review.

The diff prompt receives:

* The Git diff
* The current contents of changed Python files
* The same structured output requirements used by the rest of the reviewer

Prompt v9 remains the current baseline.

Prompt v10 tested stronger before/after attribution instructions.

A later targeted `long_function` experiment tested more operational rule guidance but did not improve recognition and was not promoted to a new baseline.

The experimental history is now:

```text
v9
    ↓
Initial 11-case diff baseline
    ↓
8/11 — 72.7%
3 FP / 0 FN
    ↓
v10 attribution experiment
    ↓
8/11 — 72.7%
3 FP / 0 FN
    ↓
Expand across all taxonomy rules
    ↓
19 cases
    ↓
v9  = 14/19 — 73.68%
v10 = 14/19 — 73.68%
    ↓
Add stronger maintainability diagnostics
    ↓
21 cases
    ↓
v9
15/21 — 71.43%
3 FP / 3 FN
    ↓
v10
15/21 — 71.43%
2 FP / 4 FN
    ↓
Target long_function recognition
    ↓
More operational definition
Concrete responsibility signals
Positive prototype
    ↓
No detection improvement
    ↓
Stop long_function prompt tuning
```

The final attribution experiment changes the interpretation of v10.

It is not simply behaviorally identical to v9.

Instead:

```text
stronger attribution constraints
        ↓
improve mutable-default attribution
        +
suppress strong duplicate-code detection
```

This is a precision/recall trade-off with no aggregate accuracy improvement.

Prompt v9 therefore remains the baseline rather than being replaced by v10.

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

The same evaluation and serialization foundation is also used by diff benchmark runs, allowing diff prompt experiments to follow the same reproducible workflow.

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
* `long_function` remains one of the weakest full-file rules.
* A targeted `long_function` experiment did not improve recognition.
* The existing full-file positive cases have a somewhat subjective boundary, but a deliberately stronger diagnostic was also missed.
* Further prompt tuning for `long_function` has been paused to avoid benchmark-specific overfitting.
* The v4 → v5 experiment fixed three existing failures but regressed `user_absolute_path.py`.
* Aggregate accuracy should not be used alone when deciding whether a prompt revision is better.

### Git Diff Review

* Diff review now has dedicated benchmark infrastructure rather than relying on manual examples.
* The diff suite has expanded from **11 to 21 cases**.
* All **nine rules in the current taxonomy** are represented.
* Additional strong diagnostic cases were added for `duplicate_code` and `long_function`.
* Prompt v9 achieves **71.43% accuracy (15/21)**.
* Prompt v10 also achieves **71.43% accuracy (15/21)**.
* The identical aggregate accuracy hides different error distributions.
* v9 produces **3 false positives and 3 false negatives**.
* v10 produces **2 false positives and 4 false negatives**.
* v10 fixes the pre-existing `mutable_default_argument` attribution failure.
* v10 regresses the strong `duplicate_code` positive that v9 detects correctly.
* Both prompts continue to misattribute pre-existing `sql_injection` and `shell_injection`.
* Both prompts correctly handle pre-existing `unreachable_code`, `list_membership_in_loop`, `path_traversal`, `string_concatenation_in_loop`, `duplicate_code`, and `long_function`.
* `duplicate_code` detection is threshold-sensitive: v9 detects the stronger diagnostic but not the original smaller example.
* `long_function` remains undetected even with a deliberately stronger multi-responsibility example.
* More explicit `long_function` prompt guidance did not change this behavior.
* Severity accuracy remains **100% for detected expected issues** under both prompts.
* Prompt v10 changes the precision/recall balance but does not improve overall accuracy.
* Prompt v9 remains the diff-review baseline.

---

## Current Evaluation State

The project now has two complementary evaluation systems:

```text
FULL-FILE REVIEW
65-case suite
Prompt v5 baseline
92.3% accuracy
      │
      ├── measures issue recognition and rule boundaries
      │
      └── long_function targeted investigation
          ├── full-file family: 2/4
          ├── both positive cases missed
          ├── both safe cases correctly ignored
          └── stronger prompt guidance produced no improvement


GIT-DIFF REVIEW
21-case suite
All 9 taxonomy rules represented
Prompt v9 baseline
15/21 — 71.43%
3 FP / 3 FN
8/8 severity — 100%
      │
      ├── attribution weaknesses
      │   ├── sql_injection
      │   └── shell_injection
      │
      ├── mutable-default attribution
      │   ├── v9  FAIL
      │   └── v10 PASS
      │
      ├── threshold-sensitive recognition
      │   └── duplicate_code
      │
      ├── conservative recognition
      │   └── long_function
      │
      └── v10 attribution experiment
          ├── 15/21 — 71.43%
          ├── 2 FP / 4 FN
          ├── fixes mutable-default attribution
          └── regresses strong duplicate-code detection
```

These should remain separate experimental tracks.

Full-file prompt improvements should be evaluated against the full-file suite.

Diff prompt improvements should be evaluated against the diff suite.

The expanded diff benchmark now covers the complete current taxonomy and contains targeted diagnostics for the two subjective maintainability rules.

The targeted `long_function` investigation did not improve recognition despite increasingly explicit rule guidance.

Further prompt tuning for this rule has therefore been paused rather than continuing to optimize against a subjective benchmark boundary.

The next experimental phase should focus on the remaining rule-specific change-attribution failures:

```text
sql_injection
shell_injection
```

Both rules are detected correctly when introduced by a diff, but both are incorrectly reported when the vulnerability already existed before an unrelated change.

Unlike `long_function`, these attribution cases have a much less subjective expected result:

```text
BEFORE vulnerable
        +
unrelated change
        +
AFTER same vulnerability
        ↓
do not report
```

They therefore provide a cleaner target for the next controlled diff-prompt experiment.

The next step is to use the clean v11 prompt, based on the v9 baseline, to investigate whether security-specific attribution guidance can fix these false positives without reproducing the broader precision/recall regression observed with v10.
