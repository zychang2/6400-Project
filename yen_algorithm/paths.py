import csv
import heapq
import argparse
routes = ["airport_routes.csv","processed_routes_china.csv","processed_routes.csv"]
nodes = {}
edges = {}
cities = {}
i = 0
for route in routes:
    with open(route,"r",encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            nodes[str(i)] = [row[0],row[3],row[6],row[12],True]
            if (cities.__contains__(row[0])):
                cities.get(row[0]).append(str(i))
            else:
                arr = []
                arr.append(str(i))
                cities[row[0]] = arr
            if (cities.__contains__(row[3] == False)):
                cities[row[3]] = []
            i += 1

    for node in nodes.keys():
        if (cities.__contains__(nodes.get(node)[1])):
            edges[node] = cities.get(nodes.get(node)[1])
        else:
            edges[node] = []


def get_routes(start, end, K):
    """
    Find K shortest paths using Yen's Algorithm.

    :param graph: Graph data structure representing nodes and edges.
    :param start: Starting node.
    :param end: Ending node.
    :param K: Number of shortest paths to find.
    :return: List of K shortest paths.
    """
    # Determine the shortest path from the start to the end.
    distances, prev_nodes = dijkstra(start, end)
    first_path = reconstruct_path(prev_nodes, start, end)

    if not first_path:
        return []

    A = [first_path]  # Store k-shortest paths
    B = []  # Potential k-shortest paths

    for k in range(1, K):
        # Iterate over the previous path to find deviation points
        for i in range(len(A[k - 1])):
            spur_node = A[k - 1][i]  # Current node as spur
            root_path = A[k - 1][:i + 1]  # From start to spur node

            # Temporarily remove edges and nodes from graph
            nodes_removed = set()
            for path in A:
                if path[:i + 1] == root_path:
                    # initial = nodes.get(path[i])
                    # newV = (initial[0],initial[1],initial[2],initial[3],False)
                    # nodes[path[i]] = newV
                    # nodes.update()
                    nodes.get(path[i])[4] = False
                    nodes_removed.add(path[i])

            for node in root_path[:-1]:
                nodes_removed.add(node)
                # initial = nodes.get(node)
                # newV = (initial[0],initial[1],initial[2],initial[3],False)
                # nodes[node] = newV
                nodes.get(node)[4] = False

            # Calculate spur path
            distances, prev_nodes = dijkstra(nodes.get(spur_node)[0], end)
            spur_path = None
            if (prev_nodes != None):
                spur_path = reconstruct_path(prev_nodes, spur_node, end)

            # If spur path exists, combine with root path
            if spur_path:
                total_path = root_path + spur_path[1:]
                if total_path not in B:
                    B.append(total_path)

            # Restore edges
            for node in nodes_removed:
                # initial = nodes.get(node)
                # newV = (initial[0],initial[1],initial[2],initial[3],True)
                # nodes[node] = newV
                nodes.get(node)[4] = True
        if not B:
            break

        # Sort by total cost and select the smallest one
        B.sort(key=lambda path: len(path))  # Adjust sorting metric as needed
        A.append(B.pop(0))

    return A



def dijkstra(start, end):
    # Priority queue to store (distance, node)
    priority_queue = []
    if cities.__contains__(start) == False:
        return None, None
    for i in cities.get(start):
        if nodes.get(i)[4] == True:
            priority_queue.append((0,i))
    # Dictionary to store the shortest distance to each node
    distances = {}
    for city in cities.keys():
        distances[city] = float('inf')
    distances[start] = 0
    # Dictionary to store the shortest path tree
    previous_nodes = {}
    for city in cities.keys():
        previous_nodes[city] = None

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        # Skip if this distance is not the current shortest
        if (distances.__contains__(nodes.get(current_node)[1])):
            if current_distance > distances[nodes.get(current_node)[1]]:
                continue
        
        if (nodes.get(current_node)[1] == end):
            previous_nodes[nodes.get(current_node)[1]] = current_node
            break

        if cities.get(nodes.get(current_node)[1]) != None:
            for neighbor in cities.get(nodes.get(current_node)[1]):
                if (nodes.get(neighbor)[4] == False):
                    continue
                weight = 1
                if (nodes.get(neighbor)[3] == nodes.get(current_node)[3]):
                    weight = 0
                distance = current_distance + weight
                # If a shorter path is found
                if (distances.__contains__(nodes.get(neighbor)[1])):
                    if distance < distances[nodes.get(neighbor)[1]]:
                        distances[nodes.get(neighbor)[1]] = distance
                        previous_nodes[nodes.get(neighbor)[1]] = current_node
                        heapq.heappush(priority_queue, (distance, neighbor))

    return distances, previous_nodes

def reconstruct_path(previous_nodes, start, end):
    """
    Reconstructs the shortest path from start to end.

    :param previous_nodes: A dictionary containing the shortest path tree.
    :param start: The starting node.
    :param end: The ending node.
    :return: A list representing the shortest path.
    """
    path = []
    current = end

    while previous_nodes.get(current) is not None:
        # path.append((nodes.get(previous_nodes.get(current))[0],nodes.get(previous_nodes.get(current))[1]))
        path.append(previous_nodes.get(current))
        current = nodes.get(previous_nodes.get(current))[0]

    path.reverse()

    # Check if a valid path exists
    if nodes.get(path[0])[0]:
        return path
    else:
        return None

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
    A = get_routes(args.s,args.e,args.k)
    if (A != None):
        for path in A:
            print("Path")
            for i in path:
                print("edge: ")
                print(nodes.get(i))