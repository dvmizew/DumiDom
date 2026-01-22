import json
import os
from datetime import datetime
from typing import Optional, List, Dict

FEEDBACK_PATH = os.environ.get("FEEDBACK_LOG_PATH", "eval/feedback.jsonl")


def log_feedback(
    question: str,
    provider: str,
    sql: str,
    rows: int,
    summary: str,
    feedback: Optional[str] = None,
    correction: Optional[str] = None,
) -> None:
    """
    Log user feedback or correction to FEEDBACK_PATH. Skips logging if both feedback and correction are missing.
    """
    if not feedback and not correction:
        return
    os.makedirs(os.path.dirname(FEEDBACK_PATH), exist_ok=True)
    entry = {k: v for k, v in dict(
        ts=datetime.utcnow().isoformat() + "Z",
        question=question,
        provider=provider,
        sql=sql,
        rows=rows,
        summary=summary,
        feedback=feedback,
        correction=correction,
    ).items() if v is not None}
    try:
        with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"(Could not log feedback: {e})")


def load_feedback_examples(max_examples: int = 3) -> List[Dict[str, str]]:
    """
    Return recent corrected or upvoted examples as few-shots for prompting.
    """
    if not os.path.exists(FEEDBACK_PATH):
        return []
    with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    def parse(line):
        try:
            item = json.loads(line)
            if item.get("correction"):
                return {"question": item.get("question", ""), "sql": item.get("correction", "")}
            if item.get("feedback") == "up" and item.get("sql"):
                return {"question": item.get("question", ""), "sql": item.get("sql", "")}
        except Exception:
            return None
    examples = [ex for ex in (parse(line) for line in lines) if ex]
    return examples[-max_examples:]
