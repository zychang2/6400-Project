from neo4j import GraphDatabase
from flask import render_template, Flask, jsonify, session, request, send_from_directory
import pprint
import json

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "neo4j://138.2.231.157:7687"
AUTH = ("neo4j", "cs6400password")

app = Flask(__name__)


def process_segment_details(segment_details):
    """
    Processes segmentDetails to remove duplicate segments between the same fromCity and toCity.
    Prefers segments that match the previous or next route.
    """
    # Initialize the new list of segments
    new_segment_details = []
    num_segments = len(segment_details)
    
    i = 0
    while i < num_segments:
        current_segment = segment_details[i]
        from_city = current_segment['fromCity']
        to_city = current_segment['toCity']
        
        # Collect all segments between the same fromCity and toCity
        duplicates = [current_segment]
        j = i + 1
        while j < num_segments:
            next_segment = segment_details[j]
            if next_segment['fromCity'] == from_city and next_segment['toCity'] == to_city:
                duplicates.append(next_segment)
                j += 1
            else:
                break
        
        # If duplicates found, select the preferred segment
        if len(duplicates) > 1:
            preferred_segment = select_preferred_segment(duplicates, new_segment_details, segment_details, i)
            new_segment_details.append(preferred_segment)
        else:
            new_segment_details.append(current_segment)
        
        # Move to the next segment (skip duplicates)
        i += len(duplicates)
    
    return new_segment_details

def select_preferred_segment(duplicates, new_segment_details, segment_details, current_index):
    """
    Selects the preferred segment from duplicates based on matching routeID or routeName
    with previous or next segments.
    """
    # Get previous and next routeIDs and routeNames if they exist
    previous_routeID = None
    previous_routeName = None
    if new_segment_details:
        previous_routeID = new_segment_details[-1].get('routeID')
        previous_routeName = new_segment_details[-1].get('routeName')
    
    next_routeID = None
    next_routeName = None
    if current_index + len(duplicates) < len(segment_details):
        next_segment = segment_details[current_index + len(duplicates)]
        next_routeID = next_segment.get('routeID')
        next_routeName = next_segment.get('routeName')
    
    # Try to find a duplicate that matches the previous or next segment's route
    for segment in duplicates:
        if (segment.get('routeID') == previous_routeID or segment.get('routeName') == previous_routeName or
            segment.get('routeID') == next_routeID or segment.get('routeName') == next_routeName):
            return segment
    
    # If no match found, you can apply additional criteria
    # For example, select the segment with the shortest duration
    shortest_duration_segment = min(duplicates, key=lambda x: x['duration'])
    return shortest_duration_segment


with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connection established.")


@app.route('/shortest_n4j', methods=['GET'])
def neo4j_shortest_path():
    inputs = request.get_json()
    start, end, k = inputs.get('source'), inputs.get('destination'), inputs.get('k', 5)

    QUERY = """
    MATCH (source:City {name: $start}), (target:City {name: $end})
    CALL gds.shortestPath.yens.stream(
    'routeGraph',
    {
        sourceNode: id(source),
        targetNode: id(target),
        k : $k,
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
            routeID: r.route_id,
            routeName: r.route_name,
            fromStation: r.from_station,
            toStation: r.to_station
        }) AS segmentDetails
    RETURN
    index AS pathIndex,
    totalCost AS pathCost,
    nodeNames,
    segmentDetails
    ORDER BY pathCost ASC
    LIMIT $k;
    """


    with driver.session() as session:
        # Execute the query
        result = session.run(QUERY, start=start, end=end, k=k * 2) 

        paths = []
        for record in result:
            paths.append(process_segment_details(record['segmentDetails']))
        # print(paths[0])
        # paths = paths[:k]
        res = []
        for path in paths:
            '''
            "previous city", "next city", "train or flight", "route ID", "route Name", "previous station", "next station", "duration"
            '''
            tmp = []
            for p in path:
                tmp.append([
                    p['fromCity'],
                    p['toCity'],
                    p['type'],
                    p['routeID'],
                    p['routeName'],
                    p['fromStation'],
                    p['toStation'],
                    p['duration']
                ])
            res.append(tmp)

        def serialize(path):
            return '?'.join(
                '|'.join(
                    str(item) for item in seg
                )
                for seg in path
            )
        
        def deserialize(s_path):
            res_1 = s_path.split('?')
            res = []
            for seg in res_1:
                res.append(seg.split('|'))
            return res
        
        s_res = {serialize(p) for p in res}
        d_res = [deserialize(p) for p in s_res][:k]
        return d_res



if __name__ == '__main__':
    # app.run()
    res = neo4j_shortest_path()
