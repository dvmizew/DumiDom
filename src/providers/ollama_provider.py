import re
from .base import Provider
from src.chain.text_to_sql import build_sql_prompt

try:
    import ollama
except Exception:
    ollama = None

class OllamaProvider(Provider):
    def __init__(self, name="ollama", model=None):
        self.name = name
        if ollama is None:
            raise RuntimeError(f"Ollama provider '{name}': package not available")
        if not model:
            raise RuntimeError(f"Ollama provider '{name}': model must be specified explicitly!")
        self.model = model

    def generate_sql(self, question, schema_context):
        prompt = build_sql_prompt(schema_context, question)
        if ollama is None:
            raise RuntimeError(f"Ollama provider '{self.name}': ollama package is not installed or failed to import.")
        try:
            stream = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                options={"temperature": 0, "num_predict": 64},
            )
            content = "".join(chunk.get('message', {}).get('content', '') for chunk in stream).strip()
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
                raise RuntimeError(f"Ollama provider '{self.name}': empty content")
            return content
        except Exception as e:
            raise RuntimeError(f"Ollama provider '{self.name}': {e}")

    def summarize(self, question, rows):
        return f"Found {len(rows)} results for: {question}"
