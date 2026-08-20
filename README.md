**\# AI Code Reviewer**

A project to learn AI engineering by building a local AI-powered code
reviewer from scratch.

The goal isn't just to call an LLM API, but to understand how modern
coding assistants are designed by implementing each component step by
step. Everything runs locally using open-weight models and Ollama.

The project emphasizes clean architecture, reproducible evaluation,
controlled prompt experimentation, structured LLM outputs, diff-aware
review, change attribution, model comparison, specialized multi-pass
review, and local execution.

**\## Roadmap**

**\### Completed**

-   ✅ Review a single file

-   ✅ Review multiple files

-   ✅ Structured JSON output

-   ✅ Benchmark runner

-   ✅ Benchmark evaluation

-   ✅ Benchmark result export

-   ✅ Benchmark result comparison

-   ✅ Rule comparison

-   ✅ Category comparison

-   ✅ Versioned prompt templates

-   ✅ Benchmark result analysis

-   ✅ Deterministic benchmark generation

-   ✅ Rule-based severity normalization

-   ✅ Controlled prompt optimization experiments

-   ✅ Cross-run regression comparison

-   ✅ Review local Git diffs

-   ✅ Diff review with current source context

-   ✅ Diff-specific benchmark format

-   ✅ Diff benchmark discovery and loading

-   ✅ Diff benchmark runner

-   ✅ Diff benchmark CLI

-   ✅ Diff benchmark result rendering

-   ✅ Diff benchmark result export

-   ✅ Diff benchmark coverage across all current taxonomy rules

-   ✅ Diff change-attribution experiments

-   ✅ Cross-run comparison for diff benchmarks

-   ✅ Review committed branch changes against a base ref

-   ✅ Cross-model diff benchmark evaluation

-   ✅ Aggregate wrong-rule / rule-mismatch reporting

-   ✅ Structured Ollama output with JSON Schema

-   ✅ Multi-pass candidate generation and verification experiment

-   ✅ Maintainability-specialist prompt

-   ✅ General + specialist diff-review architecture

-   ✅ Deterministic rule ownership and review merging

-   ✅ Specialized diff benchmark CLI

-   ✅ Configurable Ollama context size for specialized diff benchmarks

-   ✅ Persisted inference metadata in benchmark exports

-   ✅ Benchmark result schema v2

-   ✅ Context-size experiments at 4K / 8K / 16K

-   ✅ Larger MoE model evaluation with Gemma 4 26B and Qwen 3.5 35B-A3B

-   ✅ Separate unseen diff generalization benchmark suite

-   ✅ Frozen-architecture generalization evaluation

-   

**\### Planned**

-   Expand the taxonomy with new rules and corresponding benchmark
    families

-   Continue expanding unseen generalization coverage

-   Investigate repeated generalization failure patterns before
    additional prompt tuning

-   Evaluate category-specialist review architecture

-   Measure accuracy vs inference-cost tradeoffs across review
    architectures

-   Evaluate larger local models on higher-VRAM hardware

-   HTML reports

**\## Current Features**

-   Review individual Python files

-   Review entire Python projects recursively

-   Review local unstaged Git changes

-   Review committed branch changes against a base branch or commit

-   Combine Git diffs with current changed-file contents for contextual
    review

-   Focus diff reviews on issues introduced or worsened by a change

-   Structured JSON responses from the LLM

-   JSON Schema constrained Ollama generation

-   Response validation and parsing

-   Versioned prompt templates

-   Full-file benchmark execution

-   Diff-specific benchmark execution

-   Candidate-generation benchmark execution

-   Multi-pass diff benchmark execution

-   Specialized general + maintainability diff review

-   Deterministic merging of specialist and general findings

-   Automatic benchmark evaluation

-   JSON export of full-file and diff benchmark results

-   Compare aggregate benchmark results

-   Compare models by rule

-   Compare models by category

-   Compare prompt versions

-   Inspect benchmark failures and severity mismatches

-   Compare individual benchmark behavior between two runs

-   Cross-run comparison for both full-file and diff benchmarks

-   Detect fixed and regressed benchmark cases

-   Detect benchmarks that remain failing

-   Detect added and removed benchmark cases

-   Deterministic LLM generation for reproducible experiments

-   Rule-based severity normalization

-   Controlled prompt optimization and comparison

-   Cross-model diff evaluation

-   Local execution with Ollama

-   Configurable inference context for specialized diff benchmarks

-   Persisted inference metadata (`runtime`, `context_size`,
    `temperature`, `seed`)

-   Versioned benchmark-result schema

-   Expanded v13 diff-review taxonomy

-   Separate development and held-out generalization benchmark families
    for new rules

-   Configurable maintainability specialist prompt version

-   Execution-failure rendering shared across full-file and diff
    benchmarks

**\## Architecture**

The reviewer supports full-file review, working-tree diff review,
committed branch comparison, and specialized diff review while sharing
the same LLM, parsing, normalization, and structured review
infrastructure.

**\### Single-Pass Review**

``` text

                         ┌── Python File ────────────────┐

                         │                               ↓

CLI ─────────────────────┤                    Review Prompt Builder

                         │                               │

                         │                               │

                         ├── Working-Tree Git Diff ──────┤

                         │                               │

                         └── Base...HEAD Git Diff ───────┤

                                  +                      ↓

                           Changed Python Files    Diff Prompt Builder

                                  │                      │

                                  └── Current Source ────┘

                                                         ↓

                                                Local LLM (Ollama)

                                                         ↓

                                              JSON Parsing / Validation

                                                         ↓

                                             Rule / Severity Normalization

                                                         ↓

                                               Structured CodeReview
```

The Git integration supports two sources of changes:

``` text

review-diff

    ↓

git diff

    ↓

current unstaged changes



review-pr --base <ref>

    ↓

git diff <base>...HEAD

    ↓

committed branch changes
```

Both feed the same diff-review pipeline.

**\### Specialized Diff Review**

The specialized architecture was originally introduced after the 21-case
v11 diff benchmark showed that the general reviewer performed well on
bug, security, performance, and change attribution while its remaining
failures were concentrated in maintainability. Taxonomy expansion has
since moved the general reviewer to v13 while preserving the same
two-call design.

Rather than continuing to enlarge the general prompt, the reviewer now
supports a specialized two-call architecture:

``` text

                         Git Diff

                            +

                     Current Source

                            │

             ┌──────────────┴──────────────┐

             │                             │

             ↓                             ↓

      General Reviewer           Maintainability Specialist

            v11                   maintainability_v1

             │                             │

             ↓                             ↓

   Bug / Security /              duplicate_code

     Performance                 long_function

             │                             │

             └──────────────┬──────────────┘

                            ↓

                 Deterministic Rule Ownership

                            +

                       Python Merge

                            ↓

                    Structured CodeReview
```

The architecture deliberately uses exactly two LLM calls.

The current stable general v13 reviewer owns the non-maintainability
taxonomy, including:

``` text

sql_injection

shell_injection

path_traversal

mutable_default_argument

unreachable_code

list_membership_in_loop

string_concatenation_in_loop
```

The maintainability specialist owns:

``` text

duplicate_code

long_function
```

If the general reviewer also returns one of the specialist-owned rules,
that finding is discarded during the deterministic merge and the
specialist result is used instead.

No additional LLM call is used for merging.

This prevents duplicate findings and makes rule ownership explicit and
reproducible.

**\### Experimental Candidate / Verifier Pipeline**

Before the specialized architecture was introduced, a
candidate-generation and verification pipeline was also implemented:

``` text

Diff + Current Source

        ↓

Candidate Generation

        ↓

Candidate CodeReview

        ↓

Verifier

        ↓

Final CodeReview
```

This experiment demonstrated that a second verification pass could
preserve valid maintainability findings without introducing false
positives.

However, the architecture still depended on the candidate pass
discovering an issue first. A verifier cannot recover an issue that
candidate generation completely misses.

This motivated the current general + specialist architecture, where the
second call performs complementary detection rather than only
verification.

**\### Evaluation Pipeline**

All review modes can continue through the evaluation pipeline:

``` text

Structured CodeReview

      ↓

Benchmark Evaluation

      ↓

Benchmark Run

      ↓

Benchmark Serialization

      ↓

Result Comparison / Analysis
```

Diff benchmarks add an additional layer before evaluation:

``` text

Diff Benchmark Directory

        ↓

before.py + after.py + benchmark.json

        ↓

Load DiffBenchmark

        ↓

Generate Unified Diff

        +

Current after.py Source

        ↓

Diff Review

        ↓

Benchmark Evaluation

        ↓

BenchmarkRun
```

The main modules include:

``` text

reviewer/

├── engine.py

├── git_diff.py

├── benchmark_diff.py

├── diff_benchmark_runner.py

├── llm.py

├── prompts.py

├── models.py

├── taxonomy.py

├── benchmarks.py

├── benchmark_runner.py

├── benchmark_evaluator.py

├── benchmark_serialization.py

├── benchmark_comparison.py

├── result_comparison.py

└── rendering.py
```

The application keeps Git integration, LLM execution, prompt
construction, benchmark loading, benchmark execution, evaluation,
experiment comparison, serialization, and CLI rendering separate so each
part can be tested and evolved independently.

**\## Benchmark Workflow**

The benchmarking workflow is designed to support iterative prompt
engineering, model evaluation, and architecture experiments.

``` text

Review Code

      ↓

Run Benchmarks

      ↓

Export Benchmark Results

      ↓

Compare Models / Prompts / Architectures

      ↓

Inspect Failures

      ↓

Compare Runs for Regressions

      ↓

Improve Prompt / Architecture / Taxonomy / Evaluation

      ↓

Repeat
```

This makes prompt, model, and architecture experiments measurable and
reproducible rather than relying on subjective impressions.

Aggregate metrics show whether a run improved overall, while cross-run
comparison shows exactly which benchmark cases changed.

**\## Full-File Benchmarks**

The project currently contains a \*\*\*\*65-case full-file benchmark
suite\*\*\*\* designed to test both detection ability and false-positive
boundaries.

Benchmarks are deliberately built from positive, negative, and boundary
cases rather than only obvious examples.

Each full-file benchmark contains:

-   A Python source file

-   The expected findings

-   Expected rule, category, and severity

-   Automatic evaluation against the model response

-   False-positive and false-negative detection

Current benchmark categories and rules include:

\| Category \| Rules \|

\| --- \| --- \|

\| Bug \| Mutable default argument, Unreachable code \|

\| Security \| SQL injection, Shell injection, Path traversal \|

\| Performance \| List membership in loops, String concatenation in
loops \|

\| Maintainability \| Duplicate code, Long function \|

Safe and boundary cases are included throughout the rule families to
measure false positives.

Examples include parameterized SQL queries, allowlisted paths and
commands, immutable default arguments, set and dictionary membership,
`join()`-based string construction, shared helper functions, and valid
control flow.

The current Qwen 3.5 9B full-file baseline uses prompt v5:

``` text

Benchmarks         65

Passed             60

Failed              5

Accuracy           92.3%

Severity accuracy 100.0%
```

`long_function` remains one of the weakest full-file rules.

A targeted prompt investigation tested increasingly explicit
responsibility definitions but did not improve detection. Further tuning
of that rule was paused to avoid benchmark-specific overfitting.

**\## Diff Benchmarks**

Git-diff review has a separate benchmark format because evaluating a
change is different from evaluating a complete source file.

A diff benchmark is represented by a directory containing:

``` text

benchmark_case/

├── before.py

├── after.py

└── benchmark.json
```

`before.py` represents the code before the change.

`after.py` represents the current source after the change.

The benchmark system generates the diff between the two versions and
sends both the generated diff and the current `after.py` source to the
diff reviewer.

`benchmark.json` defines the expected issues introduced by the change.

Example:

``` json

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

Diff benchmarks test more than whether the model can recognize a
problem.

They also test \*\*\*\*change attribution\*\*\*\*:

> Did the diff introduce or worsen the issue, or was the issue already
> present before the change?

A useful diff reviewer should not report every problem visible in the
current file. It should focus on problems caused by the proposed change.

\*\*### Current Diff Benchmark Suite

The development suite has expanded substantially beyond the original
21-case, nine-rule checkpoint.

The current stable v13 specialized development evaluation contains:

``` text
49 benchmarks
```

It includes the original rule families plus newer bug, security, and
performance families such as:

``` text
broad_exception_swallowing
missing_none_check
resource_leak

hardcoded_secret
unsafe_deserialization
insecure_temp_file

repeated_expensive_call_in_loop
```

The suite continues to mix:

-   introduced issues
-   safe changes
-   pre-existing issues
-   attribution boundaries
-   semantic boundary cases
-   alternative manifestations of the same rule

The current stable configuration is:

``` text
Model                   qwen3.5:9b
General prompt          v13
Maintainability prompt  maintainability_v1
Context                 4096
Temperature             0
Seed                     42
Merge                    deterministic rule ownership
```

The current complete development result is:

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

The four remaining development failures are:

``` text
resource_leak
└── early return bypasses cleanup
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

The historical 21-case result remains an important frozen checkpoint:

``` text
v11 + maintainability_v1
20/21
95.24%
```

It should not be compared directly with 45/49 as though the benchmark
and taxonomy were unchanged.

## Diff Generalization Benchmarks\*\*

After reaching \*\*\*\*20/21 --- 95.24%\*\*\*\* on the established diff
benchmark suite, the specialized architecture was frozen before creating
additional benchmark cases.

The purpose was to distinguish performance on benchmarks used during
architecture development from performance on genuinely new examples.

A separate suite was therefore introduced:

``` text

diff_benchmarks_generalization/
```

The original suite remains:

``` text

diff_benchmarks/
```

The distinction is intentional:

``` text

diff_benchmarks/

        ↓

development and architecture-selection evidence

diff_benchmarks_generalization/

        ↓

unseen generalization evidence
```

The generalization cases were created without changing:

``` text

Model             qwen3.5:9b

General prompt    v11

Specialist        maintainability_v1

Context           4096

Temperature       0

Seed              42

Merge             deterministic rule ownership
```

The generalization suite currently contains \*\*\*\*20 cases covering
all nine existing taxonomy rules\*\*\*\*.

The cases use different manifestations from the original development
suite and include:

-   newly introduced issues

-   pre-existing issues that should not be attributed to the diff

-   safe boundary cases

-   alternative implementations of existing rules

-   maintainability cases testing specialist precision and recall

**\### Generalization Result**

The frozen specialized architecture produced:

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

Compared with the established development suite:

\| Suite \| Passed \| Accuracy \| FP \| FN \| Wrong Rules \| Severity \|

\| --- \| ---: \| ---: \| ---: \| ---: \| ---: \| ---: \|

\| Development \| 20/21 \| 95.24% \| 0 \| 1 \| 0 \| 100% \|

\| Generalization \| 16/20 \| 80.00% \| 3 \| 1 \| 0 \| 100% \|

Across both suites:

``` text

Passed      36/41

Accuracy    87.80%
```

The development and generalization results should still be interpreted
separately because they answer different experimental questions.

**\### Generalization Failures**

The four failures expose several distinct weaknesses.

``` text

mutable_default_argument

└── pre-existing mutable dict default

    └── false positive

        └── attribution failure

duplicate_code

└── pre-existing duplicate validation

    └── false positive

        └── attribution failure

long_function

└── introduced multi-responsibility growth

    └── false negative

        └── recognition failure

list_membership_in_loop safe case

└── reported as long_function

    └── false positive

        └── spurious maintainability-specialist finding
```

Three of the four failures therefore involve behavior from the
maintainability side of the specialized architecture.

However, the generalization suite is intentionally treated as evaluation
evidence rather than immediate prompt-training data.

The current prompts remain frozen.

**\### Generalization Findings**

The result demonstrates that the \*\*\*\*95.24% development-suite score
overestimates performance on new cases\*\*\*\*.

This validates the decision to create a separate generalization suite
rather than continuing to tune against the original 21 benchmarks.

At the same time, several areas generalize strongly.

All six unseen security cases pass:

``` text

sql_injection       2/2

shell_injection     2/2

path_traversal      2/2
```

The reviewer also correctly recognizes the new positive performance
cases for:

``` text

list_membership_in_loop

string_concatenation_in_loop
```

The current progression is therefore:

``` text

known development cases

20/21

95.24%

        ↓

freeze architecture and inference

        ↓

new unseen cases

16/20

80.00%

        ↓

generalization gap identified
```

This provides a more realistic distinction between benchmark
optimization and evidence of generalization.

The generalization suite remains separate from the original development
suite so future prompt, architecture, model, and taxonomy changes can be
evaluated against both.

\*\*### Generalization During Taxonomy Expansion

New rule families are also receiving separate held-out cases rather than
being judged only on the development examples.

Current targeted results include:

``` text
unsafe_deserialization
3/3
100%

insecure_temp_file
3/3
100%

hardcoded_secret
2/3
66.67%

missing_none_check
2/3
66.67%

repeated_expensive_call_in_loop
2/3
66.67%
```

These failures expose different behaviors:

``` text
hardcoded_secret
└── pre-existing credential
    └── attribution false positive

missing_none_check
└── alternative optional dereference
    └── recognition false negative

repeated_expensive_call_in_loop
└── pre-existing expensive operation
    └── spurious long_function finding
```

The original frozen 20-case generalization suite remains historical
evidence for the nine-rule architecture. The newer per-rule
generalization families measure the expanded taxonomy and should be
reported separately until the expanded generalization suite is complete.

## Diff Prompt Evolution\*\*

The first expanded baseline used prompt v9:

``` text

Prompt           v9

Benchmarks       21

Passed           15

Failed            6

False positives   3

False negatives   3

Accuracy         71.43%

Severity          8/8 (100.00%)
```

The main weakness was attribution of highly visible pre-existing issues.

Prompt v10 tested stronger generic before/after attribution
instructions:

``` text

Prompt           v10

Benchmarks       21

Passed           15

Failed            6

False positives   2

False negatives   4

Accuracy         71.43%

Severity          7/7 (100.00%)
```

v10 fixed pre-existing mutable-default attribution but continued to
misattribute pre-existing SQL and shell injection.

It also regressed a strong `duplicate_code` case.

Prompt v11 instead uses more concrete attribution guidance.

Before reporting a finding, the model is instructed to identify the
actual triggering code and compare it between the previous and current
versions.

The central attribution rule is:

``` text

triggering code unchanged

        +

diff changes unrelated surrounding behavior

        ↓

pre-existing issue

        ↓

do not report
```

This successfully fixed the remaining security attribution cases.

**\### Single-Pass v11 Baseline**

Qwen 3.5 9B with prompt v11 produces:

``` text

Benchmarks       21

Passed           17

Failed            4

Errors            0

False positives   0

False negatives   4

Wrong rules       0

Accuracy         80.95%

Severity          7/7 (100.00%)
```

\| Prompt \| Passed \| Accuracy \| False Positives \| False Negatives \|

\| --- \| ---: \| ---: \| ---: \| ---: \|

\| v9 \| 15/21 \| 71.43% \| 3 \| 3 \|

\| v10 \| 15/21 \| 71.43% \| 2 \| 4 \|

\| \*\*\*\*v11\*\*\*\* \| \*\*\*\*17/21\*\*\*\* \|
\*\*\*\*80.95%\*\*\*\* \| \*\*\*\*0\*\*\*\* \| \*\*\*\*4\*\*\*\* \|

Compared with v9, v11 fixes:

``` text

pre-existing mutable_default_argument

pre-existing shell_injection

pre-existing sql_injection
```

and regresses:

``` text

strong duplicate_code positive
```

The four remaining false negatives are:

``` text

duplicate_code positive

duplicate_code strong positive

long_function positive

long_function strong positive
```

All current pre-existing attribution boundary cases pass under v11.

The remaining weaknesses are therefore concentrated in
maintainability-rule recognition rather than change attribution.

\*\*## v12 / v13 Taxonomy Expansion

After the original v11 architecture was frozen and generalization was
measured, prompt development resumed specifically to support taxonomy
expansion.

The general diff prompt progressed through v12 to v13 as new rules and
rule boundaries were added.

The current stable expanded general prompt is:

``` text
v13
```

It is used with the existing `maintainability_v1` specialist for the
49-case expanded development suite.

A context regression check produced identical benchmark behavior at 4096
and 8192 tokens:

``` text
4096
45/49
91.84%
192.08s

8192
45/49
91.84%
208.46s
```

The same four benchmark cases failed at both context sizes.

The preferred expanded configuration therefore remains 4096 tokens.

## Maintainability Specialization Experiment\*\*

The concentration of all four v11 failures in maintainability motivated
an experiment with task specialization rather than further expansion of
the general prompt.

A dedicated `maintainability_v1` candidate prompt was created for only:

``` text

duplicate_code

long_function
```

This reduced the number of competing rules and allowed the model to
focus on structural maintainability reasoning.

Candidate-generation results were:

**\### Duplicate Code**

``` text

Benchmarks       3

Passed            3

Failed            0

False positives   0

False negatives   0

Accuracy         100.00%

Severity          2/2 (100.00%)
```

**\### Long Function**

``` text

Benchmarks       3

Passed            2

Failed            1

False positives   0

False negatives   1

Accuracy         66.67%

Severity          1/1 (100.00%)
```

The focused prompt therefore recovered both `duplicate_code` cases
missed by v11 and one of the two `long_function` positives.

A candidate-generation + verifier experiment was then tested.

The verifier preserved the specialist findings:

``` text

duplicate_code

3/3

100%

long_function

2/3

66.67%
```

However, verification could not recover issues missed by candidate
generation.

This led to the current specialized architecture.

**\## Specialized Two-Call Diff Review**

The strongest current diff-review architecture combines:

``` text

Call 1

v11 general reviewer

+

Call 2

maintainability_v1 specialist

+

deterministic Python merge
```

The complete 21-case benchmark produces:

``` text

Model            qwen3.5:9b

Architecture     v11 + maintainability_v1

Benchmarks       21

Passed           20

Failed            1

Errors            0

False positives   0

False negatives   1

Wrong rules       0

Accuracy         95.24%

Severity          10/10 (100.00%)

Duration          81.12s
```

Compared with the single-pass v11 baseline:

\| Architecture \| Calls \| Passed \| Accuracy \| FP \| FN \| Wrong
Rules \|

\| --- \| ---: \| ---: \| ---: \| ---: \| ---: \| ---: \|

\| v11 single-pass \| 1 \| 17/21 \| 80.95% \| 0 \| 4 \| 0 \|

\| \*\*\*\*v11 + maintainability specialist\*\*\*\* \| \*\*\*\*2\*\*\*\*
\| \*\*\*\*20/21\*\*\*\* \| \*\*\*\*95.24%\*\*\*\* \| \*\*\*\*0\*\*\*\*
\| \*\*\*\*1\*\*\*\* \| \*\*\*\*0\*\*\*\* \|

The specialized architecture recovers:

``` text

duplicate_code positive

duplicate_code strong positive

long_function strong positive
```

while preserving all previously passing bug, security, performance,
safe-change, and pre-existing attribution cases.

The only remaining false negative is:

``` text

Adding multiple responsibilities introduces long function
```

The experiment provides evidence that, for the current local model and
taxonomy:

``` text

task specialization

        ↓

higher maintainability recall

        ↓

without increasing false positives
```

The result also introduces an explicit accuracy/latency tradeoff.

The specialized architecture requires two model calls instead of one,
increasing inference time in exchange for substantially higher benchmark
accuracy.

This is now an architecture-level experiment rather than only a
prompt-engineering experiment.

\*\*## Experimental Maintainability v2 and Excessive Nesting

Taxonomy expansion reached a new maintainability candidate:

``` text
excessive_nesting
```

A four-case development family was created with:

``` text
2 positive cases
1 pre-existing attribution boundary
1 safe shallow-control-flow boundary
```

Using the established `v13 + maintainability_v1` specialized
architecture:

``` text
Benchmarks       4
Passed           2
Failed           2
Accuracy         50.00%
```

The positive cases produced one false negative and one `long_function`
wrong-rule result.

An experimental `maintainability_v2` prompt was then added instead of
overwriting `maintainability_v1`.

The specialized run still produced:

``` text
2/4
50.00%
```

but the positive cases were now recognized as maintainability problems
and classified under combinations of `long_function` and
`duplicate_code` rather than `excessive_nesting`.

The candidate + verifier pipeline was also tested:

``` text
Benchmarks       4
Passed           2
Failed           2
False negatives  2
Wrong rules      0
Accuracy         50.00%
```

The verifier correctly removed unsupported candidates but could not
invent the missing `excessive_nesting` finding.

This rule therefore remains experimental.

The next architectural question is whether maintainability ownership
should:

``` text
expand inside one specialist
split into narrower specialists
remain limited to duplicate_code + long_function
or use another decomposition
```

No generalization conclusion should be drawn for `excessive_nesting`
until this ownership problem is resolved.

## Cross-Model Diff Evaluation\*\*

Before specialized review was introduced, the complete 21-case suite was
evaluated across the local models already used by the project using the
same single-pass v11 prompt.

The benchmark suite, prompt, deterministic generation settings, and
evaluator were kept fixed. Only the model changed.

\| Model \| Passed \| Accuracy \| False Positives \| False Negatives \|

\| --- \| ---: \| ---: \| ---: \| ---: \|

\| \*\*\*\*Qwen 3.5 9B\*\*\*\* \| \*\*\*\*17/21\*\*\*\* \|
\*\*\*\*80.95%\*\*\*\* \| \*\*\*\*0\*\*\*\* \| 4 \|

\| Qwen 2.5 Coder 7B \| 15/21 \| 71.43% \| \*\*\*\*0\*\*\*\* \| 6 \|

\| Qwen 2.5 Coder 14B \| 13/21 \| 61.90% \| 4 \| 4 \|

\| Gemma 3 12B \| 13/21 \| 61.90% \| 4 \| 4 \|

\| Llama 3.1 8B \| 5/21 \| 23.81% \| 10 \| 0\* \|

\| DeepSeek Coder V2 16B \| 3/21 \| 14.29% \| 10 \| 0\* \|

`*` The zero false-negative count for Llama 3.1 8B and DeepSeek Coder V2
16B should not be interpreted as strong recall.

Both models frequently produce a finding using the wrong taxonomy rule
rather than returning no issue.

**\### Cross-Model Findings**

Qwen 3.5 9B remains the strongest current model for the project.

Under the frozen single-pass v11 architecture:

``` text

17/21

80.95%

0 false positives

0 wrong rules
```

Qwen 2.5 Coder 7B also maintains zero false positives but misses two
additional introduced performance issues.

Qwen 2.5 Coder 14B and Gemma 3 12B recover some findings but introduce
more attribution failures.

Llama 3.1 8B and DeepSeek Coder V2 16B show substantial
constrained-taxonomy rule-selection instability.

The experiment also provided stronger evidence about the maintainability
failures.

Among the models with reasonably stable taxonomy behavior:

``` text

duplicate_code

Qwen 3.5 9B            FAIL / FAIL

Qwen 2.5 Coder 7B      FAIL / FAIL

Qwen 2.5 Coder 14B     FAIL / FAIL

Gemma 3 12B            FAIL / FAIL



long_function

Qwen 3.5 9B            FAIL / FAIL

Qwen 2.5 Coder 7B      FAIL / FAIL

Qwen 2.5 Coder 14B     FAIL / FAIL

Gemma 3 12B            FAIL / FAIL
```

The two results for each rule represent the normal and stronger positive
cases.

The weakness was therefore not unique to Qwen 3.5 9B.

The later maintainability-specialist experiment showed that changing the
\*\*\*\*task decomposition\*\*\*\* could recover these findings without
changing the model.

This is an important result:

``` text

model capability

        +

task decomposition

        +

prompt scope

        ↓

review performance
```

Model size alone is not sufficient to predict reviewer quality.

**\## DeepSeek Rule-Mismatch Validation**

DeepSeek Coder V2 16B was rerun after aggregate rule-mismatch reporting
was added.

``` text

Benchmarks       21

Passed            3

Failed           18

False positives  10

False negatives   0

Wrong rules       6

Accuracy         14.29%
```

The six wrong-rule cases make the model's taxonomy-selection instability
explicit.

Examples include:

``` text

expected duplicate_code

actual   mutable_default_argument

expected long_function

actual   mutable_default_argument

expected list_membership_in_loop

actual   mutable_default_argument

expected string_concatenation_in_loop

actual   unreachable_code
```

The Wrong rules metric therefore distinguishes models that completely
miss an expected issue from models that detect something but classify it
under the wrong supported rule.

**\## Prompt Templates**

Prompt templates are versioned independently from the application code.

Different review modes and experimental architectures can use separate
templates:

``` text

prompts/

├── v1/

│   └── review.txt

├── ...

├── v5/

│   └── review.txt

├── ...

├── v9/

│   └── diff.txt

├── v10/

│   └── diff.txt

├── v11/

│   └── diff.txt

├── multipass_v1/

│   └── diff_candidates.txt

└── maintainability_v1/

    ├── diff_candidates.txt

    └── diff_verify.txt
```

Full-file review prompts use the Python source code as input.

General diff-review prompts use both the Git diff and the current
contents of changed Python files.

The diff identifies what changed, while the current source provides the
context needed to reason about the behavior of the new version.

The maintainability specialist receives the same diff/current-source
representation but uses a narrower rule scope.

The current baselines are:

``` text

Full-file review             v5

Single-pass Git-diff review  v11

Specialized Git-diff review  v11 + maintainability_v1
```

Existing prompt versions remain frozen so previous experiments can be
reproduced and compared.

**\## Prompt Evaluation**

Prompt changes are evaluated against benchmark suites using controlled
generation settings.

Early Qwen 3.5 9B experiments on the original 35-case full-file
benchmark suite produced:

\| Prompt \| Accuracy \| Passed \| False Positives \| False Negatives \|

\| --- \| ---: \| ---: \| ---: \| ---: \|

\| v1 \| 85.7% \| 30/35 \| 4 \| 1 \|

\| v2 \| 88.6% \| 31/35 \| 3 \| 1 \|

\| v3 \| 88.6% \| 31/35 \| 3 \| 1 \|

\| v4 \| 91.4% \| 32/35 \| 2 \| 1 \|

The full-file suite was subsequently expanded from 35 to 65 cases.

Prompt v5 currently produces:

``` text

Benchmarks         65

Passed             60

Failed              5

Accuracy           92.3%

Severity accuracy 100.0%
```

Diff prompt experiments are evaluated independently.

Single-pass v11 produces:

``` text

Benchmarks         21

Passed             17

Failed              4

Accuracy           80.95%

False positives     0

False negatives     4

Wrong rules         0

Severity accuracy 100.0%
```

The current specialized architecture produces:

``` text

Benchmarks         21

Passed             20

Failed              1

Accuracy           95.24%

False positives     0

False negatives     1

Wrong rules         0

Severity accuracy 100.0%
```

Severity is normalized deterministically from the detected rule instead
of trusting the severity generated by the LLM.

**\## Cross-Run Regression Comparison**

Aggregate accuracy can hide important behavior changes.

The `compare-runs` command compares two exported benchmark runs at the
individual benchmark level.

It supports both full-file and diff benchmark results.

Full-file example:

``` bash

uv run python main.py compare-runs \\

    results/v4/qwen3.5-9b-seed42-block5.json \\

    results/v5/qwen3.5-9b-seed42-block5.json
```

Diff example:

``` bash

uv run python main.py compare-runs \\

    results/diff/v9/qwen3.5-9b-expanded.json \\

    results/diff/v11/qwen3.5-9b.json
```

The comparison reports:

-   \*\*\*\*Fixed\*\*\*\* --- failed in the old run and passes in the
    new run

-   \*\*\*\*Regressed\*\*\*\* --- passed in the old run and fails in the
    new run

-   \*\*\*\*Still failing\*\*\*\* --- fails in both runs

-   \*\*\*\*Added\*\*\*\* --- exists only in the new benchmark run

-   \*\*\*\*Removed\*\*\*\* --- exists only in the old benchmark run

The v9 → v11 diff comparison produced:

``` text

Old: v9 / qwen3.5:9b — 15/21 (71.4%)

New: v11 / qwen3.5:9b — 17/21 (81.0%)

Comparable: 21 | Fixed: 3 | Regressed: 1 | Still failing: 3 | Added: 0 | Removed: 0

Fixed

✓ pre-existing mutable default

✓ pre-existing shell injection

✓ pre-existing SQL injection

Regressed

✗ strong duplicate-code positive

Still failing

• duplicate-code positive

• long-function positive

• strong long-function positive
```

This makes prompt regressions visible even when aggregate benchmark
accuracy improves.

**\### `compare-results` vs `compare-runs`**

The two commands answer different questions:

-   `compare-results` compares aggregate performance across benchmark
    result files.

-   `compare-runs` compares benchmark-by-benchmark changes between two
    specific runs.

Wrong-rule predictions are also represented explicitly in aggregate
benchmark summaries, making taxonomy-selection failures distinguishable
from ordinary false negatives.

**\## Models**

The project focuses primarily on models that can run locally on consumer
hardware with 12 GB of VRAM.

Single-pass diff benchmark results using the same v11 prompt are:

\| Model \| Diff Accuracy \| Notes \|

\| --- \| ---: \| --- \|

\| \*\*\*\*Qwen 3.5 9B\*\*\*\* \| \*\*\*\*80.95%\*\*\*\* \| Current main
model; 0 FP, 0 wrong rules \|

\| Qwen 2.5 Coder 7B \| 71.43% \| 0 FP, lower recall \|

\| Qwen 2.5 Coder 14B \| 61.90% \| More attribution failures \|

\| Gemma 3 12B \| 61.90% \| Moderate result, attribution failures \|

\| Llama 3.1 8B \| 23.81% \| Unstable constrained-rule selection \|

\| DeepSeek Coder V2 16B \| 14.29% \| Unstable constrained-rule
selection \|

Qwen 3.5 9B remains the preferred model for the current local reviewer.

The same model reaches \*\*\*\*95.24%\*\*\*\* on the current 21-case
diff suite when used with the specialized two-call architecture.

This distinction is important: model quality and review architecture are
evaluated separately.

Larger models may be evaluated in the future on machines with more VRAM
using the same frozen benchmark suite and prompts, allowing direct
comparison with the current baselines.

**\## Context-Size and Larger-Model Experiments**

After the specialized Qwen 3.5 9B baseline was frozen, the inference
context was made configurable and recorded in benchmark metadata.

The same specialized 21-case suite was then used to test context size
and larger local MoE models without changing the review prompts or
architecture.

**\### Qwen 3.5 9B Context-Size Experiment**

\| Context \| Passed \| Accuracy \| FP \| FN \| Duration \| Ollama
execution \|

\| ---: \| ---: \| ---: \| ---: \| ---: \| ---: \| --- \|

\| \*\*\*\*4096\*\*\*\* \| \*\*\*\*20/21\*\*\*\* \|
\*\*\*\*95.24%\*\*\*\* \| \*\*\*\*0\*\*\*\* \| \*\*\*\*1\*\*\*\* \|
\*\*\*\*81.58s\*\*\*\* \| 100% GPU \|

\| 8192 \| 18/21 \| 85.71% \| 0 \| 3 \| 88.09s \| 100% GPU \|

\| 16384 \| 18/21 \| 85.71% \| 0 \| 3 \| 87.88s \| 100% GPU \|

Increasing context size did not improve the current benchmark.

The 4K configuration remained both the most accurate and the fastest of
the tested context sizes.

Because the benchmark inputs already fit comfortably inside the 4K
window, a larger context window provides no demonstrated benefit for the
current suite.

**\### Larger MoE Models at 4K**

Two larger models were then evaluated with the same specialized
architecture and a 4096-token context:

\| Model \| Passed \| Accuracy \| FP \| FN \| Wrong Rules \| Duration \|
Ollama execution \|

\| --- \| ---: \| ---: \| ---: \| ---: \| ---: \| ---: \| --- \|

\| \*\*\*\*Qwen 3.5 9B\*\*\*\* \| \*\*\*\*20/21\*\*\*\* \|
\*\*\*\*95.24%\*\*\*\* \| \*\*\*\*0\*\*\*\* \| 1 \| 0 \|
\*\*\*\*81.58s\*\*\*\* \| 100% GPU \|

\| Gemma 4 26B \| 17/21 \| 80.95% \| 4 \| \*\*\*\*0\*\*\*\* \| 0 \|
146.98s \| 55% GPU / 45% CPU \|

\| Qwen 3.5 35B-A3B \| 16/21 \| 76.19% \| 5 \| \*\*\*\*0\*\*\*\* \| 0 \|
199.46s \| 45% GPU / 55% CPU \|

The larger models showed a different failure profile from Qwen 3.5 9B.

Both larger models detected every expected positive issue:

``` text

Gemma 4 26B

0 false negatives

Qwen 3.5 35B-A3B

0 false negatives
```

However, they were more aggressive about reporting issues that already
existed before the change.

Gemma 4 26B produced four attribution false positives:

``` text

pre-existing mutable_default_argument

pre-existing unreachable_code

pre-existing duplicate_code

pre-existing long_function
```

Qwen 3.5 35B-A3B produced five:

``` text

pre-existing mutable_default_argument

pre-existing unreachable_code

pre-existing duplicate_code

pre-existing string_concatenation_in_loop

pre-existing shell_injection
```

This produces a useful precision/recall distinction:

``` text

Qwen 3.5 9B

strong attribution precision

+

slightly lower recall

larger MoE models

strong positive recognition

+

weaker change attribution
```

On the current RX 6700 XT 12 GB system, the larger models also require
substantial CPU offload.

Qwen 3.5 9B remains fully GPU-resident, while Gemma 4 26B and Qwen 3.5
35B-A3B are split across CPU and GPU and are substantially slower.

The preferred specialized configuration therefore remains:

``` text

qwen3.5:9b

context 4096

v11 general

+

maintainability_v1 specialist

+

deterministic rule ownership

20/21

95.24%

0 FP

1 FN

0 wrong rules

100% severity
```

The experiment reinforces two existing project findings:

``` text

larger model

≠

better diff reviewer

larger context

≠

better diff reviewer
```

Model selection should be based on measured reviewer behavior,
attribution precision, latency, and hardware fit rather than parameter
count alone.

**\## Tech Stack**

-   Python 3.14

-   uv

-   Typer

-   Rich

-   pytest

-   Ruff

-   Ollama

-   Local open-weight LLMs

**\## Test Environment**

-   AMD Ryzen 5 5600X (6 cores)

-   AMD Radeon RX 6700 XT (12 GB VRAM)

-   32 GB system RAM

-   Arch Linux

**\## Run**

**\### Show available commands**

``` bash

uv run python main.py --help
```

**\### Review a single file**

``` bash

uv run python main.py review examples/user_lookup.py
```

**\### Review an entire folder**

``` bash

uv run python main.py review-folder examples
```

**\### Review current Git changes**

Review the current unstaged Git diff:

``` bash

uv run python main.py review-diff \\

    --model qwen3.5:9b \\

    --prompt-version v11
```

The diff reviewer combines the Git diff with the current contents of
changed Python files.

This allows the model to detect issues introduced indirectly by a
change, including cases where the affected line itself was not modified.

**\### Review committed branch changes**

Review the committed changes between a base branch or commit and `HEAD`:

``` bash

uv run python main.py review-pr \\

    --base main \\

    --model qwen3.5:9b
```

Internally this reviews:

``` text

git diff main...HEAD
```

The command reuses the existing v11 diff-review pipeline.

**\### Run the full-file benchmark suite**

``` bash

uv run python main.py benchmark benchmarks/
```

**\### Benchmark using a different model**

``` bash

uv run python main.py benchmark benchmarks/ \\

    --model qwen2.5-coder:14b
```

**\### Benchmark using a specific prompt version**

``` bash

uv run python main.py benchmark benchmarks/ \\

    --model qwen3.5:9b \\

    --prompt-version v5
```

**\### Export full-file benchmark results**

``` bash

uv run python main.py benchmark benchmarks/ \\

    --model qwen3.5:9b \\

    --prompt-version v5 \\

    --output qwen3.5-9b-seed42.json
```

**\### Run the single-pass diff benchmark suite**

``` bash

uv run python main.py benchmark-diff \\

    diff_benchmarks \\

    --model qwen3.5:9b \\

    --prompt-version v11
```

A specific rule family can also be evaluated independently:

``` bash

uv run python main.py benchmark-diff \\

    diff_benchmarks/security/sql_injection \\

    --model qwen3.5:9b \\

    --prompt-version v11
```

**\### Run maintainability candidate benchmarks**

``` bash

uv run python main.py benchmark-diff-candidates \\

    diff_benchmarks/maintainability/duplicate_code \\

    --model qwen3.5:9b \\

    --prompt-version maintainability_v1
```

**\### Run candidate + verifier benchmarks**

``` bash

uv run python main.py benchmark-diff-multi-pass \\

    diff_benchmarks/maintainability/duplicate_code \\

    --model qwen3.5:9b \\

    --prompt-version maintainability_v1
```

**\### Run the specialized diff benchmark**

Run the current expanded v13 general reviewer and maintainability
specialist together:

``` bash

uv run python main.py benchmark-diff-specialized \\

    diff_benchmarks \\

    --model qwen3.5:9b \\

    --context-size 4096 \\

    --output qwen3.5-9b-specialized.json
```

The context window is configurable with `--context-size`. The default is
`4096`.

For example:

``` bash

uv run python main.py benchmark-diff-specialized \\

    diff_benchmarks \\

    --model qwen3.5:9b \\

    --context-size 8192
```

Benchmark exports now use schema version 2 and persist the inference
configuration used for the run:

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

This makes model comparisons reproducible without relying on external
notes about the Ollama configuration.

The result is stored under:

``` text

results/diff/v11+maintainability_v1/
```

The current result is:

``` text

Benchmarks       21

Passed           20

Failed            1

Accuracy         95.24%

False positives   0

False negatives   1

Wrong rules       0

Severity         100%
```

**\### Export single-pass diff benchmark results**

``` bash

uv run python main.py benchmark-diff \\

    diff_benchmarks \\

    --model qwen3.5:9b \\

    --prompt-version v11 \\

    --output results/diff/v11/qwen3.5-9b.json
```

Cross-model runs can use the same suite and prompt:

``` bash

uv run python main.py benchmark-diff \\

    diff_benchmarks \\

    --model qwen2.5-coder:7b \\

    --prompt-version v11 \\

    --output results/diff/v11/qwen2.5-coder-7b.json
```

Diff results are stored separately from full-file results:

``` text

results/

├── v1/

├── v2/

├── ...

└── diff/

    ├── v9/

    ├── v10/

    ├── v11/

    │   ├── qwen3.5-9b.json

    │   ├── qwen2.5-coder-7b.json

    │   └── ...

    └── v11+maintainability_v1/

        └── qwen3.5-9b-specialized.json
```

Keeping diff results separate prevents fundamentally different benchmark
suites from being accidentally mixed.

**\### Compare aggregate benchmark results**

``` bash

uv run python main.py compare-results results/v5/
```

**\### Compare benchmark results by rule**

``` bash

uv run python main.py compare-results results/v5/ --by-rule
```

**\### Compare benchmark results by category**

``` bash

uv run python main.py compare-results results/v5/ --by-category
```

**\### Inspect an exported benchmark result**

``` bash

uv run python main.py analyze-result \\

    results/v5/qwen3.5-9b-seed42.json
```

**\### Compare two benchmark runs for regressions**

``` bash

uv run python main.py compare-runs \\

    results/diff/v9/qwen3.5-9b-expanded.json \\

    results/diff/v11/qwen3.5-9b.json
```

\*\*## Current Baselines

The project now distinguishes historical frozen checkpoints from the
expanded taxonomy evaluation.

``` text
FULL-FILE REVIEW

Model             qwen3.5:9b
Prompt            v5
Benchmarks        65
Passed            60
Accuracy          92.3%
Severity          100%


HISTORICAL SINGLE-PASS GIT-DIFF BASELINE

Model             qwen3.5:9b
Prompt            v11
LLM calls         1
Benchmarks        21
Passed            17
Accuracy          80.95%
False positives   0
False negatives   4
Wrong rules       0
Severity          100%


HISTORICAL SPECIALIZED GIT-DIFF DEVELOPMENT BASELINE

Model             qwen3.5:9b
Prompts           v11 + maintainability_v1
Context           4096
LLM calls         2
Benchmarks        21
Passed            20
Accuracy          95.24%
False positives   0
False negatives   1
Wrong rules       0
Severity          100%


HISTORICAL SPECIALIZED GENERALIZATION BASELINE

Model             qwen3.5:9b
Prompts           v11 + maintainability_v1
Context           4096
Benchmarks        20
Passed            16
Accuracy          80.00%
False positives   3
False negatives   1
Wrong rules       0
Severity          100%
Duration          81.17s


EXPANDED SPECIALIZED DEVELOPMENT

Model             qwen3.5:9b
Prompts           v13 + maintainability_v1
Context           4096
LLM calls         2
Benchmarks        49
Passed            45
Accuracy          91.84%
False positives   1
False negatives   2
Wrong rules       1
Errors            0
Severity          22/22 (100%)
Duration          192.08s


EXPANDED CONTEXT CHECK

Context           8192
Benchmarks        49
Passed            45
Accuracy          91.84%
Same failures     yes
Duration          208.46s


EXPERIMENTAL EXCESSIVE NESTING

Rule              excessive_nesting
Prompt experiment maintainability_v2
Benchmarks        4
Passed            2
Accuracy          50.00%
Status            experimental
```

The 21-case and 20-case v11 results remain frozen historical evidence.

The current stable expanded development architecture is:

``` text
qwen3.5:9b
+
v13 general reviewer
+
maintainability_v1 specialist
+
4096 context
+
deterministic rule ownership
```

with:

``` text
45/49
91.84%
```

The lower percentage relative to 20/21 does not represent a direct
regression: the taxonomy and benchmark suite have expanded
substantially.

Newer held-out rule families continue to be stored separately under
`diff_benchmarks_generalization/`.

Current targeted generalization evidence includes strong results for
`unsafe_deserialization` and `insecure_temp_file`, while
`hardcoded_secret`, `missing_none_check`, and
`repeated_expensive_call_in_loop` expose attribution, recognition, and
specialist-interaction weaknesses.

Future prompt changes should be motivated by repeated failure patterns
rather than individual benchmark cases.

The immediate next phase is to complete generalization coverage for the
new stable rules and decide how maintainability ownership should scale
before further taxonomy expansion.

## Project Goal\*\*

This project is primarily an AI engineering learning environment.

The objective is not only to produce useful code reviews, but to
understand the engineering behind LLM-based developer tools:

-   Structured LLM output

-   JSON Schema constrained generation

-   Prompt design and versioning

-   Deterministic generation

-   Evaluation datasets

-   False-positive and false-negative analysis

-   Model comparison

-   Cross-model evaluation

-   Prompt regression detection

-   Taxonomy design

-   Reproducible experimentation

-   Diff-aware code review

-   Change attribution

-   Context construction for LLM code analysis

-   Git branch comparison

-   Multi-pass LLM workflows

-   Specialist model calls

-   Deterministic aggregation

-   Task decomposition

-   Accuracy vs inference-cost tradeoffs

-   Local LLM inference

-   Evaluation design and failure classification

-   Development vs held-out generalization separation

-   Taxonomy-boundary evaluation

-   Recognition vs attribution failure analysis

-   Specialist ownership experiments

The reviewer is intentionally being developed incrementally so each new
capability can be evaluated before adding more complexity.
