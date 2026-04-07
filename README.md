---
title: Data Cleaner Agent
emoji: 🧹
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🧹 Data Cleaner Pro (OpenEnv)

**Live OpenEnv Server:** [Hugging Face Space](https://huggingface.co/spaces/aryan8intelligence/Data_Cleaner_Agent)

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

## Architecture & Multi-Mode Deployment
This project is fully validated for OpenEnv's strict **multi-mode deployment** (cloud, local, and Docker-ready). 

To achieve this, the environment uses **`uv`** (a lightning-fast Python package manager) and a `pyproject.toml` configuration rather than relying solely on traditional standard pip installations. 
- **Reproducibility:** The `uv.lock` file acts as a highly specific map of every sub-dependency, ensuring that automated grading servers instantly recreate the exact local environment without version conflicts.
- **Validation:** OpenEnv's automated grading scripts explicitly demand this architecture to guarantee the agent can be seamlessly deployed as a proper Python package anywhere.
*(Note: A legacy `requirements.txt` is also included in the repository to satisfy generic hackathon submission guidelines and handle basic Docker container builds, but `uv` is the core engine for complete OpenEnv compliance).*

## Setup & Installation

### Local Development

**1. Clone the repository**
```bash
git clone [https://github.com/aryan8chauhan-arch/Data_Cleaner_Agent](https://github.com/aryan8chauhan-arch/Data_Cleaner_Agent)
cd Data_Cleaner_Agent
```

**2. Install dependencies via uv**
```bash
pip install uv
uv sync
```

**3. Configure Environment Variables (.env)**
Create a `.env` file in the root directory:
```env
API_BASE_URL=[https://router.huggingface.co/v1](https://router.huggingface.co/v1)
MODEL_NAME=meta-llama/Llama-3.3-70B-Instruct
HF_TOKEN=your_token_here
```

**4. Run the OpenEnv Server**
Because this project is configured as a proper Python package, you can start the local environment server easily:
```bash
uv run server
```
*(The server will start on http://0.0.0.0:7860)*

**5. Evaluate the Agent**
In a separate terminal, use the OpenEnv CLI to run the agent against the environment:
```bash
openenv evaluate --env data-cleaner-pro --agent inference.py
```