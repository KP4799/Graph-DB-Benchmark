"""
falkordb.py

Connection module for FalkorDB.

Reads credentials from a .env file and exposes:
    - connect(): create/return a FalkorDB client + selected graph
    - health_check(): run a trivial query to verify the connection is alive

Requirements:
    pip install falkordb python-dotenv

Expected .env variables:
    FALKORDB_HOST=localhost
    FALKORDB_PORT=6379
    FALKORDB_PASSWORD=
    FALKORDB_GRAPH_NAME=wiki_vote

Note: this module is named falkordb.py per the assignment. Be careful not
to let it shadow the installed `falkordb` package if both live on the same
import path (e.g. run it from a different working directory, or rename
this file locally if you hit circular-import errors).
"""

import os
from dotenv import load_dotenv
from falkordb import FalkorDB

load_dotenv()

FALKORDB_HOST = os.environ.get("FALKORDB_HOST", "localhost")
FALKORDB_PORT = int(os.environ.get("FALKORDB_PORT", "6379"))
FALKORDB_PASSWORD = os.environ.get("FALKORDB_PASSWORD") or None
FALKORDB_GRAPH_NAME = os.environ.get("FALKORDB_GRAPH_NAME", "wiki_vote")

HEALTH_CHECK_QUERY = "RETURN 1 AS ok"


def connect():
    """
    Create a FalkorDB client and return the selected graph object used for
    running Cypher queries.
    """
    db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT, password=FALKORDB_PASSWORD)
    graph = db.select_graph(FALKORDB_GRAPH_NAME)
    return graph


def health_check(graph=None):
    """
    Run a trivial query against FalkorDB to confirm the connection is
    healthy.

    Returns True if the query succeeds and returns the expected result,
    False otherwise. Accepts an existing graph handle, or creates one if
    none is provided.
    """
    if graph is None:
        graph = connect()

    try:
        result = graph.query(HEALTH_CHECK_QUERY)
        rows = result.result_set
        return len(rows) > 0 and rows[0][0] == 1
    
    except Exception as exc:
        print(f"FalkorDB health check failed: {exc}")
        return False


if __name__ == "__main__":
    is_healthy = health_check()
    print(f"FalkorDB healthy: {is_healthy}")