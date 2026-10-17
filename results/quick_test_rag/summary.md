## quick_test_rag (rag, qwen2.5:3b, 1 conversations)

| Category | n | F1 | BLEU-1 |
|---|---|---|---|
| Multi-hop | 8 | 0.00 | 2.08 |
| Temporal | 10 | 21.67 | 18.75 |
| Open-domain | 2 | 14.29 | 12.50 |
| Overall | 20 | 12.26 | 11.46 |

| Cost | Value |
|---|---|
| Memory writes | 419 |
| LLM calls per write | 0.00 |
| Seconds per write | 0.01 |
| Writes that triggered evolution | 0.0% |
| Prompt tokens per question | 694 |
