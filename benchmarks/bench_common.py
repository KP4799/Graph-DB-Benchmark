"""
bench_common.py

Shared utilities for the SNAP Wiki-Vote benchmark suite. Imported by
traversals.py, lookups.py, aggregations.py, mixed_workload.py, and
run_all.py. This module does not run any benchmarks itself.

Responsibilities:
    - Load each database's connect() function from its connector module.
    - Provide QueryRunner, a uniform wrapper around whatever connection
      object connect() returns (a Bolt/Cypher driver for Neo4j, Memgraph,
      CognoDB, or a graph handle for FalkorDB).
    - Provide a warm-up + measured-iteration benchmark loop.
    - Compute p50 / p95 latency using the statistics module.
    - Persist results as JSON under results/.
"""
import re
import json
import os
import random
import statistics
import time
from datetime import datetime, timezone

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from databases import neo4j_db
from databases import memgraph_db
from databases import falkordb_db
from databases import cognodb
from databases import apache_age

DB_CONNECT_MODULES = {
    "neo4j": neo4j_db,
    "memgraph": memgraph_db,
    "falkordb": falkordb_db,
    "cognodb": cognodb,
    "apache_age": apache_age
}

DEFAULT_DATABASES = ["neo4j", "memgraph", "falkordb", "cognodb", "apache_age"]

RESULTS_DIR = "results"
RANDOM_SEED = 42
WARMUP_ITERATIONS = 20
MEASURED_ITERATIONS = 100

DATASET_INFO = {"nodes": 7115, "relationships": 103689}

AGE_GRAPH = "benchmark"

# Uniform query execution
class QueryRunner:
    """
    Wraps whatever object a connector's connect() returns and exposes a
    single run(query, params) -> rows method, regardless of whether the
    underlying connection is a Bolt/Cypher driver (Neo4j, Memgraph,
    CognoDB) or a FalkorDB graph handle.
    """

    def __init__(self, db_name):
        if db_name not in DB_CONNECT_MODULES:
            raise ValueError(f"Unknown database: {db_name}")

        self.db_name = db_name
        module = DB_CONNECT_MODULES[db_name]
        self.conn = module.connect()

        if db_name == "apache_age":
            self.kind = "age"
            self.cursor = self.conn.cursor()
        elif hasattr(self.conn, "session"):
            # Bolt/Cypher driver (Neo4j, Memgraph, CognoDB)
            self.kind = "bolt"
            database = getattr(module, "COGNODB_DATABASE", None)

            if db_name == "cognodb":
                self.session = self.conn.session(database=database)
            else:
                self.session = self.conn.session()
                
        elif hasattr(self.conn, "query"):
            # FalkorDB graph handle
            self.kind = "graph"
            self.session = None
        else:
            raise TypeError(
                f"Unrecognized connection object returned by "
                f"{db_name}.connect(): {type(self.conn)!r}"
            )

    def run(self, query, params=None):
        params = params or {}
        
        if self.kind == "bolt":
            result = self.session.run(query, params)
            return [list(record.values()) for record in result]
        elif self.kind == "graph":
            result = self.conn.query(query, params)
            return list(result.result_set)
        elif self.kind == "age":
            return self._run_age(query,params)

    def close(self):
        if self.kind == "bolt":
            try:
                self.session.close()
            finally:
                self.conn.close()

        elif self.kind == "age":
            self.cursor.close()
            self.conn.close()

        # FalkorDB graph handles don't require explicit closing; the
        # underlying Redis connection is managed by the client library.

    def _run_age(self, query, params):
        cypher_query = query

        for key, value in params.items():
            cypher_query = cypher_query.replace(
                f"${key}",
                f"'{value}'",
            )

        normalized = " ".join(cypher_query.split())

        if "RETURN u.id, count(*) AS votes" in normalized:
            column_definition = "(id agtype, votes agtype)"
        else:
            column_definition = "(result agtype)"

        sql = f"""
        SELECT *
        FROM cypher(
            '{AGE_GRAPH}',
            $$ {cypher_query} $$
        ) AS {column_definition}
        """

        self.cursor.execute(sql)

        return self.cursor.fetchall()

# Sampling helpers
def get_all_ids(runner):
    """Fetch every User.id currently stored in the database."""
    rows = runner.run("MATCH (u:User) RETURN u.id AS id")
    return [row[0] for row in rows]


def build_id_sequence(ids, count, seed=RANDOM_SEED):
    """
    Deterministically pre-generate `count` ids (with replacement) so the
    same sequence of ids is used across the warm-up and measured phases
    of a given benchmark run.
    """
    if not ids:
        raise ValueError("No ids available to sample from; is the database populated?")
    rng = random.Random(seed)
    return rng.choices(ids, k=count)



# Benchmark loop
def run_benchmark(query_fn, warmup=WARMUP_ITERATIONS, iterations=MEASURED_ITERATIONS):
    """
    Run `query_fn` (a zero-arg callable executing one query) `warmup`
    times without measuring, then `iterations` times while recording
    per-call latency in milliseconds using time.perf_counter().

    Returns a list of latencies in milliseconds for the measured phase.
    """
    for _ in range(warmup):
        query_fn()

    latencies_ms = []
    for _ in range(iterations):
        start = time.perf_counter()
        query_fn()
        latencies_ms.append((time.perf_counter() - start) * 1000.0)

    return latencies_ms


# Statistics
def compute_stats(latencies_ms):
    """Compute count, mean, min, max, p50, and p95 latency in milliseconds."""
    if not latencies_ms:
        return {
            "count": 0,
            "mean_ms": None,
            "min_ms": None,
            "max_ms": None,
            "p50_ms": None,
            "p95_ms": None,
        }

    ordered = sorted(latencies_ms)

    if len(ordered) >= 2:
        cut_points = statistics.quantiles(ordered, n=100, method="inclusive")
        p50 = cut_points[49]
        p95 = cut_points[94]
    else:
        p50 = p95 = ordered[0]

    return {
        "count": len(ordered),
        "mean_ms": round(statistics.mean(ordered), 4),
        "min_ms": round(ordered[0], 4),
        "max_ms": round(ordered[-1], 4),
        "p50_ms": round(p50, 4),
        "p95_ms": round(p95, 4),
    }


def save_json(filename, data):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    return path


def utc_timestamp():
    return datetime.now(timezone.utc).isoformat()
