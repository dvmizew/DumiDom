import os
import argparse
from tabulate import tabulate
from dotenv import load_dotenv

from src.chain.text_to_sql import TextToSQLChain
from src.feedback import log_feedback

def main():
    parser = argparse.ArgumentParser(description="Text-To-SQL CLI")
    parser.add_argument("question", help="NLP question to answer")
    parser.add_argument("--provider", default="naive", help="Provider: naive|openai|ollama")
    parser.add_argument("--db-path", dest="db_path", help="SQLite DB path")
    parser.add_argument("--show-rows", dest="show_rows", action="store_true", help="Show result rows")
    parser.add_argument("--no-show-rows", dest="show_rows", action="store_false", help="Hide result rows")
    parser.set_defaults(show_rows=True)
    parser.add_argument("--limit", type=int, default=10, help="Row display limit")
    parser.add_argument("--thumbs-up", dest="thumbs", action="store_const", const="up", help="Mark helpful")
    parser.add_argument("--thumbs-down", dest="thumbs", action="store_const", const="down", help="Mark not helpful")
    parser.add_argument("--correction", help="User-corrected SQL to execute and log")
    args = parser.parse_args()

    load_dotenv()
    chain = TextToSQLChain()
    sql = rows = summary = None
    try:
        sql, rows, summary = chain.run(args.question, provider_name=args.provider, db_path=args.db_path)
        # if user provided correction, run that instead
        if args.correction:
            from src.db.sqlite_db import SQLiteDB
            dbp = args.db_path or os.environ.get("SQLITE_DB_PATH", "data/demo_music.sqlite")
            db = SQLiteDB(dbp)
            rows = db.execute(args.correction)
            sql = args.correction
            summary = f"User-corrected SQL executed. {len(rows)} rows."
    except Exception as e:
        print(f"Error: {e}")
        return

    print(f"\nSQL:\n{sql}")
    if args.show_rows:
        if rows:
            print("\nResults:")
            print(tabulate(rows[:args.limit]))
        else:
            print("No rows returned")
    print(f"\nSummary:\n{summary}")
    try:
        log_feedback(
            question=args.question,
            provider=args.provider,
            sql=sql,
            rows=len(rows) if rows else 0,
            summary=summary,
            feedback=args.thumbs,
            correction=args.correction,
        )
    except Exception as e:
        print(f"(Could not log feedback: {e})")


if __name__ == "__main__":
    main()
