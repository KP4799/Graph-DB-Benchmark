"""
neo4j_db.py

Connection module for Neo4j.

Reads credentials from a .env file and exposes:
    - get_driver() / connect(): create/return a Neo4j driver instance
    - health_check(): run a trivial query to verify the connection is alive

Requirements:
    pip install neo4j python-dotenv

Expected .env variables:
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=password
    NEO4J_DATABASE=neo4j
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")
NEO4J_DATABASE = os.environ.get("NEO4J_DATABASE", "neo4j")

HEALTH_CHECK_QUERY = "RETURN 1 AS ok"


def connect():
    """Create and return a Neo4j driver instance."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    driver.verify_connectivity()
    return driver


def health_check(driver=None):
    """
    Run a trivial query against Neo4j to confirm the connection is healthy.

    Returns True if the query succeeds and returns the expected result,
    False otherwise. Accepts an existing driver, or creates/closes a
    temporary one if none is provided.
    """
    owns_driver = driver is None
    if owns_driver:
        driver = connect()

    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(HEALTH_CHECK_QUERY)
            record = result.single()
            return record is not None and record["ok"] == 1
    except Exception as exc:
        print(f"Neo4j health check failed: {exc}")
        return False
    
    finally:
        if owns_driver:
            driver.close()


if __name__ == "__main__":
    is_healthy = health_check()
    print(f"Neo4j healthy: {is_healthy}")