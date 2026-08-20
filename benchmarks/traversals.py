"""
traversals.py

Benchmarks 1-hop, 2-hop, and 3-hop VOTED_FOR traversal queries against
each connected database.

Each traversal is measured independently. If one query fails, its error
is recorded while previously completed queries remain in the results.

Run directly:
    python traversals.py
Or import and call run_benchmark_suite() from run_all.py.

Results are written to results/traversals.json.
"""

from benchmarks import bench_common as bc

QUERIES = {
    "one_hop": "MATCH (u:User {id:$id})-[:VOTED_FOR]->(n) RETURN count(n)",
    "two_hop": "MATCH (u:User {id:$id})-[:VOTED_FOR*2]->(n) RETURN count(n)",
    "three_hop": "MATCH (u:User {id:$id})-[:VOTED_FOR*3]->(n) RETURN count(n)",
}

# Distinct seed offsets keep each query's sampled id sequence independent
# and reproducible across runs.
QUERY_SEED_OFFSETS = {
    "one_hop": 1,
    "two_hop": 2,
    "three_hop": 3,
}

def run_for_database(db_name):
    runner = None
    try:
        runner = bc.QueryRunner(db_name)
        ids = bc.get_all_ids(runner)

        query_results = {}
        for query_name, query_text in QUERIES.items():
            try:
                sequence = bc.build_id_sequence(
                    ids,
                    bc.WARMUP_ITERATIONS + bc.MEASURED_ITERATIONS,
                    seed=bc.RANDOM_SEED + QUERY_SEED_OFFSETS[query_name],
                )

                seq_iter = iter(sequence)

                def query_fn(
                    _runner=runner,
                    _query=query_text,
                    _iter=seq_iter,
                ):
                    node_id = next(_iter)
                    _runner.run(
                        _query,
                        {"id": node_id},
                    )

                latencies = bc.run_benchmark(query_fn)

                query_results[query_name] = {
                    "status": "ok",
                    "stats": bc.compute_stats(latencies),
                }

                print(f"[traversals] {db_name} - {query_name}: completed")

            except Exception as exc:
                query_results[query_name] = {
                    "status": "error",
                    "error": str(exc),
                }

                print(f"[traversals] {db_name} - {query_name}: FAILED - {exc}")

        return {
            "status": "ok",
            "queries": query_results,
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
        "benchmark": "traversals",
        "timestamp": bc.utc_timestamp(),
        "dataset": bc.DATASET_INFO,
        "warmup_iterations": bc.WARMUP_ITERATIONS,
        "measured_iterations": bc.MEASURED_ITERATIONS,
        "databases": {},
    }

    for db_name in databases:
        print(f"[traversals] Benchmarking {db_name}...")
        results["databases"][db_name] = run_for_database(db_name)

    bc.save_json("traversals.json",results,)
    return results

if __name__ == "__main__":
    run_benchmark_suite()