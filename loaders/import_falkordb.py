"""
import_falkordb.py

Batch-loads data/nodes.csv and data/edges.csv into FalkorDB using the graph
model:

    (:User {id})
    (:User)-[:VOTED_FOR]->(:User)

Measures wall-clock loading time and reports:
    - Nodes per second
    - Relationships per second
    - Total wall-clock loading time

Requirements:
    pip install falkordb

Configure connection details via environment variables or edit the
constants below.
"""

import csv
import os
import time
from dotenv import load_dotenv
from falkordb import FalkorDB

load_dotenv()

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

FALKORDB_HOST = os.environ.get("FALKORDB_HOST", "localhost")
FALKORDB_PORT = int(os.environ.get("FALKORDB_PORT", "6379"))
FALKORDB_GRAPH_NAME = os.environ.get("FALKORDB_GRAPH_NAME", "wiki_vote")

NODES_CSV_PATH = os.path.join("data", "nodes.csv")
EDGES_CSV_PATH = os.path.join("data", "edges.csv")

BATCH_SIZE = 1000

# --------------------------------------------------------------------------
# Cypher statements
# --------------------------------------------------------------------------

CREATE_INDEX_QUERY = "CREATE INDEX FOR (u:User) ON (u.id)"

CREATE_NODES_QUERY = """
UNWIND $batch AS row
MERGE (u:User {id: row.id})
"""

CREATE_EDGES_QUERY = """
UNWIND $batch AS row
MATCH (source:User {id: row.source})
MATCH (target:User {id: row.target})
CREATE (source)-[:VOTED_FOR]->(target)
"""


def read_csv_rows(path):
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def chunked(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def ensure_index(graph):
    try:
        graph.query(CREATE_INDEX_QUERY)
    except Exception as exc:
        print(f"Warning: could not create index ({exc}). Continuing without it.")


def reset_graph(db):
    try:
        db.delete_graph(FALKORDB_GRAPH_NAME)
    except Exception:
        pass

    return db.select_graph(FALKORDB_GRAPH_NAME)


def load_nodes(graph, nodes):
    for batch in chunked(nodes, BATCH_SIZE):
        graph.query(CREATE_NODES_QUERY, params={"batch": batch})


def load_edges(graph, edges):
    for batch in chunked(edges, BATCH_SIZE):
        graph.query(CREATE_EDGES_QUERY, params={"batch": batch})


def main():
    nodes = read_csv_rows(NODES_CSV_PATH)
    edges = read_csv_rows(EDGES_CSV_PATH)

    db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
    graph = reset_graph(db)
    ensure_index(graph)

    wall_clock_start = time.perf_counter()

    node_start = time.perf_counter()
    load_nodes(graph, nodes)
    node_elapsed = time.perf_counter() - node_start

    edge_start = time.perf_counter()
    load_edges(graph, edges)
    edge_elapsed = time.perf_counter() - edge_start

    wall_clock_elapsed = time.perf_counter() - wall_clock_start

    nodes_per_sec = len(nodes) / node_elapsed if node_elapsed > 0 else float("inf")
    edges_per_sec = len(edges) / edge_elapsed if edge_elapsed > 0 else float("inf")

    metrics = {
        "nodes_loaded": len(nodes),
        "relationships_loaded": len(edges),
        "nodes_per_second": round(nodes_per_sec, 2),
        "relationships_per_second": round(edges_per_sec, 2),
        "wall_clock_seconds": round(wall_clock_elapsed, 2),
    }

    print("FalkorDB import complete")
    return metrics

if __name__ == "__main__":
    main()
