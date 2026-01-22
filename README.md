# Video Presentation

The project presentation is available here: [docs/Presentation.pptx](docs/Presentation.pptx)

Download and open with PowerPoint or Google Slides for details.
# Text-To-SQL System

Natural language to SQL conversion with multi-step validation, schema awareness, and multi-provider support. Now features modular Ollama providers, robust benchmarking, and cross-platform compatibility.

## Overview

This project implements a Text-to-SQL system that converts natural language questions into executable SQL queries. The system uses a multi-step pipeline with validation, schema awareness, and supports multiple LLM providers.

**Key Features:**
- Multi-step pipeline: schema extraction → prompt building → SQL generation → validation → execution
- Modular provider architecture: Naive (regex), OpenAI (gpt-4o-mini), Ollama (multiple models: phi3, qwen, codellama, starcoder, etc.)
- Centralized provider mapping and DRY benchmarking logic
- All Ollama models benchmarked sequentially and compared in one run
- SQL validation: syntax check + read-only enforcement + schema validation
- Few-shot learning with static examples for improved accuracy
- Evaluation metrics: Exact Match (EM), Execution Accuracy (EX), and error breakdowns
- Pretty console output with tabulated benchmark results
- Robust error handling and memory management (Ollama models are unloaded after use)
- Cross-platform: works on Linux, Windows, and in VS Code (tasks.json provided)

## Architecture

**Pipeline Steps:**
1. Extract database schema
2. Build prompt with few-shot examples
3. Generate SQL using selected provider
4. Validate SQL (syntax + schema checks)
5. Execute query and summarize results

## Providers

- **naive**: Simple rule-based baseline, not schema-aware.
- **openai**: Uses OpenAI GPT models, prompt includes schema context.
- **ollama-phi3, ollama-qwen, ollama-codellama, ollama-starcoder, etc.**: Modular Ollama providers, each using a specific local LLM. Prompt includes schema context. All models are benchmarked and compared in one run.

All providers now dynamically use the schema context for SQL generation. Provider selection and benchmarking are fully modular and DRY, with all Ollama models handled automatically.

## Data Model

Demo database (`demo_music.sqlite`):
## Database Schema Diagram

![Database schema diagram](docs/dbdiagram.png)

```sql
CREATE TABLE artists (artist_id INTEGER PRIMARY KEY, name TEXT UNIQUE);
CREATE TABLE albums (album_id INTEGER PRIMARY KEY, title TEXT, 
                     artist_id INTEGER, release_year INTEGER,
                     FOREIGN KEY (artist_id) REFERENCES artists(artist_id));
CREATE TABLE tracks (track_id INTEGER PRIMARY KEY, title TEXT, 
                     album_id INTEGER, duration_seconds INTEGER,
                     FOREIGN KEY (album_id) REFERENCES albums(album_id));
```

Sample data: 3 artists, 7 albums, 21 tracks.

## Core Implementation

**TextToSQLChain** (`src/chain/text_to_sql.py`):
```python
from src.chain.text_to_sql import TextToSQLChain
chain = TextToSQLChain()
sql, rows, summary = chain.run(
    "How many tracks?",
    provider_name="ollama",  # or "openai", "naive"
    db_path="data/demo_music.sqlite"
)
print("SQL:", sql)
print("Results:", rows)
print("Summary:", summary)
```

**SQL Validation** (`src/validation/sql_validator.py`):
- Syntax check via sqlglot parser
- Read-only enforcement (SELECT only)
- Schema validation (tables/columns)

## Setup & Usage

**Installation:**
```bash
git clone https://github.com/dvmizew/DumiDom.git
cd DumiDom
python3 -m venv .venv
source .venv/bin/activate
make install
make init-db
```

**Commands:**
```bash
make help                 # Show available commands
make run                  # Run demo query
make benchmark-compare    # Compare all providers (naive, openai, all Ollama models)
make clean                # Clean cache files
```

**CLI Examples:**
```bash
python -m src.cli "How many tracks?" --provider naive
python -m src.cli "Show artists" --provider ollama-qwen
python -m src.cli "Show albums" --provider ollama-phi3
```

## Evaluation Results

Latest benchmark (2026-01-22) on 17 Spider-style queries (all providers, all Ollama models):

| Provider           | EM    | EX    | Syntax Err   | Logic Err   | Exec Err   |
|--------------------|-------|-------|--------------|-------------|------------|
| naive              | 5.9%  | 11.8% | 0.0%         | 88.2%       | 0.0%       |
| ollama-codellama   | 5.9%  | 94.1% | 0.0%         | 5.9%        | 0.0%       |
| ollama-phi3        | 0.0%  | 35.3% | 52.9%        | 11.8%       | 0.0%       |
| ollama-qwen        | 17.6% | 94.1% | 0.0%         | 5.9%        | 0.0%       |
| ollama-qwen3       | 0.0%  | 0.0%  | 100.0%       | 0.0%        | 0.0%       |
| ollama-starcoder   | 0.0%  | 5.9%  | 88.2%        | 5.9%        | 0.0%       |
| openai             | 0.0%  | 0.0%  | 0.0%         | 0.0%        | 100.0%     |

## Project Structure

```
DumiDom/
├── src/
│   ├── cli.py                    # CLI entry point
│   ├── chain/
│   │   └── text_to_sql.py       # Main pipeline
│   ├── providers/
│   │   ├── base.py              # Provider interface
│   │   ├── naive_provider.py    # Regex provider
│   │   ├── openai_provider.py   # OpenAI provider
│   │   └── ollama_provider.py   # Ollama provider
│   ├── validation/
│   │   └── sql_validator.py     # SQL safety checks
│   ├── db/
│   │   └── sqlite_db.py         # Database wrapper
│   └── eval/
│       └── benchmark.py         # Evaluation metrics
├── scripts/
│   ├── init_demo_db.py          # Database initialization
│   ├── run_eval.py              # Evaluation script
│   └── benchmark_compare.py     # Multi-provider benchmark
├── data/
│   └── demo_music.sqlite        # Demo database
├── eval/
│   ├── spider_sample.json       # Test queries
│   └── feedback.jsonl           # User feedback logs
│   ├── benchmark_results.md     # Latest results
│   ├── results.csv              # CSV results
│   └── results_details.json     # Detailed results
├── Makefile                      # Build automation
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## Feedback Loop & Output

Feedback is logged for each query, including errors and results. See [src/feedback.py](src/feedback.py) for details. The feedback system is robust and only logs relevant entries, ensuring clarity and traceability for benchmarking and debugging.

All benchmark results are saved in `benchmark_results/` as Markdown, CSV, and detailed JSON. Output logic is deduplicated and robust, with clear file naming and directory management. Memory is managed efficiently by unloading Ollama models after use.

## Dependencies

- Python 3.8+
- sqlglot (SQL parsing)
- openai (OpenAI API)
- ollama (Ollama API)
- python-dotenv (environment config, optional; no longer required for Ollama)
- tabulate (output formatting)
- tqdm (progress bars)

---

## Originality Statement

This project (code and documentation) is original and created for academic requirements. It does not contain sections copied from other sources without citation. Any code, text, or idea taken from external sources is properly cited. The project complies with the ethics and academic integrity rules of FMI.

## AI Usage

AI tools (GitHub Copilot, ChatGPT) were used for code generation, explanations, and documentation structuring, as permitted by the assignment. All AI tools and sources used are listed in the References section.

## References

[1] OpenAI, GPT-4 Technical Report, https://openai.com/research/gpt-4
[2] Yu, Tao, et al., Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task, EMNLP 2018, https://arxiv.org/abs/1809.08887
[3] sqlglot Documentation, https://sqlglot.com
[4] OpenAI, ChatGPT, https://chatgpt.com/
[5] Copilot, https://copilot.microsoft.com