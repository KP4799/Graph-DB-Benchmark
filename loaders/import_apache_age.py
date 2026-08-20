import os
import time

import psycopg2
from dotenv import load_dotenv

load_dotenv()

AGE_HOST = os.getenv("AGE_HOST", "localhost")
AGE_PORT = os.getenv("AGE_PORT", "5432")
AGE_DATABASE = os.getenv("AGE_DATABASE", "postgres")
AGE_USER = os.getenv("AGE_USER", "postgres")
AGE_PASSWORD = os.getenv("AGE_PASSWORD", "password")
AGE_GRAPH = os.getenv("AGE_GRAPH", "benchmark")

NODES_CSV_PATH = os.path.join("data", "nodes.csv")
EDGES_CSV_PATH = os.path.join("data", "edges.csv")


def connect():
    conn = psycopg2.connect(
        host=AGE_HOST,
        port=AGE_PORT,
        dbname=AGE_DATABASE,
        user=AGE_USER,
        password=AGE_PASSWORD,
    )

    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("LOAD 'age';")
    cur.execute("SET search_path = ag_catalog, '$user', public;")
    return conn


def recreate_graph(cur):
    try:
        cur.execute(f"SELECT drop_graph('{AGE_GRAPH}', true);")
    except Exception:
        pass

    cur.execute(f"SELECT create_graph('{AGE_GRAPH}');")


def create_staging_tables(cur):
    cur.execute("DROP TABLE IF EXISTS nodes_import;")
    cur.execute("DROP TABLE IF EXISTS edges_import;")

    cur.execute(
        """
        CREATE TABLE nodes_import (
            id TEXT
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE edges_import (
            source TEXT,
            target TEXT
        );
        """
    )


def load_csv_into_tables(cur):
    with open(NODES_CSV_PATH, "r", encoding="utf-8") as f:
        cur.copy_expert(
            """
            COPY nodes_import(id)
            FROM STDIN
            WITH CSV HEADER
            """,
            f,
        )

    with open(EDGES_CSV_PATH, "r", encoding="utf-8") as f:
        cur.copy_expert(
            """
            COPY edges_import(source, target)
            FROM STDIN
            WITH CSV HEADER
            """,
            f,
        )


def count_rows(cur, table):
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    return cur.fetchone()[0]


def create_graph_nodes(cur):
    cur.execute("SELECT id FROM nodes_import;")

    for (node_id,) in cur.fetchall():
        cur.execute(
            f"""
            SELECT *
            FROM cypher(
                '{AGE_GRAPH}',
                $$ CREATE (:User {{id: '{node_id}'}}) $$
            ) AS (v agtype);
            """
        )


def create_graph_edges(cur):
    cur.execute("SELECT source, target FROM edges_import;")

    for source, target in cur.fetchall():
        cur.execute(
            f"""
            SELECT *
            FROM cypher(
                '{AGE_GRAPH}',
                $$
                MATCH (a:User {{id: '{source}'}})
                MATCH (b:User {{id: '{target}'}})
                CREATE (a)-[:VOTED_FOR]->(b)
                $$
            ) AS (v agtype);
            """
        )


def main():
    conn = connect()
    cur = conn.cursor()

    try:
        recreate_graph(cur)
        create_staging_tables(cur)
        load_csv_into_tables(cur)

        node_count = count_rows(cur, "nodes_import")
        edge_count = count_rows(cur, "edges_import")

        wall_start = time.perf_counter()
        
        node_start = time.perf_counter()
        create_graph_nodes(cur)
        node_elapsed = time.perf_counter() - node_start

        edge_start = time.perf_counter()
        create_graph_edges(cur)
        edge_elapsed = time.perf_counter() - edge_start

        wall_elapsed = time.perf_counter() - wall_start

    finally:
        conn.close()

    metrics = {
        "nodes_loaded": node_count,
        "relationships_loaded": edge_count,
        "nodes_per_second": round(node_count / node_elapsed, 2),
        "relationships_per_second": round(edge_count / edge_elapsed, 2),
        "wall_clock_seconds": round(wall_elapsed, 2),
    }

    print("Apache AGE import complete")
    return metrics


if __name__ == "__main__":
    main()