import os
import re
from .base import Provider
from src.chain.text_to_sql import build_sql_prompt

try:
    import ollama
except Exception:
    ollama = None

class OllamaProvider(Provider):
    name = "ollama"

    def __init__(self):
        if ollama is None:
            raise RuntimeError("ollama package not available")
        self.model = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
        # uses default ollama client

    def generate_sql(self, question, schema_context):
        # minimal prompt for speed
        prompt = build_sql_prompt(schema_context, question)
        try:
            stream = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                options={"temperature": 0, "num_predict": 64},
            )
            content = ""
            for chunk in stream:
                delta = chunk.get('message', {}).get('content', '')
                if delta:
                    content += delta
            content = content.strip()
            # unwrap ```sql fenced blocks if the model returns markdown
            fence_match = re.search(r"```(?:sql)?\s*(.*?)```", content, re.DOTALL | re.IGNORECASE)
            if fence_match:
                content = fence_match.group(1).strip()

            # drop leading labels like "SQL:" or bullets
            if content.lower().startswith("sql:"):
                content = content.split(":", 1)[1].strip()

            # if model included prose, keep from first SELECT onward
            select_match = re.search(r"(?is)(select\s.+)", content)
            if select_match:
                content = select_match.group(1).strip()

            content = content.strip()
            # ensure semicolon termination for validator
            if not content.endswith(";"):
                content += ";"
            if not content:
                raise RuntimeError("ollama returned empty content")
            return content
        except Exception as e:
            raise RuntimeError(f"ollama timeout or error: {e}")

    def summarize(self, question, rows):
        return f"Found {len(rows)} results for: {question}"
