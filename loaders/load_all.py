import json
import os

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loaders import import_neo4j
from loaders import import_memgraph
from loaders import import_falkordb
from loaders import import_cognodb
from loaders import import_apache_age


LOADERS = {
    "neo4j": import_neo4j,
    "memgraph": import_memgraph,
    "falkordb": import_falkordb,
    "cognodb": import_cognodb,
    "apache_age": import_apache_age,
}


def load_all():
    results = {}

    for name, module in LOADERS.items():
        print(f"Loading {name}...")
        results[name] = module.main()

    os.makedirs("results", exist_ok=True)

    with open("results/loading_time.json","w",encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results

if __name__ == "__main__":
    load_all()