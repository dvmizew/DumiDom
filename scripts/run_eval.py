import os
import sys
import argparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.eval.benchmark import run_benchmark

def main():
    parser = argparse.ArgumentParser(description="Run EM/EX benchmark on Spider-like dataset")
    parser.add_argument("dataset", help="Path to Spider-like JSON file")
    parser.add_argument("provider", help="Provider name (naive|openai|ollama)")
    parser.add_argument("--db-root", dest="db_root", help="Root folder containing DBs (db_id/db_id.sqlite)")
    parser.add_argument("--default-db", dest="default_db", help="Fallback SQLite DB path")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of questions")
    args = parser.parse_args()

    metrics = run_benchmark(args.dataset, args.provider, db_root=args.db_root, default_db=args.default_db, limit=args.limit)
    print(metrics)

if __name__ == "__main__":
    main()