"""
import_cognodb.py

Batch-loads data/nodes.csv and data/edges.csv into CognoDB using the graph
model:

    (:User {id})
    (:User)-[:VOTED_FOR]->(:User)

CognoDB speaks the Bolt protocol and Cypher, so it is loaded using the
official Neo4j Python driver pointed at the CognoDB instance.

Measures wall-clock loading time and reports:
    - Nodes per second
    - Relationships per second
    - Total wall-clock loading time

Requirements:
    pip install neo4j

Configure connection details via environment variables or edit the
constants below.
"""

import csv
import os
import time
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

COGNODB_URI = os.environ.get("COGNODB_URI", "bolt://localhost:7688")
COGNODB_USER = os.environ.get("COGNODB_USER", "cognodb")
COGNODB_PASSWORD = os.environ.get("COGNODB_PASSWORD", "password")
COGNODB_DATABASE = os.environ.get("COGNODB_DATABASE", None)  # None uses server default

NODES_CSV_PATH = os.path.join("data", "nodes.csv")
EDGES_CSV_PATH = os.path.join("data", "edges.csv")

BATCH_SIZE = 1000

# --------------------------------------------------------------------------
# Cypher statements
# --------------------------------------------------------------------------

CREATE_CONSTRAINT_QUERY = """
CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.id IS UNIQUE
"""

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


def clear_database(driver):
    with driver.session(database=COGNODB_DATABASE) as session:
        result = session.run("MATCH (n) DETACH DELETE n")
        result.consume()


def ensure_constraint(driver):
    with driver.session(database=COGNODB_DATABASE) as session:
        try:
            session.run(CREATE_CONSTRAINT_QUERY)
        except Exception as exc:
            print(f"Warning: could not create constraint ({exc}). Continuing without it.")

def load_nodes(driver, nodes):
    with driver.session(database=COGNODB_DATABASE) as session:

        for batch in chunked(nodes, BATCH_SIZE):

            def insert(tx, b=batch):
                result = tx.run(
                    CREATE_NODES_QUERY,
                    batch=b
                )
                result.consume()

            session.execute_write(insert)

def load_edges(driver, edges):
    with driver.session(database=COGNODB_DATABASE) as session:
        for batch in chunked(edges, BATCH_SIZE):
            def insert(tx, b=batch):
                result = tx.run(
                    CREATE_EDGES_QUERY,
                    batch=b
                )
                result.consume()

            session.execute_write(insert)

def main():
    nodes = read_csv_rows(NODES_CSV_PATH)
    edges = read_csv_rows(EDGES_CSV_PATH)

    driver = GraphDatabase.driver(COGNODB_URI, auth=(COGNODB_USER, COGNODB_PASSWORD))

    try:
        driver.verify_connectivity()
        clear_database(driver)
        ensure_constraint(driver)

        wall_clock_start = time.perf_counter()

        node_start = time.perf_counter()
        load_nodes(driver, nodes)
        node_elapsed = time.perf_counter() - node_start

        edge_start = time.perf_counter()
        load_edges(driver, edges)
        edge_elapsed = time.perf_counter() - edge_start

        wall_clock_elapsed = time.perf_counter() - wall_clock_start

    finally:
        driver.close()

    nodes_per_sec = len(nodes) / node_elapsed if node_elapsed > 0 else float("inf")
    edges_per_sec = len(edges) / edge_elapsed if edge_elapsed > 0 else float("inf")

    metrics = {
        "nodes_loaded": len(nodes),
        "relationships_loaded": len(edges),
        "nodes_per_second": round(nodes_per_sec, 2),
        "relationships_per_second": round(edges_per_sec, 2),
        "wall_clock_seconds": round(wall_clock_elapsed, 2),
    }

    print("CognoDB import complete")
    return metrics

if __name__ == "__main__":
    main()
