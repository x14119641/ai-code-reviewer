## Diff Benchmark Suite

The diff-review benchmark suite was initially introduced with **11 cases
across five rules** and was later expanded to **21 cases covering all
nine rules in the current taxonomy**.

The expanded suite deliberately combines:

-   issues introduced by a diff - pre-existing issues that should not be
    attributed to the diff - safe changes - changes whose effects appear
    in unchanged code - stronger diagnostic cases for subjective
    maintainability rules

The current coverage is:

  Category          Rule                               Cases
  ----------------- ------------------------------- --------
  Bug               Mutable default argument               2
  Bug               Unreachable code                       2
  Security          SQL injection                          2
  Security          Shell injection                        2
  Security          Path traversal                         2
  Performance       List membership in loops               3
  Performance       String concatenation in loops          2
  Maintainability   Duplicate code                         3
  Maintainability   Long function                          3
  **Total**                                           **21**

This gives every rule in the current taxonomy at least one diff-review
benchmark family.

The additional `duplicate_code` and `long_function` cases deliberately
use stronger examples to distinguish failures caused by ambiguous rule
boundaries from broader issue-recognition weaknesses.

## Benchmark Design

### List Membership in Loops

The performance cases test three distinct situations.

#### Introduced issue

`text dict → list`

The collection type changes from dictionary to list while an existing
membership check remains unchanged.

The diff introduces a performance regression and should produce:

`text list_membership_in_loop`

#### Safe change

`text dict → dict`

Only a local variable is renamed. Dictionary membership remains
efficient.

Expected result:

`text no issues`

#### Pre-existing issue

List membership inside the loop already exists before the diff.

The diff only performs a local rename.

Expected result:

`text no issues`

This case tests whether the model can distinguish an issue visible in
the current code from an issue introduced by the change.

### Unreachable Code

The positive case introduces an unconditional `raise` before an existing
`return`, making that return unreachable.

The boundary case already contains the unreachable return before the
diff and changes only an unrelated error message.

The reviewer should detect the first case and ignore the second.

### Mutable Default Argument

The positive case changes:

`python items: list[str] | None = None`

to:

`python items: list[str] = []`

This introduces a mutable default argument and should be reported.

The boundary case already contains the mutable default before the diff
and changes only local variable names.

The reviewer should therefore return no issues for the boundary case.

This case became particularly useful during prompt evolution because v9
incorrectly attributed the existing issue while later prompts were able
to suppress it.

### SQL Injection

The positive case changes a parameterized query into an interpolated SQL
string.

The diff therefore introduces `sql_injection`.

The boundary case already contains the vulnerable interpolated query
before the diff and changes only an audit message.

The existing vulnerability should not be reported because it was not
introduced by the change.

Prompt v11 successfully distinguishes both cases.

### Shell Injection

The positive case changes a safe argument-list subprocess call into an
interpolated command executed with `shell=True`.

The diff therefore introduces `shell_injection`.

The boundary case already contains the unsafe shell command before the
diff and changes only an informational message.

Prompt v11 successfully distinguishes both cases.

### Path Traversal

The positive case removes filename sanitization and changes safe path
construction into a direct join between an intended base directory and a
user-controlled path.

This allows values such as parent-directory traversal or absolute paths
to escape the intended directory.

The boundary case already contains the unsafe path construction before
the diff and changes only an informational message.

The current general baseline correctly detects the introduced case and
ignores the pre-existing case.

### String Concatenation in Loops

The positive case changes efficient `str.join()` construction into
repeated `+=` concatenation inside a loop.

The boundary case already contains repeated string concatenation before
the diff and changes only unrelated reporting logic.

The current general baseline correctly distinguishes the introduced
issue from the pre-existing one.

### Duplicate Code

The duplicate-code family contains three cases.

The original positive case introduces repeated normalization and
validation logic across two functions.

A stronger diagnostic case contains substantially more repeated parsing
and validation logic.

The third case contains duplication that already existed before the
diff.

Under the single-pass Qwen 3.5 9B + v11 baseline:

`text Original positive FAIL Strong positive FAIL Pre-existing boundary PASS`

Earlier experiments showed that v9 could detect the stronger case:

`text Strong positive v9 PASS v10 FAIL v11 FAIL`

This showed that `duplicate_code` recognition was sensitive to both the
strength of the example and prompt behavior.

Later specialist experiments changed this result substantially.

Using the focused `maintainability_v1` prompt:

`text Original positive PASS Strong positive PASS Pre-existing boundary PASS`

The specialist therefore reaches:

`text 3/3 --- 100% 0 FP 0 FN`

### Long Function

The long-function family also contains three cases.

The original positive expands a previously focused function to perform
several responsibilities:

-   input validation - iteration and aggregation - business-rule
    application - result construction

The stronger diagnostic adds:

-   required-field validation - item normalization - per-item
    validation - aggregation - discount decisions - shipping decisions -
    final result construction

Under the single-pass v11 baseline:

`text Original positive FAIL Strong positive FAIL Pre-existing boundary PASS`

A targeted general-prompt experiment tested increasingly explicit
`long_function` guidance, including operational responsibility
definitions and concrete positive examples.

Detection did not improve.

The established full-file `long_function` benchmark family showed the
same pattern:

`text Benchmarks 4 Passed 2 Failed 2 False positives 0 False negatives 2 Accuracy 50.00%`

However, the later focused maintainability specialist improved the diff
benchmark family to:

`text Original positive FAIL Strong positive PASS Pre-existing boundary PASS`

Result:

`text 2/3 --- 66.67% 0 FP 1 FN`

This distinction became important: additional general prompt tuning did
not help, while narrowing the task to a maintainability-specific prompt
did.

## Initial Diff Review Baseline

The first complete diff benchmark baseline used the original **11-case
suite**:

`text Model qwen3.5:9b Prompt v9 Cases 11`

Result:

`text Benchmarks 11 Passed 8 Failed 3 Errors 0 False positives 3 False negatives 0 Accuracy 72.7% Severity 5/5 (100.0%) Duration 32.94s`

All five positive introduced-issue cases passed.

The model successfully detected:

`text mutable_default_argument unreachable_code list_membership_in_loop sql_injection shell_injection`

All three failures involved pre-existing issues:

`text mutable_default_argument shell_injection sql_injection`

This identified **change attribution** as the primary weakness of the
initial diff reviewer.

## Expanded v9 Baseline

The suite was subsequently expanded to 21 cases covering all nine
taxonomy rules.

Qwen 3.5 9B with v9 produced:

`text Model qwen3.5:9b Prompt v9 Benchmarks 21 Passed 15 Failed 6 Errors 0 False positives 3 False negatives 3 Accuracy 71.43% Severity 8/8 (100.00%) Duration 55.79s`

The failures exposed two distinct problems:

\`\`\`text ATTRIBUTION ├── pre-existing mutable_default_argument ├──
pre-existing sql_injection └── pre-existing shell_injection

RECOGNITION ├── duplicate_code ├── long_function └── strong
long_function \`\`\`

The stronger `duplicate_code` diagnostic passed under v9.

## v10 Attribution Experiment

Prompt v10 tested stronger generic before/after attribution
instructions.

The core decision model was:

`text BEFORE safe → AFTER unsafe → report BEFORE unsafe → AFTER worse → report BEFORE unsafe → AFTER same unsafe → do not report BEFORE safe → AFTER safe → do not report`

On the complete 21-case suite:

`text Model qwen3.5:9b Prompt v10 Benchmarks 21 Passed 15 Failed 6 Errors 0 False positives 2 False negatives 4 Accuracy 71.43% Severity 7/7 (100.00%) Duration 43.89s`

v10 fixed:

`text pre-existing mutable_default_argument`

but continued to misattribute:

`text pre-existing sql_injection pre-existing shell_injection`

It also regressed:

`text strong duplicate_code positive`

The result was therefore a precision/recall trade-off rather than an
overall improvement:

\`\`\`text v9 15/21 3 FP / 3 FN

v10 15/21 2 FP / 4 FN \`\`\`

Generic attribution constraints were not sufficient to justify replacing
v9.

## Targeted Long-Function Investigation

After the expanded suite identified `long_function` as a consistent
weakness, a targeted experiment tested progressively more explicit
guidance.

The experiment included:

-   a more operational definition of distinct responsibilities -
    explicit responsibility signals - guidance for distinguishing
    several concerns from cohesive steps - a concrete
    multi-responsibility positive prototype

The result remained:

`text Original positive FAIL Strong positive FAIL Pre-existing boundary PASS`

The same behavior appeared in the established full-file benchmark
family.

This suggested that Qwen 3.5 9B was conservative when applying the
`long_function` rule inside a general review prompt.

Because increasingly explicit general prompt wording did not improve
recognition, further single-prompt tuning was stopped.

## v11 Targeted Attribution Experiment

Prompt v11 returned to the v9-style baseline and targeted the remaining
attribution failures more precisely.

Instead of making the reviewer globally more conservative, v11 instructs
the model to compare the **actual triggering code before and after the
change**.

The central principle is:

`text identify triggering code ↓ compare BEFORE and AFTER ↓ trigger unchanged + unrelated diff ↓ pre-existing issue ↓ do not report`

For security rules, this means checking whether the vulnerable SQL
construction, shell command construction, or dangerous execution
behavior itself changed.

### SQL Injection

`text Introduced SQL injection PASS Pre-existing SQL injection PASS`

Result:

`text 2/2 --- 100% 0 FP 0 FN`

### Shell Injection

`text Introduced shell injection PASS Pre-existing shell injection PASS`

Result:

`text 2/2 --- 100% 0 FP 0 FN`

Because both targeted families improved without losing detection of
newly introduced vulnerabilities, v11 was evaluated against the complete
suite.

## Single-Pass v11 Diff Baseline

Qwen 3.5 9B with prompt v11 produces:

`text Model qwen3.5:9b Prompt v11 Benchmarks 21 Passed 17 Failed 4 Errors 0 False positives 0 False negatives 4 Wrong rules 0 Accuracy 80.95% Severity 7/7 (100.00%) Duration 41.48s`

### Prompt Comparison

  ----------------------------------------------------------------------
  Prompt         Passed     Accuracy       False       False    Severity
                                       Positives   Negatives 
  --------- ----------- ------------ ----------- ----------- -----------
  v9              15/21       71.43%           3           3  8/8 (100%)

  v10             15/21       71.43%           2           4  7/7 (100%)

  **v11**     **17/21**   **80.95%**       **0**       **4**       **7/7
                                                                (100%)**
  ----------------------------------------------------------------------

v11 improves accuracy by approximately **9.5 percentage points** over v9
and v10.

More importantly, it eliminates all false positives in the current Qwen
3.5 9B diff suite.

v11 remains the strongest **single-pass** diff prompt.

## v9 → v11 Regression Analysis

The exported v9 and v11 runs were compared benchmark by benchmark.

\`\`\`text Old: v9 / qwen3.5:9b --- 15/21 (71.4%) New: v11 / qwen3.5:9b
--- 17/21 (81.0%)

Comparable: 21 Fixed: 3 Regressed: 1 Still failing: 3 Added: 0 Removed:
0 \`\`\`

### Fixed

`text pre-existing mutable_default_argument pre-existing shell_injection pre-existing sql_injection`

### Regressed

`text strong duplicate_code positive`

### Still Failing

`text duplicate_code positive long_function positive strong long_function positive`

The final behavioral change is:

\`\`\`text v9 → v11

FIXED ├── mutable_default_argument attribution ├── shell_injection
attribution └── sql_injection attribution

REGRESSED └── strong duplicate_code recognition

STILL FAILING ├── duplicate_code positive ├── long_function positive └──
strong long_function positive \`\`\`

Unlike v10, the v11 trade-off produces a clear aggregate improvement.

Prompt v11 therefore became the frozen single-pass diff-review baseline.

## Cross-Model v11 Evaluation

After establishing v11 as the Qwen 3.5 9B baseline, the complete 21-case
suite was run against the other local models already used by the
project.

The experiment kept the following fixed:

`text same 21 diff benchmarks same v11 prompt same deterministic generation settings same evaluator`

Only the model changed.

### Results

  Model                        Passed     Accuracy   False Positives   False Negatives
  ----------------------- ----------- ------------ ----------------- -----------------
  **Qwen 3.5 9B**           **17/21**   **80.95%**             **0**                 4
  Qwen 2.5 Coder 7B             15/21       71.43%             **0**                 6
  Qwen 2.5 Coder 14B            13/21       61.90%                 4                 4
  Gemma 3 12B                   13/21       61.90%                 4                 4
  Llama 3.1 8B                   5/21       23.81%                10               0\*
  DeepSeek Coder V2 16B          3/21       14.29%                10               0\*

`*` The original cross-model runs predated aggregate rule-mismatch
counting.

The zero false-negative count for Llama 3.1 8B and DeepSeek Coder V2 16B
was therefore misleading when viewed alone.

These models frequently predicted an issue using the **wrong rule**
rather than returning no issue.

This observation directly motivated an evaluator improvement that now
tracks wrong-rule failures separately from false positives and false
negatives.

## Aggregate Rule-Mismatch Evaluation

The benchmark evaluator distinguishes three important failure modes:

\`\`\`text expected no issue + issue reported ↓ false positive

expected issue + nothing reported ↓ false negative

expected issue + different rule reported ↓ wrong rule / rule mismatch

    A rule mismatch is counted when:

    ```text benchmark expects an issue + model reports at least one
    issue + none of the reported issues uses the expected rule ```

    This prevents a model that aggressively predicts incorrect rules from
    appearing to have strong recall merely because its false-negative count
    is zero.

    The metric is:

    - stored on individual benchmark evaluations - aggregated by
    `BenchmarkRun` - serialized in benchmark result exports - loaded by
    result-analysis tooling - available in rule/category summaries -
    displayed in benchmark summary output

    ### DeepSeek Validation Run

    DeepSeek Coder V2 16B was rerun against the complete v11 diff suite
    after adding the metric.

    ```text Model deepseek-coder-v2:16b Prompt v11 Benchmarks 21 Passed 3
    Failed 18 Errors 0 False positives 10 False negatives 0 Wrong rules 6
    Accuracy 14.29% Severity 3/3 (100.00%) Duration 205.06s ```

    The six wrong-rule failures were:

    ```text duplicate_code ├── normal positive └── strong positive

    long_function ├── normal positive └── strong positive

    list_membership_in_loop └── introduced positive

    string_concatenation_in_loop └── introduced positive ```

    Instead of missing these cases completely, DeepSeek reported unrelated
    supported rules.

    Examples included:

    ```text expected duplicate_code actual mutable_default_argument

    expected long_function actual mutable_default_argument

    expected list_membership_in_loop actual mutable_default_argument

    expected string_concatenation_in_loop actual unreachable_code ```

    The new aggregate summary therefore describes the model substantially
    better:

    ```text 3 passed 10 false-positive attribution failures 6 wrong-rule
    failures 0 ordinary false negatives ```

    The apparent `0 FN` no longer hides the taxonomy-selection problem.

    ## Cross-Model Failure Analysis

    ### Qwen 3.5 9B

    Single-pass v11:

    ```text 17/21 --- 80.95% 0 FP 4 FN 0 wrong rules ```

    The four failures are concentrated entirely in maintainability
    recognition:

    ```text duplicate_code ├── normal positive FAIL └── strong positive
    FAIL

    long_function ├── normal positive FAIL └── strong positive FAIL ```

    All current pre-existing attribution boundary cases pass.

    ### Qwen 2.5 Coder 7B

    ```text 15/21 --- 71.43% 0 FP 6 FN ```

    Like Qwen 3.5 9B, the 7B model produces no false positives and handles
    the current attribution boundaries well.

    It also misses all four maintainability positives.

    Its two additional false negatives are introduced performance issues:

    ```text list_membership_in_loop string_concatenation_in_loop ```

    It remains interesting as a smaller and faster reviewer, but Qwen 3.5 9B
    is substantially stronger overall.

    ### Qwen 2.5 Coder 14B

    ```text 13/21 --- 61.90% 4 FP 4 FN ```

    The larger Qwen 2.5 Coder model recovers some findings missed by the 7B
    version but performs worse on attribution.

    Its false positives include pre-existing cases such as:

    ```text mutable_default_argument string_concatenation_in_loop
    shell_injection sql_injection ```

    This demonstrates that larger parameter count does not automatically
    produce better behavior under a fixed review prompt.

    ### Gemma 3 12B

    ```text 13/21 --- 61.90% 4 FP 4 FN ```

    Gemma reaches the same aggregate accuracy as Qwen 2.5 Coder 14B but does
    not fail on exactly the same cases.

    This reinforces the importance of benchmark-level analysis.

    ### Llama 3.1 8B

    ```text 5/21 --- 23.81% 10 FP 0 ordinary FN ```

    The apparent zero false-negative count does not indicate strong recall.

    The model frequently selects incorrect rules.

    The original run predates aggregate wrong-rule counting, so a historical
    aggregate wrong-rule value is not asserted here.

    ### DeepSeek Coder V2 16B

    ```text 3/21 --- 14.29% 10 FP 0 ordinary FN 6 wrong rules ```

    DeepSeek exhibits strong rule-selection instability.

    The explicit `Wrong rules: 6` metric now captures this behavior
    directly.

    ## Maintainability Findings Across Models

    The cross-model experiment was especially useful for evaluating the
    remaining Qwen 3.5 9B maintainability failures.

    Among the models with reasonably stable taxonomy behavior, the same
    single-pass pattern appears repeatedly.

    ### Duplicate Code

    ```text Normal Strong Qwen 3.5 9B FAIL FAIL Qwen 2.5 Coder 7B FAIL
    FAIL Qwen 2.5 Coder 14B FAIL FAIL Gemma 3 12B FAIL FAIL ```

    ### Long Function

    ```text Normal Strong Qwen 3.5 9B FAIL FAIL Qwen 2.5 Coder 7B FAIL
    FAIL Qwen 2.5 Coder 14B FAIL FAIL Gemma 3 12B FAIL FAIL ```

    The important conclusion was that the maintainability failures were
    **not unique to Qwen 3.5 9B**.

    At this stage, further expansion of the general v11 prompt had
    diminishing value.

    That observation motivated the next architectural experiment: reducing
    the number of rules considered by an individual LLM call.

    ## Structured Output Improvement

    The multi-pass experiment initially exposed another problem:
    candidate-generation prompts did not always return machine-readable
    JSON.

    For example, the model could respond with prose, tool-like structures,
    or free-form findings even when the prompt requested JSON.

    The Ollama integration was therefore extended to support an optional
    structured output format.

    Instead of globally forcing every request into JSON mode,
    `generate_review()` accepts an optional schema:

    ```text generate_review( prompt, model, output_format=... ) ```

    Review requests can provide the project's review response JSON Schema.

    This constrains generated findings to the expected structure:

    ```text { "issues": [...] } ```

    while preserving the existing parser and taxonomy validation as a second
    validation boundary.

    The resulting pipeline is:

    ```text Prompt ↓ Ollama JSON Schema constraint ↓ JSON response ↓
    parse_review_response() ↓ taxonomy validation ↓ CodeReview ```

    This made experimental candidate generation significantly more reliable
    and removed output-format failures from the maintainability
    investigation.

    ## Candidate-Generation Experiment

    The first multi-pass step separated issue discovery from final review.

    A new candidate-generation prompt was introduced:

    ```text diff + current source ↓ candidate-generation prompt ↓
    potential findings ```

    The initial generic candidate prompt still struggled with the
    maintainability cases.

    This demonstrated that simply adding another LLM call did not
    automatically improve recall.

    The main problem remained the scope of the task.

    The model was still being asked to reason across the complete taxonomy.

    ## Maintainability Specialist Experiment

    A focused prompt version, `maintainability_v1`, was created
    specifically for:

    ```text
    duplicate_code
    long_function

The purpose was not to teach the model benchmark answers.

Instead, the experiment tested whether reducing taxonomy competition and
narrowing the reasoning task would improve recognition.

### Duplicate Code Candidate Results

`text Model qwen3.5:9b Prompt maintainability_v1 Benchmarks 3 Passed 3 Failed 0 Errors 0 False positives 0 False negatives 0 Wrong rules 0 Accuracy 100.00% Severity 2/2 (100.00%) Duration 10.05s`

This recovered both positive cases missed by v11:

`text Original positive PASS Strong positive PASS Pre-existing boundary PASS`

### Long Function Candidate Results

`text Model qwen3.5:9b Prompt maintainability_v1 Benchmarks 3 Passed 2 Failed 1 Errors 0 False positives 0 False negatives 1 Wrong rules 0 Accuracy 66.67% Severity 1/1 (100.00%) Duration 7.03s`

The stronger positive was recovered:

`text Original positive FAIL Strong positive PASS Pre-existing boundary PASS`

The focused prompt therefore changed maintainability behavior from:

\`\`\`text v11 general

duplicate_code 1/3 long_function 1/3 \`\`\`

to:

\`\`\`text maintainability_v1

duplicate_code 3/3 long_function 2/3 \`\`\`

This was the first strong evidence that the remaining weakness could be
addressed through **task specialization** rather than increasingly
benchmark-specific general prompt instructions.

## Candidate + Verifier Multi-Pass Experiment

A second LLM pass was then added to verify candidate findings.

The architecture was:

`text Diff + Current Source ↓ Candidate Generator ↓ Candidate Issues ↓ Verifier ↓ Final CodeReview`

The verifier was designed to reject unsupported candidate findings while
preserving valid ones.

### Duplicate Code

`text Benchmarks 3 Passed 3 Failed 0 False positives 0 False negatives 0 Accuracy 100.00% Duration 22.05s`

### Long Function

`text Benchmarks 3 Passed 2 Failed 1 False positives 0 False negatives 1 Accuracy 66.67% Duration 13.84s`

The verifier successfully preserved valid specialist findings.

However, it exposed an architectural limitation:

`text candidate generator misses issue ↓ no candidate exists ↓ verifier has nothing to verify ↓ issue remains missed`

A verifier can improve precision, but it cannot recover findings that
were never generated.

This distinction changed the direction of the experiment.

Rather than using the second call only to verify the first, the next
design gave the second call **independent specialist responsibility**.

## Full-Suite Maintainability Multi-Pass Diagnostic

The maintainability candidate/verifier architecture was intentionally
run across the complete 21-case suite as a diagnostic.

Result:

`text Model qwen3.5:9b Prompt maintainability_v1 Benchmarks 21 Passed 12 Failed 9 Errors 0 False positives 0 False negatives 9 Wrong rules 0 Accuracy 57.14% Severity 2/2 (100.00%) Duration 54.81s`

The specialist correctly handled many safe cases but missed most
positive bug, security, and performance cases.

This is expected because `maintainability_v1` was deliberately scoped to
maintainability.

The experiment provided an important architectural lesson:

`text specialist prompt ↓ strong inside its domain + weak outside its domain`

Therefore, a specialist should complement the general reviewer rather
than replace it.

## Specialized Two-Call Diff Review

The final experiment combined the strongest general reviewer with the
maintainability specialist.

The architecture is:

``` text
                 Diff + Current Source
                          │
             ┌────────────┴────────────┐
             │                         │
             ↓                         ↓
        General Pass             Specialist Pass
            v11                maintainability_v1
             │                         │
             ↓                         ↓
   bug / security /             duplicate_code
      performance               long_function
             │                         │
             └────────────┬────────────┘
                          ↓
                Deterministic Merge
                          ↓
                  Final CodeReview
```

Rule ownership is explicit.

The general reviewer owns:

``` text
mutable_default_argument
unreachable_code
sql_injection
shell_injection
path_traversal
list_membership_in_loop
string_concatenation_in_loop
```

The maintainability specialist owns:

``` text
duplicate_code
long_function
```

If the general pass returns a maintainability finding, deterministic
merge logic removes it and uses the specialist result for those rules.

No third LLM call is required.

The merge itself is ordinary Python logic.

## Specialized Full-Suite Result

The complete 21-case suite was evaluated with:

``` text
Model              qwen3.5:9b
General prompt     v11
Specialist prompt  maintainability_v1
LLM calls          2
```

Result:

``` text
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
Severity         10/10 (100.00%)
Duration         81.12s
```

This is the strongest result produced by the diff reviewer so far.

### Architecture Comparison

  ---------------------------------------------------------------------------
  Architecture           Passed     Accuracy         FP         FN      Wrong
                                                                        Rules
  ----------------- ----------- ------------ ---------- ---------- ----------
  v9 single-pass          15/21       71.43%          3          3        ---

  v10 single-pass         15/21       71.43%          2          4        ---

  v11 single-pass         17/21       80.95%          0          4          0

  **v11 +             **20/21**   **95.24%**      **0**      **1**      **0**
  maintainability                                                  
  specialist**                                                     
  ---------------------------------------------------------------------------

Relative to v11, specialization changes:

\`\`\`text 17/21 ↓ 20/21

80.95% ↓ 95.24%

4 false negatives ↓ 1 false negative

0 false positives ↓ 0 false positives

0 wrong rules ↓ 0 wrong rules \`\`\`

The improvement is therefore not produced by trading precision for
recall.

Three previously missed maintainability findings are recovered without
regressing any existing passing case.

## Specialized Benchmark-Level Analysis

The specialized architecture preserves all previously successful v11
behavior.

### Bug

\`\`\`text mutable_default_argument ├── introduced PASS └── pre-existing
PASS

unreachable_code ├── introduced PASS └── pre-existing PASS \`\`\`

### Performance

\`\`\`text list_membership_in_loop ├── safe PASS ├── introduced PASS └──
pre-existing PASS

string_concatenation_in_loop ├── introduced PASS └── pre-existing PASS

    ### Security

    ```text path_traversal ├── pre-existing PASS └── introduced PASS

    shell_injection ├── introduced PASS └── pre-existing PASS

    sql_injection ├── introduced PASS └── pre-existing PASS ```

    ### Maintainability

    ```text duplicate_code ├── normal positive PASS ├── strong positive
    PASS └── pre-existing PASS

    long_function ├── normal positive FAIL ├── strong positive PASS └──
    pre-existing PASS ```

    The only remaining failure in the entire 21-case suite is:

    ```text Adding multiple responsibilities introduces long function

This is a false negative.

## Single-Pass vs Specialized Architecture

The most important current comparison is no longer v9 vs v10 vs v11.

It is:

`text single general reviewer vs general reviewer + specialist`

### Single-Pass v11

`text LLM calls 1 Passed 17/21 Accuracy 80.95% False positives 0 False negatives 4 Wrong rules 0`

### Specialized Review

`text LLM calls 2 Passed 20/21 Accuracy 95.24% False positives 0 False negatives 1 Wrong rules 0 Duration 81.12s`

The specialized design gains approximately **14.3 percentage points** of
benchmark accuracy over v11.

The cost is additional inference.

The architecture therefore introduces a real engineering trade-off:

\`\`\`text single-pass ├── cheaper ├── faster └── lower maintainability
recall

specialized two-call ├── more expensive ├── slower └── substantially
higher recall \`\`\`

This trade-off can now be measured rather than discussed only
conceptually.

## Why Specialization Helped

The experiment provides evidence that the earlier maintainability
failures were not simply caused by insufficient model size.

The same Qwen 3.5 9B model changed from:

`text v11 general prompt 17/21 80.95%`

to:

`text v11 + maintainability specialist 20/21 95.24%`

without changing model weights or hardware.

The main variable was task decomposition.

The general prompt asks the model to reason across nine supported rules
while also performing change attribution.

The maintainability specialist reasons about only:

``` text
duplicate_code
long_function
```

This reduces rule competition and gives the prompt more room to define
structural maintainability reasoning.

The experiment therefore suggests:

`text same model + better task decomposition ↓ better reviewer`

This is different from simply adding more instructions to one
increasingly large prompt.

## Why the Verifier Alone Was Not Enough

The candidate/verifier experiment and specialist experiment answer
different questions.

A verifier answers:

`text Is this proposed finding actually supported?`

A specialist answers:

`text Are there maintainability findings that the general reviewer failed to discover?`

The distinction matters because:

`text candidate missing ↓ verifier cannot recover it`

The current architecture therefore prioritizes complementary detection.

A future architecture could combine both ideas:

`text general detection + specialist detection ↓ candidate merge ↓ optional verification ↓ final review`

but the current benchmark does not yet justify adding that third LLM
call.

## Result Analysis

The project provides complementary ways to analyze exported benchmark
results.

### Aggregate Comparison

`bash uv run python main.py compare-results results/v5/`

Results can also be grouped by rule or category:

`bash uv run python main.py compare-results results/v5/ --by-rule uv run python main.py compare-results results/v5/ --by-category`

Aggregate benchmark summaries distinguish:

`text false positives false negatives wrong rules`

rather than reducing all failed positive cases to a single detection
metric.

### Individual Run Analysis

`bash uv run python main.py analyze-result \ results/v5/qwen3.5-9b-seed42-block5.json`

This surfaces:

-   false positives - false negatives - rule mismatches - category
    mismatches - severity mismatches

### Cross-Run Regression Analysis

`bash uv run python main.py compare-runs \ results/diff/v9/qwen3.5-9b-expanded.json \ results/diff/v11/qwen3.5-9b.json`

Diff benchmark results are supported by `compare-runs`.

The comparison identifies:

-   fixed benchmarks - regressed benchmarks - benchmarks that remain
    failing - added benchmarks - removed benchmarks

Together, the analysis tools provide:

`text Aggregate metrics ↓ Rule / category analysis ↓ Benchmark-level regression analysis`

### Rule-Mismatch Semantics

A positive benchmark can fail in two distinct ways.

If the model returns nothing:

`text expected issue ↓ model reports nothing ↓ false negative`

If the model recognizes that something is wrong but selects a different
supported rule:

`text expected rule ↓ model reports different rule ↓ wrong rule`

These failures carry different diagnostic information.

A false negative suggests an issue-recognition or recall failure.

A wrong-rule result suggests taxonomy selection or instruction-following
failure.

Historical exported results that predate the metric can still be loaded.
Missing `rule_mismatches` values default to zero for compatibility, but
this should be interpreted as **not recorded** rather than proof that
the historical run contained no rule mismatches.

## Current Observations

### Full-File Review

-   Qwen 3.5 9B produced the strongest result in the initial multi-model
    comparison. - Controlled prompt iteration improved the full-file
    reviewer significantly. - Prompt v5 remains the full-file
    baseline. - v5 reaches **92.3% accuracy on 65 benchmarks**. -
    Severity accuracy remains **100%**. - `unreachable_code` currently
    performs strongly. - `long_function` remains one of the weakest
    full-file rules. - A targeted general `long_function` prompt
    experiment did not improve recognition. - Further general prompt
    tuning for that rule was paused to avoid benchmark-specific
    overfitting.

### Single-Pass Git Diff Review

-   The diff suite contains **21 cases covering all nine rules**. - v9
    achieved **15/21 --- 71.43%** with **3 FP / 3 FN**. - v10 achieved
    **15/21 --- 71.43%** with **2 FP / 4 FN**. - v11 achieves **17/21
    --- 80.95%** with **0 FP / 4 FN / 0 wrong rules** under Qwen 3.5
    9B. - v11 fixes all three attribution false positives present under
    v9. - All remaining v11 failures are maintainability false
    negatives. - v11 remains the frozen single-pass baseline.

### Specialized Git Diff Review

-   `maintainability_v1` recovers both `duplicate_code` positives. - It
    also recovers the stronger `long_function` positive. - Combining v11
    and `maintainability_v1` produces **20/21 --- 95.24%**. - The
    specialized architecture produces **0 false positives**. - It
    produces **1 false negative**. - It produces **0 wrong-rule
    failures**. - Severity accuracy remains **100%**. - No previously
    passing v11 benchmark regresses. - The only remaining failure is the
    weaker `long_function` positive. - The improvement is achieved with
    the same Qwen 3.5 9B model. - The architecture requires two LLM
    calls and therefore increases runtime.

## Cross-Model Diff Review

After establishing v11 as the strongest single-pass prompt, the complete
21-case suite was evaluated across the project's local model set.

The experiment was then repeated using the specialized architecture:

`text General reviewer v11 Maintainability maintainability_v1 Merge deterministic rule ownership Benchmarks 21 Generation deterministic`

This allows two separate questions to be evaluated:

\`\`\`text MODEL EFFECT same architecture different model

ARCHITECTURE EFFECT same model single-pass vs specialized \`\`\`

## Cross-Model Single-Pass v11 Results

The single-pass experiment kept the following fixed:

`text same 21 diff benchmarks same v11 prompt same deterministic generation settings same evaluator`

Only the model changed.

  Model                        Passed     Accuracy   False Positives   False Negatives
  ----------------------- ----------- ------------ ----------------- -----------------
  **Qwen 3.5 9B**           **17/21**   **80.95%**             **0**                 4
  Qwen 2.5 Coder 7B             15/21       71.43%             **0**                 6
  Qwen 2.5 Coder 14B            13/21       61.90%                 4                 4
  Gemma 3 12B                   13/21       61.90%                 4                 4
  Llama 3.1 8B                   5/21       23.81%                10               0\*
  DeepSeek Coder V2 16B          3/21       14.29%                10               0\*

`*` The original cross-model runs for these models predated aggregate
rule-mismatch counting.

The zero false-negative counts for Llama 3.1 8B and DeepSeek Coder V2
16B are therefore misleading when viewed alone.

These models frequently reported an issue using the wrong supported rule
rather than returning no issue.

DeepSeek was later rerun with aggregate rule-mismatch tracking enabled:

`text Passed 3/21 Accuracy 14.29% False positives 10 False negatives 0 Wrong rules 6`

Qwen 3.5 9B remained the strongest single-pass model.

## Cross-Model Specialized Evaluation

The specialized architecture was then evaluated using the same six
models.

Each benchmark is reviewed by two independent passes:

``` text
                 Diff + Current Source
                          │
             ┌────────────┴────────────┐
             │                         │
             ↓                         ↓
        General Pass             Specialist Pass
            v11                maintainability_v1
             │                         │
             ↓                         ↓
   bug / security /             duplicate_code
      performance               long_function
             │                         │
             └────────────┬────────────┘
                          ↓
                Deterministic Merge
                          ↓
                  Final CodeReview
```

The prompts, benchmark suite, evaluator, rule ownership, and
deterministic generation settings were held constant.

Only the model changed.

### Results

  -----------------------------------------------------------------------------------
  Model           Passed     Accuracy      FP      FN   Wrong   Severity     Duration
                                                        Rules            
  ---------- ----------- ------------ ------- ------- ------- ---------- ------------
  **Qwen 3.5   **20/21**   **95.24%**   **0**   **1**   **0**      10/10       81.12s
  9B**                                                            (100%) 

  Qwen 2.5         16/21       76.19%   **0**       5       0 6/6 (100%)   **38.72s**
  Coder 7B                                                               

  Qwen 2.5         16/21       76.19%       5   **0**       0      11/11      107.57s
  Coder 14B                                                       (100%) 

  Gemma 3          14/21       66.67%       7   **0**       0      11/11      183.03s
  12B                                                             (100%) 

  Llama 3.1         9/21       42.86%      10       0       2 9/9 (100%)      118.26s
  8B                                                                     

  DeepSeek          7/21       33.33%      10       0       2 7/7 (100%)      295.41s
  Coder V2                                                               
  16B                                                                    
  -----------------------------------------------------------------------------------

Qwen 3.5 9B remains clearly strongest under the specialized
architecture.

It is the only tested model that combines:

`text high recall + zero false positives + zero wrong-rule failures`

while reaching:

`text 20/21 95.24%`

## Single-Pass vs Specialized Cross-Model Comparison

The specialized architecture improves aggregate accuracy for every
tested model.

  Model                     Single-Pass v11   Specialized          Change
  ----------------------- ----------------- ------------- ---------------
  **Qwen 3.5 9B**                    80.95%    **95.24%**   **+14.29 pp**
  Qwen 2.5 Coder 7B                  71.43%    **76.19%**        +4.76 pp
  Qwen 2.5 Coder 14B                 61.90%    **76.19%**       +14.29 pp
  Gemma 3 12B                        61.90%    **66.67%**        +4.77 pp
  Llama 3.1 8B                       23.81%    **42.86%**       +19.05 pp
  DeepSeek Coder V2 16B              14.29%    **33.33%**       +19.04 pp

The important result is not merely that Qwen 3.5 9B improved.

All six tested models achieve higher benchmark accuracy when using the
specialized architecture.

This provides evidence that task decomposition has value beyond one
particular model.

However, specialization does not eliminate the underlying behavioral
differences between models.

## Specialized Model Behavior

### Qwen 3.5 9B

`text 20/21 --- 95.24% 0 FP 1 FN 0 wrong rules`

Qwen 3.5 9B produces the strongest overall result.

The architecture preserves all bug, security, performance, and
attribution successes from v11 while recovering three of the four
maintainability findings previously missed.

The only remaining failure is:

`text long_function └── weaker positive`

This model currently provides the best balance of precision and recall.

### Qwen 2.5 Coder 7B

`text 16/21 --- 76.19% 0 FP 5 FN 0 wrong rules 38.72s`

Qwen 2.5 Coder 7B remains highly conservative.

Like Qwen 3.5 9B, it produces:

`text 0 false positives 0 wrong rules`

but recall remains substantially lower.

Its failures are:

\`\`\`text duplicate_code └── weaker positive

long_function ├── weaker positive └── strong positive

performance ├── list_membership_in_loop └── string_concatenation_in_loop

    The model therefore remains interesting as a smaller and faster
    alternative when precision is more important than recall.

    ### Qwen 2.5 Coder 14B

    ```text 16/21 --- 76.19% 5 FP 0 FN 0 wrong rules 107.57s ```

    The 14B model shows almost the opposite behavior from the 7B model.

    It detects every expected positive issue:

    ```text 0 false negatives ```

    including all maintainability positives.

    However, it incorrectly reports several issues that were already present
    before the diff.

    Its five false-positive benchmark failures include pre-existing:

    ```text mutable_default_argument duplicate_code
    string_concatenation_in_loop shell_injection sql_injection ```

    The model therefore demonstrates strong issue recognition but weaker
    change attribution.

    This is an important distinction:

    ```text recognition strong attribution weaker ```

    A larger model is not automatically a better diff reviewer.

    ### Gemma 3 12B

    ```text 14/21 --- 66.67% 7 FP 0 FN 0 wrong rules 183.03s ```

    Gemma also detects all expected positive findings.

    Its primary weakness is attribution.

    Seven safe or pre-existing cases become false positives.

    The model therefore exhibits:

    ```text high recognition + low attribution precision ```

    rather than a simple issue-detection problem.

    ### Llama 3.1 8B

    ```text 9/21 --- 42.86% 10 FP 0 FN 2 wrong rules 118.26s ```

    Specialization substantially increases aggregate accuracy relative to
    its single-pass result:

    ```text 23.81% ↓ 42.86% ```

    but the reviewer remains unstable.

    Ten benchmark cases produce false positives and two positive cases use
    the wrong supported rule.

    The model therefore remains unsuitable as the default reviewer.

    ### DeepSeek Coder V2 16B

    ```text 7/21 --- 33.33% 10 FP 0 FN 2 wrong rules 295.41s ```

    DeepSeek also improves substantially over its single-pass result:

    ```text 14.29% ↓ 33.33% ```

    but remains the weakest practical candidate.

    It combines:

    ```text 10 false positives 2 wrong-rule failures very high inference
    time ```

    The specialized architecture improves its recognition, but does not
    solve its attribution and taxonomy-selection instability.

    ## Precision vs Recall Across Models

    The specialized experiment exposes distinct reviewer behaviors.

    ```text Qwen 3.5 9B strong recognition + strong attribution ↓ 20/21

    Qwen 2.5 Coder 7B weaker recognition + strong attribution ↓ conservative
    reviewer

    Qwen 2.5 Coder 14B strong recognition + weaker attribution ↓ aggressive
    reviewer

    Gemma 3 12B strong recognition + weak attribution ↓ many false positives

    Llama 3.1 / DeepSeek weak attribution + taxonomy instability ↓
    unsuitable reviewer behavior ```

    This demonstrates why aggregate accuracy alone is insufficient for model
    selection.

    Two models can reach the same accuracy while exhibiting very different
    failure modes.

    For example:

    ```text Qwen 2.5 Coder 7B 16/21 0 FP / 5 FN

    Qwen 2.5 Coder 14B 16/21 5 FP / 0 FN ```

    Both reach:

    ```text 76.19% ```

    but they represent fundamentally different reviewer trade-offs.

    ## Architecture-Level Finding

    The cross-model experiment strengthens the evidence for specialization.

    The improvement is not isolated to Qwen 3.5 9B.

    ```text SINGLE SPECIALIZED

    Qwen 3.5 9B 80.95% → 95.24% Qwen 2.5 7B 71.43% → 76.19% Qwen 2.5 14B
    61.90% → 76.19% Gemma 3 12B 61.90% → 66.67% Llama 3.1 8B 23.81% → 42.86%
    DeepSeek 16B 14.29% → 33.33% ```

    Every tested model improves in aggregate accuracy.

    This suggests that:

    ```text task decomposition ↓ reduces rule competition ↓ improves
    issue recognition ```

    is an architectural effect rather than a behavior unique to one model.

    At the same time, the experiment demonstrates that architecture cannot
    fully compensate for model behavior.

    Models with weak change attribution continue to generate false positives
    even after specialization.

    Models with unstable taxonomy selection continue to produce wrong-rule
    failures.

    The architecture and model therefore contribute independently to final
    reviewer quality.

    ## Current Model Selection

    The current preferred model remains:

    ```text Qwen 3.5 9B ```

    Under the strongest architecture:

    ```text v11 general + maintainability_v1 specialist + deterministic
    rule ownership ```

    it achieves:

    ```text 20/21 95.24% 0 false positives 1 false negative 0 wrong rules
    100% severity accuracy ```

    Qwen 2.5 Coder 7B remains the most interesting lightweight alternative:

    ```text 16/21 76.19% 0 false positives 0 wrong rules 38.72s ```

    The remaining models currently provide no compelling
    accuracy/precision/runtime advantage over these two options.

    Full-File Specialization Experiment

    After the maintainability specialist substantially improved Git-diff
    review, the same architectural idea was tested against the established
    full-file benchmark suite.

    The purpose was to determine whether the benefit came from
    specialization in general or whether it was specifically useful for the
    more complex diff-review task.

    The experiment used:

    General reviewer       v5
    Maintainability        maintainability_file_v1
    Merge                  deterministic rule ownership
    Benchmarks              65
    Model                   qwen3.5:9b
    Generation              deterministic

    The architecture mirrors the specialized diff reviewer:

                             Source File
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ↓                         ↓
               General Pass             Specialist Pass
                    v5              maintainability_file_v1
                    │                         │
                    ↓                         ↓
          bug / security /            duplicate_code
             performance               long_function
                    │                         │
                    └────────────┬────────────┘
                                 ↓
                      Deterministic Merge
                                 ↓
                         Final CodeReview

    The experiment therefore tests the same basic hypothesis as the diff
    specialization:

    same model
    +
    same benchmark suite
    +
    task decomposition
    ↓
    does specialization improve review quality?

    Specialized Full-File Result

    The specialized architecture produced:

    Model            qwen3.5:9b
    Prompt           v5+maintainability_file_v1
    Benchmarks       65
    Passed           59
    Failed            6
    Errors            0
    False positives   3
    False negatives   3
    Wrong rules       0
    Accuracy         90.77%
    Severity         30/30 (100.00%)
    Duration         239.97s

    The established v5 baseline is:

    Model            qwen3.5:9b
    Prompt           v5
    Benchmarks       65
    Passed           60
    Failed            5
    Accuracy         92.31%
    Severity         100.00%

    Therefore:

    Architecture                           Passed     Accuracy   Failed

    v5 single-pass                  60/65   92.31%    5
    v5 + maintainability specialist         59/65       90.77%        6

    Unlike the Git-diff experiment, specialization does not improve the
    full-file reviewer.

    Full-File Regression Analysis

    The baseline and specialized runs were compared benchmark by benchmark:

    Old: v5 / qwen3.5:9b — 60/65 (92.3%)
    New: v5+maintainability_file_v1 / qwen3.5:9b — 59/65 (90.8%)

    Comparable: 65
    Fixed: 0
    Regressed: 1
    Still failing: 5
    Added: 0
    Removed: 0

    Fixed

    None

    The specialist did not recover any benchmark that failed under the
    original v5 reviewer.

    Regressed

    benchmarks/maintainability/duplicate_code/shared_validation_helper_safe.py

    The baseline correctly recognized that the shared validation helper
    avoids meaningful duplication.

    The specialist instead reported duplicate_code, producing a new false
    positive.

    Still Failing

    The five existing v5 failures remain:

    benchmarks/bug/mutable_default_argument/none_default_safe.py
    benchmarks/maintainability/long_function/long_function.py
    benchmarks/maintainability/long_function/multi_responsibility_function.py
    benchmarks/performance/list_membership_in_loop/tuple_membership_in_loop_safe.py
    benchmarks/security/path_traversal/user_absolute_path.py

    The specialist therefore changes the full-file result from:

    60/65
    92.31%

    to:

    59/65
    90.77%

    without fixing any existing failure.

    Diff vs Full-File Specialization

    Running the same architectural idea across both review modes produces an
    important result.

    Git-Diff Review

    v11 single-pass
    17/21
    80.95%
    0 FP / 4 FN

            ↓ specialization

    v11 + maintainability_v1
    20/21
    95.24%
    0 FP / 1 FN

    Result:

    +3 passing benchmarks
    +14.29 percentage points
    3 maintainability findings recovered
    0 regressions

    Full-File Review

    v5 single-pass
    60/65
    92.31%

            ↓ specialization

    v5 + maintainability_file_v1
    59/65
    90.77%

    Result:

    0 benchmarks fixed
    1 benchmark regressed
    -1.54 percentage points
    additional inference cost

    The effect of specialization is therefore strongly dependent on the
    review task.

    DIFF REVIEW
    general reviewer must reason about:
        issue recognition
        +
        nine-rule taxonomy
        +
        before/after semantics
        +
        change attribution
            ↓
    specialization helps


    FULL-FILE REVIEW
    general reviewer sees:
        current source
        +
        nine-rule taxonomy
            ↓
    v5 already performs strongly
            ↓
    specialization adds little
            +
            can introduce false positives

    This suggests that specialization is most useful when the general review
    task contains enough competing reasoning responsibilities to interfere
    with issue recognition.

    It should therefore not automatically be applied to every review mode.

    Architecture Generalization Finding

    The combined experiments refine the earlier conclusion that
    specialization improves reviewer quality.

    The evidence now shows something more specific:

    specialization
        ≠
    universally better reviewer

    Instead:

    task complexity
            +
    rule competition
            +
    change attribution
            ↓
    determines whether specialization is useful

    For Git-diff review, decomposition produces a substantial improvement:

    80.95%
        ↓
    95.24%

    For full-file review, the same strategy slightly reduces performance:

    92.31%
        ↓
    90.77%

    This is useful negative experimental evidence.

    It demonstrates that the architecture should be selected according to
    the characteristics of the review task rather than applying additional
    LLM passes by default.

    The current preferred architectures are therefore:

    FULL-FILE REVIEW

    Qwen 3.5 9B
    +
    v5
    +
    single pass

    60/65
    92.31%


    GIT-DIFF REVIEW

    Qwen 3.5 9B
    +
    v11 general reviewer
    +
    maintainability_v1 specialist
    +
    deterministic rule ownership

    20/21
    95.24%

    ## Current Observations

    ### Full-File Review

    - Qwen 3.5 9B produced the strongest result in the initial multi-model
    comparison. - Controlled prompt iteration improved the full-file
    reviewer significantly. - Prompt v5 remains the full-file baseline. - v5
    reaches **92.3% accuracy on 65 benchmarks**. - Severity accuracy
    remains **100%**. - `unreachable_code` currently performs
    strongly. - `long_function` remains one of the weakest full-file
    rules. - A targeted general `long_function` prompt experiment did not
    improve recognition. - Further general prompt tuning for that rule was
    paused to avoid benchmark-specific overfitting. - Full-file
    maintainability specialization was evaluated using
    v5 + maintainability_file_v1. - The specialized architecture achieved
    59/65 --- 90.77%, compared with 60/65 --- 92.31% for v5. - It
    fixed 0 existing failures and introduced 1 regression. - The
    regression was the safe shared_validation_helper_safe.py
    duplicate-code case. - Full-file specialization therefore does not
    currently justify its additional inference cost. - v5 single-pass
    remains the preferred full-file architecture.

    ### Single-Pass Git Diff Review

    - The diff suite contains **21 cases covering all nine
    rules**. - v9 achieved **15/21 --- 71.43%** with **3 FP
    / 3 FN**. - v10 achieved **15/21 --- 71.43%** with **2
    FP / 4 FN**. - v11 achieves **17/21 --- 80.95%** with
    **0 FP / 4 FN / 0 wrong rules** under Qwen 3.5 9B. - v11 fixes
    all three attribution false positives present under v9. - All remaining
    v11 failures are maintainability false negatives. - v11 remains the
    frozen single-pass baseline.

    ### Specialized Git Diff Review

    - `maintainability_v1` recovers both `duplicate_code` positives
    under Qwen 3.5 9B. - It also recovers the stronger `long_function`
    positive. - Combining v11 and `maintainability_v1` produces
    **20/21 --- 95.24%**. - The architecture produces **0 false
    positives**. - It produces **1 false negative**. - It
    produces **0 wrong-rule failures**. - Severity accuracy remains
    **100%**. - No previously passing v11 benchmark regresses. - The
    only remaining Qwen 3.5 9B failure is the weaker `long_function`
    positive. - The architecture requires two LLM calls and therefore
    increases inference cost.

    ### Cross-Model Specialized Review

    - Every tested model improves in aggregate accuracy under the
    specialized architecture. - Qwen 3.5 9B improves from **80.95% →
    95.24%**. - Qwen 2.5 Coder 7B improves from **71.43% →
    76.19%**. - Qwen 2.5 Coder 14B improves from **61.90% →
    76.19%**. - Gemma 3 12B improves from **61.90% → 66.67%**. -
    Llama 3.1 8B improves from **23.81% → 42.86%**. - DeepSeek Coder
    V2 16B improves from **14.29% → 33.33%**. - Qwen 3.5 9B is the
    only tested model combining very high accuracy with **0 FP and 0
    wrong rules**. - Qwen 2.5 Coder 7B remains conservative with **0
    FP / 0 wrong rules**, but has lower recall. - Qwen 2.5 Coder 14B
    reaches the same accuracy as the 7B model but with the opposite error
    profile: **5 FP / 0 FN**. - Gemma has strong positive
    recognition but substantially weaker attribution. - Llama and DeepSeek
    improve numerically but remain unstable reviewers. - Larger model size
    does not automatically improve diff-review quality.

    ### Architecture

    - Adding more generic prompt instructions showed diminishing returns. -
    Candidate generation alone did not solve the maintainability problem. -
    Verification improved confidence but could not recover missing
    candidates. - Narrow maintainability specialization substantially
    improved issue recognition. - A specialist should complement rather than
    replace the general reviewer. - Deterministic rule ownership avoids
    requiring an additional merge LLM call. - Cross-model results provide
    evidence that specialization is not specific to one model. - Model
    quality and reviewer architecture are separate experimental variables. -
    Task decomposition is now a first-class architectural component. -
    However, the full-file experiment demonstrates that specialization is
    not universally beneficial. - Full-file specialization fixed no
    existing benchmark and introduced one regression. - The value of
    specialization therefore depends on task complexity and reviewer
    responsibilities. - Specialization should be introduced only when
    benchmark evidence demonstrates a measurable benefit.

    ## Reproducibility State

    Benchmark result schema version 2 now persists inference metadata.

    Current frozen specialized inference settings are:

    ```text
    runtime       ollama
    context_size  4096
    temperature   0
    seed          42

These settings should remain fixed while unseen diff benchmarks are
added so future changes measure generalization rather than simultaneous
inference-configuration changes.

## Current Evaluation State

\`\`\`text FULL-FILE REVIEW 65-case suite Prompt v5 Qwen 3.5 9B 60/65
--- 92.3% 100% severity accuracy │ ├── specialization experiment │ └──
v5 + maintainability_file_v1 │ 59/65 --- 90.77% │ 0 fixed / 1 regression
│ → specialization rejected │ └── preferred architecture └── v5
single-pass

SINGLE-PASS GIT-DIFF REVIEW 21-case suite Prompt v11 Qwen 3.5 9B 17/21
--- 80.95% 0 FP / 4 FN / 0 wrong rules │ └── all failures in
maintainability

SPECIALIZED GIT-DIFF REVIEW General v11 + Maintainability
maintainability_v1 + Deterministic rule ownership │ ↓ Qwen 3.5 9B 20/21
--- 95.24% 0 FP / 1 FN / 0 wrong rules 10/10 severity --- 100% 81.12s │
└── remaining failure └── long_function weaker positive

CROSS-MODEL SPECIALIZED REVIEW │ ├── Qwen 3.5 9B │ └── 20/21 --- 95.24%
│ 0 FP / 1 FN / 0 wrong │ ├── Qwen 2.5 Coder 7B │ └── 16/21 --- 76.19% │
0 FP / 5 FN / 0 wrong │ ├── Qwen 2.5 Coder 14B │ └── 16/21 --- 76.19% │
5 FP / 0 FN / 0 wrong │ ├── Gemma 3 12B │ └── 14/21 --- 66.67% │ 7 FP /
0 FN / 0 wrong │ ├── Llama 3.1 8B │ └── 9/21 --- 42.86% │ 10 FP / 0 FN /
2 wrong │ └── DeepSeek Coder V2 16B └── 7/21 --- 33.33% 10 FP / 0 FN / 2
wrong \`\`\`

## Inference Configuration Metadata

Benchmark runs now record the inference settings that materially affect
local model evaluation.

The persisted configuration is represented by an `InferenceConfig` and
currently records:

``` text
runtime
context_size
temperature
seed
```

The default configuration is:

``` text
runtime       ollama
context_size  4096
temperature   0
seed          42
```

Benchmark result exports now use schema version 2 and include the
inference block directly in JSON:

``` json
{
  "schema_version": 2,
  "inference": {
    "runtime": "ollama",
    "context_size": 4096,
    "temperature": 0,
    "seed": 42
  }
}
```

The serializer already recursively supports dataclasses, so the nested
inference configuration is serialized through the existing benchmark
serialization pipeline.

This change makes comparisons more reproducible because a result file
now records both:

``` text
what was evaluated
+
how inference was configured
```

rather than requiring context size and deterministic generation settings
to be reconstructed from external notes.

The specialized diff benchmark exposes context size through:

``` bash
uv run python main.py benchmark-diff-specialized \
    diff_benchmarks \
    --model qwen3.5:9b \
    --context-size 4096
```

The default remains 4096.

## Context-Window Experiment

With context size configurable, the frozen specialized Qwen 3.5 9B
architecture was evaluated at 4K, 8K, and 16K.

The model, prompts, benchmark suite, temperature, seed, evaluator, and
merge behavior were unchanged.

Only context size changed.

### Results

  -----------------------------------------------------------------------------------
     Context      Passed     Accuracy      FP      FN   Wrong   Severity     Duration
                                                        Rules            
  ---------- ----------- ------------ ------- ------- ------- ---------- ------------
    **4096**   **20/21**   **95.24%**   **0**   **1**   **0**      10/10   **81.58s**
                                                                  (100%) 

        8192       18/21       85.71%       0       3       0 8/8 (100%)       88.09s

       16384       18/21       85.71%       0       3       0 8/8 (100%)       87.88s
  -----------------------------------------------------------------------------------

Ollama reported Qwen 3.5 9B as 100% GPU-resident for all three
configurations.

Observed model size increased only modestly as the context window grew:

``` text
4096   approximately 5.6 GB
8192   approximately 5.9 GB
16384  approximately 6.2 GB
```

The larger context windows did not improve benchmark behavior.

The 8K and 16K runs both produced three false negatives, compared with
one false negative at 4K.

The current benchmark inputs therefore do not justify a larger context
window.

The preferred inference configuration remains:

``` text
context_size 4096
temperature  0
seed         42
```

This experiment also demonstrates why context size should be recorded as
benchmark metadata rather than treated as an invisible runtime detail.

## Larger MoE Specialized Evaluation

After freezing the specialized architecture and adding inference
metadata, two larger MoE models were evaluated at the same 4096-token
context.

The experiment kept fixed:

``` text
21 diff benchmarks
v11 general prompt
maintainability_v1 specialist
deterministic rule ownership
temperature 0
seed 42
context 4096
same evaluator
```

Only the model changed.

### Results

  ----------------------------------------------------------------------------------
  Model          Passed     Accuracy      FP      FN   Wrong   Severity     Duration
                                                       Rules            
  --------- ----------- ------------ ------- ------- ------- ---------- ------------
  **Qwen      **20/21**   **95.24%**   **0**       1       0      10/10   **81.58s**
  3.5 9B**                                                       (100%) 

  Gemma 4         17/21       80.95%       4   **0**       0      11/11      146.98s
  26B                                                            (100%) 

  Qwen 3.5        16/21       76.19%       5   **0**       0      11/11      199.46s
  35B-A3B                                                        (100%) 
  ----------------------------------------------------------------------------------

### Gemma 4 26B

Ollama reported:

``` text
model      gemma4:26b
size       18 GB
processor  45% CPU / 55% GPU
context    4096
```

The model detected every introduced positive issue, including both
`long_function` positives.

Its four failures were all false positives on pre-existing issues:

``` text
mutable_default_argument
unreachable_code
duplicate_code
long_function
```

The behavior is therefore:

``` text
recognition strong
+
attribution weaker
```

rather than a lack of issue-detection capability.

### Qwen 3.5 35B-A3B

Ollama reported:

``` text
model      qwen3.5:35b-a3b
size       23 GB
processor  55% CPU / 45% GPU
context    4096
```

This model also detected every expected positive issue.

Its five failures were all false positives on pre-existing issues:

``` text
mutable_default_argument
unreachable_code
duplicate_code
string_concatenation_in_loop
shell_injection
```

The MoE architecture therefore did not translate into a practical memory
footprint comparable to a small dense model on this machine.

Although only part of the model is active for a token, the model weights
still require enough memory that Ollama offloads a substantial portion
to system RAM.

This contributes to the substantially longer runtime.

## Larger-Model Hardware Comparison

The local test system is:

``` text
CPU   AMD Ryzen 5 5600X — 6 cores
GPU   AMD Radeon RX 6700 XT — 12 GB VRAM
RAM   32 GB
OS    Arch Linux
```

Observed execution:

  Model                   Ollama size CPU/GPU split         Duration
  ------------------ ---------------- ------------------- ----------
  Qwen 3.5 9B          \~5.6 GB at 4K 100% GPU                81.58s
  Gemma 4 26B                   18 GB 45% CPU / 55% GPU      146.98s
  Qwen 3.5 35B-A3B              23 GB 55% CPU / 45% GPU      199.46s

The larger models are runnable on the current machine, but neither is
competitive with Qwen 3.5 9B on the combined quality/runtime metric.

The experiment demonstrates that local model selection must consider:

``` text
benchmark accuracy
+
false-positive behavior
+
false-negative behavior
+
change attribution
+
VRAM residency
+
CPU offload
+
latency
```

Parameter count alone is not a useful selection rule.

## Updated Model Selection

The preferred specialized diff-review configuration remains:

``` text
Model             qwen3.5:9b
Context           4096
Temperature       0
Seed              42
General prompt    v11
Specialist        maintainability_v1
Merge             deterministic rule ownership

Passed            20/21
Accuracy          95.24%
False positives   0
False negatives   1
Wrong rules       0
Severity          100%
Duration          81.58s
Execution         100% GPU
```

The new experiments strengthen rather than weaken the existing
model-selection decision.

The larger MoE models have higher positive-case recall, but their weaker
change attribution creates substantially more false positives.

For a diff reviewer, that distinction is critical:

``` text
finding a real issue somewhere in the file
≠
proving that the diff introduced the issue
```

The current Qwen 3.5 9B configuration provides the strongest balance of
attribution precision, recall, latency, and hardware fit among the
tested configurations.

## Frozen-Architecture Generalization Experiment

After establishing the specialized Qwen 3.5 9B configuration as the
strongest diff-review architecture, further prompt tuning was stopped.

The frozen configuration was:

``` text
Model             qwen3.5:9b
General prompt    v11
Specialist        maintainability_v1
Merge             deterministic rule ownership
Context           4096
Temperature       0
Seed              42
```

The established development benchmark result was:

``` text
Benchmarks        21
Passed            20
Failed             1
Accuracy          95.24%
False positives    0
False negatives    1
Wrong rules        0
Severity          100%
```

Rather than modifying the prompts to recover the remaining failure, the
next experiment tested whether this result generalized to new benchmark
examples.

### Generalization Suite Design

A separate suite was introduced:

``` text
diff_benchmarks_generalization/
```

It is deliberately kept separate from:

``` text
diff_benchmarks/
```

The distinction is:

``` text
diff_benchmarks/
        ↓
development / architecture-selection evidence

diff_benchmarks_generalization/
        ↓
unseen generalization evidence
```

The generalization cases were created after the architecture, prompts,
model, and inference configuration had been frozen.

They were therefore not used to produce the original 20/21 result.

The suite contains **20 new cases covering all nine existing taxonomy
rules**.

The cases test:

``` text
alternative positive manifestations
+
pre-existing attribution boundaries
+
safe changes
+
maintainability boundaries
+
specialist false-positive behavior
```

The same command and frozen architecture were then used across the
complete generalization suite:

``` bash
uv run python main.py benchmark-diff-specialized \
    diff_benchmarks_generalization \
    --model qwen3.5:9b \
    --context-size 4096
```

## Generalization Result

The frozen architecture produced:

``` text
Model            qwen3.5:9b
Prompt           v11+maintainability_v1
Benchmarks       20
Passed           16
Failed            4
Errors            0
False positives   3
False negatives   1
Wrong rules       0
Accuracy         80.00%
Severity          8/8 (100.00%)
Duration         81.17s
```

The comparison with the development suite is:

  Suite              Passed   Accuracy   FP   FN   Wrong Rules   Severity
  ---------------- -------- ---------- ---- ---- ------------- ----------
  Development         20/21     95.24%    0    1             0       100%
  Generalization      16/20     80.00%    3    1             0       100%

Across both suites:

``` text
Benchmarks       41
Passed           36
Failed            5
Accuracy         87.80%
```

The combined number is useful as a descriptive total, but the two suites
should remain analytically separate.

The development suite influenced architecture and prompt decisions.

The generalization suite did not.

## Generalization Benchmark-Level Analysis

### Mutable Default Argument

``` text
Changing None default to mutable set introduces shared state
PASS

Pre-existing mutable dict default is not introduced by diff
FAIL
```

The failure is:

``` text
expected    no issues
actual      mutable_default_argument
```

This is a false-positive attribution failure.

The reviewer correctly recognizes the alternative mutable-default
manifestation using a set, but incorrectly reports a mutable dictionary
default that already existed before the diff.

Result:

``` text
1/2
```

### Unreachable Code

``` text
Adding statement after continue introduces unreachable code
PASS

Pre-existing unreachable code after return is not introduced by diff
PASS
```

The reviewer generalizes both recognition and attribution to the new
control-flow examples.

Result:

``` text
2/2
```

### SQL Injection

``` text
Changing parameterized query to string concatenation introduces SQL injection
PASS

Pre-existing SQL injection is not introduced by diff
PASS
```

Result:

``` text
2/2
```

### Shell Injection

``` text
Changing argument list to interpolated shell command introduces shell injection
PASS

Pre-existing shell injection is not introduced by diff
PASS
```

Result:

``` text
2/2
```

### Path Traversal

``` text
Removing filename restriction introduces path traversal
PASS

Pre-existing direct user path is not introduced by diff
PASS
```

Result:

``` text
2/2
```

The complete unseen security subset therefore produces:

``` text
sql_injection       2/2
shell_injection     2/2
path_traversal      2/2

TOTAL               6/6
```

This is strong evidence that the existing security behavior generalizes
across these alternative manifestations.

### List Membership in Loops

``` text
Changing membership container from set to list introduces repeated linear lookup
PASS

Pre-existing list membership in loop is not introduced by diff
FAIL
```

The failure is unusual:

``` text
expected    no issues
actual      long_function
```

The reviewer does not incorrectly attribute `list_membership_in_loop`.

Instead, the maintainability specialist generates an unrelated
`long_function` finding.

This is therefore classified as:

``` text
false positive
+
spurious specialist finding
```

rather than a performance-rule recognition failure.

Result:

``` text
1/2
```

### String Concatenation in Loops

``` text
Replacing join with repeated string concatenation introduces loop allocation
PASS

Pre-existing string concatenation in loop is not introduced by diff
PASS
```

Result:

``` text
2/2
```

Both positive performance manifestations are therefore recognized
successfully.

### Duplicate Code

The generalization family contains three cases:

``` text
Duplicating validation logic introduces duplicate code
PASS

Pre-existing duplicate validation is not introduced by diff
FAIL

Similar validation functions are not meaningful duplicate code
PASS
```

The positive case demonstrates successful recognition on new duplicated
validation logic.

The similar-but-distinct boundary also passes.

The failure occurs when genuine duplication exists in both versions but
was not introduced by the diff:

``` text
expected    no issues
actual      duplicate_code
```

This is an attribution false positive.

Result:

``` text
2/3
```

### Long Function

The generalization family also contains three cases:

``` text
Cohesive profile normalization growth is not a long function
PASS

Growing order processing into multiple responsibilities introduces a long function
FAIL

Pre-existing long function is not introduced by unrelated helper addition
PASS
```

The safe cohesive-growth boundary passes.

The pre-existing long-function attribution case also passes.

The positive case fails:

``` text
expected    long_function
actual      no issues
```

This is a recognition false negative.

Result:

``` text
2/3
```

## Generalization Failure Classification

The four failures can be grouped by cause.

``` text
ATTRIBUTION

mutable_default_argument
└── pre-existing mutable dictionary
    └── false positive

duplicate_code
└── pre-existing duplicate validation
    └── false positive


RECOGNITION

long_function
└── introduced multi-responsibility growth
    └── false negative


SPURIOUS SPECIALIST DETECTION

performance safe case
└── unrelated long_function prediction
    └── false positive
```

Aggregate:

``` text
False positives   3
False negatives   1
Wrong rules       0
```

Three of the four failures involve maintainability-specialist behavior:

``` text
duplicate_code attribution FP
long_function recognition FN
spurious long_function FP
```

This makes maintainability the clearest current area for further
investigation.

However, the generalization set is still relatively small.

The result is therefore recorded as evidence rather than immediately
used to modify `maintainability_v1`.

## Development vs Generalization Gap

The main result of the experiment is:

``` text
DEVELOPMENT

20/21
95.24%

        ↓

GENERALIZATION

16/20
80.00%
```

The difference is:

``` text
-15.24 percentage points
```

This demonstrates that the development benchmark score was optimistic as
an estimate of performance on new examples.

That does not invalidate the specialized architecture.

The architecture still substantially outperformed the earlier
single-pass reviewer on the development suite and shows strong behavior
on many unseen rule families.

Instead, the result demonstrates why architecture selection and
generalization measurement must be separated.

The earlier experimental process was:

``` text
benchmark
    ↓
inspect failures
    ↓
modify prompt / architecture
    ↓
benchmark again
```

That process is useful for development, but repeated optimization
against the same suite makes the final score increasingly less
informative about unseen behavior.

The generalization suite introduces a second evaluation layer:

``` text
DEVELOPMENT SUITE
        ↓
design / select architecture
        ↓
freeze architecture
        ↓
GENERALIZATION SUITE
        ↓
measure unseen behavior
```

This is a more rigorous evaluation structure.

## Current Generalization Interpretation

The unseen result exposes both strengths and weaknesses.

Strong generalization currently appears in:

``` text
unreachable_code
sql_injection
shell_injection
path_traversal
string_concatenation_in_loop
```

The new positive `list_membership_in_loop` manifestation also passes.

The weaker areas are:

``` text
change attribution on some non-security rules
+
duplicate_code attribution
+
long_function recognition
+
maintainability-specialist precision
```

Security is particularly strong:

``` text
6/6 unseen security cases
```

This is notable because change attribution was originally one of the
main weaknesses of the diff reviewer.

The current v11 security attribution behavior survives all six new
security examples.

## Generalization Methodology Going Forward

The generalization suite should remain separate from the development
suite.

A failure in the generalization suite should not automatically trigger a
prompt modification.

Otherwise:

``` text
generalization case
        ↓
prompt tuned to fix it
        ↓
case becomes development data
        ↓
generalization evidence weakened
```

Instead, changes should be motivated by repeated behavioral patterns
across multiple examples.

The preferred process is:

``` text
observe failure
        ↓
classify failure
        ↓
add broader evidence where necessary
        ↓
identify repeated pattern
        ↓
design architectural or prompt hypothesis
        ↓
evaluate against development + held-out cases
```

This preserves the distinction between fixing a benchmark and improving
the reviewer.

The first generalization experiment therefore changes the next project
priority.

The project no longer needs to ask only:

``` text
Can the current nine rules reach a higher score?
```

It should increasingly ask:

``` text
Does the architecture remain useful as
taxonomy and benchmark diversity increase?
```

## Current Conclusions

The project has now moved beyond both single-prompt optimization and
single-model architectural testing.

The experimental progression is:

`text full-file review ↓ single-pass diff review ↓ change-attribution tuning ↓ cross-model evaluation ↓ failure-classification improvements ↓ candidate generation ↓ candidate verification ↓ maintainability specialization ↓ general + specialist architecture ↓ cross-model architecture validation`

The strongest current configuration remains:

\`\`\`text Qwen 3.5 9B + v11 general reviewer + maintainability_v1
specialist + deterministic rule ownership

20/21 95.24% 0 false positives 1 false negative 0 wrong rules 100%
severity accuracy \`\`\`

The cross-model experiment adds an important result:

`text same specialization architecture ↓ all six models improve`

This provides evidence that specialization is not merely a Qwen
3.5-specific prompt optimization.

However:

`text better architecture ≠ all models become good reviewers`

The model still determines important behavioral characteristics.

Qwen 2.5 Coder 7B remains conservative.

Qwen 2.5 Coder 14B and Gemma detect more positive issues but struggle
with attribution.

Llama and DeepSeek remain unstable despite substantial percentage
improvements.

The main conclusions are therefore:

`text model choice + prompt design + task decomposition + change attribution + deterministic aggregation ↓ reviewer quality`

No single component is sufficient by itself.

The current **20/21 specialized Qwen 3.5 9B result should now remain
frozen as the architectural baseline**.

The next experimental priority should be benchmark generalization rather
than further tuning against the same 21 cases.

The existing prompts should remain unchanged while new unseen diff
benchmarks are added.

That will test whether:

`text 95.24% on current suite ↓ survives unseen cases ↓ evidence of generalization`

rather than continuing to optimize against a small known benchmark set.
\### Full-File vs Diff Architectural Baselines

The full-file specialization experiment adds an important qualification
to the specialization results.

FULL-FILE

v5 single-pass 60/65 92.31%

specialized 59/65 90.77%

→ specialization rejected

GIT-DIFF

v11 single-pass 17/21 80.95%

specialized 20/21 95.24%

→ specialization retained

The strongest configurations are therefore different for each task:

FULL-FILE REVIEW

Qwen 3.5 9B + v5 single-pass

60/65 92.31%

GIT-DIFF REVIEW

Qwen 3.5 9B + v11 general reviewer + maintainability_v1 specialist +
deterministic rule ownership

20/21 95.24% 0 false positives 1 false negative 0 wrong rules 100%
severity accuracy

This strengthens the broader architectural conclusion:

more LLM calls ≠ better reviewer

Instead:

model choice + prompt design + task characteristics + change
attribution + appropriate task decomposition + deterministic aggregation
↓ reviewer quality

Specialization should therefore be introduced only when benchmark
evidence demonstrates that decomposing the task solves a measurable
weakness.

The 20/21 specialized diff result and 60/65 v5 full-file result should
now remain frozen as the two architectural baselines.

The first frozen-architecture generalization experiment is now complete.

The current diff-review evidence is:

``` text
DEVELOPMENT

Qwen 3.5 9B
+
v11
+
maintainability_v1
+
deterministic rule ownership

20/21
95.24%


GENERALIZATION

same model
+
same prompts
+
same architecture
+
same 4K deterministic inference configuration

16/20
80.00%
```

This result is more informative than simply continuing to optimize the
original 21 cases.

It demonstrates that:

``` text
high development benchmark accuracy
        ≠
equivalent unseen accuracy
```

while also showing that several rule families, especially security,
generalize strongly.

The current architecture should therefore remain frozen while the
project moves into broader taxonomy and benchmark expansion.

The next phase should focus on:

``` text
new rules
+
new benchmark families
+
continued held-out generalization coverage
+
failure-pattern analysis
```

rather than immediately modifying prompts to recover the four current
generalization failures.

Prompt or architecture changes should be justified by repeated patterns
across multiple examples.

The project has therefore progressed from:

``` text
build reviewer
        ↓
optimize reviewer
        ↓
compare models
        ↓
specialize architecture
        ↓
freeze architecture
        ↓
measure generalization
```

to the next phase:

``` text
expand problem coverage
        ↓
measure whether architecture scales
        ↓
identify systematic weaknesses
        ↓
iterate only when evidence justifies it
```

The current frozen baselines are:

``` text
FULL-FILE

60/65
92.31%


DIFF DEVELOPMENT

20/21
95.24%


DIFF GENERALIZATION

16/20
80.00%
```

These should remain clearly separated in future documentation and result
analysis.

## Taxonomy Expansion: Resource Leak

After completing the first frozen-architecture generalization
experiment, the project moved from prompt optimization into taxonomy
expansion.

The first new rule added in this phase is:

``` text
resource_leak
```

Category:

``` text
bug
```

Severity:

``` text
medium
```

This expands the supported taxonomy from:

``` text
9 rules
```

to:

``` text
10 rules
```

The purpose of the new rule is to detect resources introduced by a diff
that are no longer reliably released.

The initial benchmark family focuses on resource lifecycle changes
rather than simply detecting calls such as `open()`.

The reviewer should distinguish:

``` text
resource acquired
+
cleanup removed or bypassed
        ↓
report resource_leak

resource already leaked before diff
        ↓
do not report

resource protected by reliable cleanup
        ↓
do not report
```

This preserves the central diff-review principle:

``` text
issue exists in current code
        ≠
diff introduced issue
```

## Resource-Leak Development Benchmarks

Four development cases were added under:

``` text
diff_benchmarks/bug/resource_leak/
```

They cover:

``` text
Removing context manager introduces resource leak
        ↓
positive

Adding early return before close introduces resource leak
        ↓
positive control-flow case

Pre-existing unclosed file is not introduced by diff
        ↓
attribution boundary

Try finally cleanup safely releases opened resource
        ↓
safe cleanup boundary
```

The initial general prompt did not recognize the new rule reliably.

A new general diff prompt version, `v12`, was therefore introduced.

The change extends the general reviewer to reason about resource
lifecycle while preserving the existing specialist architecture:

``` text
General pass
    v12

Maintainability specialist
    maintainability_v1

Merge
    deterministic rule ownership
```

No additional specialist was introduced for `resource_leak`.

The rule remains owned by the general reviewer.

## v12 Resource-Leak Result

Qwen 3.5 9B with the v12 general prompt produced:

``` text
Model            qwen3.5:9b
Prompt           v12
Benchmarks       4
Passed           3
Failed           1
Errors           0
False positives  0
False negatives  1
Wrong rules      0
Accuracy         75.00%
Severity         1/1 (100.00%)
Duration         7.52s
```

Benchmark-level behavior:

``` text
Removing context manager introduces resource leak
PASS

Adding early return before close introduces resource leak
FAIL

Pre-existing unclosed file is not introduced by diff
PASS

Try finally cleanup safely releases opened resource
PASS
```

The remaining failure is:

``` text
expected    resource_leak
actual      no issues
```

The reviewer therefore recognizes the straightforward lifecycle
regression but still misses the more subtle control-flow case where an
early return bypasses cleanup.

Importantly, both negative cases pass.

The new rule therefore does not initially introduce a false-positive
attribution problem in its development family.

## Expanded Development Diff Suite

Adding `resource_leak` expands the development diff suite from:

``` text
21 cases
9 rules
```

to:

``` text
25 cases
10 rules
```

The specialized architecture was rerun using:

``` text
Model                   qwen3.5:9b
General prompt          v12
Maintainability prompt  maintainability_v1
Context                 4096
Temperature             0
Seed                     42
```

Result:

``` text
Benchmarks       25
Passed           22
Failed            3
Errors            0
False positives   0
False negatives   3
Wrong rules       0
Accuracy         88.00%
Severity         10/10 (100.00%)
Duration         84.18s
```

The three failures are:

``` text
resource_leak
└── early return bypasses close

unreachable_code
└── introduced unreachable return

long_function
└── weaker multi-responsibility positive
```

The result is intentionally not compared directly with the earlier 20/21
score as though it represented a regression on an unchanged benchmark.

Both the taxonomy and benchmark suite have expanded.

The relevant interpretation is:

``` text
old architecture baseline
21 cases / 9 rules

new taxonomy evaluation
25 cases / 10 rules
```

The earlier 20/21 result therefore remains historical evidence for the
nine-rule architecture rather than being replaced by the new number.

## Resource-Leak Generalization Experiment

After establishing the initial `resource_leak` behavior on file-resource
examples, three additional cases were added to the separate
generalization suite.

These cases were designed to test whether the rule generalized beyond
the exact file-handling patterns used during development.

In particular, the held-out cases use socket-resource lifecycle behavior
rather than simply repeating `open()` / `close()` examples.

The frozen v12 architecture was evaluated without adding
benchmark-specific examples to the prompt.

Result:

``` text
Resource-leak generalization

Passed    3/3
Accuracy  100%
FP        0
FN        0
```

This is an important distinction from the development result:

``` text
Development
3/4
75%

Generalization
3/3
100%
```

Across the complete `resource_leak` benchmark family:

``` text
Development       3/4
Generalization    3/3
                  ───
Combined          6/7
Accuracy          85.71%
```

The combined result is descriptive only.

Development and generalization evidence should continue to be reported
separately because the development cases influenced the creation of v12,
while the held-out cases did not.

## Resource-Leak Interpretation

The current evidence can be summarized as:

``` text
Basic resource-leak recognition
PASS

Pre-existing issue attribution
PASS

Reliable cleanup boundary
PASS

Alternative resource type
PASS

Control-flow cleanup bypass
FAIL
```

The 3/3 held-out result is particularly useful because the new cases
exercise a different resource type.

This suggests that v12 is not merely matching the exact syntax of the
development file examples.

Instead, there is initial evidence that the reviewer learned a broader
resource-lifecycle concept:

``` text
acquire resource
        ↓
determine cleanup responsibility
        ↓
check whether diff removes reliable cleanup
        ↓
report only when the change introduces the leak
```

However, the development failure also shows that lifecycle reasoning
through control flow remains weaker.

The current evidence therefore does not justify claiming complete
`resource_leak` coverage.

## Why v12 Should Remain Frozen

The remaining development failure could be targeted with additional
prompt examples or increasingly specific instructions.

That is deliberately not being done yet.

The project has already established the risk of repeatedly tuning
prompts against individual benchmark failures.

The current evidence is:

``` text
development resource_leak
3/4

held-out resource_leak
3/3
```

Immediately modifying v12 to recover the single development miss would
weaken the value of the current generalization result and risk
benchmark-specific overfitting.

The preferred approach remains:

``` text
observe failure
        ↓
record failure
        ↓
add independent evidence
        ↓
look for repeated pattern
        ↓
modify architecture or prompt only when justified
```

The early-return cleanup failure should therefore remain recorded as a
known limitation rather than being immediately optimized away.

## Updated Evaluation State

The project now supports:

``` text
10 taxonomy rules
```

The original frozen nine-rule baselines remain:

``` text
FULL-FILE

65 cases
v5
Qwen 3.5 9B

60/65
92.31%


DIFF DEVELOPMENT — NINE-RULE BASELINE

21 cases
v11 + maintainability_v1
Qwen 3.5 9B

20/21
95.24%
0 FP
1 FN
0 wrong rules


DIFF GENERALIZATION — NINE-RULE BASELINE

20 cases
same frozen architecture

16/20
80.00%
3 FP
1 FN
0 wrong rules
```

The taxonomy-expansion state is now:

``` text
DIFF DEVELOPMENT — TEN RULES

25 cases
v12 + maintainability_v1
Qwen 3.5 9B

22/25
88.00%
0 FP
3 FN
0 wrong rules
100% severity


RESOURCE_LEAK GENERALIZATION

3 new held-out cases

3/3
100%
0 FP
0 FN
```

The development suite and held-out suite should continue to remain
separate.

## Continued Taxonomy Expansion

After validating `resource_leak`, taxonomy expansion continued using the
same experimental process:

``` text
define rule
        ↓
add development benchmarks
        ↓
make the minimum justified prompt/taxonomy change
        ↓
run targeted benchmark
        ↓
run complete development regression
        ↓
add separate generalization cases
        ↓
measure behavior on alternative manifestations
```

The objective of this phase is no longer to maximize the score of a
small fixed benchmark.

Instead, the project is testing whether the diff-review architecture
continues to behave reliably as:

``` text
number of supported rules increases
+
benchmark diversity increases
+
rule boundaries become more difficult
```

The general reviewer has progressed from:

``` text
v11
    ↓
v12
    ↓
v13
```

while the established maintainability specialist remains independently
versioned.

The primary expanded specialized configuration evaluated during this
phase is:

``` text
Model                   qwen3.5:9b
General prompt          v13
Maintainability prompt  maintainability_v1
Context                 4096
Temperature             0
Seed                     42
Merge                    deterministic rule ownership
```

The larger taxonomy means the new results should not be compared
directly with the historical 20/21 nine-rule result as though the
benchmark had remained unchanged.

The historical baselines remain useful experimental checkpoints.

## Expanded Security Taxonomy

The security taxonomy was expanded with additional rules covering
security problems that were absent from the original benchmark.

Among the newly evaluated rules are:

``` text
hardcoded_secret
unsafe_deserialization
insecure_temp_file
```

These additions increase the diversity of security reasoning required
from the general reviewer.

The reviewer must distinguish not only whether dangerous code exists,
but whether the Git diff actually introduced the triggering condition.

### Unsafe Deserialization

The development family includes cases such as:

``` text
JSON deserialization remains safe after unrelated processing change
        ↓
safe boundary

Replacing JSON parsing with pickle introduces unsafe deserialization
        ↓
positive

Deserializing supplied payload with pickle introduces unsafe deserialization
        ↓
positive

Pre-existing pickle deserialization is not introduced by diff
        ↓
attribution boundary
```

Separate generalization cases were introduced using YAML-loading
behavior rather than repeating the pickle examples.

Generalization result:

``` text
Pre-existing unsafe YAML deserialization is not introduced by diff
PASS

Using safe YAML loader does not introduce unsafe deserialization
PASS

Replacing safe YAML loading with unsafe loader introduces unsafe deserialization
PASS
```

Aggregate:

``` text
Benchmarks       3
Passed           3
Failed           0
False positives  0
False negatives  0
Wrong rules      0
Accuracy         100.00%
Severity         1/1 (100.00%)
```

This provides evidence that the rule generalizes beyond the exact
deserialization API used in development.

### Hardcoded Secret

The development suite includes multiple secret-introduction and
attribution patterns, including:

``` text
environment-provided secret
        ↓
hardcoded credential

runtime-provided password
        ↓
hardcoded credential

pre-existing hardcoded credential
        ↓
unrelated change
```

Generalization cases were then created using alternative credential
configurations.

The initial generalization result was:

``` text
Replacing environment database URL with embedded credential introduces hardcoded secret
PASS

Loading database credential from environment does not hardcode secret
PASS

Pre-existing credential in configuration mapping is not introduced by diff
FAIL
```

Result:

``` text
Benchmarks       3
Passed           2
Failed           1
False positives  1
False negatives  0
Wrong rules      0
Accuracy         66.67%
Severity         1/1 (100.00%)
```

The failure was an attribution false positive:

``` text
expected    no issues
actual      hardcoded_secret
```

This reinforces a recurring theme in diff review:

``` text
correctly recognizing a security problem
        ≠
correctly proving that the diff introduced it
```

### Insecure Temporary File

The rule detects changes that replace secure temporary-file handling
with predictable temporary paths.

Generalization result:

``` text
Using mkstemp safely does not introduce insecure temporary file
PASS

Replacing secure tempfile with predictable process ID path introduces insecure temp file
PASS

Pre-existing predictable temporary path is not introduced by diff
PASS
```

Aggregate:

``` text
Benchmarks       3
Passed           3
Failed           0
False positives  0
False negatives  0
Wrong rules      0
Accuracy         100.00%
Severity         1/1 (100.00%)
```

The rule therefore successfully generalizes across alternative
temporary-file construction patterns in the current held-out examples.

## Expanded Bug Taxonomy

The bug taxonomy was expanded beyond:

``` text
mutable_default_argument
unreachable_code
resource_leak
```

with additional behavioral rules.

One of the new families is:

``` text
missing_none_check
```

The rule targets changes that introduce unsafe use of values that may
now be `None`.

Development examples include:

``` text
optional value protected by None guard
        ↓
safe

existing unsafe optional use
        ↓
unrelated change
        ↓
pre-existing

guard removed
        ↓
unsafe dereference

return behavior changed to optional
        ↓
caller remains unchecked
```

A separate generalization family produced:

``` text
Optional session used for method call without None check
FAIL

Optional mapping checked for None before indexing remains safe
PASS

Pre-existing optional value indexing is not introduced by diff
PASS
```

Result:

``` text
Benchmarks       3
Passed           2
Failed           1
False positives  0
False negatives  1
Wrong rules      0
Accuracy         66.67%
```

The failure is a recognition miss rather than an attribution error.

This suggests that the current reviewer handles some optional-value
patterns but does not yet apply the rule consistently across different
dereference forms.

## Expanded Performance Taxonomy

The performance taxonomy was expanded with:

``` text
repeated_expensive_call_in_loop
```

The rule is intended to detect expensive work moved inside a loop when
the operation is invariant across iterations and could remain outside
the loop.

The important boundary is:

``` text
expensive operation
+
same input every iteration
        ↓
potential repeated_expensive_call_in_loop

expensive operation
+
input depends on current iteration
        ↓
cannot safely hoist
        ↓
do not report
```

### Development Cases

The development family contains four cases:

``` text
Moving regex compilation into loop introduces repeated expensive call
        ↓
positive

Expensive call with iteration-dependent input cannot be hoisted
        ↓
safe semantic boundary

Pre-existing repeated regex compilation is not introduced by diff
        ↓
attribution boundary

Moving invariant JSON parsing into loop introduces repeated expensive call
        ↓
positive alternative manifestation
```

The current v13 specialized result is:

``` text
Benchmarks       4
Passed           3
Failed           1
Errors           0
False positives  1
False negatives  0
Wrong rules      0
Accuracy         75.00%
Severity         2/2 (100.00%)
```

The remaining failure is:

``` text
Expensive call with iteration-dependent input cannot be hoisted

expected    no issues
actual      repeated_expensive_call_in_loop
```

This is an important semantic false positive.

The model recognizes the expensive operation but fails to account for
the fact that its input changes on every iteration.

### Structured-Output Failure Discovered During Evaluation

One complete-suite run also exposed an execution failure on the
invariant JSON-parsing benchmark.

The model began reasoning about `unsafe_deserialization` and produced an
invalid JSON response instead of the required review object.

This produced an execution error rather than an ordinary benchmark
classification failure.

A subsequent deterministic rerun returned valid output and correctly
classified the case.

This incident distinguishes:

``` text
review-quality failure
```

from:

``` text
model output / protocol failure
```

These should remain separate in benchmark reporting.

### Generalization Cases

The generalization family uses alternative expensive operations:

``` text
Expensive hash depending on current loop item cannot be hoisted
PASS

Pre-existing repeated file metadata lookup is not introduced by diff
FAIL

Moving invariant file metadata lookup into loop introduces repeated expensive call
PASS
```

Result:

``` text
Benchmarks       3
Passed           2
Failed           1
False positives  1
False negatives  0
Wrong rules      0
Accuracy         66.67%
Severity         1/1 (100.00%)
```

The failing benchmark was reported as:

``` text
long_function
```

rather than `repeated_expensive_call_in_loop`.

This is another example of specialist precision affecting a benchmark
outside the specialist's intended conceptual domain.

## Expanded v13 Development Suite

After the taxonomy additions, the complete specialized development suite
contains:

``` text
49 benchmarks
```

The suite was evaluated using:

``` text
Model                   qwen3.5:9b
General prompt          v13
Maintainability prompt  maintainability_v1
Context                 4096
Temperature             0
Seed                     42
```

A stable complete run produced:

``` text
Benchmarks       49
Passed           45
Failed            4
Errors            0
False positives   1
False negatives   2
Wrong rules       1
Accuracy         91.84%
Severity         22/22 (100.00%)
Duration         192.08s
```

The four failures were:

``` text
RESOURCE LEAK

Adding early return before close introduces resource leak
expected    resource_leak
actual      no issues

→ false negative


LONG FUNCTION

Adding multiple responsibilities introduces long function
expected    long_function
actual      no issues

→ false negative


REPEATED EXPENSIVE CALL IN LOOP

Expensive call with iteration-dependent input cannot be hoisted
expected    no issues
actual      repeated_expensive_call_in_loop

→ false positive


INSECURE TEMP FILE

Constructing predictable temporary filename from user identifier introduces insecure temp file
expected    insecure_temp_file
actual      path_traversal

→ wrong rule
```

The historical specialized baseline was:

``` text
21 cases
9 rules
20/21
95.24%
```

The expanded evaluation is:

``` text
49 cases
expanded taxonomy
45/49
91.84%
```

The lower percentage does not represent a direct regression on an
unchanged benchmark.

The reviewer is being evaluated against a substantially broader problem
space.

## v13 Context-Window Regression Check

The expanded 49-case v13 suite was also tested at:

``` text
8192
```

while keeping the remaining configuration unchanged.

Result:

``` text
Benchmarks       49
Passed           45
Failed            4
Errors            0
False positives   1
False negatives   2
Wrong rules       1
Accuracy         91.84%
Severity         22/22 (100.00%)
Duration         208.46s
```

The benchmark-level failures were identical to the 4096-token run.

Therefore:

``` text
4096
45/49
91.84%

8192
45/49
91.84%
```

The larger context window provides no accuracy improvement on the
expanded suite and increases runtime.

The preferred context remains:

``` text
4096
```

## Benchmark Infrastructure Failure Rendering

Taxonomy expansion also exposed a benchmark-runner bug that had
previously remained dormant.

The failure-rendering code assumed that every benchmark object
contained:

``` text
benchmark.code_path
```

That is valid for the original full-file benchmark representation.

Diff benchmarks instead contain:

``` text
before_path
after_path
```

and expose the current review target through:

``` text
display_path
```

The bug only appeared when a diff benchmark produced an actual execution
failure.

Normal benchmark passes and ordinary evaluation failures never entered
the execution-failure rendering path.

The renderer was updated to use the common benchmark display abstraction
rather than directly accessing the full-file-only `code_path` field.

This is an infrastructure fix rather than a reviewer-quality change.

It does not alter benchmark classification results.

## Maintainability Taxonomy Expansion

After expanding the general-review taxonomy, the latest rule
investigated in the current expansion phase was:

``` text
excessive_nesting
```

Category:

``` text
maintainability
```

The development family contains four cases:

``` text
Replacing guard clauses with deeply nested conditions introduces excessive nesting
        ↓
positive

Introducing nested loop and branching structure creates excessive nesting
        ↓
positive

Pre-existing deeply nested control flow is not introduced by diff
        ↓
attribution boundary

Simple loop with one conditional does not introduce excessive nesting
        ↓
safe boundary
```

## Excessive Nesting with Existing Specialist

The first evaluation used:

``` text
v13
+
maintainability_v1
```

Result:

``` text
Benchmarks       4
Passed           2
Failed           2
Errors           0
False positives  0
False negatives  1
Wrong rules      1
Accuracy         50.00%
```

Benchmark behavior:

``` text
Replacing guard clauses with deeply nested conditions introduces excessive nesting
FAIL
expected    excessive_nesting
actual      no issues

Introducing nested loop and branching structure creates excessive nesting
FAIL
expected    excessive_nesting
actual      long_function

Pre-existing deeply nested control flow is not introduced by diff
PASS

Simple loop with one conditional does not introduce excessive nesting
PASS
```

The result was expected to some extent because `maintainability_v1` was
originally designed to own only:

``` text
duplicate_code
long_function
```

It did not yet contain explicit `excessive_nesting` ownership.

## Maintainability v2 Experiment

A new experimental specialist version was introduced:

``` text
maintainability_v2
```

The purpose is to extend the maintainability specialist beyond its
original two-rule taxonomy.

The experiment also required the maintainability prompt version to
become a configurable part of the specialized benchmark command rather
than being implicitly fixed to `maintainability_v1`.

This preserves reproducibility:

``` text
maintainability_v1
        ↓
historical two-rule specialist

maintainability_v2
        ↓
expanded maintainability experiment
```

The older prompt is not overwritten.

### Initial Specialized Evaluation

Using the expanded specialist directly in the specialized architecture
produced:

``` text
Benchmarks       4
Passed           2
Failed           2
Errors           0
False positives  0
False negatives  0
Wrong rules      2
Accuracy         50.00%
```

The positive excessive-nesting cases were recognized as maintainability
problems, but the specialist selected existing rules instead:

``` text
expected    excessive_nesting
actual      long_function, duplicate_code
```

and:

``` text
expected    excessive_nesting
actual      duplicate_code, long_function, duplicate_code
```

This is different from complete issue-recognition failure.

The model recognizes structural maintainability complexity but does not
reliably select the new taxonomy rule.

### Multi-Pass Verification Evaluation

The candidate + verifier multi-pass architecture was also evaluated
using:

``` text
maintainability_v2
```

Result:

``` text
Benchmarks       4
Passed           2
Failed           2
Errors           0
False positives  0
False negatives  2
Wrong rules      0
Accuracy         50.00%
```

Both positive cases became:

``` text
expected    excessive_nesting
actual      no issues
```

The verifier therefore removed the incorrect maintainability candidates
but could not recover the desired rule.

This reproduces an architectural lesson already observed earlier:

``` text
candidate generation
        ↓
wrong or missing candidate
        ↓
verifier can reject
        ↓
verifier cannot independently invent correct finding
```

The verifier improves precision but does not solve rule discovery.

## Excessive Nesting Interpretation

The current `excessive_nesting` experiment should be recorded as an
experimental taxonomy result rather than tuned immediately until it
passes.

Current evidence:

``` text
Development cases   4
Passed              2
Failed              2
Accuracy            50.00%
```

The negative boundaries are currently strong:

``` text
pre-existing nesting
PASS

simple non-excessive nesting
PASS
```

The weakness is positive rule identification.

Under the original specialist:

``` text
positive 1
        ↓
no issue

positive 2
        ↓
long_function
```

Under the expanded specialist:

``` text
positive cases
        ↓
maintainability complexity recognized
        ↓
wrong maintainability rules selected
```

Under candidate + verifier:

``` text
incorrect candidates
        ↓
rejected
        ↓
no correct excessive_nesting candidate remains
```

This suggests that `excessive_nesting` overlaps semantically with
existing maintainability concepts strongly enough that taxonomy
separation is harder for the current model.

That raises a broader taxonomy-design question:

``` text
Can the model reliably distinguish:

long_function
vs
duplicate_code
vs
excessive_nesting

when several structural maintainability signals coexist?
```

No generalization result should be treated as meaningful for
`excessive_nesting` until the development behavior and ownership
strategy are settled.

## Current Expanded Evaluation State

Historical frozen results remain:

``` text
FULL-FILE BASELINE

65 cases
Qwen 3.5 9B
v5 single-pass

60/65
92.31%


NINE-RULE DIFF DEVELOPMENT BASELINE

21 cases
Qwen 3.5 9B
v11 + maintainability_v1

20/21
95.24%
0 FP / 1 FN / 0 wrong


NINE-RULE DIFF GENERALIZATION

20 cases
same frozen architecture

16/20
80.00%
3 FP / 1 FN / 0 wrong
```

Taxonomy expansion has produced the larger development evaluation:

``` text
EXPANDED DIFF DEVELOPMENT

49 cases
Qwen 3.5 9B
v13 + maintainability_v1
context 4096

45/49
91.84%

False positives   1
False negatives   2
Wrong rules       1
Errors            0
Severity          22/22 — 100%
Duration          192.08s
```

The same expanded suite at 8192 context produced:

``` text
45/49
91.84%
```

with identical benchmark failures and higher runtime.

The preferred context therefore remains:

``` text
4096
```

The current known expanded-suite failures are:

``` text
resource_leak
└── early-return cleanup bypass
    └── false negative

long_function
└── weaker multi-responsibility case
    └── false negative

repeated_expensive_call_in_loop
└── iteration-dependent expensive operation
    └── false positive

insecure_temp_file
└── predictable user-derived temp path
    └── reported as path_traversal
        └── wrong rule
```

Targeted generalization testing has also exposed further boundary
behavior in newer rules, including:

``` text
hardcoded_secret
└── pre-existing credential attribution weakness

missing_none_check
└── alternative dereference recognition weakness

repeated_expensive_call_in_loop
└── specialist false-positive interaction
```

The maintainability expansion experiment currently adds:

``` text
excessive_nesting

development
2/4
50.00%
```

but this rule should still be considered experimental until its
interaction with the maintainability specialist architecture is
resolved.

## Current Conclusions

The taxonomy-expansion phase provides a more realistic picture of
reviewer quality than the original 20/21 result alone.

The reviewer has scaled from:

``` text
21 development cases
```

to:

``` text
49 development cases
```

while maintaining:

``` text
91.84% accuracy
100% severity accuracy
```

under the current stable `v13 + maintainability_v1` architecture.

The remaining failures cover several distinct failure classes:

``` text
RECOGNITION

resource_leak
long_function
missing_none_check generalization


ATTRIBUTION

hardcoded_secret generalization


SEMANTIC BOUNDARY PRECISION

repeated_expensive_call_in_loop


TAXONOMY SELECTION

insecure_temp_file vs path_traversal


SPECIALIST PRECISION

spurious maintainability findings on unrelated benchmark families


MAINTAINABILITY TAXONOMY OVERLAP

excessive_nesting
vs
long_function
vs
duplicate_code
```

This is precisely the type of information taxonomy expansion was
intended to produce.

The project should therefore avoid optimizing every isolated failure.

The next architectural decisions should be driven by repeated failure
patterns rather than individual benchmark cases.

## Current Preferred Architecture

For the established expanded taxonomy excluding unresolved experimental
maintainability ownership changes, the preferred configuration remains:

``` text
Model                   qwen3.5:9b
General prompt          v13
Maintainability prompt  maintainability_v1
Context                 4096
Temperature             0
Seed                     42
Runtime                  Ollama
Merge                    deterministic rule ownership
```

Current expanded development result:

``` text
45/49
91.84%
```

The 8192-token experiment provides no benefit.

`maintainability_v2` should remain an experimental prompt version while
the new `excessive_nesting` rule is investigated.

It should not silently replace the established `maintainability_v1`
baseline.

## Next Experimental Phase

The immediate objective is no longer simply:

``` text
add another rule
```

The taxonomy has become large enough to evaluate the architecture
itself.

The next phase should consolidate the expansion work and answer:

``` text
Does each rule have sufficient:

development coverage
+
positive manifestations
+
safe boundaries
+
pre-existing attribution boundaries
+
held-out generalization coverage?
```

The workflow should therefore be:

``` text
1. Freeze the current expanded development state

2. Complete generalization families for the newly added stable rules

3. Keep development and generalization results separate

4. Classify failures by:
       recognition
       attribution
       semantic boundary
       taxonomy selection
       specialist interaction

5. Evaluate excessive_nesting as an experimental maintainability rule

6. Decide whether the maintainability specialist should:
       expand ownership
       remain two-rule
       split into narrower specialists
       or use another architecture

7. Only then modify prompts if repeated evidence justifies it
```

The project has therefore progressed from:

``` text
build reviewer
        ↓
optimize prompts
        ↓
improve attribution
        ↓
compare models
        ↓
specialize maintainability
        ↓
freeze architecture
        ↓
measure generalization
        ↓
expand taxonomy
```

to:

``` text
broader taxonomy
        ↓
broader development suite
        ↓
per-rule generalization
        ↓
failure-pattern analysis
        ↓
architecture scaling evaluation
```

This is the appropriate point to stop treating individual benchmark
failures as prompt-tuning targets and begin evaluating whether the
reviewer design scales as a complete system.
