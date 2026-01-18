import os
from typing import Dict, Optional
from tqdm import tqdm
from src.chain.text_to_sql import TextToSQLChain
from src.validation.sql_validator import normalize_sql
from src.db.sqlite_db import SQLiteDB
from src.eval.spider_loader import load_spider

def exact_match(pred, gold):
    try:
        return normalize_sql(pred) == normalize_sql(gold)
    except Exception:
        return pred.strip().lower() == gold.strip().lower()


def execution_accuracy(pred_sql, gold_sql, db_path):
    db = SQLiteDB(db_path)
    try:
        pred_rows = db.execute(pred_sql)
    except Exception:
        return False
    try:
        gold_rows = db.execute(gold_sql)
    except Exception:
        return False
    return pred_rows == gold_rows


def run_benchmark(
    dataset_path: str,
    provider: str,
    db_root: Optional[str] = None,
    default_db: Optional[str] = None,
    limit: Optional[int] = None,
) -> Dict:
    """Run EM/EX/error metrics over a Spider-like dataset.

    If db_root is provided, uses db_root/{db_id}/{db_id}.sqlite; otherwise uses default_db.
    Returns dict with count, em, ex, syntax_error_rate, logic_error_rate, results list.
    """
    data = load_spider(dataset_path)
    if limit:
        data = data[:limit]

    chain = TextToSQLChain()
    em_total = 0
    ex_total = 0
    syntax_errors = 0
    logic_errors = 0
    results = []

    for item in tqdm(data, desc=f"benchmark ({provider})"):
        question = item["question"]
        gold_sql = item["query"]
        db_id = item.get("db_id")
        db_path = default_db
        if db_root and db_id:
            candidate = os.path.join(db_root, db_id, f"{db_id}.sqlite")
            if os.path.exists(candidate):
                db_path = candidate
        
        pred_sql = ""
        rows = []
        error_type = None
        try:
            pred_sql, rows, _summary = chain.run(question, provider_name=provider, db_path=db_path)
        except Exception as e:
            error_type = "syntax" if "syntax" in str(e).lower() else "execution"
            syntax_errors += 1
            pred_sql = ""
            rows = []
        
        em = False
        ex = False
        if pred_sql:
            em = exact_match(pred_sql, gold_sql)
            em_total += em
            if db_path:
                ex = execution_accuracy(pred_sql, gold_sql, db_path)
                ex_total += ex
                if not ex and not error_type:
                    logic_errors += 1
                    error_type = "logic"
        
        results.append({
            "question": question,
            "gold_sql": gold_sql,
            "pred_sql": pred_sql,
            "em": em,
            "ex": ex,
            "error": error_type,
        })

    n = len(data)
    return {
        "count": n,
        "provider": provider,
        "em": round(em_total / n, 4) if n else 0.0,
        "ex": round(ex_total / n, 4) if n else 0.0,
        "syntax_error_rate": round(syntax_errors / n, 4) if n else 0.0,
        "logic_error_rate": round(logic_errors / n, 4) if n else 0.0,
        "results": results,
    }