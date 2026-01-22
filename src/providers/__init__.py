from .naive_provider import NaiveProvider
try:
    from .openai_provider import OpenAIProvider
except Exception:
    OpenAIProvider = None
try:
    from .ollama_provider import OllamaProvider
except Exception:
    OllamaProvider = None

PROVIDERS = {
    "naive": NaiveProvider,
    "openai": OpenAIProvider,
    # Ollama models
    "ollama-phi3": (lambda: OllamaProvider(name="ollama-phi3", model="phi3:medium")) if OllamaProvider is not None else None,
    "ollama-qwen": (lambda: OllamaProvider(name="ollama-qwen", model="qwen2.5:7b")) if OllamaProvider is not None else None,
    "ollama-codellama": (lambda: OllamaProvider(name="ollama-codellama", model="codellama:7b")) if OllamaProvider is not None else None,
    "ollama-hrida": (lambda: OllamaProvider(name="ollama-hrida", model="HridaAI/hrida-t2sql-128k:latest")) if OllamaProvider is not None else None,
    "ollama-deepseek": (lambda: OllamaProvider(name="ollama-deepseek", model="deepseek-coder:6.7b")) if OllamaProvider is not None else None,
    "ollama-duckdb": (lambda: OllamaProvider(name="ollama-duckdb", model="duckdb-nsql:7b")) if OllamaProvider is not None else None,
    # Aliases
    "ollama": (lambda: OllamaProvider(name="ollama-qwen", model="qwen2.5:7b")) if OllamaProvider is not None else None,
    "ollama-all": [
        (lambda: OllamaProvider(name="ollama-phi3", model="phi3:medium")) if OllamaProvider is not None else None,
        (lambda: OllamaProvider(name="ollama-qwen", model="qwen2.5:7b")) if OllamaProvider is not None else None,
        (lambda: OllamaProvider(name="ollama-codellama", model="codellama:7b")) if OllamaProvider is not None else None,
        (lambda: OllamaProvider(name="ollama-hrida", model="HridaAI/hrida-t2sql-128k:latest")) if OllamaProvider is not None else None,
        (lambda: OllamaProvider(name="ollama-deepseek", model="deepseek-coder:6.7b")) if OllamaProvider is not None else None,
        (lambda: OllamaProvider(name="ollama-duckdb", model="duckdb-nsql:7b")) if OllamaProvider is not None else None,
    ],
}