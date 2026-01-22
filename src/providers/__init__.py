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
    "ollama-phi3": (lambda: OllamaProvider(name="ollama-phi3", model="phi3:medium")) if OllamaProvider else None,
    "ollama-qwen": (lambda: OllamaProvider(name="ollama-qwen", model="qwen2.5:7b")) if OllamaProvider else None,
    "ollama-qwen3": (lambda: OllamaProvider(name="ollama-qwen3", model="qwen3:1.7b")) if OllamaProvider else None,
    "ollama-codellama": (lambda: OllamaProvider(name="ollama-codellama", model="codellama:7b")) if OllamaProvider else None,
    "ollama-starcoder": (lambda: OllamaProvider(name="ollama-starcoder", model="starcoder:latest")) if OllamaProvider else None,
    # Aliases
    "ollama": (lambda: OllamaProvider(name="ollama-qwen", model="qwen2.5:7b")) if OllamaProvider else None,
    "ollama-all": [
        (lambda: OllamaProvider(name="ollama-phi3", model="phi3:medium")) if OllamaProvider else None,
        (lambda: OllamaProvider(name="ollama-qwen", model="qwen2.5:7b")) if OllamaProvider else None,
        (lambda: OllamaProvider(name="ollama-qwen3", model="qwen3:1.7b")) if OllamaProvider else None,
        (lambda: OllamaProvider(name="ollama-codellama", model="codellama:7b")) if OllamaProvider else None,
        (lambda: OllamaProvider(name="ollama-starcoder", model="starcoder:latest")) if OllamaProvider else None,
    ],
}