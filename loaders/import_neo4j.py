"""
import_neo4j.py

Batch-loads data/nodes.csv and data/edges.csv into Neo4j using the graph
model:

    (:User {id})
    (:User)-[:VOTED_FOR]->(:User)

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

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")
NEO4J_DATABASE = os.environ.get("NEO4J_DATABASE", "neo4j")

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
    with driver.session(database=NEO4J_DATABASE) as session:
        session.run("MATCH (n) DETACH DELETE n")


def ensure_constraint(driver):
    with driver.session(database=NEO4J_DATABASE) as session:
        session.run(CREATE_CONSTRAINT_QUERY)


def load_nodes(driver, nodes):
    with driver.session(database=NEO4J_DATABASE) as session:
        for batch in chunked(nodes, BATCH_SIZE):
            session.execute_write(lambda tx, b=batch: tx.run(CREATE_NODES_QUERY, batch=b))


def load_edges(driver, edges):
    with driver.session(database=NEO4J_DATABASE) as session:
        for batch in chunked(edges, BATCH_SIZE):
            session.execute_write(lambda tx, b=batch: tx.run(CREATE_EDGES_QUERY, batch=b))


def main():
    nodes = read_csv_rows(NODES_CSV_PATH)
    edges = read_csv_rows(EDGES_CSV_PATH)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

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

    print("Neo4j import complete")
    return metrics


if __name__ == "__main__":
    main()
