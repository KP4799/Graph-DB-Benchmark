# Graph Database Benchmark Suite

A benchmarking framework for comparing the performance of multiple graph database systems using the SNAP Wiki-Vote dataset.

The framework evaluates the following graph databases:

- Neo4j
- Memgraph
- FalkorDB
- CognoDB
- Apache AGE

The benchmark focuses on graph-specific operations, including data loading, graph traversals, node lookups, aggregation queries, and mixed read/write workloads.

---

## Dataset

This project uses the **Wiki-Vote** dataset from the **Stanford Network Analysis Project (SNAP)**.

The dataset represents Wikipedia administrator elections as a directed graph:

- Vertices represent users.
- Directed edges represent votes between users.

### Dataset Statistics

| Metric | Value |
| --- | --- |
| Nodes | 7,115 |
| Relationships | 103,689 |

### Graph Model

```cypher
(:User {id})

(:User)-[:VOTED_FOR]->(:User)
```

### Dataset Files

```text
data/
├── nodes.csv
└── edges.csv
```

---

## Project Structure

```text
.
├── benchmarks/
│   ├── aggregations.py
│   ├── bench_common.py
│   ├── lookups.py
│   ├── mixed_workload.py
│   ├── run_all.py
│   └── traversals.py
│
├── databases/
│   ├── apache_age.py
│   ├── cognodb.py
│   ├── falkordb_db.py
│   ├── memgraph_db.py
│   └── neo4j_db.py
│
├── loaders/
│   ├── import_apache_age.py
│   ├── import_cognodb.py
│   ├── import_falkordb.py
│   ├── import_memgraph.py
│   ├── import_neo4j.py
│   └── load_all.py
│
├── data/
├── results/
│   └── charts/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Requirements

- Python 3.10+
- Docker
- Docker Compose

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd <repository-name>
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Start the database containers:

```bash
docker compose up -d
```

Verify that all containers are running:

```bash
docker compose ps
```

---

## Running the entire pipeline

To run the entire pipeline run:

```bash
python run_benchmarks.py
```

The pipeline automatically:

- Clears previously loaded data.
- Creates a new graph when required.
- Imports all nodes.
- Imports all relationships.
- Measures loading performance.
- Tests all benchmarks.
- Stores the result of respective benchmarks.
- Generates charts to help visualize the results.

## Loading the same dataset to all databases

```bash
python loaders/load_all.py
```

## Running Individual Benchmarks

### Traversal Benchmark

```bash
python -m benchmarks.traversals
```

Output:

```text
results/traversals.json
```

---

### Lookup Benchmark

```bash
python -m benchmarks.lookups
```

Output:

```text
results/lookups.json
```

---

### Aggregation Benchmark

```bash
python -m benchmarks.aggregations
```

Output:

```text
results/aggregations.json
```

---

### Mixed Workload Benchmark

```bash
python -m benchmarks.mixed_workload
```

Output:

```text
results/mixed_workload.json
```
---

## Benchmark Charts

Charts are generated from the JSON benchmark results and provide visual comparisons of the measured database performance.

Charts cover:

- Loading throughput
- Loading time
- Traversal latency
- Lookup latency
- Aggregation latency
- Mixed-workload throughput

The charts are generated from the recorded benchmark results rather than manually entered values.

### Chart Interpretation

- Loading charts compare nodes/second, relationships/second, and total loading time.
- Traversal charts compare latency across one-hop, two-hop, and three-hop traversals.
- Lookup charts compare point and indexed lookup latency.
- The aggregation chart compares aggregation latency.
- The mixed-workload chart compares sustained QPS.
- Latency values are shown in milliseconds (ms).
- Throughput values are shown as operations per second or queries per second (QPS).

Some database results differ by large multiples. Logarithmic scaling is therefore used where necessary so that results from all databases remain visible in the same chart.

Bar-value labels are displayed directly on the bars where appropriate.

A failed or unavailable benchmark result is not treated as zero. It is displayed as unavailable or failed instead.

The charts are intended as visual summaries. The JSON files in `results/` remain the authoritative machine-readable benchmark results.

---

### Generating Charts

Run:

```bash
python generate_charts.py
```

---

## Results Directory

```text
results/
├── aggregations.json
├── loading_time.json
├── lookups.json
├── mixed_workload.json
├── summary.json
├── traversals.json
└── charts/

```

## Benchmark Queries and Results

### 1. Data Loading

Measures the efficiency of dataset ingestion.

Query:

```cypher
(:User {id})

(:User)-[:VOTED_FOR]->(:User)
```

Recorded metrics:

- Nodes loaded
- Relationships loaded
- Nodes per second
- Relationships per second
- Total loading time

### Results

| Database | Nodes/sec | Relationships/sec | Total Time (s) |
| --- | ---: | ---: | ---: |
| Neo4j | 3,949.04 | 13,067.11 | 9.74 |
| Memgraph | 80,273.63 | 67047.43 | 1.64 |
| FalkorDB | 11,7243.5 | 10,6942.33 | 1.03 |
| CognoDB | 626.18 | 623.90 | 177.56 |
| Apache AGE | 2457.60 | 300.71 | 347.71 |

---

### 2. Traversal Performance

Measures the latency of graph traversal operations.

Queries:

**1-Hop Traversal**

```cypher
MATCH (u:User {id:$id})-[:VOTED_FOR]->(n)
RETURN count(n)
```

**2-Hop Traversal**

```cypher
MATCH (u:User {id:$id})-[:VOTED_FOR*2]->(n)
RETURN count(n)
```

**3-Hop Traversal**

```cypher
MATCH (u:User {id:$id})-[:VOTED_FOR*3]->(n)
RETURN count(n)
```

Recorded metrics:

- Mean latency
- Minimum latency
- Maximum latency
- P50 latency
- P95 latency

### Results (Mean Latency in ms)

| Database | 1-Hop | 2-Hop | 3-Hop |
| --- | ---: | ---: | ---: |
| Neo4j | 3.82 | 3.99 | 15.07 |
| Memgraph | 0.41 | 0.47 | 2.98 |
| FalkorDB | 0.40 | 0.45 | 1.94 |
| CognoDB | 307.19 | 316.42 | Failed |
| Apache AGE | 1.78 | 7.43 | 7.47 |

---

### 3. Lookup Performance

Measures the efficiency of node retrieval.

Queries:

**Point Lookup**

```cypher
MATCH (u:User {id:$id})
RETURN u
```

**Indexed Lookup**

```cypher
MATCH (u:User)
WHERE u.id >= $id
RETURN count(u)
```

Recorded metrics:

- Mean latency
- Minimum latency
- Maximum latency
- P50 latency
- P95 latency

### Results (Mean Latency in ms)

| Database | Point Lookup | Indexed Lookup |
| --- | ---: | ---: |
| Neo4j | 2.78 | 3.72 |
| Memgraph | 0.41 | 0.93 |
| FalkorDB | 0.36 | 2.77 |
| CognoDB | 304.56 | 307.20 |
| Apache AGE | 1.67 | 4.74 |

---

### 4. Aggregation Performance

Measures the execution time of aggregation queries.

Query:

```cypher
MATCH (u:User)-[:VOTED_FOR]->()
RETURN u.id, count(*) AS votes
ORDER BY votes DESC
LIMIT 10
```

Recorded metrics:

- Mean latency
- Minimum latency
- Maximum latency
- P50 latency
- P95 latency

### Results (Mean Latency in ms)

| Database | Aggregation |
| --- | ---: |
| Neo4j | 30.47 |
| Memgraph | 29.39 |
| FalkorDB | 23.59 |
| CognoDB | 380.53 |
| Apache AGE | 164.09 |

---

### 5. Mixed Workload Performance

Measures database throughput under concurrent read and write operations.

Configuration:

- 10 concurrent clients
- 80% read operations
- 20% write operations
- 2-second warm-up period
- 10-second measurement period

Read query:

```cypher
MATCH (u:User {id:$id})-[:VOTED_FOR]->(n)
RETURN count(n)
```

Write query:

```cypher
MERGE (a:User {id:$source_id})
MERGE (b:User {id:$target_id})
CREATE (a)-[:VOTED_FOR]->(b)
```

Recorded metrics:

- Sustained queries per second (QPS)
- Total operations
- Read operations
- Write operations
- Query latency

### Results

| Database | QPS | Total Operations |
| --- | ---: | ---: |
| Neo4j | 504.64 | 5,090 |
| Memgraph | 2,465.64 | 24,663 |
| FalkorDB | 4,214,44 | 42,147 |
| CognoDB | 26.64 | 270 |
| Apache AGE | 299.41 | 2,996 |

---

### 6. Storage Footprint

Measures the amount of persistent storage used after the dataset is fully loaded.

### Results

| Database | Storage |
| --- | ---: |
| Neo4j | 523 MB |
| Memgraph | 433 MB |
| FalkorDB | 4 KB* |
| CognoDB | 143 MB |
| Apache AGE | 26.9 MB |

\* FalkorDB primarily stores data in memory. The on-disk directory contains only metadata and does not accurately represent the actual memory footprint.

---
## Performance Analysis

### Loading Performance

- FalkorDB achieved the highest measured ingestion throughput and the shortest total loading time in the recorded results. Memgraph was the second-fastest overall for loading.
- Neo4j showed moderate loading performance.
- CognoDB and Apache AGE required substantially more time to load the dataset, particularly during relationship creation.

### Traversal Performance

- Memgraph and FalkorDB produced the lowest latency for the shallow traversal workloads.
- Memgraph remained consistently fast as traversal depth increased.
- FalkorDB was very fast for one-hop traversal, but its deeper traversal results showed substantially higher maximum and P95 latency, indicating greater variability.
- Neo4j maintained functional and relatively consistent performance across all three traversal depths.
- Apache AGE showed predictable traversal latency, although its two-hop and three-hop results were slower than its one-hop result.
- CognoDB completed the one-hop and two-hop measurements but the three-hop traversal failed because of a database connection failure.
- The benchmark reports the completed queries and records the failed query separately.

### Lookup Performance

- FalkorDB achieved the lowest point-lookup latency, followed closely by Memgraph.
- Neo4j and Apache AGE also completed point lookups with low-millisecond latency.
- For indexed lookup, Memgraph produced the lowest mean latency among the evaluated systems.
- CognoDB showed substantially higher latency for both point and indexed lookup operations, with mean latency in the hundreds of milliseconds.

### Aggregation Performance

- FalkorDB achieved the lowest measured aggregation latency, followed by Memgraph and Neo4j.
- CognoDB completed the aggregation benchmark but showed substantially higher latency than the other databases.
- Apache AGE did not produce a usable aggregation result because the query failed due to the result-row and column-definition requirements of the Apache AGE `cypher()` interface.

### Mixed Workload Performance

- The mixed workload benchmark measures sustained throughput under 10 concurrent clients using an 80% read / 20% write workload.
- FalkorDB achieved the highest sustained QPS in the recorded results, followed by Memgraph.
- Neo4j completed the workload successfully with lower throughput than FalkorDB and Memgraph.
- Apache AGE achieved lower throughput than the leading systems.
- CognoDB produced the lowest sustained QPS and substantially higher mean latency.
- For this benchmark, **sustained QPS is the primary performance metric** because the workload is specifically designed to measure concurrent read/write throughput. Latency statistics are supplementary and describe the responsiveness and variability of successful operations.

### Storage Footprint

- The recorded storage measurements show different persistent storage requirements across the evaluated systems.
- Neo4j and Memgraph used substantially more persistent disk space than the measured Apache AGE and CognoDB footprints.
- FalkorDB's reported 4 KB directory size should not be interpreted as its complete runtime memory or storage requirement because the graph data is primarily maintained in memory.

---

## Benchmark Limitations

The results should be interpreted within the following conditions:

- All databases were evaluated using the same Wiki-Vote dataset.
- The same graph model was used across the systems.
- Benchmark queries use the Cypher-compatible graph model supported by each system.
- The benchmarks were executed in the configured local/container environment.
- Latency measurements represent client-side query execution time measured by the Python benchmark.
- Iteration-based benchmarks use 20 warm-up iterations followed by 100 measured iterations.
- The mixed workload uses 10 concurrent clients, an 80:20 read/write mix, a 2-second warm-up period, and a 10-second measured period.
- Failed benchmark operations are reported as failures rather than being treated as zero performance.
- Storage measurements are implementation-specific and should not be interpreted as perfectly equivalent across different storage architectures.
- Results can vary depending on hardware, database version, container configuration, cache state, network conditions, and repeated execution.

---

## Reference

Leskovec, J., Huttenlocher, D., and Kleinberg, J.

SNAP: Stanford Network Analysis Project.

Wiki-Vote Dataset.
