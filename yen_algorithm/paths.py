import csv
import heapq
import argparse
routes = ["airport_routes.csv","processed_routes_china.csv","processed_routes.csv"]
nodes = {}
from_nodes = set()
to_nodes = set()
edges = {}
cities = {}
for route in routes:
    with open(route,"r",encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            nodes[str(i)] = [row[0],row[6],row[12],True]
            from_nodes.add(str(i))
            nodes[str(i + 1)] = [row[3],row[6],row[12],True]
            to_nodes.add(str(i + 1))
            edges[str(i)] = [str(i + 1)]
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


def dijkstra(start, end, nodes, edges):
    # Priority queue to store (distance, node)
    priority_queue = []
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
        
        if (nodes.get(current_node)[0] == end):
            previous_nodes[nodes.get(current_node)[0]] = previous_node
            final_node = current_node
            break

        for neighbor in edges.get(current_node):
            if (nodes.get(neighbor)[3] == False):
                continue
            weight = 1
            if (nodes.get(neighbor)[2] == nodes.get(current_node)[2]):
                weight = 0
            distance = current_distance + weight
            if (distances.__contains__(neighbor)):
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(priority_queue,(distance, current_node, neighbor))


    return distances, final_node, previous_nodes

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

def yen_k_shortest_paths(source, target, k, nodes, edges):
    # Step 1: Find the shortest path and initialize lists
    A = []  # List of shortest paths
    B = []  # List of potential paths

    # Find the first shortest path using Dijkstra
    distances, final, prev = dijkstra(source, target, nodes, edges)
    if not final:
        return A
    _, path, citie = reconstruct_path(prev, final)
    A.append((path,citie))

    # Step 2: Find the k shortest paths
    for k_i in range(1, k):
        for i in range(len(A[k_i - 1][0]) - 1):
            spur_node = A[k_i - 1][0][i]
            root_path = A[k_i - 1][0][:i + 1]
            city_path1 = A[k_i - 1][1][:i + 1]

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
            distances, final, prev = dijkstra(city, target, nodes, edges)

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
                _, reg, cityP = reconstruct_path(prev, final)
                if (root_path[-1] in from_nodes):
                    total_path = root_path[:-1] + reg
                    total_pathC = city_path1[:-1] + cityP
                else:
                    total_path = root_path[:] + reg
                    total_pathC = city_path1[:] + reg
                # print(total_path)
                B.append((total_path,total_pathC))

        # If no potential paths are found, break
        if not B:
            break

        # Sort B by path cost and add the lowest-cost path to A
        B.sort(key=lambda path: path_cost(path[0]))
        A.append(B.pop(0))

    return A

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="program to find path from start to end")
    parser.add_argument("-s", type=str, help="start city", required=True)
    parser.add_argument("-e", type=str, help="end city", required=True)
    parser.add_argument("-k", type=int, help="number of paths wanted", required=True)
    args = parser.parse_args()
    # distances, prev = dijkstra(args.s,args.e)
    # path = None
    # if (prev != None):
    #     path = reconstruct_path(prev, args.s, args.e)
    # if path != None:
    #     for i in path:
    #         print("start city: " + nodes.get(i)[0])
    #         print("end city: " + nodes.get(i)[1])
    A = yen_k_shortest_paths(args.s,args.e,args.k, nodes, edges)
    # if (A != None):
    #     for path in A:
    #         print("Path")
    #         for i in path:
    #             print("edge: ")
    #             print(nodes.get(i))
    print(A)