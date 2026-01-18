# Text-To-SQL System

Natural language to SQL conversion with multi-step validation, schema awareness, and multi-provider support.

## Overview

This project implements a Text-to-SQL system that converts natural language questions into executable SQL queries. The system uses a multi-step pipeline with validation, schema awareness, and supports multiple LLM providers.

**Key Features:**
- Multi-step pipeline: schema extraction → prompt building → SQL generation → validation → execution
- Three provider implementations: Naive (regex), OpenAI (gpt-4o-mini), Ollama (qwen3:1.7b local)
- SQL validation: syntax check + read-only enforcement + schema validation
- Few-shot learning from user feedback
- Evaluation metrics: Exact Match (EM) and Execution Accuracy (EX)

## Architecture

**Pipeline Steps:**
1. Extract database schema
2. Build prompt with few-shot examples
3. Generate SQL using selected provider
4. Validate SQL (syntax + schema checks)
5. Execute query and summarize results

**Providers:**
- **Naive**: Regex patterns (baseline)
- **OpenAI**: gpt-4o-mini API
- **Ollama**: qwen3:1.7b local model

## Data Model

Demo database (`demo_music.sqlite`):

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
class TextToSQLChain:
    def run(self, question: str, provider_name: str = "naive") -> dict:
        schema = self.db.describe_schema()
        sql = self.provider.generate_sql(question, schema)
        is_valid, error = validate_sql(sql, schema)
        if not is_valid:
            return {"error": error}
        rows = self.db.execute(sql)
        return {"sql": sql, "rows": rows}
```

**SQL Validation** (`src/validation/sql_validator.py`):
- Syntax check via sqlglot parser
- Read-only enforcement (SELECT only)
- Schema validation (tables/columns)

## Setup & Usage

**Installation:**
```bash
git clone <repository-url>
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
make benchmark-compare    # Compare all providers
make clean               # Clean cache files
```

**CLI Examples:**
```bash
python -m src.cli "How many tracks?" --provider naive
python -m src.cli "Show artists" --provider ollama
```

## Evaluation Results

Latest benchmark on 17 Spider-style queries:

| Provider | EM   | EX   | Syntax Errors | Latency    |
|----------|------|------|---------------|------------|
| Naive    | 5.9% | 5.9% | 5.9%          | ~30ms      |
| OpenAI   | 0.0% | 0.0% | 100.0%        | ~500ms     |
| Ollama   | 0.0% | 0.0% | 100.0%        | ~4s/query  |

Results: `eval/results.csv`, Details: `eval/results_details.json`

## Project Structure

```
DumiDom/
├── src/
│   ├── cli.py                    # CLI entry point
│   ├── chain/
│   │   ├── text_to_sql.py       # Main pipeline
│   │   └── prompting.py         # Prompt building
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
├── docs/
│   └── benchmark_results.md     # Latest results
├── Makefile                      # Build automation
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## Dependencies

- Python 3.8+
- sqlglot (SQL parsing)
- openai (OpenAI API)
- ollama (Ollama API)
- python-dotenv (environment config)
- tabulate (output formatting)
- tqdm (progress bars)

## Compliance

This project satisfies T1 assignment requirements:
- Multi-step LLM chain with validation
- Multiple provider implementations
- Schema-aware prompting
- Error handling and logging
- Feedback-driven few-shot learning
- Comprehensive evaluation metrics

## References

[1] OpenAI. (2023). GPT-4 Technical Report. https://openai.com/research/gpt-4

[2] Yu et al. (2018). Spider: A Large-Scale Human-Labeled Dataset. EMNLP 2018. https://arxiv.org/abs/1809.08887

[3] sqlglot Documentation. https://sqlglot.com