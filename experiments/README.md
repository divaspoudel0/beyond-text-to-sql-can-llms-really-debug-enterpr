# Experiments: Beyond Text-to-SQL Reproduction

## Overview

This directory contains the experiments and outcomes from reproducing the paper
"Beyond Text-to-SQL: Can LLMs Really Debug Enterprise ETL SQL?" (arXiv:2601.18119).

## Structure

- `proxy_bench/` - 10-task proxy benchmark following the Squirrel Benchmark taxonomy
  - `tasks.json` - The proxy benchmark tasks (5 syntax + 5 semantic)
  - `evaluate.py` - Evaluation script using Graph Match Score (GM)
  - `results_summary.json` - Summary of results

- `poster.html` - Reproduction poster HTML

## Key Results

### Proxy Benchmark (Qwen2.5-Coder-7B-Instruct)

| Metric | Proxy Results | Paper (Claude-4-Sonnet) |
|--------|---------------|-------------------------|
| Squirrel-Syntax GM | 99.31% | 36.46% |
| Squirrel-Semantic GM | 52.40% | 32.17% |

**Note:** Proxy tasks are much simpler than the real Squirrel Benchmark (985 tasks),
which explains the higher scores. The paper's tasks average 140+ lines with deep ASTs,
while our proxy tasks are 25-30 lines.

### Paper Claims Verification

All 4 major claims confirmed as internally consistent:

1. ✅ 469 syntax + 516 semantic tasks from 1,000+ seed scripts
2. ✅ Claude-4-Sonnet: 36.46% GM (syntax), 32.17% (semantic)
3. ✅ DeepSeek-V3: 30.28% GM, Qwen-2.5-Coder-32B: 23.45% GM
4. ✅ Scripts: 420+ tokens, 17.34-21.62 functions/script

## Limitations

- Squirrel Benchmark dataset is gated (Dream-AI-HUST/sql_benchmarks)
- Only 1 model evaluated via HF Inference API (credits limited)
- HF Jobs required credits (402 Payment Required)
