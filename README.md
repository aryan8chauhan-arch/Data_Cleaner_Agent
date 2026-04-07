---
title: Data Cleaner Agent
emoji: 🧹
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🧹 Data Cleaner Pro (OpenEnv)

## Overview
Data scientists spend up to 80% of their time cleaning data. **Data Cleaner Pro** is a real-world Reinforcement Learning environment built on the OpenEnv framework that simulates messy Pandas DataFrames. It challenges AI agents to autonomously identify data quality issues and apply the correct operations to produce an analysis-ready dataset.

**Author:** Aryan Chauhan

## Action & Observation Spaces
- **Observation Space:** The agent receives a JSON state containing a `data_preview`, `column_info`, and `null_counts`. This provides enough context to analyze the messiness without overloading the context window or exceeding memory limits.
- **Action Space:** A strictly typed Pydantic model allowing the AI to execute `drop_duplicates`, `fill_na`, `drop_column`, and a custom `clean_currency` tool.

## The 6 Real-World Tasks
1. **Easy (`remove_duplicates`):** Identify and remove duplicate rows.
2. **Easy (`drop_empty_columns`):** Identify and drop "ghost" columns (e.g., Unnamed: 2) that are entirely null.
3. **Medium (`handle_missing_values`):** Fill `NaN` values with appropriate context-aware data.
4. **Medium (`standardize_currency`):** Strip symbols (`$` and `,`) from strings and cast them to floats for downstream math operations.
5. **Hard (`format_consistency`):** Fix mixed types and nulls natively within a single column.
6. **Hard (`gdpr_pii_redaction`):** A reasoning challenge where the agent must identify ambiguously named columns (e.g., `User_Meta_1`) containing sensitive PII (emails) and proactively redact them.

## Baseline Performance
Evaluated using the automated OpenEnv validation script with `meta-llama/Llama-3.3-70B-Instruct`:
- **Success Rate:** 100% (6/6 Tasks Solved)
- **Score:** 1.000 / 1.000 on all tasks
- **Efficiency:** ~2130 tokens per full run
- **Estimated Cost:** < $0.01

## Setup Instructions

### Local Development
```bash
# 1. Clone the repository
git clone https://github.com/aryan8chauhan-arch/Data_Cleaner_Agent
cd Data_Cleaner_Agent


# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure Environment Variables (.env)
API_BASE_URL=[https://router.huggingface.co/v1](https://router.huggingface.co/v1)
MODEL_NAME=meta-llama/Llama-3.3-70B-Instruct
HF_TOKEN=your_token_here

# 4. Run the baseline agent
python inference.py