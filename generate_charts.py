import json
import os

import matplotlib.pyplot as plt


RESULTS_DIR = "results"
CHARTS_DIR = os.path.join(RESULTS_DIR, "charts")


def load_json(filename):
    path = os.path.join(RESULTS_DIR, filename)

    if not os.path.exists(path):
        print(f"Skipping {filename}: file not found.")
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_chart(filename):
    os.makedirs(CHARTS_DIR, exist_ok=True)
    path = os.path.join(CHARTS_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Created {path}")


def add_bar_labels(ax, bars):
    for bar in bars:
        height = bar.get_height()

        if height <= 0:
            continue

        ax.annotate(
            f"{height:.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            rotation=0,
        )


def generate_loading_chart(metric, title, ylabel, filename):
    data = load_json("loading_time.json")

    if not data:
        return

    databases = []
    values = []

    for db, result in data.items():
        value = result.get(metric)

        if value is not None:
            databases.append(db)
            values.append(value)

    if not values:
        return

    fig, ax = plt.subplots(figsize=(12, 7))

    bars = ax.bar(databases, values)

    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_yscale("log")

    ax.grid(axis="y", alpha=0.3)

    add_bar_labels(ax, bars)

    plt.xticks(rotation=20)
    save_chart(filename)


def generate_lookup_chart():
    data = load_json("lookups.json")

    if not data:
        return

    databases = []
    point_values = []
    indexed_values = []

    for db, result in data.get("databases", {}).items():
        if result.get("status") != "ok":
            continue

        queries = result.get("queries", {})

        point = queries.get("point_lookup", {})
        indexed = queries.get("indexed_lookup", {})

        point_p95 = point.get("stats", {}).get("p95_ms")
        indexed_p95 = indexed.get("stats", {}).get("p95_ms")

        if point_p95 is None or indexed_p95 is None:
            continue

        databases.append(db)
        point_values.append(point_p95)
        indexed_values.append(indexed_p95)

    if not databases:
        return

    x = range(len(databases))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 7))

    bars1 = ax.bar(
        [i - width / 2 for i in x],
        point_values,
        width,
        label="Point lookup",
    )

    bars2 = ax.bar(
        [i + width / 2 for i in x],
        indexed_values,
        width,
        label="Indexed lookup",
    )

    ax.set_title("Lookup Performance (P95)")
    ax.set_ylabel("Latency (ms)")
    ax.set_yscale("log")
    ax.set_xticks(list(x))
    ax.set_xticklabels(databases, rotation=20)
    ax.legend()

    ax.grid(axis="y", alpha=0.3)

    add_bar_labels(ax, bars1)
    add_bar_labels(ax, bars2)

    save_chart("lookups.png")


def generate_aggregation_chart():
    data = load_json("aggregations.json")

    if not data:
        return

    databases = []
    values = []

    for db, result in data.get("databases", {}).items():
        if result.get("status") != "ok":
            continue

        stats = result.get("stats", {})
        value = stats.get("p95_ms")

        if value is None:
            continue

        databases.append(db)
        values.append(value)

    if not databases:
        print("No successful aggregation results found.")
        return

    fig, ax = plt.subplots(figsize=(12, 7))

    bars = ax.bar(databases, values)

    ax.set_title("Aggregation Performance (P95)")
    ax.set_ylabel("Latency (ms)")
    ax.set_yscale("log")

    ax.grid(axis="y", alpha=0.3)

    add_bar_labels(ax, bars)

    plt.xticks(rotation=20)

    save_chart("aggregations.png")


def generate_mixed_workload_chart():
    data = load_json("mixed_workload.json")

    if not data:
        return

    databases = []
    values = []

    for db, result in data.get("databases", {}).items():
        if result.get("status") != "ok":
            continue

        value = result.get("stats", {}).get("sustained_qps")

        if value is None:
            continue

        databases.append(db)
        values.append(value)

    if not databases:
        return

    fig, ax = plt.subplots(figsize=(12, 7))

    bars = ax.bar(databases, values)

    ax.set_title("Mixed Workload Throughput")
    ax.set_ylabel("Sustained QPS")
    ax.set_yscale("log")

    ax.grid(axis="y", alpha=0.3)

    add_bar_labels(ax, bars)

    plt.xticks(rotation=20)

    save_chart("mixed_workload_qps.png")


def generate_traversal_chart():
    data = load_json("traversals.json")

    if not data:
        return

    databases = []

    one_hop = []
    two_hop = []
    three_hop = []

    for db, result in data.get("databases", {}).items():
        if result.get("status") != "ok":
            continue

        queries = result.get("queries", {})

        values = []

        for query_name in ["one_hop", "two_hop", "three_hop"]:
            query = queries.get(query_name, {})

            if query.get("status") != "ok":
                values.append(None)
                continue

            value = query.get("stats", {}).get("p95_ms")
            values.append(value)

        if all(value is None for value in values):
            continue

        databases.append(db)
        one_hop.append(values[0])
        two_hop.append(values[1])
        three_hop.append(values[2])

    if not databases:
        return

    x = range(len(databases))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 7))

    def safe_values(values):
        return [value if value is not None else float("nan") for value in values]

    bars1 = ax.bar(
        [i - width for i in x],
        safe_values(one_hop),
        width,
        label="1-hop",
    )

    bars2 = ax.bar(
        x,
        safe_values(two_hop),
        width,
        label="2-hop",
    )

    bars3 = ax.bar(
        [i + width for i in x],
        safe_values(three_hop),
        width,
        label="3-hop",
    )

    ax.set_title("Traversal Performance (P95)")
    ax.set_ylabel("Latency (ms)")
    ax.set_yscale("log")
    ax.set_xticks(list(x))
    ax.set_xticklabels(databases, rotation=20)
    ax.legend()

    ax.grid(axis="y", alpha=0.3)

    add_bar_labels(ax, bars1)
    add_bar_labels(ax, bars2)
    add_bar_labels(ax, bars3)

    save_chart("traversals.png")


def main():
    os.makedirs(CHARTS_DIR, exist_ok=True)

    generate_loading_chart(
        "nodes_per_second",
        "Node Loading Throughput",
        "Nodes / second",
        "loading_nodes_per_second.png",
    )

    generate_loading_chart(
        "relationships_per_second",
        "Relationship Loading Throughput",
        "Relationships / second",
        "loading_relationships_per_second.png",
    )

    generate_loading_chart(
        "wall_clock_seconds",
        "Database Loading Time",
        "Seconds",
        "loading_time.png",
    )

    generate_lookup_chart()
    generate_aggregation_chart()
    generate_mixed_workload_chart()
    generate_traversal_chart()

    print("\nAll charts generated.")


if __name__ == "__main__":
    main()