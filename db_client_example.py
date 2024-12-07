from neo4j import GraphDatabase

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "neo4j://138.2.231.157:7687"
AUTH = ("neo4j", "cs6400password")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connection established.")

# sanity check
records, summary, keys = driver.execute_query(
    "MATCH (c:City {name: $name}) RETURN c.name AS name",
    name="nanjing",
    database_="neo4j",
)

for c in records:
    print(c)

records, summary, keys = driver.execute_query(
    "MATCH (c:City {name: $name}) RETURN c.name AS name",
    name="nanjing",
    database_="neo4j",
)

QUERY = """
MATCH (source:City {name: 'zaozhuang'}), (target:City {name: 'tokyo'})
CALL gds.shortestPath.yens.stream(
  'routeGraph',
  {
    sourceNode: id(source),
    targetNode: id(target),
    k : 3,
    relationshipWeightProperty: 'weight'
  }
)
YIELD index, totalCost, nodeIds, costs
WITH index, totalCost,
     [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS nodeNames,
     costs
UNWIND range(0, size(nodeNames)-2) AS i
MATCH (from:City {name: nodeNames[i]})-[r:CONNECTS]->(to:City {name: nodeNames[i+1]})
WHERE r.duration = costs[i+1] - costs[i]
WITH index, totalCost, nodeNames,
     collect({
        fromCity: from.name,
        toCity: to.name,
        type: r.type,
        duration: r.duration,
        price: COALESCE(r.price, null),
        routeName: r.route_name
     }) AS segmentDetails
RETURN
  index AS pathIndex,
  totalCost AS pathCost,
  nodeNames,
  segmentDetails
ORDER BY pathCost ASC
LIMIT 5;
"""

with driver.session() as session:
    # Execute the query
    result = session.run(QUERY)

    # Process the results
    paths = []
    for record in result:
        paths.append({
            "pathIndex": record["pathIndex"],
            "pathCost": record["pathCost"],
            "nodeNames": record["nodeNames"],
            "segmentDetails": record["segmentDetails"]
        })

    print(paths)
    exit(0)
    for path in paths:
        print(f"Path Index: {path['pathIndex']}")
        print(f"Total Cost: {path['pathCost']}")
        print(f"Node Names: {path['nodeNames']}")
        print("Segment Details:")
        for segment in path["segmentDetails"]:
            print(f"  - From: {segment['fromCity']}, To: {segment['toCity']}, Type: {segment['type']}, Duration: {segment['duration']} mins, Cost: {segment['price']}, Route: {segment['routeName']}")
        print()
