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
            raise RuntimeError("Ollama provider: package not available")
        self.model = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")

    def generate_sql(self, question, schema_context):
        prompt = build_sql_prompt(schema_context, question)
        try:
            stream = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                options={"temperature": 0, "num_predict": 64},
            )
            content = "".join(chunk.get('message', {}).get('content', '') for chunk in stream).strip()
            # unwrap ```sql fenced blocks if the model returns markdown
            fence_match = re.search(r"```(?:sql)?\\s*(.*?)```", content, re.DOTALL | re.IGNORECASE)
            if fence_match:
                content = fence_match.group(1).strip()
            if content.lower().startswith("sql:"):
                content = content.split(":", 1)[1].strip()
            select_match = re.search(r"(?is)(select\\s.+)", content)
            if select_match:
                content = select_match.group(1).strip()
            content = content.strip()
            if not content.endswith(";"):
                content += ";"
            if not content:
                raise RuntimeError("Ollama provider: empty content")
            return content
        except Exception as e:
            raise RuntimeError(f"Ollama provider: {e}")

    def summarize(self, question, rows):
        return f"Found {len(rows)} results for: {question}"
