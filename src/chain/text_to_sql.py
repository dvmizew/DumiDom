import os
from src.providers import PROVIDERS
from src.db.sqlite_db import SQLiteDB
from src.validation.sql_validator import validate_sql

class TextToSQLChain:
    def __init__(self):
        pass

    def run(self, question, provider_name="naive", db_path=None):
        db = SQLiteDB(db_path or os.environ.get("SQLITE_DB_PATH", "data/demo_music.sqlite"))
        schema_ctx = db.describe_schema()
        tables = db.tables()

        ProviderCls = PROVIDERS.get(provider_name)
        if ProviderCls is None:
            raise RuntimeError(f"Provider '{provider_name}' not available")
        provider = ProviderCls()

        sql = provider.generate_sql(question, schema_ctx, few_shots=None)
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
