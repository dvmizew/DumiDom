from typing import Dict, Set, Tuple
import sqlglot
import sqlglot.expressions as exp

ALLOWED_STATEMENTS = {exp.Select, exp.Union, exp.With}


def validate_sql(sql, tables):
    try:
        parsed = sqlglot.parse_one(sql, dialect="sqlite")
    except Exception as e:
        return False, f"parse_error: {e}"

    if not isinstance(parsed, tuple(ALLOWED_STATEMENTS)):
        return False, "only SELECT/UNION/CTE statements are allowed"

    # check tables
    for table in parsed.find_all(exp.Table):
        name = table.name
        if name not in tables:
            return False, f"unknown table: {name}"

    # check columns
    known_cols = {f"{t}.{c}" for t, cols in tables.items() for c in cols}
    for col in parsed.find_all(exp.Column):
        if col.table and col.name:
            fq = f"{col.table}.{col.name}"
            if fq not in known_cols and col.table not in tables:
                return False, f"unknown column: {fq}"

    return True, "ok"


def normalize_sql(sql):
    return sqlglot.transpile(sql, read="sqlite", write="sqlite", normalize=True, pretty=False)[0]
