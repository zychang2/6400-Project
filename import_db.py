from neo4j import GraphDatabase

# Connection details
NEO4J_URI = "neo4j://138.2.231.157:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "cs6400password"

# Cypher queries
DELETE_EXISTING_DATA = """
MATCH (n)
DETACH DELETE n;
"""

IMPORT_DATA = """
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/zychang2/6400-Project/refs/heads/main/yen_algorithm/merged_routes.csv' AS row
MERGE (from_city:City {name: row.from_city, region_name: row.from_region_name})
MERGE (to_city:City {name: row.to_city, region_name: row.to_region_name})
MERGE (from_city)-[r:CONNECTS {route_id: row.route_id}]->(to_city)
ON CREATE SET 
    r.type = row.type,
    r.from_station = row.from_station,
    r.to_station = row.to_station,
    r.route_name = row.route_name,
    r.enabled = row.enabled = 'true'
FOREACH(ignoreMe IN CASE WHEN row.duration IS NOT NULL AND row.duration <> '' THEN [1] ELSE [] END |
    SET r.duration =  toFloat(row.duration)
)
FOREACH(ignoreMe IN CASE WHEN row.distance IS NOT NULL AND row.distance <> '' THEN [1] ELSE [] END |
    SET r.distance = toFloat(row.distance)
)
FOREACH(ignoreMe IN CASE WHEN row.cost IS NOT NULL AND row.cost <> '' THEN [1] ELSE [] END |
    SET r.price = toFloat(row.cost)
);
"""

SET_WEIGHT_AND_COST = """
MATCH ()-[r:CONNECTS]->()
SET r.weight = r.duration;

MATCH ()-[r:CONNECTS]->()
SET r.cost = r.duration;
"""

DROP_AND_PROJECT_GRAPH = """
CALL gds.graph.drop('routeGraph') YIELD graphName;

CALL gds.graph.project(
  'routeGraph',
  'City',  
  {
    CONNECTS: { properties: ['weight'] }
  }
);
"""

def execute_query(driver, query):
    with driver.session() as session:
        session.run(query)

def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        print("Deleting existing data...")
        execute_query(driver, DELETE_EXISTING_DATA)

        print("Importing data from CSV...")
        execute_query(driver, IMPORT_DATA)

        print("Setting weights and costs...")
        execute_query(driver, SET_WEIGHT_AND_COST)

        print("Dropping and projecting graph for GDS...")
        execute_query(driver, DROP_AND_PROJECT_GRAPH)

        print("Database setup complete!")
    finally:
        driver.close()

if __name__ == "__main__":
    main()
