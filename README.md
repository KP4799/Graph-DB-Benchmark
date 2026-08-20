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

## Loading the Dataset

Load the dataset into all databases:

```bash
python loaders/load_all.py
```

The loading pipeline automatically:

- Clears previously loaded data.
- Creates a new graph when required.
- Imports all nodes.
- Imports all relationships.
- Measures loading performance.

Loading results are stored in:

```text
results/loading_time.json
```

---

## Running the Complete Benchmark Suite

Run all benchmarks:

```bash
python benchmarks/run_all.py
```

A combined report is generated automatically.

Benchmark results are stored in:

```text
results/summary.json
```

---

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

## Benchmark Queries

### 1. Loading Queries

#### Node Creation

```cypher
UNWIND $batch AS row
MERGE (u:User {id: row.id})
```

#### Relationship Creation

```cypher
UNWIND $batch AS row
MATCH (source:User {id: row.source})
MATCH (target:User {id: row.target})
CREATE (source)-[:VOTED_FOR]->(target)
```

---

### 2. Traversal Queries

#### One-Hop Traversal

```cypher
MATCH (u:User {id: $id})-[:VOTED_FOR]->(neighbor)
RETURN neighbor.id
```

#### Two-Hop Traversal

```cypher
MATCH (u:User {id: $id})-[:VOTED_FOR]->()-[:VOTED_FOR]->(neighbor)
RETURN neighbor.id
```

#### Three-Hop Traversal

```cypher
MATCH (u:User {id: $id})
      -[:VOTED_FOR]->()
      -[:VOTED_FOR]->()
      -[:VOTED_FOR]->(neighbor)
RETURN neighbor.id
```

---

### 3. Lookup Queries

#### Point Lookup

```cypher
MATCH (u:User {id: $id})
RETURN u
```

#### Indexed Lookup

```cypher
MATCH (u:User)
WHERE u.id = $id
RETURN u
```

---

### 4. Aggregation Query

```cypher
MATCH (u:User)-[:VOTED_FOR]->()
RETURN u.id, count(*) AS votes
ORDER BY votes DESC
LIMIT 10
```

---

### 5. Mixed Workload Queries

The mixed workload benchmark simulates concurrent client activity using an
80:20 read-to-write ratio.

#### Read Operation

```cypher
MATCH (u:User {id: $id})
RETURN u
```

#### Write Operation

```cypher
CREATE (:BenchmarkNode {
    id: $id
})
```

#### Workload Configuration

| Parameter | Value |
| --- | --- |
| Concurrent clients | 10 |
| Read operations | 80% |
| Write operations | 20% |
| Warm-up duration | 2 seconds |
| Measured duration | 10 seconds |

---

## Benchmark Metrics

### 1. Loading Performance

Measures the efficiency of dataset ingestion.

Recorded metrics:

- Nodes loaded
- Relationships loaded
- Nodes per second
- Relationships per second
- Total loading time

---

### 2. Traversal Performance

Measures the latency of graph traversal operations.

Queries:

- One-hop traversal
- Two-hop traversal
- Three-hop traversal

Recorded metrics:

- Mean latency
- Minimum latency
- Maximum latency
- P50 latency
- P95 latency

---

### 3. Lookup Performance

Measures the efficiency of node retrieval.

Queries:

- Point lookup
- Indexed lookup

Recorded metrics:

- Mean latency
- Minimum latency
- Maximum latency
- P50 latency
- P95 latency

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

---

### 5. Mixed Workload Performance

Measures database throughput under concurrent read and write operations.

Configuration:

- 10 concurrent clients
- 80% read operations
- 20% write operations

Recorded metrics:

- Sustained queries per second (QPS)
- Total operations
- Read operations
- Write operations
- Query latency

---

## Results Directory

```text
results/
├── aggregations.json
├── loading_time.json
├── lookups.json
├── mixed_workload.json
├── summary.json
└── traversals.json
```

---

## Benchmark Results

### 1. Data Loading

Measures the efficiency of dataset ingestion.

Graph model:

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
| Neo4j | 3,949.049 | 13,067.11 | 9.74 |
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

FalkorDB achieved the highest ingestion throughput, followed closely by Memgraph. Neo4j demonstrated moderate loading performance, while Apache AGE and CognoDB required substantially more time to create relationships.

### Traversal Performance

Memgraph consistently achieved the lowest traversal latency across all traversal depths. FalkorDB performed similarly for one-hop traversals but exhibited higher variance during deeper traversals. Neo4j maintained stable performance across all traversal depths. Apache AGE showed predictable but slower execution times.

CognoDB experienced connection failures during traversal benchmarking, so traversal results were unavailable.

### Lookup Performance

FalkorDB and Memgraph achieved the fastest point lookups. Neo4j and Apache AGE performed well but with slightly higher latency. CognoDB required significantly more time for both point and indexed lookups.

### Aggregation Performance

FalkorDB achieved the lowest aggregation latency, followed by Memgraph and Neo4j. CognoDB exhibited substantially higher execution times.

Apache AGE aggregation results were unavailable because the Cypher query used in the benchmark was incompatible with Apache AGE's result definition requirements.

### Mixed Workload Performance

FalkorDB achieved the highest throughput under concurrent read/write workloads. Memgraph also demonstrated excellent throughput and low latency. Neo4j maintained stable performance with moderate throughput.

Apache AGE sustained approximately 290 queries per second under mixed workloads, while CognoDB demonstrated the lowest throughput among all evaluated systems.

---

## Storage Footprint

Storage footprint was intentionally excluded from the benchmark because these implementations differ significantly, direct comparison of on-disk storage would not provide a consistent metric across all database systems.

---

## Reference

Leskovec, J., Huttenlocher, D., and Kleinberg, J.

SNAP: Stanford Network Analysis Project.

Wiki-Vote Dataset.
