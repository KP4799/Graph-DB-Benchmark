"""
memgraph_db.py

Connection module for Memgraph.

Memgraph speaks the Bolt protocol and Cypher, so it is accessed using the
official Neo4j Python driver, which is Memgraph's recommended Python
client.

Reads credentials from a .env file and exposes:
    - connect(): create/return a driver instance
    - health_check(): run a trivial query to verify the connection is alive

Requirements:
    pip install neo4j python-dotenv

Expected .env variables:
    MEMGRAPH_URI=bolt://localhost:7687
    MEMGRAPH_USER=
    MEMGRAPH_PASSWORD=
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

MEMGRAPH_URI = os.environ.get("MEMGRAPH_URI", "bolt://localhost:7687")
MEMGRAPH_USER = os.environ.get("MEMGRAPH_USER", "")
MEMGRAPH_PASSWORD = os.environ.get("MEMGRAPH_PASSWORD", "")

HEALTH_CHECK_QUERY = "RETURN 1 AS ok"


def connect():
    """Create and return a driver instance connected to Memgraph."""
    driver = GraphDatabase.driver(MEMGRAPH_URI, auth=(MEMGRAPH_USER, MEMGRAPH_PASSWORD))
    driver.verify_connectivity()
    return driver


def health_check(driver=None):
    """
    Run a trivial query against Memgraph to confirm the connection is
    healthy.

    Returns True if the query succeeds and returns the expected result,
    False otherwise. Accepts an existing driver, or creates/closes a
    temporary one if none is provided.
    """
    owns_driver = driver is None
    if owns_driver:
        driver = connect()

    try:
        with driver.session() as session:
            result = session.run(HEALTH_CHECK_QUERY)
            record = result.single()
            return record is not None and record["ok"] == 1
    except Exception as exc:
        print(f"Memgraph health check failed: {exc}")
        return False
    
    finally:
        if owns_driver:
            driver.close()


if __name__ == "__main__":
    is_healthy = health_check()
    print(f"Memgraph healthy: {is_healthy}")