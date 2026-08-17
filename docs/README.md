## Diff Benchmark Suite

The diff-review benchmark suite was initially introduced with **11 cases across five rules** and was later expanded to **21 cases covering all nine rules in the current taxonomy**.

The expanded suite deliberately combines:

- issues introduced by a diff
- pre-existing issues that should not be attributed to the diff
- safe changes
- changes whose effects appear in unchanged code
- stronger diagnostic cases for subjective maintainability rules

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
| Maintainability | Duplicate code | 3 |
| Maintainability | Long function | 3 |
| **Total** | | **21** |

This gives every rule in the current taxonomy at least one diff-review benchmark family.

The additional `duplicate_code` and `long_function` cases deliberately use stronger examples to distinguish failures caused by ambiguous rule boundaries from broader issue-recognition weaknesses.

---

## Benchmark Design

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

This case tests whether the model can distinguish an issue visible in the current code from an issue introduced by the change.

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

This case became particularly useful during prompt evolution because v9 incorrectly attributed the existing issue while later prompts were able to suppress it.

### SQL Injection

The positive case changes a parameterized query into an interpolated SQL string.

The diff therefore introduces `sql_injection`.

The boundary case already contains the vulnerable interpolated query before the diff and changes only an audit message.

The existing vulnerability should not be reported because it was not introduced by the change.

Prompt v11 successfully distinguishes both cases.

### Shell Injection

The positive case changes a safe argument-list subprocess call into an interpolated command executed with `shell=True`.

The diff therefore introduces `shell_injection`.

The boundary case already contains the unsafe shell command before the diff and changes only an informational message.

Prompt v11 successfully distinguishes both cases.

### Path Traversal

The positive case removes filename sanitization and changes safe path construction into a direct join between an intended base directory and a user-controlled path.

This allows values such as parent-directory traversal or absolute paths to escape the intended directory.

The boundary case already contains the unsafe path construction before the diff and changes only an informational message.

The current baseline correctly detects the introduced case and ignores the pre-existing case.

### String Concatenation in Loops

The positive case changes efficient `str.join()` construction into repeated `+=` concatenation inside a loop.

The boundary case already contains repeated string concatenation before the diff and changes only unrelated reporting logic.

The current baseline correctly distinguishes the introduced issue from the pre-existing one.

### Duplicate Code

The duplicate-code family contains three cases.

The original positive case introduces repeated normalization and validation logic across two functions.

A stronger diagnostic case contains substantially more repeated parsing and validation logic.

The third case contains duplication that already existed before the diff.

Under the current Qwen 3.5 9B + v11 baseline:

```text
Original positive       FAIL
Strong positive         FAIL
Pre-existing boundary   PASS
```

Earlier experiments showed that v9 could detect the stronger case:

```text
Strong positive
v9   PASS
v10  FAIL
v11  FAIL
```

This shows that `duplicate_code` recognition is sensitive to both the strength of the example and prompt behavior.

The v11 attribution improvements therefore come with a maintainability-recall trade-off compared with v9.

### Long Function

The long-function family also contains three cases.

The original positive expands a previously focused function to perform several responsibilities:

- input validation
- iteration and aggregation
- business-rule application
- result construction

The stronger diagnostic adds:

- required-field validation
- item normalization
- per-item validation
- aggregation
- discount decisions
- shipping decisions
- final result construction

Under the current baseline:

```text
Original positive       FAIL
Strong positive         FAIL
Pre-existing boundary   PASS
```

A targeted prompt experiment tested increasingly explicit `long_function` guidance, including operational responsibility definitions and concrete positive examples.

Detection did not improve.

The established full-file `long_function` benchmark family showed the same pattern:

```text
Benchmarks       4
Passed           2
Failed           2
False positives  0
False negatives  2
Accuracy         50.00%
```

Both safe cases passed while both positives remained false negatives.

Further prompt tuning for this rule was therefore stopped to avoid benchmark-specific overfitting.

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

All three failures involved pre-existing issues:

```text
mutable_default_argument
shell_injection
sql_injection
```

This identified **change attribution** as the primary weakness of the initial diff reviewer.

---

## Expanded v9 Baseline

The suite was subsequently expanded to 21 cases covering all nine taxonomy rules.

Qwen 3.5 9B with v9 produced:

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

The failures exposed two distinct problems:

```text
ATTRIBUTION
├── pre-existing mutable_default_argument
├── pre-existing sql_injection
└── pre-existing shell_injection

RECOGNITION
├── duplicate_code
├── long_function
└── strong long_function
```

The stronger `duplicate_code` diagnostic passed under v9.

---

## v10 Attribution Experiment

Prompt v10 tested stronger generic before/after attribution instructions.

The core decision model was:

```text
BEFORE safe   → AFTER unsafe       → report
BEFORE unsafe → AFTER worse        → report
BEFORE unsafe → AFTER same unsafe  → do not report
BEFORE safe   → AFTER safe         → do not report
```

On the complete 21-case suite:

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

v10 fixed:

```text
pre-existing mutable_default_argument
```

but continued to misattribute:

```text
pre-existing sql_injection
pre-existing shell_injection
```

It also regressed:

```text
strong duplicate_code positive
```

The result was therefore a precision/recall trade-off rather than an overall improvement:

```text
v9
15/21
3 FP / 3 FN

v10
15/21
2 FP / 4 FN
```

Generic attribution constraints were not sufficient to justify replacing v9.

---

## Targeted Long-Function Investigation

After the expanded suite identified `long_function` as a consistent weakness, a targeted experiment tested progressively more explicit guidance.

The experiment included:

- a more operational definition of distinct responsibilities
- explicit responsibility signals
- guidance for distinguishing several concerns from cohesive steps
- a concrete multi-responsibility positive prototype

The result remained:

```text
Original positive       FAIL
Strong positive         FAIL
Pre-existing boundary   PASS
```

The same behavior appeared in the established full-file benchmark family.

This suggests that Qwen 3.5 9B is conservative when applying the current `long_function` rule.

Because increasingly explicit prompt wording did not improve general recognition, further tuning was stopped.

---

## v11 Targeted Attribution Experiment

Prompt v11 returned to the v9-style baseline and targeted the remaining attribution failures more precisely.

Instead of making the reviewer globally more conservative, v11 instructs the model to compare the **actual triggering code before and after the change**.

The central principle is:

```text
identify triggering code
        ↓
compare BEFORE and AFTER
        ↓
trigger unchanged + unrelated diff
        ↓
pre-existing issue
        ↓
do not report
```

For security rules, this means checking whether the vulnerable SQL construction, shell command construction, or dangerous execution behavior itself changed.

### SQL Injection

```text
Introduced SQL injection       PASS
Pre-existing SQL injection     PASS
```

Result:

```text
2/2 — 100%
0 FP
0 FN
```

### Shell Injection

```text
Introduced shell injection     PASS
Pre-existing shell injection   PASS
```

Result:

```text
2/2 — 100%
0 FP
0 FN
```

Because both targeted families improved without losing detection of newly introduced vulnerabilities, v11 was evaluated against the complete suite.

---

## Current v11 Diff Baseline

Qwen 3.5 9B with prompt v11 produces:

```text
Model            qwen3.5:9b
Prompt           v11
Benchmarks       21
Passed           17
Failed            4
Errors            0
False positives   0
False negatives   4
Accuracy         80.95%
Severity          7/7 (100.00%)
Duration         41.48s
```

This is the strongest diff-review result so far.

### Prompt Comparison

| Prompt | Passed | Accuracy | False Positives | False Negatives | Severity |
| --- | ---: | ---: | ---: | ---: | ---: |
| v9 | 15/21 | 71.43% | 3 | 3 | 8/8 (100%) |
| v10 | 15/21 | 71.43% | 2 | 4 | 7/7 (100%) |
| **v11** | **17/21** | **80.95%** | **0** | **4** | **7/7 (100%)** |

v11 improves accuracy by approximately **9.5 percentage points** over v9 and v10.

More importantly, it eliminates all false positives in the current Qwen 3.5 9B diff suite.

---

## v9 → v11 Regression Analysis

The exported v9 and v11 runs were compared benchmark by benchmark.

```text
Old: v9 / qwen3.5:9b — 15/21 (71.4%)
New: v11 / qwen3.5:9b — 17/21 (81.0%)

Comparable: 21
Fixed: 3
Regressed: 1
Still failing: 3
Added: 0
Removed: 0
```

### Fixed

```text
pre-existing mutable_default_argument
pre-existing shell_injection
pre-existing sql_injection
```

### Regressed

```text
strong duplicate_code positive
```

### Still Failing

```text
duplicate_code positive
long_function positive
strong long_function positive
```

The final behavioral change is:

```text
v9 → v11

FIXED
├── mutable_default_argument attribution
├── shell_injection attribution
└── sql_injection attribution

REGRESSED
└── strong duplicate_code recognition

STILL FAILING
├── duplicate_code positive
├── long_function positive
└── strong long_function positive
```

Unlike v10, the v11 trade-off produces a clear aggregate improvement.

Prompt v11 is therefore the current diff-review baseline.

---

## Cross-Model v11 Evaluation

After establishing v11 as the Qwen 3.5 9B baseline, the complete 21-case suite was run against the other local models already used by the project.

The experiment kept the following fixed:

```text
same 21 diff benchmarks
same v11 prompt
same deterministic generation settings
same evaluator
```

Only the model changed.

### Results

| Model | Passed | Accuracy | False Positives | False Negatives |
| --- | ---: | ---: | ---: | ---: |
| **Qwen 3.5 9B** | **17/21** | **80.95%** | **0** | 4 |
| Qwen 2.5 Coder 7B | 15/21 | 71.43% | **0** | 6 |
| Qwen 2.5 Coder 14B | 13/21 | 61.90% | 4 | 4 |
| Gemma 3 12B | 13/21 | 61.90% | 4 | 4 |
| Llama 3.1 8B | 5/21 | 23.81% | 10 | 0* |
| DeepSeek Coder V2 16B | 3/21 | 14.29% | 10 | 0* |

`*` The zero false-negative count for Llama 3.1 8B and DeepSeek Coder V2 16B is misleading when viewed alone.

These models frequently predict an issue using the **wrong rule** rather than returning no issue.

Those failures are surfaced individually by the evaluator but are not currently represented as a separate aggregate summary count.

This cross-model experiment therefore exposed a useful future evaluation improvement: aggregate summaries should distinguish rule mismatches from ordinary false positives and false negatives.

---

## Cross-Model Failure Analysis

### Qwen 3.5 9B

```text
17/21 — 80.95%
0 FP
4 FN
```

The four failures are concentrated entirely in maintainability recognition:

```text
duplicate_code
├── normal positive   FAIL
└── strong positive   FAIL

long_function
├── normal positive   FAIL
└── strong positive   FAIL
```

All current pre-existing attribution boundary cases pass.

This remains the strongest overall model/prompt combination.

### Qwen 2.5 Coder 7B

```text
15/21 — 71.43%
0 FP
6 FN
```

Like Qwen 3.5 9B, the 7B model produces no false positives and handles the current attribution boundaries well.

It also misses all four maintainability positives.

Its two additional false negatives are introduced performance issues:

```text
list_membership_in_loop
string_concatenation_in_loop
```

The result suggests a useful trade-off:

```text
Qwen 2.5 Coder 7B
    ↓
strong precision / attribution
    +
lower issue-recognition recall
```

It remains interesting as a smaller and faster reviewer, but Qwen 3.5 9B is substantially stronger overall.

### Qwen 2.5 Coder 14B

```text
13/21 — 61.90%
4 FP
4 FN
```

The larger Qwen 2.5 Coder model recovers some findings missed by the 7B version but performs worse on attribution.

Its false positives include pre-existing cases such as:

```text
mutable_default_argument
string_concatenation_in_loop
shell_injection
sql_injection
```

This demonstrates that larger parameter count does not automatically produce better behavior under a fixed review prompt.

The 14B model trades stronger recall in some areas for weaker change attribution.

### Gemma 3 12B

```text
13/21 — 61.90%
4 FP
4 FN
```

Gemma reaches the same aggregate accuracy as Qwen 2.5 Coder 14B but does not fail on exactly the same cases.

This reinforces the importance of benchmark-level analysis.

Two models with identical aggregate scores can exhibit substantially different review behavior.

### Llama 3.1 8B

```text
5/21 — 23.81%
10 FP
0 ordinary FN
```

The apparent zero false-negative count does not indicate strong recall.

The model frequently selects incorrect rules, including repeated `sql_injection` predictions for unrelated benchmark cases.

Its behavior therefore reflects broader taxonomy/instruction-following instability rather than merely conservative issue detection.

### DeepSeek Coder V2 16B

```text
3/21 — 14.29%
10 FP
0 ordinary FN
```

DeepSeek exhibits similar but even stronger rule-selection instability.

Examples include predicting:

```text
mutable_default_argument
```

for unrelated maintainability cases and:

```text
unreachable_code
```

for a string-concatenation performance case.

The result suggests that this model/prompt pairing is currently unsuitable for the constrained taxonomy reviewer.

---

## Maintainability Findings Across Models

The cross-model experiment was especially useful for evaluating the remaining Qwen 3.5 9B maintainability failures.

Among the models with reasonably stable taxonomy behavior, the same pattern appears repeatedly.

### Duplicate Code

```text
                       Normal     Strong
Qwen 3.5 9B            FAIL       FAIL
Qwen 2.5 Coder 7B      FAIL       FAIL
Qwen 2.5 Coder 14B     FAIL       FAIL
Gemma 3 12B             FAIL       FAIL
```

### Long Function

```text
                       Normal     Strong
Qwen 3.5 9B            FAIL       FAIL
Qwen 2.5 Coder 7B      FAIL       FAIL
Qwen 2.5 Coder 14B     FAIL       FAIL
Gemma 3 12B             FAIL       FAIL
```

Llama 3.1 8B and DeepSeek Coder V2 16B are not strong evidence for this comparison because their taxonomy selection is unstable across the suite.

The important conclusion is that the remaining maintainability failures are **not unique to Qwen 3.5 9B**.

Several different local models fail to apply the current `duplicate_code` and `long_function` definitions to the positive benchmark cases.

Combined with the earlier targeted `long_function` prompt experiment, this reduces the value of continuing to tune v11 specifically to force these cases to pass.

The current evidence suggests a broader interaction between:

```text
subjective maintainability rules
        +
constrained taxonomy
        +
local model recognition thresholds
```

rather than a simple Qwen 3.5 9B prompt defect.

---

## Model Selection

The current diff-review model comparison can be summarized as:

```text
Qwen 3.5 9B
├── best overall accuracy
├── 0 false positives
├── strongest issue recall among precise models
└── current default

Qwen 2.5 Coder 7B
├── 0 false positives
├── good attribution
├── lower recall
└── useful smaller/faster alternative

Qwen 2.5 Coder 14B
├── stronger recognition in some cases
└── weaker attribution

Gemma 3 12B
├── moderate overall result
└── attribution failures remain

Llama 3.1 8B
└── unstable constrained-rule selection

DeepSeek Coder V2 16B
└── unstable constrained-rule selection
```

Qwen 3.5 9B therefore remains the preferred model for the current local reviewer.

The project may later be evaluated on hardware with more VRAM using substantially larger coding or reasoning models.

Because the benchmark suite and prompt versions are frozen and reproducible, those future models can be evaluated directly against the current baseline.

---

## Result Analysis

The project provides complementary ways to analyze exported benchmark results.

### Aggregate Comparison

```bash
uv run python main.py compare-results results/v5/
```

Results can also be grouped by rule or category:

```bash
uv run python main.py compare-results results/v5/ --by-rule
uv run python main.py compare-results results/v5/ --by-category
```

### Individual Run Analysis

```bash
uv run python main.py analyze-result \
    results/v5/qwen3.5-9b-seed42-block5.json
```

This surfaces:

- false positives
- false negatives
- rule mismatches
- category mismatches
- severity mismatches

### Cross-Run Regression Analysis

```bash
uv run python main.py compare-runs \
    results/diff/v9/qwen3.5-9b-expanded.json \
    results/diff/v11/qwen3.5-9b.json
```

Diff benchmark results are supported by `compare-runs`.

The comparison identifies:

- fixed benchmarks
- regressed benchmarks
- benchmarks that remain failing
- added benchmarks
- removed benchmarks

Together, the analysis tools provide:

```text
Aggregate metrics
        ↓
Rule / category analysis
        ↓
Benchmark-level regression analysis
```

### Evaluation Limitation Identified by Cross-Model Testing

The cross-model experiment exposed one limitation in the current aggregate summaries.

A positive benchmark can fail because:

```text
expected issue
    ↓
model reports nothing
    ↓
false negative
```

but it can also fail because:

```text
expected rule
    ↓
model reports a different rule
    ↓
rule mismatch
```

The evaluator already exposes rule mismatches in individual results.

However, aggregate summaries currently emphasize false-positive and false-negative counts without a separate wrong-rule count.

This can make models with unstable rule selection appear less problematic than they actually are.

For example:

```text
False negatives: 0
```

does not necessarily mean all expected issues were recognized correctly if several positive cases instead failed through rule mismatches.

A future evaluator improvement should therefore consider exposing rule mismatches explicitly in aggregate benchmark summaries.

---

## Current Observations

### Full-File Review

- Qwen 3.5 9B produced the strongest result in the initial multi-model comparison.
- Controlled prompt iteration improved the full-file reviewer significantly.
- Prompt v5 remains the full-file baseline.
- v5 reaches **92.3% accuracy on 65 benchmarks**.
- Severity accuracy remains **100%**.
- `unreachable_code` currently performs strongly.
- `long_function` remains one of the weakest full-file rules.
- A targeted `long_function` experiment did not improve recognition.
- Further prompt tuning for that rule was paused to avoid benchmark-specific overfitting.
- Aggregate accuracy should not be used alone when deciding whether a prompt revision is better.

### Git Diff Review

- The diff suite contains **21 cases covering all nine rules**.
- v9 achieved **15/21 — 71.43%** with **3 FP / 3 FN**.
- v10 achieved **15/21 — 71.43%** with **2 FP / 4 FN**.
- v11 achieves **17/21 — 80.95%** with **0 FP / 4 FN**.
- v11 fixes all three attribution false positives present under v9.
- Pre-existing mutable-default, SQL-injection, and shell-injection cases now pass.
- Newly introduced SQL and shell vulnerabilities remain correctly detected.
- v11 regresses the strong `duplicate_code` case that v9 detected.
- All remaining Qwen 3.5 9B failures are maintainability false negatives.
- Severity accuracy remains **100% for detected expected issues**.
- v11 is the current diff-review baseline.

### Cross-Model Diff Review

- Qwen 3.5 9B remains the strongest model at **80.95%**.
- Qwen 2.5 Coder 7B is second at **71.43%** and also produces zero false positives.
- Qwen 2.5 Coder 14B and Gemma 3 12B both reach **61.90%** but exhibit more attribution failures.
- Llama 3.1 8B and DeepSeek Coder V2 16B perform poorly with the constrained taxonomy prompt.
- Larger parameter count does not automatically improve diff-review performance.
- Models with identical aggregate accuracy can fail on different benchmark cases.
- The `duplicate_code` and `long_function` positives are missed across several otherwise reasonably behaving models.
- The remaining maintainability weakness is therefore not specific to Qwen 3.5 9B.
- Cross-model testing exposed the need for clearer aggregate reporting of wrong-rule failures.

---

## Current Evaluation State

```text
FULL-FILE REVIEW
65-case suite
Prompt v5 baseline
Qwen 3.5 9B
60/65 — 92.3%
100% severity accuracy
      │
      └── known weakness
          └── long_function


GIT-DIFF REVIEW
21-case suite
All 9 taxonomy rules represented
Prompt v11 baseline
Qwen 3.5 9B
17/21 — 80.95%
0 FP / 4 FN
7/7 severity — 100%
      │
      ├── attribution
      │   └── all current pre-existing boundaries PASS
      │
      ├── robust introduced-issue detection
      │   ├── mutable_default_argument
      │   ├── unreachable_code
      │   ├── sql_injection
      │   ├── shell_injection
      │   ├── path_traversal
      │   ├── list_membership_in_loop
      │   └── string_concatenation_in_loop
      │
      └── remaining recognition weaknesses
          ├── duplicate_code
          │   ├── normal positive FAIL
          │   └── strong positive FAIL
          │
          └── long_function
              ├── normal positive FAIL
              └── strong positive FAIL


CROSS-MODEL v11
      │
      ├── Qwen 3.5 9B
      │   └── 17/21 — 80.95%
      │
      ├── Qwen 2.5 Coder 7B
      │   └── 15/21 — 71.43%
      │
      ├── Qwen 2.5 Coder 14B
      │   └── 13/21 — 61.90%
      │
      ├── Gemma 3 12B
      │   └── 13/21 — 61.90%
      │
      ├── Llama 3.1 8B
      │   └── 5/21 — 23.81%
      │
      └── DeepSeek Coder V2 16B
          └── 3/21 — 14.29%
```

The single-pass diff-review prompt investigation is now sufficiently mature to stop optimizing specifically around the remaining maintainability cases.

The main findings are:

```text
concrete before/after trigger comparison
        ↓
improves change attribution

generic conservatism
        ↓
can suppress legitimate findings

subjective maintainability rules
        ↓
remain difficult across several local models

larger model
        ↓
does not automatically mean better reviewer

aggregate accuracy alone
        ↓
is insufficient for understanding model behavior
```

The immediate next engineering improvement should be small and evaluation-focused:

```text
make aggregate failure summaries distinguish
wrong-rule / rule-mismatch failures more clearly
```

After that evaluation improvement, the project can move beyond further single-prompt tuning and into the next architectural experiment.