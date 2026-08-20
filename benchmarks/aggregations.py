"""
aggregations.py

Benchmarks a top-10 aggregation query (votes cast per user, descending)
against each connected database.

The aggregation query is measured independently. If the query fails, the
error is recorded in the query result rather than causing the entire
database benchmark result to be discarded.

Run directly:
    python aggregations.py
Or import and call run_benchmark_suite() from run_all.py.

Results are written to results/aggregations.json.
"""

from benchmarks import bench_common as bc


AGGREGATION_QUERY = """
MATCH (u:User)-[:VOTED_FOR]->()
RETURN u.id, count(*) AS votes
ORDER BY votes DESC
LIMIT 10
"""


def run_for_database(db_name):
    runner = None

    try:
        runner = bc.QueryRunner(db_name)
        try:

            def query_fn(_runner=runner):
                _runner.run(AGGREGATION_QUERY)

            latencies = bc.run_benchmark(query_fn)

            print(f"[aggregations] {db_name} - aggregation: completed")

            return {
                "status": "ok",
                "query": {
                    "status": "ok",
                    "stats": bc.compute_stats(latencies),
                },
            }

        except Exception as exc:
            print(f"[aggregations] {db_name} - aggregation: FAILED - {exc}")

            return {
                "status": "ok",
                "query": {
                    "status": "error",
                    "error": str(exc),
                },
            }

    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
        }

    finally:
        if runner is not None:
            runner.close()


def run_benchmark_suite(databases=None):
    databases = databases or bc.DEFAULT_DATABASES

    results = {
        "benchmark": "aggregations",
        "timestamp": bc.utc_timestamp(),
        "dataset": bc.DATASET_INFO,
        "warmup_iterations": bc.WARMUP_ITERATIONS,
        "measured_iterations": bc.MEASURED_ITERATIONS,
        "databases": {},
    }

    for db_name in databases:
        print(f"[aggregations] Benchmarking {db_name}...")
        results["databases"][db_name] = run_for_database(db_name)

    bc.save_json("aggregations.json",results,)
    return results


if __name__ == "__main__":
    run_benchmark_suite()