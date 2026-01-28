PYTHON := python3
.PHONY: help install init-db run benchmark-compare clean

help:
	@echo "Available targets:"
	@echo "  make install           - Install dependencies from requirements.txt"
	@echo "  make init-db           - Initialize demo database"
	@echo "  make run               - Run Text-to-SQL demo query"
	@echo "  make benchmark-compare - Run benchmark on all providers"
	@echo "  make clean             - Remove cache files and artifacts"
	@echo "  make help              - Show this help message"

install:
	$(PYTHON) -m pip install -r requirements.txt

init-db:
	$(PYTHON) scripts/init_demo_db.py

run:
	$(PYTHON) -m src.cli "How many tracks are there?" --provider naive

benchmark-compare:
	$(PYTHON) -m scripts.benchmark_compare eval/spider_sample.json --db data/demo_music.sqlite --providers naive openai ollama --output-md docs/benchmark_results.md --output-csv eval/results.csv

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf .pytest_cache .coverage htmlcov 2>/dev/null || true
