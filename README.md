# AI Code Reviewer

A project to learn AI engineering by building a local AI-powered code
reviewer from scratch.

The goal is not just to call an LLM API, but to understand how modern
coding assistants are designed by implementing each component step by
step. Everything runs locally using open-weight models and Ollama.

The project emphasizes clean architecture, reproducible evaluation,
controlled prompt experimentation, structured LLM outputs, diff-aware
review, change attribution, model comparison, specialized multi-pass
review, held-out generalization testing, and local execution.

## Roadmap

### Completed

-   ✅ Review a single file
-   ✅ Review multiple files
-   ✅ Structured JSON output
-   ✅ Benchmark runner and automatic evaluation
-   ✅ Benchmark result export, comparison, and analysis
-   ✅ Rule and category comparison
-   ✅ Versioned prompt templates
-   ✅ Deterministic benchmark generation
-   ✅ Rule-based severity normalization
-   ✅ Controlled prompt optimization experiments
-   ✅ Cross-run regression comparison
-   ✅ Review local Git diffs
-   ✅ Diff review with current source context
-   ✅ Diff-specific benchmark format, discovery, runner, CLI,
    rendering, and export
-   ✅ Diff change-attribution experiments
-   ✅ Review committed branch changes against a base ref
-   ✅ Cross-model diff benchmark evaluation
-   ✅ Aggregate wrong-rule / rule-mismatch reporting
-   ✅ Structured Ollama output with JSON Schema
-   ✅ Multi-pass candidate generation and verification experiment
-   ✅ Maintainability-specialist prompt
-   ✅ General + specialist diff-review architecture
-   ✅ Deterministic rule ownership and review merging
-   ✅ Specialized diff benchmark CLI
-   ✅ Configurable Ollama context size
-   ✅ Persisted inference metadata in benchmark exports
-   ✅ Benchmark result schema v2
-   ✅ Context-size experiments at 4K / 8K / 16K
-   ✅ Larger MoE model evaluation with Gemma 4 26B and Qwen 3.5 35B-A3B
-   ✅ Separate development and held-out generalization suites
-   ✅ Frozen nine-rule generalization evaluation
-   ✅ Expanded v13 taxonomy development suite
-   ✅ Expanded 49-case development evaluation
-   ✅ Expanded 41-case held-out generalization evaluation
-   ✅ Development/generalization gap measured for the expanded
    architecture
-   ✅ Experimental `excessive_nesting` investigation

### Next

-   Investigate repeated failure patterns across the frozen development
    and generalization suites
-   Design and evaluate Architecture v2 without changing the frozen
    evaluation data
-   Revisit specialist ownership and specialist interference
-   Evaluate narrower/category specialists and verification strategies
-   Measure accuracy vs inference-cost tradeoffs across architectures
-   Evaluate realistic multi-file PRs and repository-scale diffs
-   Improve practical `review-pr` workflow and reporting
-   Add HTML reports
-   Explore more agentic repository-review behavior
-   Revisit LM Studio / alternative local runtimes where useful
-   Evaluate larger models on higher-VRAM hardware
-   Final evaluation, documentation, examples, limitations, and
    portfolio/release polish

## Current Features

-   Review individual Python files
-   Review Python projects recursively
-   Review local unstaged Git changes
-   Review committed branch changes against a base branch or commit
-   Combine Git diffs with current changed-file contents
-   Focus diff reviews on issues introduced or worsened by a change
-   Structured JSON responses
-   JSON Schema constrained Ollama generation
-   Response validation and parsing
-   Versioned prompt templates
-   Full-file benchmark execution
-   Diff-specific benchmark execution
-   Candidate-generation benchmark execution
-   Multi-pass diff benchmark execution
-   Specialized general + maintainability diff review
-   Deterministic specialist/general merging
-   Automatic benchmark evaluation
-   JSON result export
-   Aggregate, rule, category, prompt, and cross-run comparisons
-   False-positive, false-negative, and wrong-rule classification
-   Deterministic LLM generation
-   Rule-based severity normalization
-   Cross-model evaluation
-   Configurable inference context
-   Persisted inference metadata (`runtime`, `context_size`,
    `temperature`, `seed`)
-   Benchmark result schema v2
-   Separate development and held-out generalization families
-   Execution-failure rendering shared across benchmark modes

## Architecture

### Single-Pass Review

``` text
                         ┌── Python File ────────────────┐
                         │                               ↓
CLI ─────────────────────┤                    Review Prompt Builder
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

Git review supports both:

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

### Specialized Diff Review

The current stable expanded architecture preserves the two-call design
introduced during the original v11 experiments, but the general reviewer
has progressed to v13.

``` text
                         Git Diff
                            +
                     Current Source
                            │
             ┌──────────────┴──────────────┐
             │                             │
             ↓                             ↓
      General Reviewer           Maintainability Specialist
            v13                   maintainability_v1
             │                             │
             ↓                             ↓
 Bug / Security / Performance      duplicate_code
 + expanded general rules          long_function
             │                             │
             └──────────────┬──────────────┘
                            ↓
                 Deterministic Rule Ownership
                            +
                       Python Merge
                            ↓
                    Structured CodeReview
```

The architecture deliberately uses exactly two LLM calls. The merge is
deterministic Python logic; there is no third LLM merge call.

The current general reviewer owns non-maintainability rules including:

``` text
mutable_default_argument
unreachable_code
broad_exception_swallowing
missing_none_check
resource_leak

sql_injection
shell_injection
path_traversal
hardcoded_secret
unsafe_deserialization
insecure_temp_file

list_membership_in_loop
string_concatenation_in_loop
repeated_expensive_call_in_loop
```

The maintainability specialist owns:

``` text
duplicate_code
long_function
```

`excessive_nesting` remains experimental and is not part of the stable
taxonomy baseline.

If the general reviewer returns a specialist-owned rule, that finding is
discarded during deterministic merging and specialist ownership wins.

### Experimental Candidate / Verifier Pipeline

An earlier experiment used:

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

The verifier could remove unsupported candidates and preserve valid
findings, but it could not recover an issue that candidate generation
completely missed. This motivated complementary specialist detection
rather than verification alone.

## Evaluation Pipeline

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

Diff benchmarks add:

``` text
before.py + after.py + benchmark.json
        ↓
Generate Unified Diff
        +
Current after.py Source
        ↓
Diff Review
        ↓
Benchmark Evaluation
```

The project keeps Git integration, LLM execution, prompt construction,
benchmark loading, execution, evaluation, comparison, serialization, and
rendering separate so they can evolve independently.

## Benchmark Workflow

``` text
Review Code
      ↓
Run Development Benchmarks
      ↓
Export Results
      ↓
Inspect Failures / Compare Runs
      ↓
Change Prompt / Architecture / Taxonomy
      ↓
Re-run Development Evaluation
      ↓
Evaluate Frozen Held-Out Generalization
      ↓
Measure Generalization Gap
```

The held-out suite is intentionally not treated as prompt-training data.

## Full-File Benchmarks

The full-file suite contains 65 cases designed to test detection and
false-positive boundaries.

Current baseline:

``` text
Model             qwen3.5:9b
Prompt            v5
Benchmarks        65
Passed            60
Failed             5
Accuracy          92.31%
Severity          100%
```

The full-file taxonomy represents the original rule families:

  -----------------------------------------------------------------------
  Category                            Rules
  ----------------------------------- -----------------------------------
  Bug                                 Mutable default argument,
                                      Unreachable code

  Security                            SQL injection, Shell injection,
                                      Path traversal

  Performance                         List membership in loops, String
                                      concatenation in loops

  Maintainability                     Duplicate code, Long function
  -----------------------------------------------------------------------

`long_function` remains one of the weakest full-file rules. Targeted
prompt changes did not improve it, so further benchmark-specific tuning
was stopped.

## Diff Benchmarks

Each diff benchmark is represented by:

``` text
benchmark_case/
├── before.py
├── after.py
└── benchmark.json
```

The benchmark system generates the unified diff and sends both the diff
and current `after.py` source to the reviewer.

Diff evaluation asks a stricter question than full-file review:

> Did the change introduce or worsen the issue, or was the issue already
> present before the change?

This makes change attribution a first-class part of the benchmark.

## Historical Nine-Rule Checkpoints

The original 21-case development suite and 20-case held-out suite remain
frozen historical evidence.

### Single-pass v11

``` text
Model             qwen3.5:9b
Prompt            v11
LLM calls         1
Benchmarks        21
Passed            17
Accuracy          80.95%
False positives    0
False negatives    4
Wrong rules        0
Severity          100%
```

### Specialized v11 + maintainability_v1

``` text
Model             qwen3.5:9b
Prompts           v11 + maintainability_v1
Context           4096
LLM calls         2
Benchmarks        21
Passed            20
Accuracy          95.24%
False positives    0
False negatives    1
Wrong rules        0
Severity          100%
```

### Frozen nine-rule generalization

``` text
Model             qwen3.5:9b
Prompts           v11 + maintainability_v1
Context           4096
Benchmarks        20
Passed            16
Accuracy          80.00%
False positives    3
False negatives    1
Wrong rules        0
Severity          100%
Duration          81.17s
```

These results remain useful checkpoints, but they should not be compared
directly with the expanded v13 suite as though the taxonomy and data
were unchanged.

## Expanded v13 Development Evaluation

The stable expanded development suite contains 49 benchmarks across the
original families and newer rules.

Configuration:

``` text
Model                   qwen3.5:9b
General prompt          v13
Maintainability prompt  maintainability_v1
Context                 4096
Temperature             0
Seed                     42
Merge                    deterministic rule ownership
```

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
Duration         192.08s
```

Remaining development failures:

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

### Expanded context regression check

At 8192 context:

``` text
Benchmarks        49
Passed            45
Accuracy          91.84%
Same failures     yes
Duration          208.46s
```

No accuracy benefit was observed, so 4096 remains preferred.

## Expanded Held-Out Generalization Evaluation

The expanded held-out suite is stored separately under:

``` text
diff_benchmarks_generalization/
```

It now provides a complete evaluation checkpoint for the current stable
expanded architecture.

Configuration:

``` text
Model                   qwen3.5:9b
General prompt          v13
Maintainability prompt  maintainability_v1
Context                 4096
Temperature             0
Seed                     42
Merge                    deterministic rule ownership
```

Final expanded generalization result:

``` text
Benchmarks       41
Passed           33
Failed            8
Errors            0
False positives   5
False negatives   3
Wrong rules       0
Accuracy         80.49%
Severity         13/13 (100.00%)
Duration         158.06s
```

Comparison with the expanded development suite:

  Suite                       Cases   Passed   Accuracy   FP   FN   Wrong rules
  ------------------------- ------- -------- ---------- ---- ---- -------------
  Development                    49       45     91.84%    1    2             1
  Held-out generalization        41       33     80.49%    5    3             0

The expanded generalization gap is:

``` text
91.84% - 80.49% = 11.35 percentage points
```

This is now one of the most important results in the project: the
architecture remains strong on the development suite, but performance
drops materially on unseen manifestations and attribution boundaries.

### Expanded Generalization Failures

``` text
missing_none_check
└── optional session method call
    └── false negative
    └── recognition/generalization

mutable_default_argument
└── pre-existing mutable dict default
    └── false positive
    └── attribution

duplicate_code
└── pre-existing duplicate validation
    └── false positive
    └── attribution / specialist

long_function
└── introduced multi-responsibility growth
    └── false negative
    └── specialist recall

list_membership_in_loop safe attribution case
└── reported as long_function
    └── false positive
    └── specialist interference

repeated_expensive_call_in_loop pre-existing case
└── reported as long_function
    └── false positive
    └── specialist interference

string_concatenation_in_loop
└── introduced repeated concatenation
    └── false negative
    └── recognition/generalization

hardcoded_secret
└── pre-existing credential
    └── false positive
    └── attribution
```

The failures expose repeated classes rather than one isolated weak rule:

``` text
RECOGNITION / GENERALIZATION
├── missing_none_check
└── string_concatenation_in_loop

ATTRIBUTION
├── mutable_default_argument
└── hardcoded_secret

MAINTAINABILITY SPECIALIST RECALL
└── long_function

MAINTAINABILITY SPECIALIST PRECISION / INTERFERENCE
├── duplicate_code attribution
├── list_membership_in_loop safe case → long_function
└── repeated_expensive_call_in_loop pre-existing case → long_function
```

This is why the next step should be architecture analysis rather than
immediately editing prompts for eight individual examples.

## Experimental Excessive Nesting

`excessive_nesting` was explored as a possible maintainability
expansion.

Development family:

``` text
Benchmarks       4
Passed           2
Accuracy         50.00%
```

An experimental `maintainability_v2` prompt did not improve aggregate
performance. Candidate + verifier testing also remained 2/4 because
verification could remove unsupported candidates but could not invent
the missing rule.

The rule overlaps semantically with existing maintainability concepts
enough that ownership is unclear.

Status:

``` text
excessive_nesting
└── experimental
└── not part of the stable expanded baseline
```

It should not block the completed expanded-generalization milestone.

## Prompt Evolution

The important historical progression is:

``` text
v9
15/21
71.43%
3 FP / 3 FN

v10
15/21
71.43%
2 FP / 4 FN

v11
17/21
80.95%
0 FP / 4 FN
```

v11 fixed the major attribution failures by requiring the reviewer to
identify the triggering code and compare it before and after the diff.

The central rule became:

``` text
triggering code unchanged
+
diff changes unrelated surrounding behavior
↓
pre-existing issue
↓
do not report
```

Maintainability remained weak under the general prompt, motivating
`maintainability_v1`.

Taxonomy expansion later progressed the general prompt through v12 to
the current stable v13.

## Maintainability Specialization

The focused specialist recovered both `duplicate_code` positives missed
by v11 and one of the two `long_function` positives.

Historical specialist candidate results:

``` text
duplicate_code
3/3
100%

long_function
2/3
66.67%
```

This produced the two-call architecture and demonstrated that task
decomposition can improve reviewer behavior without changing the model.

The expanded generalization suite now shows the other side of this
tradeoff: the specialist can also create cross-rule false positives,
especially `long_function` findings on safe or pre-existing
non-maintainability cases.

This specialist interference is a primary Architecture v2 research
target.

## Cross-Model Evaluation

Historical single-pass v11 results:

  Model                        Passed     Accuracy   False Positives   False Negatives
  ----------------------- ----------- ------------ ----------------- -----------------
  **Qwen 3.5 9B**           **17/21**   **80.95%**             **0**                 4
  Qwen 2.5 Coder 7B             15/21       71.43%             **0**                 6
  Qwen 2.5 Coder 14B            13/21       61.90%                 4                 4
  Gemma 3 12B                   13/21       61.90%                 4                 4
  Llama 3.1 8B                   5/21       23.81%                10               0\*
  DeepSeek Coder V2 16B          3/21       14.29%                10               0\*

`*` The apparent zero false-negative count for the weakest models was
misleading because they frequently selected the wrong supported rule.
This motivated explicit wrong-rule tracking.

## Context-Size and Larger-Model Experiments

Historical specialized 21-case context test:

     Context      Passed     Accuracy      FP      FN     Duration
  ---------- ----------- ------------ ------- ------- ------------
    **4096**   **20/21**   **95.24%**   **0**   **1**   **81.58s**
        8192       18/21       85.71%       0       3       88.09s
       16384       18/21       85.71%       0       3       87.88s

Larger models at 4K on the same historical suite:

  --------------------------------------------------------------------------------
  Model          Passed     Accuracy         FP         FN      Wrong     Duration
  --------- ----------- ------------ ---------- ---------- ---------- ------------
  **Qwen      **20/21**   **95.24%**      **0**          1          0   **81.58s**
  3.5 9B**                                                            

  Gemma 4         17/21       80.95%          4      **0**          0      146.98s
  26B                                                                 

  Qwen 3.5        16/21       76.19%          5      **0**          0      199.46s
  35B-A3B                                                             
  --------------------------------------------------------------------------------

The larger models showed stronger positive recognition but weaker change
attribution and required CPU offload on the RX 6700 XT.

The project therefore keeps the practical lesson:

``` text
larger model ≠ better diff reviewer
larger context ≠ better diff reviewer
```

## Prompt Templates

Prompt templates are versioned independently from application code.

Representative structure:

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
├── v12/
│   └── diff.txt
├── v13/
│   └── diff.txt
├── multipass_v1/
│   └── diff_candidates.txt
├── maintainability_v1/
│   ├── diff_candidates.txt
│   └── diff_verify.txt
└── maintainability_v2/
    └── ...
```

Current important prompt baselines:

``` text
Full-file review                  v5
Historical single-pass diff       v11
Historical specialized diff       v11 + maintainability_v1
Expanded specialized diff         v13 + maintainability_v1
```

Old prompt versions remain frozen for reproducibility.

## Cross-Run Regression Comparison

`compare-runs` compares two exports benchmark by benchmark and reports:

-   Fixed
-   Regressed
-   Still failing
-   Added
-   Removed

Example:

``` bash
uv run python main.py compare-runs \
    results/diff/v9/qwen3.5-9b-expanded.json \
    results/diff/v11/qwen3.5-9b.json
```

This is complementary to `compare-results`, which compares aggregate
performance.

## Tech Stack

-   Python 3.14
-   uv
-   Typer
-   Rich
-   pytest
-   Ruff
-   Ollama
-   Local open-weight LLMs

## Test Environment

-   AMD Ryzen 5 5600X
-   AMD Radeon RX 6700 XT --- 12 GB VRAM
-   32 GB system RAM
-   Arch Linux

## Run

Show commands:

``` bash
uv run python main.py --help
```

Review a file:

``` bash
uv run python main.py review examples/user_lookup.py
```

Review a folder:

``` bash
uv run python main.py review-folder examples
```

Review current Git changes:

``` bash
uv run python main.py review-diff \
    --model qwen3.5:9b \
    --prompt-version v13
```

Review committed branch changes:

``` bash
uv run python main.py review-pr \
    --base main \
    --model qwen3.5:9b
```

Run full-file benchmarks:

``` bash
uv run python main.py benchmark benchmarks/ \
    --model qwen3.5:9b \
    --prompt-version v5
```

Run a single-pass diff benchmark:

``` bash
uv run python main.py benchmark-diff \
    diff_benchmarks \
    --model qwen3.5:9b \
    --prompt-version v13
```

Run the specialized development suite:

``` bash
uv run python main.py benchmark-diff-specialized \
    diff_benchmarks \
    --model qwen3.5:9b \
    --prompt-version v13 \
    --context-size 4096
```

Run the frozen expanded generalization suite:

``` bash
uv run python main.py benchmark-diff-specialized \
    diff_benchmarks_generalization \
    --model qwen3.5:9b \
    --prompt-version v13 \
    --context-size 4096
```

Run maintainability candidates:

``` bash
uv run python main.py benchmark-diff-candidates \
    diff_benchmarks/maintainability/duplicate_code \
    --model qwen3.5:9b \
    --prompt-version maintainability_v1
```

Run candidate + verifier:

``` bash
uv run python main.py benchmark-diff-multi-pass \
    diff_benchmarks/maintainability/duplicate_code \
    --model qwen3.5:9b \
    --prompt-version maintainability_v1
```

Compare results:

``` bash
uv run python main.py compare-results results/v5/
uv run python main.py compare-results results/v5/ --by-rule
uv run python main.py compare-results results/v5/ --by-category
```

Analyze an exported result:

``` bash
uv run python main.py analyze-result results/v5/qwen3.5-9b-seed42.json
```

## Current Baselines

``` text
FULL-FILE REVIEW
qwen3.5:9b
v5
60/65
92.31%


HISTORICAL SINGLE-PASS DIFF
qwen3.5:9b
v11
17/21
80.95%


HISTORICAL SPECIALIZED DIFF DEVELOPMENT
qwen3.5:9b
v11 + maintainability_v1
20/21
95.24%


HISTORICAL SPECIALIZED DIFF GENERALIZATION
qwen3.5:9b
v11 + maintainability_v1
16/20
80.00%


EXPANDED SPECIALIZED DEVELOPMENT
qwen3.5:9b
v13 + maintainability_v1
context 4096
45/49
91.84%
1 FP / 2 FN / 1 wrong
severity 100%


EXPANDED HELD-OUT GENERALIZATION
qwen3.5:9b
v13 + maintainability_v1
context 4096
33/41
80.49%
5 FP / 3 FN / 0 wrong
severity 100%


EXPANDED GENERALIZATION GAP
11.35 percentage points


EXPERIMENTAL EXCESSIVE NESTING
maintainability_v2
2/4
50.00%
not part of stable baseline
```

The 49-case development suite and 41-case generalization suite are now
the frozen evidence base for the next architecture phase.

Future architecture changes should be evaluated against these suites
rather than changing benchmark cases to match the new design.

## Next Project Phase: Architecture v2

The immediate question is no longer "which benchmark case should we add
next?"

It is:

> Can the architecture reduce repeated recognition, attribution, and
> specialist-interference failures without overfitting to the frozen
> benchmarks?

Likely investigation areas include:

1.  specialist ownership boundaries;
2.  narrower category/rule specialists;
3.  whether maintainability should inspect every diff;
4.  verification or gating of specialist findings;
5.  cross-rule conflict handling;
6.  candidate generation vs complementary detection;
7.  latency and call-count tradeoffs;
8.  behavior on larger realistic PRs.

After Architecture v2, the project should move toward real-world PR
evaluation, HTML/reporting, repository-scale usability, and eventually
more agentic review behavior.

## Project Goal

This project is primarily an AI engineering learning environment.

The objective is not only to produce useful code reviews, but to
understand:

-   Structured LLM output
-   JSON Schema constrained generation
-   Prompt design and versioning
-   Deterministic generation
-   Evaluation datasets
-   False-positive and false-negative analysis
-   Wrong-rule analysis
-   Model comparison
-   Cross-model evaluation
-   Prompt regression detection
-   Taxonomy design
-   Reproducible experimentation
-   Diff-aware code review
-   Change attribution
-   Context construction
-   Git branch comparison
-   Multi-pass LLM workflows
-   Specialist model calls
-   Deterministic aggregation
-   Task decomposition
-   Accuracy vs inference-cost tradeoffs
-   Local LLM inference
-   Development vs held-out generalization
-   Recognition vs attribution failure analysis
-   Specialist ownership and interference
-   Architecture evaluation on frozen data
-   Real-world repository review
-   Practical reporting and eventual agentic workflows

The reviewer is intentionally developed incrementally so each capability
can be evaluated before adding more complexity.
