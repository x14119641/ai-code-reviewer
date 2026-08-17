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

The current general baseline correctly detects the introduced case and ignores the pre-existing case.

### String Concatenation in Loops

The positive case changes efficient `str.join()` construction into repeated `+=` concatenation inside a loop.

The boundary case already contains repeated string concatenation before the diff and changes only unrelated reporting logic.

The current general baseline correctly distinguishes the introduced issue from the pre-existing one.

### Duplicate Code

The duplicate-code family contains three cases.

The original positive case introduces repeated normalization and validation logic across two functions.

A stronger diagnostic case contains substantially more repeated parsing and validation logic.

The third case contains duplication that already existed before the diff.

Under the single-pass Qwen 3.5 9B + v11 baseline:

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

This showed that `duplicate_code` recognition was sensitive to both the strength of the example and prompt behavior.

Later specialist experiments changed this result substantially.

Using the focused `maintainability_v1` prompt:

```text
Original positive       PASS
Strong positive         PASS
Pre-existing boundary   PASS
```

The specialist therefore reaches:

```text
3/3 — 100%
0 FP
0 FN
```

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

Under the single-pass v11 baseline:

```text
Original positive       FAIL
Strong positive         FAIL
Pre-existing boundary   PASS
```

A targeted general-prompt experiment tested increasingly explicit `long_function` guidance, including operational responsibility definitions and concrete positive examples.

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

However, the later focused maintainability specialist improved the diff benchmark family to:

```text
Original positive       FAIL
Strong positive         PASS
Pre-existing boundary   PASS
```

Result:

```text
2/3 — 66.67%
0 FP
1 FN
```

This distinction became important: additional general prompt tuning did not help, while narrowing the task to a maintainability-specific prompt did.

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

This suggested that Qwen 3.5 9B was conservative when applying the `long_function` rule inside a general review prompt.

Because increasingly explicit general prompt wording did not improve recognition, further single-prompt tuning was stopped.

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

## Single-Pass v11 Diff Baseline

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
Wrong rules       0
Accuracy         80.95%
Severity          7/7 (100.00%)
Duration         41.48s
```

### Prompt Comparison

| Prompt | Passed | Accuracy | False Positives | False Negatives | Severity |
| --- | ---: | ---: | ---: | ---: | ---: |
| v9 | 15/21 | 71.43% | 3 | 3 | 8/8 (100%) |
| v10 | 15/21 | 71.43% | 2 | 4 | 7/7 (100%) |
| **v11** | **17/21** | **80.95%** | **0** | **4** | **7/7 (100%)** |

v11 improves accuracy by approximately **9.5 percentage points** over v9 and v10.

More importantly, it eliminates all false positives in the current Qwen 3.5 9B diff suite.

v11 remains the strongest **single-pass** diff prompt.

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

Prompt v11 therefore became the frozen single-pass diff-review baseline.

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

`*` The original cross-model runs predated aggregate rule-mismatch counting.

The zero false-negative count for Llama 3.1 8B and DeepSeek Coder V2 16B was therefore misleading when viewed alone.

These models frequently predicted an issue using the **wrong rule** rather than returning no issue.

This observation directly motivated an evaluator improvement that now tracks wrong-rule failures separately from false positives and false negatives.

---

## Aggregate Rule-Mismatch Evaluation

The benchmark evaluator distinguishes three important failure modes:

```text
expected no issue + issue reported
        ↓
false positive

expected issue + nothing reported
        ↓
false negative

expected issue + different rule reported
        ↓
wrong rule / rule mismatch
```

A rule mismatch is counted when:

```text
benchmark expects an issue
        +
model reports at least one issue
        +
none of the reported issues uses the expected rule
```

This prevents a model that aggressively predicts incorrect rules from appearing to have strong recall merely because its false-negative count is zero.

The metric is:

- stored on individual benchmark evaluations
- aggregated by `BenchmarkRun`
- serialized in benchmark result exports
- loaded by result-analysis tooling
- available in rule/category summaries
- displayed in benchmark summary output

### DeepSeek Validation Run

DeepSeek Coder V2 16B was rerun against the complete v11 diff suite after adding the metric.

```text
Model            deepseek-coder-v2:16b
Prompt           v11
Benchmarks       21
Passed            3
Failed           18
Errors            0
False positives  10
False negatives   0
Wrong rules       6
Accuracy         14.29%
Severity          3/3 (100.00%)
Duration         205.06s
```

The six wrong-rule failures were:

```text
duplicate_code
├── normal positive
└── strong positive

long_function
├── normal positive
└── strong positive

list_membership_in_loop
└── introduced positive

string_concatenation_in_loop
└── introduced positive
```

Instead of missing these cases completely, DeepSeek reported unrelated supported rules.

Examples included:

```text
expected duplicate_code
actual   mutable_default_argument

expected long_function
actual   mutable_default_argument

expected list_membership_in_loop
actual   mutable_default_argument

expected string_concatenation_in_loop
actual   unreachable_code
```

The new aggregate summary therefore describes the model substantially better:

```text
3 passed
10 false-positive attribution failures
6 wrong-rule failures
0 ordinary false negatives
```

The apparent `0 FN` no longer hides the taxonomy-selection problem.

---

## Cross-Model Failure Analysis

### Qwen 3.5 9B

Single-pass v11:

```text
17/21 — 80.95%
0 FP
4 FN
0 wrong rules
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

### Gemma 3 12B

```text
13/21 — 61.90%
4 FP
4 FN
```

Gemma reaches the same aggregate accuracy as Qwen 2.5 Coder 14B but does not fail on exactly the same cases.

This reinforces the importance of benchmark-level analysis.

### Llama 3.1 8B

```text
5/21 — 23.81%
10 FP
0 ordinary FN
```

The apparent zero false-negative count does not indicate strong recall.

The model frequently selects incorrect rules.

The original run predates aggregate wrong-rule counting, so a historical aggregate wrong-rule value is not asserted here.

### DeepSeek Coder V2 16B

```text
3/21 — 14.29%
10 FP
0 ordinary FN
6 wrong rules
```

DeepSeek exhibits strong rule-selection instability.

The explicit `Wrong rules: 6` metric now captures this behavior directly.

---

## Maintainability Findings Across Models

The cross-model experiment was especially useful for evaluating the remaining Qwen 3.5 9B maintainability failures.

Among the models with reasonably stable taxonomy behavior, the same single-pass pattern appears repeatedly.

### Duplicate Code

```text
                       Normal     Strong
Qwen 3.5 9B            FAIL       FAIL
Qwen 2.5 Coder 7B      FAIL       FAIL
Qwen 2.5 Coder 14B     FAIL       FAIL
Gemma 3 12B            FAIL       FAIL
```

### Long Function

```text
                       Normal     Strong
Qwen 3.5 9B            FAIL       FAIL
Qwen 2.5 Coder 7B      FAIL       FAIL
Qwen 2.5 Coder 14B     FAIL       FAIL
Gemma 3 12B            FAIL       FAIL
```

The important conclusion was that the maintainability failures were **not unique to Qwen 3.5 9B**.

At this stage, further expansion of the general v11 prompt had diminishing value.

That observation motivated the next architectural experiment: reducing the number of rules considered by an individual LLM call.

---

## Structured Output Improvement

The multi-pass experiment initially exposed another problem: candidate-generation prompts did not always return machine-readable JSON.

For example, the model could respond with prose, tool-like structures, or free-form findings even when the prompt requested JSON.

The Ollama integration was therefore extended to support an optional structured output format.

Instead of globally forcing every request into JSON mode, `generate_review()` accepts an optional schema:

```text
generate_review(
    prompt,
    model,
    output_format=...
)
```

Review requests can provide the project's review response JSON Schema.

This constrains generated findings to the expected structure:

```text
{
    "issues": [...]
}
```

while preserving the existing parser and taxonomy validation as a second validation boundary.

The resulting pipeline is:

```text
Prompt
   ↓
Ollama JSON Schema constraint
   ↓
JSON response
   ↓
parse_review_response()
   ↓
taxonomy validation
   ↓
CodeReview
```

This made experimental candidate generation significantly more reliable and removed output-format failures from the maintainability investigation.

---

## Candidate-Generation Experiment

The first multi-pass step separated issue discovery from final review.

A new candidate-generation prompt was introduced:

```text
diff + current source
        ↓
candidate-generation prompt
        ↓
potential findings
```

The initial generic candidate prompt still struggled with the maintainability cases.

This demonstrated that simply adding another LLM call did not automatically improve recall.

The main problem remained the scope of the task.

The model was still being asked to reason across the complete taxonomy.

---

## Maintainability Specialist Experiment

A focused prompt version, `maintainability_v1`, was created specifically for:

```text
duplicate_code
long_function
```

The purpose was not to teach the model benchmark answers.

Instead, the experiment tested whether reducing taxonomy competition and narrowing the reasoning task would improve recognition.

### Duplicate Code Candidate Results

```text
Model            qwen3.5:9b
Prompt           maintainability_v1
Benchmarks       3
Passed           3
Failed            0
Errors            0
False positives   0
False negatives   0
Wrong rules       0
Accuracy         100.00%
Severity          2/2 (100.00%)
Duration         10.05s
```

This recovered both positive cases missed by v11:

```text
Original positive       PASS
Strong positive         PASS
Pre-existing boundary   PASS
```

### Long Function Candidate Results

```text
Model            qwen3.5:9b
Prompt           maintainability_v1
Benchmarks       3
Passed           2
Failed            1
Errors            0
False positives   0
False negatives   1
Wrong rules       0
Accuracy         66.67%
Severity          1/1 (100.00%)
Duration          7.03s
```

The stronger positive was recovered:

```text
Original positive       FAIL
Strong positive         PASS
Pre-existing boundary   PASS
```

The focused prompt therefore changed maintainability behavior from:

```text
v11 general

duplicate_code   1/3
long_function    1/3
```

to:

```text
maintainability_v1

duplicate_code   3/3
long_function    2/3
```

This was the first strong evidence that the remaining weakness could be addressed through **task specialization** rather than increasingly benchmark-specific general prompt instructions.

---

## Candidate + Verifier Multi-Pass Experiment

A second LLM pass was then added to verify candidate findings.

The architecture was:

```text
Diff + Current Source
        ↓
Candidate Generator
        ↓
Candidate Issues
        ↓
Verifier
        ↓
Final CodeReview
```

The verifier was designed to reject unsupported candidate findings while preserving valid ones.

### Duplicate Code

```text
Benchmarks       3
Passed            3
Failed            0
False positives   0
False negatives   0
Accuracy         100.00%
Duration         22.05s
```

### Long Function

```text
Benchmarks       3
Passed            2
Failed            1
False positives   0
False negatives   1
Accuracy         66.67%
Duration         13.84s
```

The verifier successfully preserved valid specialist findings.

However, it exposed an architectural limitation:

```text
candidate generator misses issue
        ↓
no candidate exists
        ↓
verifier has nothing to verify
        ↓
issue remains missed
```

A verifier can improve precision, but it cannot recover findings that were never generated.

This distinction changed the direction of the experiment.

Rather than using the second call only to verify the first, the next design gave the second call **independent specialist responsibility**.

---

## Full-Suite Maintainability Multi-Pass Diagnostic

The maintainability candidate/verifier architecture was intentionally run across the complete 21-case suite as a diagnostic.

Result:

```text
Model            qwen3.5:9b
Prompt           maintainability_v1
Benchmarks       21
Passed           12
Failed            9
Errors            0
False positives   0
False negatives   9
Wrong rules       0
Accuracy         57.14%
Severity          2/2 (100.00%)
Duration         54.81s
```

The specialist correctly handled many safe cases but missed most positive bug, security, and performance cases.

This is expected because `maintainability_v1` was deliberately scoped to maintainability.

The experiment provided an important architectural lesson:

```text
specialist prompt
        ↓
strong inside its domain
        +
weak outside its domain
```

Therefore, a specialist should complement the general reviewer rather than replace it.

---

## Specialized Two-Call Diff Review

The final experiment combined the strongest general reviewer with the maintainability specialist.

The architecture is:

```text
                         Diff + Current Source
                                  │
                   ┌──────────────┴──────────────┐
                   │                             │
                   ↓                             ↓
              General Pass               Specialist Pass
                  v11                   maintainability_v1
                   │                             │
                   ↓                             ↓
         bug / security /              duplicate_code
            performance                 long_function
                   │                             │
                   └──────────────┬──────────────┘
                                  ↓
                       Deterministic Merge
                                  ↓
                          Final CodeReview
```

Rule ownership is explicit.

The general reviewer owns:

```text
mutable_default_argument
unreachable_code
sql_injection
shell_injection
path_traversal
list_membership_in_loop
string_concatenation_in_loop
```

The maintainability specialist owns:

```text
duplicate_code
long_function
```

If the general pass returns a maintainability finding, deterministic merge logic removes it and uses the specialist result for those rules.

No third LLM call is required.

The merge itself is ordinary Python logic.

---

## Specialized Full-Suite Result

The complete 21-case suite was evaluated with:

```text
Model                  qwen3.5:9b
General prompt         v11
Specialist prompt      maintainability_v1
LLM calls              2
```

Result:

```text
Model            qwen3.5:9b
Prompt           v11+maintainability_v1
Benchmarks       21
Passed           20
Failed            1
Errors            0
False positives   0
False negatives   1
Wrong rules       0
Accuracy         95.24%
Severity          10/10 (100.00%)
Duration         81.12s
```

This is the strongest result produced by the diff reviewer so far.

### Architecture Comparison

| Architecture | Passed | Accuracy | FP | FN | Wrong Rules |
| --- | ---: | ---: | ---: | ---: | ---: |
| v9 single-pass | 15/21 | 71.43% | 3 | 3 | — |
| v10 single-pass | 15/21 | 71.43% | 2 | 4 | — |
| v11 single-pass | 17/21 | 80.95% | 0 | 4 | 0 |
| **v11 + maintainability specialist** | **20/21** | **95.24%** | **0** | **1** | **0** |

Relative to v11, specialization changes:

```text
17/21
    ↓
20/21

80.95%
    ↓
95.24%

4 false negatives
    ↓
1 false negative

0 false positives
    ↓
0 false positives

0 wrong rules
    ↓
0 wrong rules
```

The improvement is therefore not produced by trading precision for recall.

Three previously missed maintainability findings are recovered without regressing any existing passing case.

---

## Specialized Benchmark-Level Analysis

The specialized architecture preserves all previously successful v11 behavior.

### Bug

```text
mutable_default_argument
├── introduced      PASS
└── pre-existing    PASS

unreachable_code
├── introduced      PASS
└── pre-existing    PASS
```

### Performance

```text
list_membership_in_loop
├── safe            PASS
├── introduced      PASS
└── pre-existing    PASS

string_concatenation_in_loop
├── introduced      PASS
└── pre-existing    PASS
```

### Security

```text
path_traversal
├── pre-existing    PASS
└── introduced      PASS

shell_injection
├── introduced      PASS
└── pre-existing    PASS

sql_injection
├── introduced      PASS
└── pre-existing    PASS
```

### Maintainability

```text
duplicate_code
├── normal positive       PASS
├── strong positive       PASS
└── pre-existing          PASS

long_function
├── normal positive       FAIL
├── strong positive       PASS
└── pre-existing          PASS
```

The only remaining failure in the entire 21-case suite is:

```text
Adding multiple responsibilities introduces long function
```

This is a false negative.

---

## Single-Pass vs Specialized Architecture

The most important current comparison is no longer v9 vs v10 vs v11.

It is:

```text
single general reviewer
        vs
general reviewer + specialist
```

### Single-Pass v11

```text
LLM calls         1
Passed            17/21
Accuracy          80.95%
False positives   0
False negatives   4
Wrong rules       0
```

### Specialized Review

```text
LLM calls         2
Passed            20/21
Accuracy          95.24%
False positives   0
False negatives   1
Wrong rules       0
Duration          81.12s
```

The specialized design gains approximately **14.3 percentage points** of benchmark accuracy over v11.

The cost is additional inference.

The architecture therefore introduces a real engineering trade-off:

```text
single-pass
├── cheaper
├── faster
└── lower maintainability recall

specialized two-call
├── more expensive
├── slower
└── substantially higher recall
```

This trade-off can now be measured rather than discussed only conceptually.

---

## Why Specialization Helped

The experiment provides evidence that the earlier maintainability failures were not simply caused by insufficient model size.

The same Qwen 3.5 9B model changed from:

```text
v11 general prompt
17/21
80.95%
```

to:

```text
v11 + maintainability specialist
20/21
95.24%
```

without changing model weights or hardware.

The main variable was task decomposition.

The general prompt asks the model to reason across nine supported rules while also performing change attribution.

The maintainability specialist reasons about only:

```text
duplicate_code
long_function
```

This reduces rule competition and gives the prompt more room to define structural maintainability reasoning.

The experiment therefore suggests:

```text
same model
    +
better task decomposition
    ↓
better reviewer
```

This is different from simply adding more instructions to one increasingly large prompt.

---

## Why the Verifier Alone Was Not Enough

The candidate/verifier experiment and specialist experiment answer different questions.

A verifier answers:

```text
Is this proposed finding actually supported?
```

A specialist answers:

```text
Are there maintainability findings that the general reviewer failed to discover?
```

The distinction matters because:

```text
candidate missing
    ↓
verifier cannot recover it
```

The current architecture therefore prioritizes complementary detection.

A future architecture could combine both ideas:

```text
general detection
        +
specialist detection
        ↓
candidate merge
        ↓
optional verification
        ↓
final review
```

but the current benchmark does not yet justify adding that third LLM call.

---

## Current Model Selection

The single-pass cross-model comparison remains useful for separating model behavior from architecture behavior.

```text
Qwen 3.5 9B
├── best single-pass accuracy
├── 0 false positives
├── 0 observed wrong-rule failures
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
├── 10 false positives
├── 6 wrong-rule failures
└── unstable constrained-rule selection
```

Qwen 3.5 9B remains the preferred local model.

The specialist experiment also shows that improving architecture can currently provide more value than simply selecting a larger local model.

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

Aggregate benchmark summaries distinguish:

```text
false positives
false negatives
wrong rules
```

rather than reducing all failed positive cases to a single detection metric.

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

### Rule-Mismatch Semantics

A positive benchmark can fail in two distinct ways.

If the model returns nothing:

```text
expected issue
    ↓
model reports nothing
    ↓
false negative
```

If the model recognizes that something is wrong but selects a different supported rule:

```text
expected rule
    ↓
model reports different rule
    ↓
wrong rule
```

These failures carry different diagnostic information.

A false negative suggests an issue-recognition or recall failure.

A wrong-rule result suggests taxonomy selection or instruction-following failure.

Historical exported results that predate the metric can still be loaded. Missing `rule_mismatches` values default to zero for compatibility, but this should be interpreted as **not recorded** rather than proof that the historical run contained no rule mismatches.

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
- A targeted general `long_function` prompt experiment did not improve recognition.
- Further general prompt tuning for that rule was paused to avoid benchmark-specific overfitting.

### Single-Pass Git Diff Review

- The diff suite contains **21 cases covering all nine rules**.
- v9 achieved **15/21 — 71.43%** with **3 FP / 3 FN**.
- v10 achieved **15/21 — 71.43%** with **2 FP / 4 FN**.
- v11 achieves **17/21 — 80.95%** with **0 FP / 4 FN / 0 wrong rules** under Qwen 3.5 9B.
- v11 fixes all three attribution false positives present under v9.
- All remaining v11 failures are maintainability false negatives.
- v11 remains the frozen single-pass baseline.

### Specialized Git Diff Review

- `maintainability_v1` recovers both `duplicate_code` positives.
- It also recovers the stronger `long_function` positive.
- Combining v11 and `maintainability_v1` produces **20/21 — 95.24%**.
- The specialized architecture produces **0 false positives**.
- It produces **1 false negative**.
- It produces **0 wrong-rule failures**.
- Severity accuracy remains **100%**.
- No previously passing v11 benchmark regresses.
- The only remaining failure is the weaker `long_function` positive.
- The improvement is achieved with the same Qwen 3.5 9B model.
- The architecture requires two LLM calls and therefore increases runtime.

### Cross-Model Diff Review

- Qwen 3.5 9B remains the strongest single-pass model at **80.95%**.
- Qwen 2.5 Coder 7B is second at **71.43%** and also produces zero false positives.
- Qwen 2.5 Coder 14B and Gemma 3 12B both reach **61.90%** but exhibit more attribution failures.
- Llama 3.1 8B and DeepSeek Coder V2 16B perform poorly with the constrained taxonomy prompt.
- Larger parameter count does not automatically improve diff-review performance.
- Aggregate wrong-rule reporting makes taxonomy-selection failures explicit.
- DeepSeek Coder V2 16B produces **6 wrong-rule failures** in the current validation run.

### Architecture

- Adding more generic prompt instructions showed diminishing returns.
- Candidate generation alone did not solve the maintainability problem.
- Verification improved confidence but could not recover missing candidates.
- Narrow maintainability specialization substantially improved issue recognition.
- A specialist should complement rather than replace the general reviewer.
- Deterministic rule ownership avoids requiring an additional merge LLM call.
- Task decomposition is now a first-class experimental variable alongside model and prompt selection.

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


SINGLE-PASS GIT-DIFF REVIEW
21-case suite
All 9 taxonomy rules represented
Prompt v11
Qwen 3.5 9B
17/21 — 80.95%
0 FP / 4 FN / 0 wrong rules
7/7 severity — 100%
      │
      ├── attribution
      │   └── all current pre-existing boundaries PASS
      │
      └── maintainability recognition
          ├── duplicate_code
          │   ├── normal positive FAIL
          │   └── strong positive FAIL
          │
          └── long_function
              ├── normal positive FAIL
              └── strong positive FAIL


MAINTAINABILITY SPECIALIST
Prompt maintainability_v1
Qwen 3.5 9B
      │
      ├── duplicate_code
      │   └── 3/3 — 100%
      │
      └── long_function
          └── 2/3 — 66.67%


SPECIALIZED GIT-DIFF REVIEW
General v11
+
Maintainability maintainability_v1
+
Deterministic rule ownership
      │
      ↓
Qwen 3.5 9B
20/21 — 95.24%
0 FP / 1 FN / 0 wrong rules
10/10 severity — 100%
81.12s
      │
      ├── bug
      │   └── all PASS
      │
      ├── security
      │   └── all PASS
      │
      ├── performance
      │   └── all PASS
      │
      └── maintainability
          ├── duplicate_code
          │   └── all PASS
          │
          └── long_function
              ├── strong positive PASS
              ├── pre-existing PASS
              └── normal positive FAIL


CROSS-MODEL SINGLE-PASS v11
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
              10 FP / 0 FN / 6 wrong rules
```

---

## Current Conclusions

The project has now moved beyond single-prompt optimization.

The main experimental progression has been:

```text
full-file review
        ↓
single-pass diff review
        ↓
change-attribution tuning
        ↓
cross-model evaluation
        ↓
failure-classification improvements
        ↓
candidate generation
        ↓
candidate verification
        ↓
maintainability specialization
        ↓
general + specialist architecture
```

The strongest current result is:

```text
Qwen 3.5 9B
v11 general reviewer
+
maintainability_v1 specialist
+
deterministic rule ownership

20/21
95.24%
0 false positives
1 false negative
0 wrong rules
100% severity accuracy
```

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
are difficult under broad single-pass prompts

focused specialist prompt
        ↓
substantially improves maintainability recall

candidate verification
        ↓
can validate findings but cannot recover missing candidates

general + specialist detection
        ↓
provides complementary coverage

deterministic rule ownership
        ↓
avoids an unnecessary merge LLM call

same model + better task decomposition
        ↓
can outperform a broader single-pass architecture

larger model
        ↓
does not automatically mean better reviewer

higher accuracy
        ↓
must be considered alongside inference cost

aggregate accuracy alone
        ↓
is insufficient for understanding model behavior
```

The current architecture has therefore demonstrated a measurable benefit from specialization.

The next architectural question is no longer whether multi-pass review can help.

It is whether additional specialization — for example separate security, bug, performance, and maintainability reviewers — provides enough additional accuracy or robustness to justify the increased inference cost and system complexity.

The current **20/21 specialized result should remain frozen as the baseline for that next experiment**.