import os
from src.db.sqlite_db import SQLiteDB
from src.validation.sql_validator import validate_sql

STATIC_FEW_SHOTS = [
    {"question": "How many tracks?", "sql": "SELECT COUNT(*) FROM tracks;"},
    {
        "question": "Show artists with more than 1 album",
        "sql": "SELECT artists.name, COUNT(albums.id) FROM artists LEFT JOIN albums ON albums.artist_id = artists.id GROUP BY artists.id HAVING COUNT(albums.id) > 1;",
    },
    {
        "question": "List top 5 albums by track count",
        "sql": "SELECT albums.title, artists.name, COUNT(tracks.id) AS track_count FROM albums JOIN artists ON albums.artist_id = artists.id LEFT JOIN tracks ON tracks.album_id = albums.id GROUP BY albums.id ORDER BY track_count DESC LIMIT 5;",
    },
    {
        "question": "List all rock tracks",
        "sql": "SELECT name FROM tracks WHERE genre = 'Rock';",
    },
    {
        "question": "Which album has the longest track?",
        "sql": "SELECT albums.title, MAX(tracks.duration) FROM albums JOIN tracks ON tracks.album_id = albums.id GROUP BY albums.id ORDER BY MAX(tracks.duration) DESC LIMIT 1;",
    },
    {
        "question": "Average track duration by genre",
        "sql": "SELECT genre, AVG(duration) FROM tracks GROUP BY genre;",
    },
    {
        "question": "List albums released after 2015",
        "sql": "SELECT title, year FROM albums WHERE year > 2015;",
    },
    {
        "question": "Album release years",
        "sql": "SELECT DISTINCT year FROM albums ORDER BY year;",
    },
]

INSTRUCTIONS = (
    "Write one valid SQLite SELECT statement using only the provided schema. "
    "Output raw SQL only: no markdown, no prose, no backticks. Start with SELECT. "
    "Use GROUP BY / HAVING when counting per entity. If unclear, add LIMIT 5. "
    "Do NOT use table aliases; reference full table names in qualified columns (e.g., artists.name)."
)

def build_sql_prompt(schema, question):
    """Build a complete prompt with schema, instructions, static and dynamic examples, and the question."""
    lines = ["Schema:", schema, "", "Instructions:", INSTRUCTIONS, "", "Examples:"]
    # static few-shots
    for ex in STATIC_FEW_SHOTS:
        lines.append(f"Q: {ex['question']}")
        lines.append(f"SQL: {ex['sql']}")
    # dynamic few-shots from feedback
    try:
        from src.feedback import load_feedback_examples
        feedback_examples = load_feedback_examples(max_examples=3)
        if feedback_examples:
            lines.append("# User feedback examples:")
            for ex in feedback_examples:
                lines.append(f"Q: {ex['question']}")
                lines.append(f"SQL: {ex['sql']}")
    except Exception:
        pass
    lines.append("")
    lines.append(f"Question: {question}")
    lines.append("SQL:")
    return "\n".join(lines)

class TextToSQLChain:
    def __init__(self):
        pass

    def run(self, question, provider_name="naive", db_path=None):
        vague = False
        if len(question.strip().split()) < 4 or question.strip().lower() in {"query", "search", "find", "show", "list", "get"}:
            vague = True
        elif any(x in question.lower() for x in ["something", "anything", "data", "info", "information", "details"]):
            vague = True

        from src.providers import PROVIDERS
        db = SQLiteDB(db_path or os.environ.get("SQLITE_DB_PATH", "data/demo_music.sqlite"))
        schema_ctx = db.describe_schema()
        tables = db.tables()
        ProviderCls = PROVIDERS.get(provider_name)
        if ProviderCls is None:
            raise RuntimeError(f"Provider '{provider_name}' not available")
        provider = ProviderCls()

        attempts = 2
        last_error = None
        for attempt in range(attempts):
            q = question
            if vague:
                q = question + "\n# Clarify: Be specific and use concrete columns and values from the schema."
            if attempt == 0:
                sql = provider.generate_sql(q, schema_ctx)
            else:
                # retry
                error_msg = f"Previous SQL was invalid: {last_error}. Please fix the SQL."
                q = q + f"\n# {error_msg}"
                sql = provider.generate_sql(q, schema_ctx)
            ok, msg = validate_sql(sql, tables)
            if ok:
                try:
                    db.explain(sql)
                    rows = db.execute(sql)
                    summary = provider.summarize(question, rows)
                    return sql, rows, summary
                except Exception as e:
                    last_error = str(e)
                    continue
            else:
                last_error = msg
                continue
        raise RuntimeError(f"validation_failed: {last_error}")