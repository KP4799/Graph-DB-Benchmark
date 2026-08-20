# from databases.cognodb import connect, COGNODB_DATABASE

# driver = connect()
# session = driver.session(database=COGNODB_DATABASE)

# for i in range(150):
#     result = session.run(
#         "MATCH (u:User {id:$id})-[:VOTED_FOR]->(n) RETURN count(n)",
#         id="1"
#     )
#     result.consume()

#     if i % 10 == 0:
#         print("completed", i)

# session.close()
# driver.close()

from databases import cognodb
import time

driver = cognodb.connect()
session = driver.session(database=cognodb.COGNODB_DATABASE)

try:
    print("Running 3-hop query...")

    start = time.perf_counter()

    result = session.run("""
        MATCH (u:User {id:$id})-[:VOTED_FOR*3]->(n)
        RETURN count(n)
    """, {"id": "6"})

    record = result.single()

    elapsed = time.perf_counter() - start

    print("RESULT:", record)
    print("TIME:", elapsed)

finally:
    session.close()
    driver.close()

