"""
mixed_workload.py

Benchmarks an 80% read / 20% write workload using 10 concurrent clients.

Primary metric:
    Sustained queries per second (QPS)

Results:
    results/mixed_workload.json
"""

import random
import threading
import time
import uuid

from benchmarks import bench_common as bc


NUM_CLIENTS = 10
READ_RATIO = 0.8
WRITE_RATIO = 0.2

WARMUP_SECONDS = 2.0
MEASURED_SECONDS = 10.0

READ_QUERY = """
MATCH (u:User {id:$id})-[:VOTED_FOR]->(n)
RETURN count(n)
"""

WRITE_QUERY = """
MERGE (a:User {id:$source_id})
MERGE (b:User {id:$target_id})
CREATE (a)-[:VOTED_FOR]->(b)
"""

CLEANUP_QUERY = """
MATCH (u:User)
WHERE u.id STARTS WITH 'bench-write-'
DETACH DELETE u
"""

PREFIX = "bench-write-"

def worker(db_name, ids, end_time, counts, errors, index):
    runner = bc.QueryRunner(db_name)
    rng = random.Random(index)

    try:
        while time.perf_counter() < end_time:
            is_write = rng.random() < WRITE_RATIO
            try:
                if is_write:
                    runner.run(
                        WRITE_QUERY,
                        {
                            "source_id": PREFIX + uuid.uuid4().hex,
                            "target_id": PREFIX + uuid.uuid4().hex,
                        },
                    )
                    counts[index]["write"] += 1
                else:
                    runner.run(
                        READ_QUERY,
                        {"id": rng.choice(ids)},
                    )
                    counts[index]["read"] += 1

            except Exception as exc:
                errors[index].append(str(exc))

    finally:
        runner.close()


def run_phase(db_name, ids, duration):
    start = time.perf_counter()
    end = start + duration

    counts = [
        {"read": 0, "write": 0}
        for _ in range(NUM_CLIENTS)
    ]
    errors = [[] for _ in range(NUM_CLIENTS)]

    threads = [
        threading.Thread(
            target=worker,
            args=(db_name, ids, end, counts, errors, i),
            daemon=True,
        )
        for i in range(NUM_CLIENTS)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    elapsed = time.perf_counter() - start

    reads = sum(c["read"] for c in counts)
    writes = sum(c["write"] for c in counts)
    failures = sum(len(e) for e in errors)

    return reads, writes, failures, errors, elapsed


def cleanup(db_name):
    try:
        runner = bc.QueryRunner(db_name)
        runner.run(CLEANUP_QUERY)
        runner.close()
    except Exception as exc:
        print(f"[mixed_workload] Cleanup failed for {db_name}: {exc}")


def run_for_database(db_name):
    runner = None
    try:
        runner = bc.QueryRunner(db_name)
        ids = bc.get_all_ids(runner)

        if not ids:
            return {
                "status": "error",
                "error": "No User ids found",
            }

    except Exception as exc:
        return {
            "status": "error",
            "error": f"setup failed: {exc}",
        }

    finally:
        if runner:
            runner.close()

    try:
        # Warm-up
        run_phase(
            db_name,
            ids,
            WARMUP_SECONDS,
        )

        # Measured phase
        reads, writes, failures, errors, elapsed = run_phase(
            db_name,
            ids,
            MEASURED_SECONDS,
        )

        total = reads + writes

        result = {
            "status": "ok",
            "stats": {
                "concurrent_clients": NUM_CLIENTS,
                "read_ratio": READ_RATIO,
                "write_ratio": WRITE_RATIO,
                "total_operations": total,
                "read_operations": reads,
                "write_operations": writes,
                "failed_operations": failures,
                "measured_duration_seconds": round(elapsed, 4),
                "sustained_qps": round(total / elapsed, 2),
            },
        }

        if failures:
            result["stats"]["error_messages"] = [
                message
                for client_errors in errors
                for message in client_errors
            ][:10]

        return result

    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
        }

    finally:
        cleanup(db_name)


def run_benchmark_suite(databases=None):
    databases = databases or bc.DEFAULT_DATABASES

    results = {
        "benchmark": "mixed_workload",
        "timestamp": bc.utc_timestamp(),
        "dataset": bc.DATASET_INFO,
        "config": {
            "concurrent_clients": NUM_CLIENTS,
            "read_ratio": READ_RATIO,
            "write_ratio": WRITE_RATIO,
            "warmup_seconds": WARMUP_SECONDS,
            "measured_seconds": MEASURED_SECONDS,
        },
        "databases": {},
    }

    for db_name in databases:
        print(f"[mixed_workload] Benchmarking {db_name}...")
        results["databases"][db_name] = run_for_database(db_name)

    bc.save_json("mixed_workload.json", results)
    return results


if __name__ == "__main__":
    run_benchmark_suite()