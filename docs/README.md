## Results

The benchmark suite has grown incrementally as the reviewer and taxonomy have evolved.

The initial experiments used a **35-case benchmark suite**. The current suite contains **65 benchmark cases**, including positive, negative, and boundary cases across security, bugs, maintainability, and performance rules.

Results from different stages should not always be compared directly because the benchmark suite, prompt, generation settings, and severity evaluation strategy have evolved over time.

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

After the initial prompt experiments, the benchmark suite was expanded incrementally from **35 to 65 cases**.

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

The current Qwen 3.5 9B result on the **65-case benchmark suite** is:

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

The two `long_function` cases indicate that maintainability detection remains the clearest weak area in the current prompt.

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

### Result Analysis

The project provides three complementary ways to analyze exported benchmark results.

#### Aggregate comparison

Compare multiple benchmark runs:

```bash
uv run python main.py compare-results results/v5/
```

Results can also be grouped by rule or category:

```bash
uv run python main.py compare-results results/v5/ --by-rule
uv run python main.py compare-results results/v5/ --by-category
```

#### Individual run analysis

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

#### Cross-run regression analysis

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

### Current Observations

* Qwen 3.5 9B produced the strongest result in the initial multi-model comparison.
* Qwen 2.5 Coder 7B provided a strong speed-to-accuracy trade-off in the initial model benchmark.
* Controlled prompt iteration improved Qwen 3.5 9B from **85.7% with v1** to **91.4% with v4** on the original 35-case suite.
* Explicit rule-specific detection boundaries were more effective than generic false-positive suppression instructions.
* Expanding the suite from 35 to 65 cases exposed additional generalization and boundary failures that were not visible in the smaller suite.
* Prompt v5 reaches **92.3% accuracy on 65 benchmarks** with **100% severity accuracy**.
* The new `unreachable_code` rule currently passes all five of its benchmark cases.
* `long_function` remains the clearest weak rule in the current prompt.
* Cross-run comparison shows that prompt improvements can fix multiple cases while simultaneously introducing unrelated regressions.
* The v4 → v5 experiment fixed three existing failures but regressed `user_absolute_path.py`.
* Aggregate accuracy should therefore not be used alone when deciding whether a prompt revision is better.
