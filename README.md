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

---

## Benchmark Results

### Loading Performance

| Database | Nodes/s | Relationships/s | Total Loading Time (s) |
| --- | ---: | ---: | ---: |
| Neo4j | 11,045.59 | 26,725.49 | 4.52 |
| Memgraph | 130,705.65 | 100,213.00 | 1.09 |
| FalkorDB | 257,269.81 | 106,129.94 | 1.00 |
| CognoDB | 615.62 | 657.96 | 169.15 |
| Apache AGE | 3,707.37 | 504.18 | 207.58 |

---

### Traversal Performance

#### One-Hop Traversal

| Database | Mean (ms) | Min (ms) | Max (ms) | P50 (ms) | P95 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Neo4j | 3.1171 | 1.2357 | 55.8724 | 1.4923 | 2.2015 |
| Memgraph | 0.4251 | 0.3659 | 0.6799 | 0.4094 | 0.5089 |
| FalkorDB | 0.4001 | 0.3463 | 0.5623 | 0.3928 | 0.4684 |
| CognoDB | N/A | N/A | N/A | N/A | N/A |
| Apache AGE | 1.8034 | 1.7165 | 1.9967 | 1.7818 | 1.9426 |

#### Two-Hop Traversal

| Database | Mean (ms) | Min (ms) | Max (ms) | P50 (ms) | P95 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Neo4j | 3.1311 | 1.1261 | 52.7896 | 1.4181 | 4.4697 |
| Memgraph | 0.4948 | 0.3655 | 1.2873 | 0.4322 | 0.8692 |
| FalkorDB | 0.8664 | 0.3182 | 14.5158 | 0.4155 | 2.4284 |
| CognoDB | N/A | N/A | N/A | N/A | N/A |
| Apache AGE | 7.5993 | 7.3412 | 8.5126 | 7.5439 | 7.9855 |

#### Three-Hop Traversal

| Database | Mean (ms) | Min (ms) | Max (ms) | P50 (ms) | P95 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Neo4j | 14.9737 | 1.0886 | 153.8304 | 2.7495 | 75.7484 |
| Memgraph | 2.9499 | 0.3737 | 49.2621 | 0.8948 | 9.5374 |
| FalkorDB | 17.6588 | 0.3746 | 592.0545 | 1.6244 | 77.9699 |
| CognoDB | N/A | N/A | N/A | N/A | N/A |
| Apache AGE | 7.6206 | 7.2946 | 12.5057 | 7.4191 | 8.9119 |

---

### Lookup Performance

#### Point Lookup

| Database | Mean (ms) | Min (ms) | Max (ms) | P50 (ms) | P95 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Neo4j | 2.1708 | 0.9539 | 60.7630 | 1.0974 | 1.3548 |
| Memgraph | 0.4325 | 0.3752 | 0.6396 | 0.4115 | 0.5357 |
| FalkorDB | 0.3432 | 0.3061 | 0.4542 | 0.3408 | 0.3736 |
| CognoDB | 305.7940 | 247.8012 | 602.0118 | 306.2041 | 398.1651 |
| Apache AGE | 1.6361 | 1.5715 | 2.2696 | 1.6185 | 1.6907 |

#### Indexed Lookup

| Database | Mean (ms) | Min (ms) | Max (ms) | P50 (ms) | P95 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Neo4j | 3.0551 | 0.9419 | 55.3579 | 1.6151 | 3.1001 |
| Memgraph | 0.9455 | 0.4090 | 1.4739 | 0.9783 | 1.3803 |
| FalkorDB | 2.7369 | 0.3680 | 6.9185 | 2.7984 | 4.9612 |
| CognoDB | 296.9969 | 254.2659 | 511.3868 | 305.0512 | 363.7036 |
| Apache AGE | 4.8545 | 3.4722 | 6.2192 | 4.9835 | 5.9565 |

---

### Aggregation Performance

| Database | Mean (ms) | Min (ms) | Max (ms) | P50 (ms) | P95 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Neo4j | 35.4815 | 19.3751 | 185.3736 | 23.6717 | 77.5986 |
| Memgraph | 29.7219 | 27.8929 | 61.9413 | 29.1890 | 31.7870 |
| FalkorDB | 23.6177 | 23.0729 | 24.9030 | 23.5383 | 24.3465 |
| CognoDB | 356.5055 | 300.4478 | 612.9394 | 312.9764 | 583.3221 |
| Apache AGE | N/A | N/A | N/A | N/A | N/A |

---

### Mixed Workload Performance

| Database | QPS | Mean Latency (ms) | Total Operations | Read Operations | Write Operations |
| --- | ---: | ---: | ---: | ---: | ---: |
| Neo4j | 500.72 | 19.7507 | 5,060 | 4,042 | 1,018 |
| Memgraph | 1,929.53 | 5.1758 | 19,300 | 15,438 | 3,862 |
| FalkorDB | 3,240.66 | 3.0807 | 32,412 | 25,807 | 6,605 |
| CognoDB | 29.08 | 277.8901 | 296 | 244 | 52 |
| Apache AGE | 289.74 | 34.2927 | 2,900 | 2,313 | 587 |

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


## Metrics

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
| Neo4j | 11,045.59 | 26,725.49 | 4.52 |
| Memgraph | 130,705.65 | 100,213.00 | 1.09 |
| FalkorDB | 257,269.81 | 106,129.94 | 1.00 |
| CognoDB | 615.62 | 657.96 | 169.15 |
| Apache AGE | 3,707.37 | 504.18 | 207.58 |

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
| Neo4j | 3.12 | 3.13 | 14.97 |
| Memgraph | 0.43 | 0.49 | 2.95 |
| FalkorDB | 0.40 | 0.87 | 17.66 |
| CognoDB | Failed | Failed | Failed |
| Apache AGE | 1.80 | 7.60 | 7.62 |

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
| Neo4j | 2.17 | 3.06 |
| Memgraph | 0.43 | 0.95 |
| FalkorDB | 0.34 | 2.74 |
| CognoDB | 305.79 | 297.00 |
| Apache AGE | 1.64 | 4.85 |

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
| Neo4j | 35.48 |
| Memgraph | 29.72 |
| FalkorDB | 23.62 |
| CognoDB | 356.51 |
| Apache AGE | Failed |

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
| Neo4j | 500.72 | 5,060 |
| Memgraph | 1,929.53 | 19,300 |
| FalkorDB | 3,240.66 | 32,412 |
| CognoDB | 29.08 | 296 |
| Apache AGE | 289.74 | 2,900 |

---

### 6. Storage Footprint

Measures the amount of persistent storage used after the dataset is fully loaded.

### Results

| Database | Storage |
| --- | ---: |
| Neo4j | 523 MB |
| Memgraph | 433 MB |
| FalkorDB | 4 KB* |
| CognoDB | Not available |
| Apache AGE | 26.9 MB |

\* FalkorDB primarily stores data in memory. The on-disk directory contains only metadata and does not accurately represent the actual memory footprint.