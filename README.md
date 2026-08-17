# AI Code Reviewer

A project to learn AI engineering by building a local AI-powered code reviewer from scratch.

The goal isn't just to call an LLM API, but to understand how modern coding assistants are designed by implementing each component step by step. Everything runs locally using open-weight models and Ollama.

The project emphasizes clean architecture, reproducible evaluation, controlled prompt experimentation, structured LLM outputs, diff-aware review, change attribution, model comparison, specialized multi-pass review, and local execution.

## Roadmap

### Completed

- ✅ Review a single file
- ✅ Review multiple files
- ✅ Structured JSON output
- ✅ Benchmark runner
- ✅ Benchmark evaluation
- ✅ Benchmark result export
- ✅ Benchmark result comparison
- ✅ Rule comparison
- ✅ Category comparison
- ✅ Versioned prompt templates
- ✅ Benchmark result analysis
- ✅ Deterministic benchmark generation
- ✅ Rule-based severity normalization
- ✅ Controlled prompt optimization experiments
- ✅ Cross-run regression comparison
- ✅ Review local Git diffs
- ✅ Diff review with current source context
- ✅ Diff-specific benchmark format
- ✅ Diff benchmark discovery and loading
- ✅ Diff benchmark runner
- ✅ Diff benchmark CLI
- ✅ Diff benchmark result rendering
- ✅ Diff benchmark result export
- ✅ Diff benchmark coverage across all current taxonomy rules
- ✅ Diff change-attribution experiments
- ✅ Cross-run comparison for diff benchmarks
- ✅ Review committed branch changes against a base ref
- ✅ Cross-model diff benchmark evaluation
- ✅ Aggregate wrong-rule / rule-mismatch reporting
- ✅ Structured Ollama output with JSON Schema
- ✅ Multi-pass candidate generation and verification experiment
- ✅ Maintainability-specialist prompt
- ✅ General + specialist diff-review architecture
- ✅ Deterministic rule ownership and review merging
- ✅ Specialized diff benchmark CLI

### Planned

- Continue benchmark and taxonomy expansion where useful
- Evaluate category-specialist review architecture
- Measure accuracy vs inference-cost tradeoffs across review architectures
- Evaluate larger local models on higher-VRAM hardware
- HTML reports

## Current Features

- Review individual Python files
- Review entire Python projects recursively
- Review local unstaged Git changes
- Review committed branch changes against a base branch or commit
- Combine Git diffs with current changed-file contents for contextual review
- Focus diff reviews on issues introduced or worsened by a change
- Structured JSON responses from the LLM
- JSON Schema constrained Ollama generation
- Response validation and parsing
- Versioned prompt templates
- Full-file benchmark execution
- Diff-specific benchmark execution
- Candidate-generation benchmark execution
- Multi-pass diff benchmark execution
- Specialized general + maintainability diff review
- Deterministic merging of specialist and general findings
- Automatic benchmark evaluation
- JSON export of full-file and diff benchmark results
- Compare aggregate benchmark results
- Compare models by rule
- Compare models by category
- Compare prompt versions
- Inspect benchmark failures and severity mismatches
- Compare individual benchmark behavior between two runs
- Cross-run comparison for both full-file and diff benchmarks
- Detect fixed and regressed benchmark cases
- Detect benchmarks that remain failing
- Detect added and removed benchmark cases
- Deterministic LLM generation for reproducible experiments
- Rule-based severity normalization
- Controlled prompt optimization and comparison
- Cross-model diff evaluation
- Local execution with Ollama

## Architecture

The reviewer supports full-file review, working-tree diff review, committed branch comparison, and specialized diff review while sharing the same LLM, parsing, normalization, and structured review infrastructure.

### Single-Pass Review

```text
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

```text
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

### Specialized Diff Review

Experiments with the 21-case diff benchmark showed that the general v11 prompt performed well on bug, security, performance, and change attribution, while its remaining failures were concentrated entirely in maintainability rules.

Rather than continuing to enlarge the general prompt, the reviewer now supports a specialized two-call architecture:

```text
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

The general v11 reviewer remains responsible for:

```text
sql_injection
shell_injection
path_traversal
mutable_default_argument
unreachable_code
list_membership_in_loop
string_concatenation_in_loop
```

The maintainability specialist owns:

```text
duplicate_code
long_function
```

If the general reviewer also returns one of the specialist-owned rules, that finding is discarded during the deterministic merge and the specialist result is used instead.

No additional LLM call is used for merging.

This prevents duplicate findings and makes rule ownership explicit and reproducible.

### Experimental Candidate / Verifier Pipeline

Before the specialized architecture was introduced, a candidate-generation and verification pipeline was also implemented:

```text
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

This experiment demonstrated that a second verification pass could preserve valid maintainability findings without introducing false positives.

However, the architecture still depended on the candidate pass discovering an issue first. A verifier cannot recover an issue that candidate generation completely misses.

This motivated the current general + specialist architecture, where the second call performs complementary detection rather than only verification.

### Evaluation Pipeline

All review modes can continue through the evaluation pipeline:

```text
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

```text
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

```text
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

The application keeps Git integration, LLM execution, prompt construction, benchmark loading, benchmark execution, evaluation, experiment comparison, serialization, and CLI rendering separate so each part can be tested and evolved independently.

## Benchmark Workflow

The benchmarking workflow is designed to support iterative prompt engineering, model evaluation, and architecture experiments.

```text
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

This makes prompt, model, and architecture experiments measurable and reproducible rather than relying on subjective impressions.

Aggregate metrics show whether a run improved overall, while cross-run comparison shows exactly which benchmark cases changed.

## Full-File Benchmarks

The project currently contains a **65-case full-file benchmark suite** designed to test both detection ability and false-positive boundaries.

Benchmarks are deliberately built from positive, negative, and boundary cases rather than only obvious examples.

Each full-file benchmark contains:

- A Python source file
- The expected findings
- Expected rule, category, and severity
- Automatic evaluation against the model response
- False-positive and false-negative detection

Current benchmark categories and rules include:

| Category | Rules |
| --- | --- |
| Bug | Mutable default argument, Unreachable code |
| Security | SQL injection, Shell injection, Path traversal |
| Performance | List membership in loops, String concatenation in loops |
| Maintainability | Duplicate code, Long function |

Safe and boundary cases are included throughout the rule families to measure false positives.

Examples include parameterized SQL queries, allowlisted paths and commands, immutable default arguments, set and dictionary membership, `join()`-based string construction, shared helper functions, and valid control flow.

The current Qwen 3.5 9B full-file baseline uses prompt v5:

```text
Benchmarks         65
Passed             60
Failed              5
Accuracy           92.3%
Severity accuracy 100.0%
```

`long_function` remains one of the weakest full-file rules.

A targeted prompt investigation tested increasingly explicit responsibility definitions but did not improve detection. Further tuning of that rule was paused to avoid benchmark-specific overfitting.

## Diff Benchmarks

Git-diff review has a separate benchmark format because evaluating a change is different from evaluating a complete source file.

A diff benchmark is represented by a directory containing:

```text
benchmark_case/
├── before.py
├── after.py
└── benchmark.json
```

`before.py` represents the code before the change.

`after.py` represents the current source after the change.

The benchmark system generates the diff between the two versions and sends both the generated diff and the current `after.py` source to the diff reviewer.

`benchmark.json` defines the expected issues introduced by the change.

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

Diff benchmarks test more than whether the model can recognize a problem.

They also test **change attribution**:

> Did the diff introduce or worsen the issue, or was the issue already present before the change?

A useful diff reviewer should not report every problem visible in the current file. It should focus on problems caused by the proposed change.

### Current Diff Benchmark Suite

The suite has expanded from the original 11 cases to **21 cases covering all nine rules in the current taxonomy**.

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

The suite includes:

- introduced issues
- safe changes
- pre-existing issues
- changes affecting unchanged code
- stronger diagnostic maintainability cases

Examples include:

```text
dict → list
→ introduces expensive membership checks
→ report the performance issue

pre-existing list membership + local rename
→ issue existed before the diff
→ report nothing

None default → []
→ introduces mutable default argument
→ report the bug

pre-existing mutable default + local rename
→ issue existed before the diff
→ report nothing

parameterized SQL → interpolated SQL
→ introduces SQL injection
→ report the security issue

pre-existing SQL injection + unrelated logging change
→ vulnerable SQL construction is unchanged
→ report nothing
```

## Diff Prompt Evolution

The first expanded baseline used prompt v9:

```text
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

Prompt v10 tested stronger generic before/after attribution instructions:

```text
Prompt           v10
Benchmarks       21
Passed           15
Failed            6
False positives   2
False negatives   4
Accuracy         71.43%
Severity          7/7 (100.00%)
```

v10 fixed pre-existing mutable-default attribution but continued to misattribute pre-existing SQL and shell injection.

It also regressed a strong `duplicate_code` case.

Prompt v11 instead uses more concrete attribution guidance.

Before reporting a finding, the model is instructed to identify the actual triggering code and compare it between the previous and current versions.

The central attribution rule is:

```text
triggering code unchanged
        +
diff changes unrelated surrounding behavior
        ↓
pre-existing issue
        ↓
do not report
```

This successfully fixed the remaining security attribution cases.

### Single-Pass v11 Baseline

Qwen 3.5 9B with prompt v11 produces:

```text
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

| Prompt | Passed | Accuracy | False Positives | False Negatives |
| --- | ---: | ---: | ---: | ---: |
| v9 | 15/21 | 71.43% | 3 | 3 |
| v10 | 15/21 | 71.43% | 2 | 4 |
| **v11** | **17/21** | **80.95%** | **0** | **4** |

Compared with v9, v11 fixes:

```text
pre-existing mutable_default_argument
pre-existing shell_injection
pre-existing sql_injection
```

and regresses:

```text
strong duplicate_code positive
```

The four remaining false negatives are:

```text
duplicate_code positive
duplicate_code strong positive
long_function positive
long_function strong positive
```

All current pre-existing attribution boundary cases pass under v11.

The remaining weaknesses are therefore concentrated in maintainability-rule recognition rather than change attribution.

## Maintainability Specialization Experiment

The concentration of all four v11 failures in maintainability motivated an experiment with task specialization rather than further expansion of the general prompt.

A dedicated `maintainability_v1` candidate prompt was created for only:

```text
duplicate_code
long_function
```

This reduced the number of competing rules and allowed the model to focus on structural maintainability reasoning.

Candidate-generation results were:

### Duplicate Code

```text
Benchmarks       3
Passed            3
Failed            0
False positives   0
False negatives   0
Accuracy         100.00%
Severity          2/2 (100.00%)
```

### Long Function

```text
Benchmarks       3
Passed            2
Failed            1
False positives   0
False negatives   1
Accuracy         66.67%
Severity          1/1 (100.00%)
```

The focused prompt therefore recovered both `duplicate_code` cases missed by v11 and one of the two `long_function` positives.

A candidate-generation + verifier experiment was then tested.

The verifier preserved the specialist findings:

```text
duplicate_code
3/3
100%

long_function
2/3
66.67%
```

However, verification could not recover issues missed by candidate generation.

This led to the current specialized architecture.

## Specialized Two-Call Diff Review

The strongest current diff-review architecture combines:

```text
Call 1
v11 general reviewer

+

Call 2
maintainability_v1 specialist

+

deterministic Python merge
```

The complete 21-case benchmark produces:

```text
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

| Architecture | Calls | Passed | Accuracy | FP | FN | Wrong Rules |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v11 single-pass | 1 | 17/21 | 80.95% | 0 | 4 | 0 |
| **v11 + maintainability specialist** | **2** | **20/21** | **95.24%** | **0** | **1** | **0** |

The specialized architecture recovers:

```text
duplicate_code positive
duplicate_code strong positive
long_function strong positive
```

while preserving all previously passing bug, security, performance, safe-change, and pre-existing attribution cases.

The only remaining false negative is:

```text
Adding multiple responsibilities introduces long function
```

The experiment provides evidence that, for the current local model and taxonomy:

```text
task specialization
        ↓
higher maintainability recall
        ↓
without increasing false positives
```

The result also introduces an explicit accuracy/latency tradeoff.

The specialized architecture requires two model calls instead of one, increasing inference time in exchange for substantially higher benchmark accuracy.

This is now an architecture-level experiment rather than only a prompt-engineering experiment.

## Cross-Model Diff Evaluation

Before specialized review was introduced, the complete 21-case suite was evaluated across the local models already used by the project using the same single-pass v11 prompt.

The benchmark suite, prompt, deterministic generation settings, and evaluator were kept fixed. Only the model changed.

| Model | Passed | Accuracy | False Positives | False Negatives |
| --- | ---: | ---: | ---: | ---: |
| **Qwen 3.5 9B** | **17/21** | **80.95%** | **0** | 4 |
| Qwen 2.5 Coder 7B | 15/21 | 71.43% | **0** | 6 |
| Qwen 2.5 Coder 14B | 13/21 | 61.90% | 4 | 4 |
| Gemma 3 12B | 13/21 | 61.90% | 4 | 4 |
| Llama 3.1 8B | 5/21 | 23.81% | 10 | 0* |
| DeepSeek Coder V2 16B | 3/21 | 14.29% | 10 | 0* |

`*` The zero false-negative count for Llama 3.1 8B and DeepSeek Coder V2 16B should not be interpreted as strong recall.

Both models frequently produce a finding using the wrong taxonomy rule rather than returning no issue.

### Cross-Model Findings

Qwen 3.5 9B remains the strongest current model for the project.

Under the frozen single-pass v11 architecture:

```text
17/21
80.95%
0 false positives
0 wrong rules
```

Qwen 2.5 Coder 7B also maintains zero false positives but misses two additional introduced performance issues.

Qwen 2.5 Coder 14B and Gemma 3 12B recover some findings but introduce more attribution failures.

Llama 3.1 8B and DeepSeek Coder V2 16B show substantial constrained-taxonomy rule-selection instability.

The experiment also provided stronger evidence about the maintainability failures.

Among the models with reasonably stable taxonomy behavior:

```text
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

The two results for each rule represent the normal and stronger positive cases.

The weakness was therefore not unique to Qwen 3.5 9B.

The later maintainability-specialist experiment showed that changing the **task decomposition** could recover these findings without changing the model.

This is an important result:

```text
model capability
        +
task decomposition
        +
prompt scope
        ↓
review performance
```

Model size alone is not sufficient to predict reviewer quality.

## DeepSeek Rule-Mismatch Validation

DeepSeek Coder V2 16B was rerun after aggregate rule-mismatch reporting was added.

```text
Benchmarks       21
Passed            3
Failed           18
False positives  10
False negatives   0
Wrong rules       6
Accuracy         14.29%
```

The six wrong-rule cases make the model's taxonomy-selection instability explicit.

Examples include:

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

The Wrong rules metric therefore distinguishes models that completely miss an expected issue from models that detect something but classify it under the wrong supported rule.

## Prompt Templates

Prompt templates are versioned independently from the application code.

Different review modes and experimental architectures can use separate templates:

```text
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

General diff-review prompts use both the Git diff and the current contents of changed Python files.

The diff identifies what changed, while the current source provides the context needed to reason about the behavior of the new version.

The maintainability specialist receives the same diff/current-source representation but uses a narrower rule scope.

The current baselines are:

```text
Full-file review             v5
Single-pass Git-diff review  v11
Specialized Git-diff review  v11 + maintainability_v1
```

Existing prompt versions remain frozen so previous experiments can be reproduced and compared.

## Prompt Evaluation

Prompt changes are evaluated against benchmark suites using controlled generation settings.

Early Qwen 3.5 9B experiments on the original 35-case full-file benchmark suite produced:

| Prompt | Accuracy | Passed | False Positives | False Negatives |
| --- | ---: | ---: | ---: | ---: |
| v1 | 85.7% | 30/35 | 4 | 1 |
| v2 | 88.6% | 31/35 | 3 | 1 |
| v3 | 88.6% | 31/35 | 3 | 1 |
| v4 | 91.4% | 32/35 | 2 | 1 |

The full-file suite was subsequently expanded from 35 to 65 cases.

Prompt v5 currently produces:

```text
Benchmarks         65
Passed             60
Failed              5
Accuracy           92.3%
Severity accuracy 100.0%
```

Diff prompt experiments are evaluated independently.

Single-pass v11 produces:

```text
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

```text
Benchmarks         21
Passed             20
Failed              1
Accuracy           95.24%
False positives     0
False negatives     1
Wrong rules         0
Severity accuracy 100.0%
```

Severity is normalized deterministically from the detected rule instead of trusting the severity generated by the LLM.

## Cross-Run Regression Comparison

Aggregate accuracy can hide important behavior changes.

The `compare-runs` command compares two exported benchmark runs at the individual benchmark level.

It supports both full-file and diff benchmark results.

Full-file example:

```bash
uv run python main.py compare-runs \
    results/v4/qwen3.5-9b-seed42-block5.json \
    results/v5/qwen3.5-9b-seed42-block5.json
```

Diff example:

```bash
uv run python main.py compare-runs \
    results/diff/v9/qwen3.5-9b-expanded.json \
    results/diff/v11/qwen3.5-9b.json
```

The comparison reports:

- **Fixed** — failed in the old run and passes in the new run
- **Regressed** — passed in the old run and fails in the new run
- **Still failing** — fails in both runs
- **Added** — exists only in the new benchmark run
- **Removed** — exists only in the old benchmark run

The v9 → v11 diff comparison produced:

```text
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

This makes prompt regressions visible even when aggregate benchmark accuracy improves.

### `compare-results` vs `compare-runs`

The two commands answer different questions:

- `compare-results` compares aggregate performance across benchmark result files.
- `compare-runs` compares benchmark-by-benchmark changes between two specific runs.

Wrong-rule predictions are also represented explicitly in aggregate benchmark summaries, making taxonomy-selection failures distinguishable from ordinary false negatives.

## Models

The project focuses primarily on models that can run locally on consumer hardware with 12 GB of VRAM.

Single-pass diff benchmark results using the same v11 prompt are:

| Model | Diff Accuracy | Notes |
| --- | ---: | --- |
| **Qwen 3.5 9B** | **80.95%** | Current main model; 0 FP, 0 wrong rules |
| Qwen 2.5 Coder 7B | 71.43% | 0 FP, lower recall |
| Qwen 2.5 Coder 14B | 61.90% | More attribution failures |
| Gemma 3 12B | 61.90% | Moderate result, attribution failures |
| Llama 3.1 8B | 23.81% | Unstable constrained-rule selection |
| DeepSeek Coder V2 16B | 14.29% | Unstable constrained-rule selection |

Qwen 3.5 9B remains the preferred model for the current local reviewer.

The same model reaches **95.24%** on the current 21-case diff suite when used with the specialized two-call architecture.

This distinction is important: model quality and review architecture are evaluated separately.

Larger models may be evaluated in the future on machines with more VRAM using the same frozen benchmark suite and prompts, allowing direct comparison with the current baselines.

## Tech Stack

- Python 3.14
- uv
- Typer
- Rich
- pytest
- Ruff
- Ollama
- Local open-weight LLMs

## Test Environment

- AMD Radeon RX 6700 XT (12 GB VRAM)
- Arch Linux

## Run

### Show available commands

```bash
uv run python main.py --help
```

### Review a single file

```bash
uv run python main.py review examples/user_lookup.py
```

### Review an entire folder

```bash
uv run python main.py review-folder examples
```

### Review current Git changes

Review the current unstaged Git diff:

```bash
uv run python main.py review-diff \
    --model qwen3.5:9b \
    --prompt-version v11
```

The diff reviewer combines the Git diff with the current contents of changed Python files.

This allows the model to detect issues introduced indirectly by a change, including cases where the affected line itself was not modified.

### Review committed branch changes

Review the committed changes between a base branch or commit and `HEAD`:

```bash
uv run python main.py review-pr \
    --base main \
    --model qwen3.5:9b
```

Internally this reviews:

```text
git diff main...HEAD
```

The command reuses the existing v11 diff-review pipeline.

### Run the full-file benchmark suite

```bash
uv run python main.py benchmark benchmarks/
```

### Benchmark using a different model

```bash
uv run python main.py benchmark benchmarks/ \
    --model qwen2.5-coder:14b
```

### Benchmark using a specific prompt version

```bash
uv run python main.py benchmark benchmarks/ \
    --model qwen3.5:9b \
    --prompt-version v5
```

### Export full-file benchmark results

```bash
uv run python main.py benchmark benchmarks/ \
    --model qwen3.5:9b \
    --prompt-version v5 \
    --output qwen3.5-9b-seed42.json
```

### Run the single-pass diff benchmark suite

```bash
uv run python main.py benchmark-diff \
    diff_benchmarks \
    --model qwen3.5:9b \
    --prompt-version v11
```

A specific rule family can also be evaluated independently:

```bash
uv run python main.py benchmark-diff \
    diff_benchmarks/security/sql_injection \
    --model qwen3.5:9b \
    --prompt-version v11
```

### Run maintainability candidate benchmarks

```bash
uv run python main.py benchmark-diff-candidates \
    diff_benchmarks/maintainability/duplicate_code \
    --model qwen3.5:9b \
    --prompt-version maintainability_v1
```

### Run candidate + verifier benchmarks

```bash
uv run python main.py benchmark-diff-multi-pass \
    diff_benchmarks/maintainability/duplicate_code \
    --model qwen3.5:9b \
    --prompt-version maintainability_v1
```

### Run the specialized diff benchmark

Run the general v11 reviewer and maintainability specialist together:

```bash
uv run python main.py benchmark-diff-specialized \
    diff_benchmarks \
    --model qwen3.5:9b \
    --output qwen3.5-9b-specialized.json
```

The result is stored under:

```text
results/diff/v11+maintainability_v1/
```

The current result is:

```text
Benchmarks       21
Passed           20
Failed            1
Accuracy         95.24%
False positives   0
False negatives   1
Wrong rules       0
Severity         100%
```

### Export single-pass diff benchmark results

```bash
uv run python main.py benchmark-diff \
    diff_benchmarks \
    --model qwen3.5:9b \
    --prompt-version v11 \
    --output results/diff/v11/qwen3.5-9b.json
```

Cross-model runs can use the same suite and prompt:

```bash
uv run python main.py benchmark-diff \
    diff_benchmarks \
    --model qwen2.5-coder:7b \
    --prompt-version v11 \
    --output results/diff/v11/qwen2.5-coder-7b.json
```

Diff results are stored separately from full-file results:

```text
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

Keeping diff results separate prevents fundamentally different benchmark suites from being accidentally mixed.

### Compare aggregate benchmark results

```bash
uv run python main.py compare-results results/v5/
```

### Compare benchmark results by rule

```bash
uv run python main.py compare-results results/v5/ --by-rule
```

### Compare benchmark results by category

```bash
uv run python main.py compare-results results/v5/ --by-category
```

### Inspect an exported benchmark result

```bash
uv run python main.py analyze-result \
    results/v5/qwen3.5-9b-seed42.json
```

### Compare two benchmark runs for regressions

```bash
uv run python main.py compare-runs \
    results/diff/v9/qwen3.5-9b-expanded.json \
    results/diff/v11/qwen3.5-9b.json
```

## Current Baselines

The current experimental baselines are:

```text
FULL-FILE REVIEW

Model             qwen3.5:9b
Prompt            v5
Benchmarks        65
Passed            60
Accuracy          92.3%
Severity          100%


SINGLE-PASS GIT-DIFF REVIEW

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


SPECIALIZED GIT-DIFF REVIEW

Model             qwen3.5:9b
Prompts           v11 + maintainability_v1
LLM calls         2
Benchmarks        21
Passed            20
Accuracy          95.24%
False positives   0
False negatives   1
Wrong rules       0
Severity          100%
Duration          81.12s
```

The only remaining specialized diff-review failure is:

```text
long_function
```

specifically the weaker:

```text
Adding multiple responsibilities introduces long function
```

The current evidence suggests that task specialization can substantially improve maintainability recall without increasing false positives.

The next architectural question is whether broader category specialization can provide additional gains worth the increased inference cost.

## Project Goal

This project is primarily an AI engineering learning environment.

The objective is not only to produce useful code reviews, but to understand the engineering behind LLM-based developer tools:

- Structured LLM output
- JSON Schema constrained generation
- Prompt design and versioning
- Deterministic generation
- Evaluation datasets
- False-positive and false-negative analysis
- Model comparison
- Cross-model evaluation
- Prompt regression detection
- Taxonomy design
- Reproducible experimentation
- Diff-aware code review
- Change attribution
- Context construction for LLM code analysis
- Git branch comparison
- Multi-pass LLM workflows
- Specialist model calls
- Deterministic aggregation
- Task decomposition
- Accuracy vs inference-cost tradeoffs
- Local LLM inference
- Evaluation design and failure classification

The reviewer is intentionally being developed incrementally so each new capability can be evaluated before adding more complexity.