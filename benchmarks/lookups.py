"""
lookups.py

Benchmarks point lookup and indexed range lookup queries against each
connected database.

Each lookup query is measured independently. If one query fails, its error
is recorded while previously completed queries remain in the results.

Note: node ids are stored as strings (as produced by the CSV import
pipeline), so the indexed lookup's `u.id >= $id` comparison is a string
comparison, not a numeric one. This matches how the data was loaded and
still exercises the id index, but the exact set of nodes counted won't
match a numeric range comparison. If your import pipeline stores ids as
integers instead, this query's semantics change to a true numeric range
scan; no code changes are needed either way since both are read via the
same $id parameter.

Run directly:
    python lookups.py
Or import and call run_benchmark_suite() from run_all.py.

Results are written to results/lookups.json.
"""

from benchmarks import bench_common as bc

QUERIES = {
    "point_lookup": "MATCH (u:User {id:$id}) RETURN u",
    "indexed_lookup": "MATCH (u:User) WHERE u.id >= $id RETURN count(u)",
}

QUERY_SEED_OFFSETS = {
    "point_lookup": 11,
    "indexed_lookup": 12,
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

                print(f"[lookups] {db_name} - {query_name}: completed")

            except Exception as exc:
                query_results[query_name] = {
                    "status": "error",
                    "error": str(exc),
                }

                print(f"[lookups] {db_name} - {query_name}: FAILED - {exc}")

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
        "benchmark": "lookups",
        "timestamp": bc.utc_timestamp(),
        "dataset": bc.DATASET_INFO,
        "warmup_iterations": bc.WARMUP_ITERATIONS,
        "measured_iterations": bc.MEASURED_ITERATIONS,
        "databases": {},
    }

    for db_name in databases:
        print(f"[lookups] Benchmarking {db_name}...")
        results["databases"][db_name] = run_for_database(db_name)

    bc.save_json("lookups.json",results,)
    return results


if __name__ == "__main__":
    run_benchmark_suite()