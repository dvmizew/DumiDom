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
    """Build a complete prompt with schema, instructions, examples, and the question."""
    lines = ["Schema:", schema, "", "Instructions:", INSTRUCTIONS, "", "Examples:"]
    for ex in STATIC_FEW_SHOTS:
        lines.append(f"Q: {ex['question']}")
        lines.append(f"SQL: {ex['sql']}")
    lines.append("")
    lines.append(f"Question: {question}")
    lines.append("SQL:")
    return "\n".join(lines)


class TextToSQLChain:
    def __init__(self):
        pass

    def run(self, question, provider_name="naive", db_path=None):
        from src.providers import PROVIDERS
        
        db = SQLiteDB(db_path or os.environ.get("SQLITE_DB_PATH", "data/demo_music.sqlite"))
        schema_ctx = db.describe_schema()
        tables = db.tables()

        ProviderCls = PROVIDERS.get(provider_name)
        if ProviderCls is None:
            raise RuntimeError(f"Provider '{provider_name}' not available")
        provider = ProviderCls()

        sql = provider.generate_sql(question, schema_ctx)
        ok, msg = validate_sql(sql, tables)
        if not ok:
            raise RuntimeError(f"validation_failed: {msg}")

        try:
            db.explain(sql)
            rows = db.execute(sql)
            summary = provider.summarize(question, rows)
            return sql, rows, summary
        except Exception as e:
            raise RuntimeError(f"execution_error: {e}")