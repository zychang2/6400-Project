import csv
import heapq
import argparse
from flask import Flask, request, jsonify
from neo4j import GraphDatabase

app = Flask(__name__)

URI = "neo4j://138.2.231.157:7687"
AUTH = ("neo4j", "cs6400password")


with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connection established.")



routes = ["airport_routes.csv","processed_routes_china.csv","processed_routes_japan.csv"]
nodes = {}
from_nodes = set()
to_nodes = set()
edges = {}
edge_weights = {}
cities = {}
i = 0
for route in routes:
    with open(route,"r",encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)
        for row in csv_reader:
            nodes[str(i)] = [row[0],row[6],row[12],True,row[7],row[8],row[9],row[13]]
            from_nodes.add(str(i))
            nodes[str(i + 1)] = [row[3],row[6],row[12],True,row[7],row[8],row[9],row[13]]
            to_nodes.add(str(i + 1))
            edges[str(i)] = [str(i + 1)]
            edge_weights[(str(i),str(i+1))] = int(row[9])
            if (cities.__contains__(row[0])):
                cities.get(row[0]).append(str(i))
            else:
                arr = []
                arr.append(str(i))
                cities[row[0]] = arr
            if (cities.__contains__(row[3])  == False):
                cities[row[3]] = []
            i += 2

    for node in to_nodes:
        if (cities.__contains__(nodes.get(node)[0])):
            edges[node] = cities.get(nodes.get(node)[0])
        else:
            edges[node] = []

    for node in to_nodes:
        if (cities.__contains__(nodes.get(node)[0])):
            edges[node] = cities.get(nodes.get(node)[0])
        else:
            edges[node] = []


def dijkstra(start, end, visited):
    # Priority queue to store (distance, node)
    priority_queue = []
    # visited = set()
    if cities.__contains__(start) == False:
        return None, None, None
    distances = {}
    previous_nodes = {}
    for node in nodes:
        distances[node] = float('inf')
    for i in cities.get(start):
        if nodes.get(i)[3] == True:
            priority_queue.append((0,"",i))
            previous_nodes[i] = ""
            distances[i] = 0
    # Dictionary to store the shortest distance to each node
    # Dictionary to store the shortest path tree
    final_node = None

    while priority_queue:
        current_distance, previous_node, current_node = heapq.heappop(priority_queue)

        # Skip if this distance is not the current shortest
        if (distances.__contains__(nodes.get(current_node)[0])):
            if current_distance > distances[nodes.get(current_node)[0]]:
                continue
        if nodes.get(previous_node) != None:
            if (visited.__contains__(nodes.get(current_node)[0]) and (nodes.get(current_node)[0] != nodes.get(previous_node)[0])):
                continue
        visited.add(nodes.get(current_node)[0])
        if (nodes.get(current_node)[0] == end):
            previous_nodes[nodes.get(current_node)[0]] = previous_node
            final_node = current_node
            break

        for neighbor in edges.get(current_node):
            if (nodes.get(neighbor)[3] == False):
                continue
            if (visited.__contains__(nodes.get(neighbor)[0]) and (nodes.get(current_node)[0] != nodes.get(neighbor)[0])):
                continue
            weight = 30
            if (edge_weights.__contains__((current_node, neighbor))):
                weight = edge_weights[(current_node, neighbor)]
            elif (nodes.get(neighbor)[2] == nodes.get(current_node)[2]):
                weight = 0
            distance = current_distance + weight
            if (distances.__contains__(neighbor)):
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(priority_queue,(distance, current_node, neighbor))

    distance = None
    if final_node != None:
        distance = distances[final_node]
    return distance, final_node, previous_nodes

def reconstruct_path(previous_nodes , end):
    """
    Reconstructs the shortest path from start to end.

    :param previous_nodes: A dictionary containing the shortest path tree.
    :param start: The starting node.
    :param end: The ending node.
    :return: A list representing the shortest path.
    """
    path = []
    paired_path = []
    city_path = []
    current = end
    if (end == None):
        return None, None
    city_path.append(nodes.get(end)[0])
    while previous_nodes.get(current) != "" and previous_nodes.get(current) != None:
        # path.append((nodes.get(previous_nodes.get(current))[0],nodes.get(previous_nodes.get(current))[1]))
        paired_path.append((previous_nodes.get(current),current))
        path.append(current)
        city_path.append(nodes.get(previous_nodes.get(current))[0])
        current = previous_nodes.get(current)
    path.append(current)
    path.reverse()
    paired_path.reverse()
    city_path.reverse()
    # Check if a valid path exists
    return paired_path, path, city_path

def path_cost(path):
    cost = 0
    prev = None
    for node in path:
        if (prev != None):
            if(nodes.get(prev)[2] != nodes.get(node)[2]):
                cost += 1
        prev = node
    return cost


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

@app.route('/self_yen', methods=['GET'])
def yen_k_shortest_paths():
    source = request.args.get('source', type=str)
    target = request.args.get('target', type=str)
    k = request.args.get('k', type=int)

    # Step 1: Find the shortest path and initialize lists
    A = []  # List of shortest paths
    B = []  # List of potential paths

    # Find the first shortest path using Dijkstra
    visited = set()
    distance, final, prev = dijkstra(source, target, visited)
    if not final:
        return A
    pair, path, citie = reconstruct_path(prev, final)
    A.append((path,citie,distance,pair))

    # Step 2: Find the k shortest paths
    for k_i in range(1, k):
        for i in range(len(A[k_i - 1][0]) - 1):
            spur_node = A[k_i - 1][0][i]
            root_path = A[k_i - 1][0][:i + 1]
            city_path1 = A[k_i - 1][1][:i + 1]
            root_pair = A[k_i - 1][3][:i + 1]
            # Temporarily remove edges and nodes
            removed_edges = []
            for path in A:
                if city_path1 == path[1][:i + 1]:
                    edge = (path[0][i], path[0][i + 1])
                    if (edge not in removed_edges):
                        # print("beggining")
                        # print(edge)
                        removed_edges.append(edge)
                        # print(nodes.get(path[0][i]))
                        # print(edges[path[0][i]])
                        edges[path[0][i]].remove(path[0][i + 1])
                        # print(edges[path[0][i]])

            # Find the spur path from the spur node to the target
            city = nodes.get(spur_node)[0]
            # print("City: " + city)
            # print("Target: " + target)
            visited = set()
            if (root_path[-1] in from_nodes):
                for n in root_path[:-1]:
                    visited.add(nodes.get(n)[0])
            else:
                for n in root_path:
                    visited.add(nodes.get(n)[0])

            distance, final, prev = dijkstra(city, target, visited)

            # Restore removed edges
            for edge in removed_edges:
                # print("HERE")
                # print(edge)
                # print(edge[1])
                edges[edge[0]].append(edge[1])
                # print(edges[edge[0]])

            # If a spur path exists, add the total path to B
            if final:
                # print("another print")
                pair , reg, cityP = reconstruct_path(prev, final)
                if (root_path[-1] in from_nodes):
                    total_path = root_path[:-1] + reg
                    total_pathC = city_path1[:-1] + cityP
                    pair = root_pair[:-1] + pair
                else:
                    total_path = root_path[:] + reg
                    total_pathC = city_path1[:] + cityP
                    pair = root_path[:] + pair
                # print(total_path)
                B.append((total_path,total_pathC, distance,pair))

        # If no potential paths are found, break
        if not B:
            break

        # Sort B by path cost and add the lowest-cost path to A
        B.sort(key=lambda path: path[2])
        path = B.pop(0)
        while(path in A):
            path = B.pop(0)
        if path != None:
            A.append(path)
    final_list = []
    for paths in A:
        new_path = []
        for i in range(len(paths[0])):
            if (i % 2 == 0):
                node1 = nodes.get(paths[0][i])
                node2 = nodes.get(paths[0][i + 1])
                #start city, end city, type, route id, routename, from station, to station, duration
                new_path.append((node1[0], node2[0], node1[1],node1[2],node1[7], node1[4],node1[5],node1[6]))
        final_list.append(new_path)
    
    final_json = {"data": final_list}
    return jsonify(final_json)


@app.route('/shortest_n4j', methods=['GET'])
def neo4j_shortest_path():
    start = request.args.get('source', type=str)
    end = request.args.get('target', type=str)
    k = request.args.get('k', type=int)

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
        
        js = {"data": d_res}
        return jsonify(js)


if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="program to find path from start to end")
#     parser.add_argument("-s", type=str, help="start city", required=True)
#     parser.add_argument("-e", type=str, help="end city", required=True)
#     parser.add_argument("-k", type=int, help="number of paths wanted", required=True)
#     args = parser.parse_args()
#     # distances, prev = dijkstra(args.s,args.e)
#     # path = None
#     # if (prev != None):
#     #     path = reconstruct_path(prev, args.s, args.e)
#     # if path != None:
#     #     for i in path:
#     #         print("start city: " + nodes.get(i)[0])
#     #         print("end city: " + nodes.get(i)[1])
#     A = yen_k_shortest_paths(args.s,args.e,args.k)
#     # if (A != None):
#     #     for path in A:
#     #         print("Path")
#     #         for i in path:
#     #             print("edge: ")
#     #             print(nodes.get(i))
#     print(A)