## Results

The benchmark suite currently contains **35 benchmark cases** covering security, bugs, maintainability, performance, and false-positive scenarios.

### Model Comparison

The following results were produced during the initial **v1 model comparison** before deterministic generation settings and rule-based severity normalization were introduced:

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

These results are useful as an early model comparison, but they should not be directly compared with newer controlled prompt experiments because the evaluation setup has since changed.

Benchmark generation now uses `temperature=0` and a fixed seed to reduce run-to-run variation. Severity is also derived deterministically from the detected rule rather than relying on the model's severity prediction.

### Prompt Evaluation

Using Qwen 3.5 9B with the same 35-case benchmark suite and controlled generation settings:

| Prompt | Accuracy | Passed | False Positives | False Negatives |
| ------ | -------- | ------ | --------------- | --------------- |
| v1     | 85.7%    | 30/35  | 4               | 1               |
| v2     | 88.6%    | 31/35  | 3               | 1               |
| v3     | 88.6%    | 31/35  | 3               | 1               |
| v4     | 91.4%    | 32/35  | 2               | 1               |

The experiments showed that making rule-specific detection boundaries explicit was more effective than adding increasingly general instructions intended to suppress false positives.

Prompt v4 is currently the strongest controlled result, reaching **91.4% accuracy** with **2 false positives**, **1 false negative**, and **100% severity accuracy** for correctly detected issues.

### Result Analysis

The comparison tool can display results grouped by:

* Rule
* Category
* Prompt version

For example:

```bash
uv run python main.py compare-results results/v1/
uv run python main.py compare-results results/v1/ --by-rule
uv run python main.py compare-results results/v1/ --by-category
```

Individual benchmark runs can also be inspected in detail:

```bash
uv run python main.py analyze-result results/v4/qwen3.5-9b-seed42.json
```

This surfaces:

* False positives
* False negatives
* Rule mismatches
* Category mismatches
* Severity mismatches

### Current Observations

* Qwen 3.5 9B produced the strongest result in the initial multi-model comparison.
* Qwen 2.5 Coder 7B provided a strong speed-to-accuracy trade-off in the initial model benchmark.
* Controlled prompt iteration improved Qwen 3.5 9B from **85.7% with v1** to **91.4% with v4**.
* Rule-specific detection boundaries reduced false positives more effectively than additional general prompt instructions.
* The remaining v4 benchmark failures are primarily false-positive and maintainability-classification cases rather than severity calibration problems.
