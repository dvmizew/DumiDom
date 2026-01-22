import os
import sys
import json
from typing import List, Dict
from tabulate import tabulate
from src.eval.benchmark import run_benchmark
from src.providers import PROVIDERS

OLLAMA_MODELS = [
    "ollama-phi3",
    "ollama-qwen",
    "ollama-qwen3",
    "ollama-codellama",
    "ollama-starcoder",
]

def provider_row(provider, m):
    return [
        provider,
        f"{m['em']:.1%}",
        f"{m['ex']:.1%}",
        f"{m['syntax_error_rate']:.1%}",
        f"{m['logic_error_rate']:.1%}",
        f"{m['execution_error_rate']:.1%}"
    ]

def error_metrics(provider_name, msg):
    return {
        "count": 0,
        "provider": provider_name,
        "em": 0.0,
        "ex": 0.0,
        "syntax_error_rate": 0.0,
        "logic_error_rate": 0.0,
        "execution_error_rate": 1.0,
        "results": [],
        "error": msg,
    }

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def run_multi_provider(dataset_path: str, default_db: str, providers: List[str], limit: int = None) -> Dict:
    """Run benchmarks across multiple providers and return aggregated results."""
    import subprocess
    results = {}
    openai_error = None
    ollama_model_map = {
        "ollama-phi3": "phi3:medium",
        "ollama-qwen": "qwen2.5:7b",
        "ollama-qwen3": "qwen3:1.7b",
        "ollama-codellama": "codellama:7b",
        "ollama-starcoder": "starcoder:latest",
    }
    for provider_name in providers:
        prov = PROVIDERS.get(provider_name)
        if prov is None:
            print(f"Skipping {provider_name} (not available)")
            continue
        try:
            print(f"\nBenchmarking {provider_name}...")
            metrics = run_benchmark(dataset_path, provider_name, default_db=default_db, limit=limit)
            results[provider_name] = metrics
        except Exception as e:
            msg = str(e)
            print(f"\n[ERROR] {provider_name} failed: {msg}\n")
            error_obj = error_metrics(provider_name, msg)
            if provider_name == "openai":
                if "quota" in msg.lower() and ("exceeded" in msg.lower() or "reached" in msg.lower()):
                    openai_error = "OpenAI quota exceeded"
                    error_obj["error"] = openai_error
                else:
                    openai_error = msg
            results[provider_name] = error_obj
        # stop Ollama model to free resources
        model_id = ollama_model_map.get(provider_name)
        if model_id:
            try:
                print(f"Stopping Ollama model: {model_id}")
                subprocess.run(["ollama", "stop", model_id], check=False)
            except Exception as e:
                print(f"(Could not stop Ollama model {model_id}: {e})")
    return results

def print_console_table(results: Dict):
    if not results:
        print("No results.")
        return
    headers = ["Provider", "EM", "EX", "Syntax Err", "Logic Err", "Exec Err"]
    rows = []
    for provider, m in sorted(results.items()):
        rows.append(provider_row(provider, m))
        print(f"\nModel: {provider}")
        print(f"  Exact Match (EM): {m['em']:.1%}")
        print(f"  Execution Accuracy (EX): {m['ex']:.1%}")
        print(f"  Syntax Errors: {m['syntax_error_rate']:.1%}")
        print(f"  Logic Errors: {m['logic_error_rate']:.1%}")
        print(f"  Execution Errors: {m['execution_error_rate']:.1%}")
    print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

def generate_markdown_table(results: Dict) -> str:
    if not results:
        return "No results."
    headers = ["Provider", "EM", "EX", "Syntax Err", "Logic Err", "Exec Err"]
    rows = [provider_row(provider, m) for provider, m in sorted(results.items())]
    table_md = tabulate(rows, headers=headers, tablefmt="github")
    return "# Benchmark Results\n\n" + table_md

def generate_csv_table(results: Dict) -> str:
    if not results:
        return "Provider,EM,EX,SyntaxErr,LogicErr,ExecErr"
    lines = ["Provider,EM,EX,SyntaxErr,LogicErr,ExecErr"]
    for provider, m in sorted(results.items()):
        row = provider_row(provider, m)
        lines.append(",".join(str(x).replace('%','') if i>0 else str(x) for i,x in enumerate(row)))
    return "\n".join(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run multi-provider benchmarks and generate reports")
    parser.add_argument("dataset", help="Path to Spider-like JSON file")
    parser.add_argument("--db", dest="default_db", required=True, help="Default SQLite DB path")
    parser.add_argument("--providers", nargs="+", default=["naive"], help="Providers to benchmark (naive|openai|ollama-qwen|ollama-phi3)")
    parser.add_argument("--all-available", action="store_true", help="Run all available providers")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of questions")
    parser.add_argument("--output-md", dest="output_md", help="Output Markdown file")
    parser.add_argument("--output-csv", dest="output_csv", help="Output CSV file")
    parser.add_argument("--output-json", dest="output_json", help="Output very detailed JSON file (all predictions, errors, etc)")
    args = parser.parse_args()

    providers = []
    for p in args.providers:
        if p == "ollama" or p == "ollama-all":
            for m in OLLAMA_MODELS:
                if PROVIDERS.get(m) is not None:
                    providers.append(m)
        else:
            providers.append(p)
    if args.all_available:
        providers = [p for p in (["naive", "openai"] + OLLAMA_MODELS) if PROVIDERS.get(p) is not None]
        print(f"Available providers: {providers}\n")

    results = run_multi_provider(args.dataset, args.default_db, providers, limit=args.limit)
    md_table = generate_markdown_table(results)
    csv_table = generate_csv_table(results)

    print_console_table(results)
    out_dir = "benchmark_results"
    os.makedirs(out_dir, exist_ok=True)
    if args.output_md:
        md_path = os.path.join(out_dir, os.path.basename(args.output_md))
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_table)
        print(f"Saved markdown to {md_path}")
    if args.output_csv:
        csv_path = os.path.join(out_dir, os.path.basename(args.output_csv))
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(csv_table)
        print(f"Saved CSV to {csv_path}")
    # Save details JSON
    details_path = os.path.join(out_dir, os.path.basename(args.output_csv).replace(".csv", "_details.json")) if args.output_csv else os.path.join(out_dir, "benchmark_details.json")
    with open(details_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Saved details to {details_path}")
    # Save very detailed results if requested
    if getattr(args, "output_json", None):
        detailed_path = os.path.join(out_dir, os.path.basename(args.output_json))
        all_details = [dict(item, provider=provider)
                      for provider, prov_result in results.items()
                      for item in prov_result.get("results", [])]
        with open(detailed_path, "w", encoding="utf-8") as f:
            json.dump(all_details, f, indent=2, ensure_ascii=False)
        print(f"Saved very detailed results to {detailed_path}")


if __name__ == "__main__":
    main()