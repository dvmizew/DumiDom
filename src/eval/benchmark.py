import os
from typing import Dict, Optional
from tqdm import tqdm
from src.chain.text_to_sql import TextToSQLChain
from src.validation.sql_validator import normalize_sql
from src.db.sqlite_db import SQLiteDB
import json

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
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if limit:
        data = data[:limit]

    chain = TextToSQLChain()
    stats = dict(em=0, ex=0, syntax=0, logic=0, execution=0)
    results = []
    for item in tqdm(data, desc=f"benchmark ({provider})"):
        question, gold_sql = item["question"], item["query"]
        db_id = item.get("db_id")
        db_path = default_db
        if db_root and db_id:
            candidate = os.path.join(db_root, db_id, f"{db_id}.sqlite")
            if os.path.exists(candidate):
                db_path = candidate
        error_type = None
        try:
            pred_sql, _, _ = chain.run(question, provider_name=provider, db_path=db_path)
        except Exception as e:
            msg = str(e).lower()
            pred_sql = ""
            if "validation_failed" in msg or "syntax" in msg:
                error_type = "syntax"; stats["syntax"] += 1
            else:
                error_type = "execution"; stats["execution"] += 1
        if not pred_sql and error_type is None:
            error_type = "syntax"; stats["syntax"] += 1
        em = ex = False
        if pred_sql:
            em = exact_match(pred_sql, gold_sql)
            stats["em"] += int(em)
            if db_path:
                ex = execution_accuracy(pred_sql, gold_sql, db_path)
                stats["ex"] += int(ex)
                if not ex:
                    stats["logic"] += 1; error_type = "logic"
        results.append(dict(question=question, gold_sql=gold_sql, pred_sql=pred_sql, em=em, ex=ex, error=error_type))
    n = len(data)
    return dict(
        count=n,
        provider=provider,
        em=round(stats["em"] / n, 4) if n else 0.0,
        ex=round(stats["ex"] / n, 4) if n else 0.0,
        syntax_error_rate=round(stats["syntax"] / n, 4) if n else 0.0,
        logic_error_rate=round(stats["logic"] / n, 4) if n else 0.0,
        execution_error_rate=round(stats["execution"] / n, 4) if n else 0.0,
        results=results,
    )