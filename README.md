# 6400-Project: Multi-Transportation Travel Planner

## Project Setup
 - Database system: Neo4j
 - Database Documentation: PLACEHOLDER
 - Python Environment Dependencies: `requirements.txt` file in the root folder, use `pip install -r requirements.txt` to install all the dependencies.

## Data Preparation

### Japan Railway
 - Go to `JPRailway` folder.
 - Running `Process.ipynb` will add missing station information and correct station names.
 - Running `translation.ipynb` will apply translation to station names and find the situated city for each station.
 - Running `city.ipynb` will extract the top 5 stations that can reach the most regions for each city. Next, running `duration.ipynb` will apply the duration and distance estimation to the data.
 - The above concludes all the preprocessing. Some extreme special cases are not covered and are instead hardcoded into the output files, so the results may be different from what is actually used.
 - The data used in the projects is in `JPRailway/Useful/` folder.
### China Railway
 - Go to `CNRailway` folder.
 - Run all the blocks in `processing.ipynb`, it will automatically preprocess the data found on other GitHub repos into our required CSV format. (Other GitHub repos can be found in references)
 - Copy the generated `processed_routes.csv` to `yen_algorithm` folder.
 - Rename the file to `processed_routes_china.csv` for the algorithm to work with.

### Flight
- Go to `AirlineData` folder.
- Aviation Edge API called on every airport in japan_china_airports.csv
- Example API response in `res1.json`
- unique airline routes formated in `airport_routes.csv`

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
 - Prepare a new terminal.
 - Go to `frontend` folder.
 - Run `npm install` to install dependencies for the frontend.
 - Run `npm start` to start the frontend service.
 - Prepare another new terminal.
 - Go to `yen_algorithm` folder.
 - Run `python .\paths.py` to start the backend service.
 - Access `http://localhost:3000/` in your web browser to access the frontend UI.

## References

### Japan Railway
 - Station Data: https://github.com/piuccio/open-data-jp-railway-stations
 - Line Data: https://github.com/piuccio/open-data-jp-railway-lines
 - Prefecture Data: https://github.com/piuccio/open-data-jp-prefectures
### China Railway
 - Line Data: https://github.com/youjiajia/train_data_crawler
 - Station Data: https://github.com/listenzcc/China-rail-way-stations-data

### Flight
 - Flight data: https://aviation-edge.com/
