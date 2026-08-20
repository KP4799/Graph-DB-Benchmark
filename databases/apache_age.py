import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

AGE_HOST = os.getenv("AGE_HOST", "localhost")
AGE_PORT = os.getenv("AGE_PORT", "5432")
AGE_DATABASE = os.getenv("AGE_DATABASE", "postgres")
AGE_USER = os.getenv("AGE_USER", "postgres")
AGE_PASSWORD = os.getenv("AGE_PASSWORD", "")
AGE_GRAPH = os.getenv("AGE_GRAPH", "benchmark")

def connect():
    conn = psycopg2.connect(
        host=AGE_HOST,
        port=AGE_PORT,
        dbname=AGE_DATABASE,
        user=AGE_USER,
        password=AGE_PASSWORD,
    )

    cur = conn.cursor()
    cur.execute("LOAD 'age';")
    cur.execute("SET search_path = ag_catalog, '$user', public;")
    conn.commit()
    return conn


def health_check():
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM ag_graph;")
        cur.fetchall()
        return True

    except Exception as exc:
        print(exc)
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    print(f"Apache AGE healthy: {health_check()}")