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
        "sql": "SELECT tracks.name FROM tracks WHERE tracks.genre = 'Rock';",
    },
    {
        "question": "Which album has the longest track?",
        "sql": "SELECT albums.title, MAX(tracks.duration) FROM albums JOIN tracks ON tracks.album_id = albums.id GROUP BY albums.id ORDER BY MAX(tracks.duration) DESC LIMIT 1;",
    },
    {
        "question": "Average track duration by genre",
        "sql": "SELECT tracks.genre, AVG(tracks.duration) FROM tracks GROUP BY tracks.genre;",
    },
    {
        "question": "List albums released after 2015",
        "sql": "SELECT albums.title, albums.year FROM albums WHERE albums.year > 2015;",
    },
    {
        "question": "Album release years",
        "sql": "SELECT DISTINCT albums.year FROM albums ORDER BY albums.year;",
    },
]

INSTRUCTIONS = (
    "You are an expert SQL generator. Your task is to write a single valid SQLite SELECT statement using only the provided schema. "
    "Output ONLY raw SQL, on a single line if possible: no markdown, no explanations, no backticks, no text, no comments, no code fences. "
    "Start your answer with SELECT. Do NOT include any introductory or closing text. "
    "If you are unsure, return: SELECT 1 WHERE 0; (a valid but empty result). "
    "Do NOT use table aliases; always use full table names in qualified columns (e.g., artists.name). "
    "Use GROUP BY / HAVING when counting per entity. If unclear, add LIMIT 5. "
    "NEVER output anything except valid SQL. "
    "Examples of what NOT to do:"
    "\nINCORRECT: ```sql SELECT * FROM tracks; ```"
    "\nINCORRECT: The SQL query is: SELECT * FROM tracks;"
    "\nINCORRECT: SELECT * FROM tracks; -- list all tracks"
    "\nINCORRECT: SELECT * FROM tracks; /* list all tracks */"
    "\nINCORRECT: SELECT * FROM tracks;\nExplanation: This query lists all tracks."
    "\nCORRECT: SELECT * FROM tracks;"
)

def build_sql_prompt(schema, question):
    """Build a complete prompt with schema, instructions, static and dynamic examples, and the question."""
    lines = ["Schema:", schema, "", "Instructions:", INSTRUCTIONS, "", "Examples:"]
    for ex in STATIC_FEW_SHOTS:
        lines.append(f"Q: {ex['question']}")
        lines.append(f"SQL: {ex['sql']}")
    try:
        from src.feedback import load_feedback_examples
        for ex in load_feedback_examples(max_examples=3) or []:
            lines.append(f"Q: {ex['question']}")
            lines.append(f"SQL: {ex['sql']}")
    except Exception:
        pass
    lines += ["", f"Question: {question}", "SQL:"]
    return "\n".join(lines)

class TextToSQLChain:
    def __init__(self):
        pass

    def run(self, question, provider_name="naive", db_path=None):
        qstr = question.strip().lower()
        vague = len(qstr.split()) < 4 or qstr in {"query", "search", "find", "show", "list", "get"} or any(x in qstr for x in ["something", "anything", "data", "info", "information", "details"])

        from src.providers import PROVIDERS
        db = SQLiteDB(db_path or os.environ.get("SQLITE_DB_PATH", "data/demo_music.sqlite"))
        schema_ctx = db.describe_schema()
        tables = db.tables()
        ProviderCls = PROVIDERS.get(provider_name)
        if not ProviderCls:
            raise RuntimeError(
                f"Provider '{provider_name}' not available. "
                "Possible fixes: check the provider name, install required dependencies, or check your .env configuration."
            )
        provider = ProviderCls()

        last_error = None
        for attempt in range(2):
            q = question
            if vague:
                q += "\n# Clarify: Be specific and use concrete columns and values from the schema."
            if attempt == 1 and last_error:
                q += f"\n# Previous SQL was invalid: {last_error}. Please fix the SQL."
            sql = provider.generate_sql(q, schema_ctx)
            ok, msg = validate_sql(sql, tables)
            if ok:
                try:
                    db.explain(sql)
                    rows = db.execute(sql)
                    return sql, rows, provider.summarize(question, rows)
                except Exception as e:
                    last_error = str(e)
            else:
                last_error = msg
        raise RuntimeError(f"validation_failed: {last_error}")