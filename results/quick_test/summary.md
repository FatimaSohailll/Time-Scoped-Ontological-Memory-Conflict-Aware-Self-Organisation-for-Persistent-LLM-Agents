## quick_test (amem, qwen2.5:3b, 1 conversations)

| Category | n | F1 | BLEU-1 |
|---|---|---|---|
| Multi-hop | 8 | 30.83 | 19.27 |
| Temporal | 10 | 19.56 | 15.44 |
| Open-domain | 2 | 0.00 | 11.94 |
| Overall | 20 | 22.11 | 16.62 |

| Cost | Value |
|---|---|
| Memory writes | 419 |
| LLM calls per write | 2.94 |
| Seconds per write | 4.10 |
| Writes that triggered evolution | 81.1% |
| Prompt tokens per question | 2280 |
