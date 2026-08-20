"""
prepare_dataset.py

Reads a SNAP-style edge list (data/raw/wiki-Vote.txt), strips comment
lines, extracts the unique node IDs, and writes two CSV files:
    - data/nodes.csv  (columns: id)
    - data/edges.csv  (columns: source,target)

Also prints the number of nodes and the number of relationships (edges).
"""

import csv
import os

INPUT_PATH = os.path.join("data", "raw", "wiki-Vote.txt")
NODES_OUTPUT_PATH = os.path.join("data", "nodes.csv")
EDGES_OUTPUT_PATH = os.path.join("data", "edges.csv")


def parse_edges(input_path):
    """Read the raw file, skip comment lines, and return a list of
    (source, target) tuples plus the set of unique node ids."""
    edges = []
    nodes = set()

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Ignore blank lines and comment lines (SNAP files use '#')
            if not line or line.startswith("#"):
                continue

            # Edges are typically whitespace/tab separated: "source target"
            parts = line.split()
            if len(parts) < 2:
                # Skip malformed lines instead of crashing
                continue

            source, target = parts[0], parts[1]

            edges.append((source, target))
            nodes.add(source)
            nodes.add(target)

    return edges, nodes


def write_nodes_csv(nodes, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id"])
        for node_id in sorted(nodes, key=lambda x: (len(x), x)):
            writer.writerow([node_id])


def write_edges_csv(edges, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target"])
        for source, target in edges:
            writer.writerow([source, target])


def main():
    edges, nodes = parse_edges(INPUT_PATH)

    write_nodes_csv(nodes, NODES_OUTPUT_PATH)
    write_edges_csv(edges, EDGES_OUTPUT_PATH)

    print(f"Number of nodes: {len(nodes)}")
    print(f"Number of relationships: {len(edges)}")


if __name__ == "__main__":
    main()