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
    "ollama-qwen": (lambda: OllamaProvider(name="ollama-qwen", model="qwen2.5:7b")) if OllamaProvider else None,
    "ollama-phi3": (lambda: OllamaProvider(name="ollama-phi3", model="phi3:medium")) if OllamaProvider else None,
    "ollama": (lambda: OllamaProvider(name="ollama-qwen", model="qwen2.5:7b")) if OllamaProvider else None,
    "ollama-all": [
        (lambda: OllamaProvider(name="ollama-qwen", model="qwen2.5:7b")) if OllamaProvider else None,
        (lambda: OllamaProvider(name="ollama-phi3", model="phi3:medium")) if OllamaProvider else None,
    ],
}