"""
cognodb.py

Connection module for CognoDB.

CognoDB speaks the Bolt protocol and Cypher, so it is accessed using the
official Neo4j Python driver pointed at the CognoDB instance.

Reads credentials from a .env file and exposes:
    - connect(): create/return a driver instance
    - health_check(): run a trivial query to verify the connection is alive

Requirements:
    pip install neo4j python-dotenv

Expected .env variables:
    COGNODB_URI=bolt://localhost:7688
    COGNODB_USER=cognodb
    COGNODB_PASSWORD=password
    COGNODB_DATABASE=
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

COGNODB_URI = os.environ.get("COGNODB_URI")
COGNODB_USER = os.environ.get("COGNODB_USER", "cognodb")
COGNODB_PASSWORD = os.environ.get("COGNODB_PASSWORD")
COGNODB_DATABASE = os.environ.get("COGNODB_DATABASE") or None

HEALTH_CHECK_QUERY = "RETURN 1 AS ok"


def connect():
    """Create and return a driver instance connected to CognoDB."""
    driver = GraphDatabase.driver(COGNODB_URI, auth=(COGNODB_USER, COGNODB_PASSWORD))
    driver.verify_connectivity()
    return driver


def health_check(driver=None):
    """
    Run a trivial query against CognoDB to confirm the connection is
    healthy.

    Returns True if the query succeeds and returns the expected result,
    False otherwise. Accepts an existing driver, or creates/closes a
    temporary one if none is provided.
    """
    owns_driver = driver is None
    if owns_driver:
        driver = connect()

    try:
        with driver.session(database=COGNODB_DATABASE) as session:
            result = session.run(HEALTH_CHECK_QUERY)
            record = result.single()
            return record is not None and record["ok"] == 1
        
    except Exception as exc:
        print(f"CognoDB health check failed: {exc}")
        return False
    
    finally:
        if owns_driver:
            driver.close()


if __name__ == "__main__":
    is_healthy = health_check()
    print(f"CognoDB healthy: {is_healthy}")