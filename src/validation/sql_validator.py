import sqlglot
import sqlglot.expressions as exp

ALLOWED_STATEMENTS = {exp.Select, exp.Union, exp.With}


def validate_sql(sql, tables):
    try:
        parsed = sqlglot.parse_one(sql, dialect="sqlite")
    except Exception as e:
        return False, f"parse error: {e}"
    if not isinstance(parsed, tuple(ALLOWED_STATEMENTS)):
        return False, "not a SELECT/UNION/CTE statement"
    tables_set = set(tables)
    for table in parsed.find_all(exp.Table):
        if table.name not in tables_set:
            return False, f"unknown table: {table.name}"
    known_cols = {f"{t}.{c}" for t, cols in tables.items() for c in cols}
    for col in parsed.find_all(exp.Column):
        if col.table and col.name and f"{col.table}.{col.name}" not in known_cols:
            return False, f"unknown column: {col.table}.{col.name}"
    return True, "ok"


def normalize_sql(sql):
    return sqlglot.transpile(sql, read="sqlite", write="sqlite", normalize=True, pretty=False)[0]
