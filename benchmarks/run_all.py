"""
run_all.py

Loads all databases, then runs the complete benchmark suite:

    1. Data loading
    2. Traversals
    3. Lookups
    4. Aggregations
    5. Mixed workload

Results are written to:
    results/loading_time.json
    results/traversals.json
    results/lookups.json
    results/aggregations.json
    results/mixed_workload.json
    results/summary.json

Usage:
    python -m benchmarks.run_all
"""

import time
from loaders.load_all import load_all
from benchmarks import aggregations
from benchmarks import lookups
from benchmarks import mixed_workload
from benchmarks import traversals
from benchmarks import bench_common
from generate_charts import main as generate_charts


def run_all(databases=None):
    databases = databases or bench_common.DEFAULT_DATABASES

    unknown = [
        db
        for db in databases
        if db not in bench_common.DB_CONNECT_MODULES
    ]

    if unknown:
        raise ValueError(
            f"Unknown database(s): {unknown}. "
            f"Valid options: {bench_common.DEFAULT_DATABASES}"
        )

    print("========================================")
    print("Loading databases")
    print("========================================\n")

    overall_start = time.perf_counter()
    loading_results = load_all()

    loading_metrics = {
        db: loading_results[db]
        for db in databases
        if db in loading_results
    }

    print("\n======================================")
    print(f"Running benchmarks for: {', '.join(databases)}")
    print("========================================\n")

    summary = {
        "timestamp": bench_common.utc_timestamp(),
        "dataset": bench_common.DATASET_INFO,
        "databases": databases,
        "loading_metrics": loading_metrics,
        "results": {},
    }

    summary["results"]["traversals"] = (traversals.run_benchmark_suite(databases))
    summary["results"]["lookups"] = (lookups.run_benchmark_suite(databases))
    summary["results"]["aggregations"] = (aggregations.run_benchmark_suite(databases))
    summary["results"]["mixed_workload"] = (mixed_workload.run_benchmark_suite(databases))

    summary["total_wall_clock_seconds"] = round(time.perf_counter() - overall_start,2,)

    bench_common.save_json("summary.json",summary,)
    generate_charts()

    print("\n========================================")
    print("All benchmarks complete")
    print("========================================\n")

    print(f"Total benchmark time: {summary['total_wall_clock_seconds']}s")

    print("\nResults:")
    print("  results/loading_time.json")
    print("  results/traversals.json")
    print("  results/lookups.json")
    print("  results/aggregations.json")
    print("  results/mixed_workload.json")
    print("  results/summary.json")

    return summary


if __name__ == "__main__":
    run_all()