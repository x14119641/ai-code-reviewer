## Results

The benchmark suite currently contains **35 benchmark cases** covering security, bugs, maintainability, performance, and false-positive scenarios.

### Overall Comparison

Example results using prompt version **v1**:

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

The comparison tool can also display detailed results grouped by:

- Rule
- Category
- Prompt version

For example:

```bash
uv run python main.py compare-results results/v1/
uv run python main.py compare-results results/v1/ --by-rule
uv run python main.py compare-results results/v1/ --by-category
```

### Current observations

- Qwen 3.5 9B currently achieves the highest overall benchmark accuracy.
- Qwen 2.5 Coder 7B provides the best speed-to-accuracy trade-off.
- Coding-specialized models outperform general-purpose models on most benchmark categories.
- DeepSeek Coder V2 and Llama 3.1 leave room for improvement on this benchmark suite despite their strong general coding capabilities.