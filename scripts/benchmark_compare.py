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
    openai_error = None
    for provider_name in providers:
        if PROVIDERS.get(provider_name) is None:
            print(f"Skipping {provider_name} (not available)")
            continue
        try:
            print(f"\nBenchmarking {provider_name}...")
            metrics = run_benchmark(dataset_path, provider_name, default_db=default_db, limit=limit)
            results[provider_name] = metrics
        except Exception as e:
            msg = str(e)
            print(f"\n[ERROR] {provider_name} failed: {msg}\n")
            # Detect quota exceeded for OpenAI
            quota_msg = None
            if provider_name == "openai":
                if "quota" in msg.lower() and ("exceeded" in msg.lower() or "reached" in msg.lower()):
                    quota_msg = "OpenAI quota exceeded"
                    openai_error = quota_msg
                else:
                    openai_error = msg
                results[provider_name] = {
                    "count": 0,
                    "provider": provider_name,
                    "em": 0.0,
                    "ex": 0.0,
                    "syntax_error_rate": 0.0,
                    "logic_error_rate": 0.0,
                    "execution_error_rate": 1.0,
                    "results": [],
                    "error": quota_msg if quota_msg else msg,
                }
            else:
                results[provider_name] = {
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
    if openai_error:
        print(f"\n[OPENAI ERROR] {openai_error}\n")
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
            f"{m['execution_error_rate']:.1%}"
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
            f"{m['execution_error_rate']:.1%}"
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
    parser.add_argument("--output-json", dest="output_json", help="Output very detailed JSON file (all predictions, errors, etc)")
    args = parser.parse_args()

    providers = args.providers
    if args.all_available:
        providers = [p for p in ["naive", "openai", "ollama"] if PROVIDERS.get(p) is not None]
        print(f"Available providers: {providers}\n")

    results = run_multi_provider(args.dataset, args.default_db, providers, limit=args.limit)
    
    md_table = generate_markdown_table(results)
    csv_table = generate_csv_table(results)

    print_console_table(results)
    # save results
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
    # save json details
    details_path = os.path.join(out_dir, os.path.basename(args.output_csv).replace(".csv", "_details.json")) if args.output_csv else os.path.join(out_dir, "benchmark_details.json")
    with open(details_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Saved details to {details_path}")

    # save very detailed results (all predictions, errors, etc) if requested
    if getattr(args, "output_json", None):
        detailed_path = os.path.join(out_dir, os.path.basename(args.output_json))
        # flatten all results for all providers
        all_details = []
        for provider, prov_result in results.items():
            for item in prov_result.get("results", []):
                row = dict(item)
                row["provider"] = provider
                all_details.append(row)
        with open(detailed_path, "w", encoding="utf-8") as f:
            json.dump(all_details, f, indent=2, ensure_ascii=False)
        print(f"Saved very detailed results to {detailed_path}")


if __name__ == "__main__":
    main()