# 6400-Project: Multi-Transportation Travel Planner

## Project Setup
Database system: Neo4j
Database Documentation: PLACEHOLDER
Python Environment Dependencies: requirements.txt file in the root folder

## Data Preparation

### Japan Railway

### China Railway

### Flight

## Database Neo4j Construction
~~~
// head -n 1 processed_routes_air.csv > combined_routes.csv && tail -n +2 -q processed_routes_*.csv >> combined_routes.csv
// LOAD CSV WITH HEADERS FROM 'file:///combined_routes.csv' AS row // local import
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/zychang2/6400-Project/refs/heads/main/yen_algorithm/merged_routes.csv' AS row

// Create cities
// MERGE (from_city:City {name: row.from_city, region_id: row.from_region_id, region_name: row.from_region_name})
// MERGE (to_city:City {name: row.to_city, region_id: row.to_region_id, region_name: row.to_region_name})
MERGE (from_city:City {name: row.from_city, region_name: row.from_region_name})
MERGE (to_city:City {name: row.to_city, region_name: row.to_region_name})

// Link cities
MERGE (from_city)-[r:CONNECTS {route_id: row.route_id}]->(to_city)
ON CREATE SET 
    r.type = row.type,
    r.from_station = row.from_station,
    r.to_station = row.to_station,
    r.route_name = row.route_name,
    r.enabled = row.enabled = 'true'

// Handle optional fields
FOREACH(ignoreMe IN CASE WHEN row.duration IS NOT NULL AND row.duration <> '' THEN [1] ELSE [] END |
    SET r.duration =  toFloat(row.duration)
)
FOREACH(ignoreMe IN CASE WHEN row.distance IS NOT NULL AND row.distance <> '' THEN [1] ELSE [] END |
    SET r.distance = toFloat(row.distance)
)
FOREACH(ignoreMe IN CASE WHEN row.cost IS NOT NULL AND row.cost <> '' THEN [1] ELSE [] END |
    SET r.price = toFloat(row.cost)
)
FOREACH(ignoreMe IN CASE WHEN (row.cost IS NULL OR row.cost = '') AND row.duration IS NOT NULL AND row.type = 'flight' THEN [1] ELSE [] END |
    SET r.price = toFloat(row.duration) * 7.0
)
FOREACH(ignoreMe IN CASE WHEN (row.cost IS NULL OR row.cost = '') AND row.duration IS NOT NULL AND row.type = 'train' THEN [1] ELSE [] END |
    SET r.price = toFloat(row.duration) * 5.25
);
~~~

## Running the Project

## References

### Japan Railway

### China Railway

### Flight