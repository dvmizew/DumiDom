import os
import sys
import json
from typing import List, Dict
from tabulate import tabulate

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.eval.benchmark import run_benchmark
from src.providers import PROVIDERS

def run_multi_provider(dataset_path: str, default_db: str, providers: List[str], limit: int = None) -> Dict:
    """Run benchmarks across multiple providers and return aggregated results."""
    results = {}
    for provider_name in providers:
        if PROVIDERS.get(provider_name) is None:
            print(f"Skipping {provider_name} (not available)")
            continue
        try:
            print(f"\nBenchmarking {provider_name}...")
            metrics = run_benchmark(dataset_path, provider_name, default_db=default_db, limit=limit)
            results[provider_name] = metrics
        except Exception as e:
            print(f"Error: {provider_name} failed: {e}")
    return results


def generate_markdown_table(results: Dict) -> str:
    if not results:
        return "No results."

    headers = ["Provider", "EM", "EX", "Syntax Err", "Logic Err", "Exec Err"]
    rows = []
    for provider, m in sorted(results.items()):
        rows.append([
            provider,
            f"{m['em']:.1%}",
            f"{m['ex']:.1%}",
            f"{m['syntax_error_rate']:.1%}",
            f"{m['logic_error_rate']:.1%}",
            f"{m['execution_error_rate']:.1%}",
        ])

    table_md = tabulate(rows, headers=headers, tablefmt="github")
    return "# Benchmark Results\n\n" + table_md


def print_console_table(results: Dict):
    if not results:
        print("No results.")
        return
    headers = ["Provider", "EM", "EX", "Syntax Err", "Logic Err", "Exec Err"]
    rows = []
    for provider, m in sorted(results.items()):
        rows.append([
            provider,
            f"{m['em']:.1%}",
            f"{m['ex']:.1%}",
            f"{m['syntax_error_rate']:.1%}",
            f"{m['logic_error_rate']:.1%}",
            f"{m['execution_error_rate']:.1%}",
        ])
    print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))


def generate_csv_table(results: Dict) -> str:
    if not results:
        return "Provider,EM,EX,SyntaxErr,LogicErr,ExecErr"
    
    lines = ["Provider,EM,EX,SyntaxErr,LogicErr,ExecErr"]
    for provider, m in sorted(results.items()):
        lines.append(
            f"{provider},{m['em']:.4f},{m['ex']:.4f},{m['syntax_error_rate']:.4f},"
            f"{m['logic_error_rate']:.4f},{m['execution_error_rate']:.4f}"
        )
    return "\n".join(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run multi-provider benchmarks and generate reports")
    parser.add_argument("dataset", help="Path to Spider-like JSON file")
    parser.add_argument("--db", dest="default_db", required=True, help="Default SQLite DB path")
    parser.add_argument("--providers", nargs="+", default=["naive"], help="Providers to benchmark (naive|openai|ollama)")
    parser.add_argument("--all-available", action="store_true", help="Run all available providers")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of questions")
    parser.add_argument("--output-md", dest="output_md", help="Output Markdown file")
    parser.add_argument("--output-csv", dest="output_csv", help="Output CSV file")
    args = parser.parse_args()

    providers = args.providers
    if args.all_available:
        providers = [p for p in ["naive", "openai", "ollama"] if PROVIDERS.get(p) is not None]
        print(f"Available providers: {providers}\n")

    results = run_multi_provider(args.dataset, args.default_db, providers, limit=args.limit)
    
    md_table = generate_markdown_table(results)
    csv_table = generate_csv_table(results)

    print_console_table(results)
    
    if args.output_md:
        os.makedirs(os.path.dirname(args.output_md) or ".", exist_ok=True)
        with open(args.output_md, "w", encoding="utf-8") as f:
            f.write(md_table)
        print(f"Saved markdown to {args.output_md}")
    
    if args.output_csv:
        os.makedirs(os.path.dirname(args.output_csv) or ".", exist_ok=True)
        with open(args.output_csv, "w", encoding="utf-8") as f:
            f.write(csv_table)
        print(f"Saved CSV to {args.output_csv}")
    
    # save json details
    details_path = args.output_csv.replace(".csv", "_details.json") if args.output_csv else "eval/benchmark_details.json"
    os.makedirs(os.path.dirname(details_path) or ".", exist_ok=True)
    with open(details_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Saved details to {details_path}")


if __name__ == "__main__":
    main()