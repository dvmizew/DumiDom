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
):
    os.makedirs(os.path.dirname(FEEDBACK_PATH), exist_ok=True)
    entry = dict(
        ts=datetime.utcnow().isoformat() + "Z",
        question=question,
        provider=provider,
        sql=sql,
        rows=rows,
        summary=summary,
        feedback=feedback,
        correction=correction,
    )
    with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_feedback_examples(max_examples: int = 3) -> List[Dict[str, str]]:
    """Return recent corrected or upvoted examples as few-shots for prompting."""
    if not os.path.exists(FEEDBACK_PATH):
        return []
    examples = []
    with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                item = json.loads(line)
                if item.get("correction"):
                    examples.append({"question": item.get("question", ""), "sql": item.get("correction", "")})
                elif item.get("feedback") == "up" and item.get("sql"):
                    examples.append({"question": item.get("question", ""), "sql": item.get("sql", "")})
            except Exception:
                continue
    return examples[-max_examples:]
