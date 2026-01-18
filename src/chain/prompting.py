from typing import Optional, List, Dict

STATIC_FEW_SHOTS = [
    {"question": "How many tracks?", "sql": "SELECT COUNT(*) FROM tracks;"},
]

INSTRUCTIONS = "Write SQLite SELECT. Use schema. If vague use LIMIT 5. SQL only."

def build_sql_prompt(schema, question, previous_sql=None, error_message=None, extra_examples=None):
    lines = ["Schema:", schema, "", "Instructions:", INSTRUCTIONS, "", "Examples:"]
    examples = list(STATIC_FEW_SHOTS)
    if extra_examples:
        examples.extend(extra_examples)
    for ex in examples:
        lines.append(f"Q: {ex['question']}")
        lines.append(f"SQL: {ex['sql']}")
    lines.append("")
    lines.append(f"Question: {question}")
    if previous_sql is not None and error_message is not None:
        lines.append(f"Previous SQL: {previous_sql}")
        lines.append(f"Error: {error_message}")
        lines.append("Provide a corrected SQL.")
    else:
        lines.append("Write SQL only.")
    return "\n".join(lines)