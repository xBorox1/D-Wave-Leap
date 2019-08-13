import networkx as nx
import csv
import math
from utilities import *
from itertools import product
import numpy as np

# format:
# nodes.csv: id|enu_east|enu_north|enu_up|lla_longitude|lla_latitude|lla_altitude
# edges.csv: id_1|id_2|distance|time_0|time_1|...|time_23
# TODO: lokalizacje magazynów, paczkomatów itp

GRAPH_PATH = '../tests/bruxelles'
TIME_WINDOWS_DIFF = 30
TIME_WINDOWS_RADIUS = 60
DIST_TO_TIME = float(1) / float(444)

def create_graph_from_csv(path):
    g = nx.DiGraph(directed=True)

    with open(path+"/vertex_weigths.csv", mode='r') as e_infile:
        reader = csv.reader(e_infile)
        next(reader)
        for row in reader:
            id1 = int(row[0])
            id2 = int(row[1])
            dist = float(row[2])
            time = float(dist * float(DIST_TO_TIME))
            g.add_edge(id1, id2, distance=dist, time=time)

    return g

def read_full_test(path, graph_path = GRAPH_PATH):
    graph = create_graph_from_csv(graph_path)
    in_file = open(path, 'r')
    
    # Smaller id's of sources and orders.
    nodes_id = list()

    # Reading magazines.
    next(in_file)
    nodes_id = [int(s) for s in in_file.readline().split() if s.isdigit()]
    magazines_num = len(nodes_id)

    # Reading destinations, time_windows and weights. 
    next(in_file)
    dests_num = int(in_file.readline())
    nodes_num = dests_num + magazines_num

    time_windows = np.zeros((nodes_num), dtype=int)
    weights = np.zeros((nodes_num), dtype=int)

    for i in range(dests_num):
        order = in_file.readline().split()
        
        dest = int(order[0])
        time_window = int(floor_to_value(float(order[1]), float(TIME_WINDOWS_DIFF)) + float(TIME_WINDOWS_RADIUS))
        weight = int(order[3])

        nodes_id.append(dest)
        time_windows[i + magazines_num] = time_window
        weights[i + magazines_num] = weight

    # Creating costs and time_costs matrix.
    costs = np.zeros((nodes_num, nodes_num), dtype=float)
    time_costs = np.zeros((nodes_num, nodes_num), dtype=float)

    for i, j in product(range(nodes_num), range(nodes_num)):
        d1 = nodes_id[i]
        d2 = nodes_id[j]
        path = nx.shortest_path(graph, source = d1, target = d2, weight = 'distance')
        
        prev = d1
        for node in path[1:]:
            edge = graph.get_edge_data(prev, node)
            costs[i][j] += edge['distance']
            time_costs[i][j] += edge['time']
            prev = node

    result = dict()
    result['sources'] = [i for i in range(magazines_num)]
    result['dests'] =  [i for i in range(magazines_num, nodes_num)]
    result['costs'] = costs
    result['time_costs'] = time_costs
    result['weights'] = weights
    result['time_windows'] = time_windows

    in_file.close()
    return result

def read_test(path):
    in_file = open(path, 'r')
    
    # Number of magazines.
    magazines_num = int(in_file.readline())

    # Number of destinations. 
    dests_num = int(in_file.readline())

    nodes_num = magazines_num + dests_num

    time_windows = np.zeros((nodes_num), dtype=int)
    weights = np.zeros((nodes_num), dtype=int)

    for i in range(dests_num):
        order = in_file.readline().split()
        
        weight = int(order[0])
        time_window = float(order[1]) + float(TIME_WINDOWS_RADIUS)

        time_windows[i + magazines_num] = time_window
        weights[i + magazines_num] = weight

    # Creating costs and time_costs matrix.
    costs = np.zeros((nodes_num, nodes_num), dtype=float)
    time_costs = np.zeros((nodes_num, nodes_num), dtype=float)

    for i, j in product(range(nodes_num), range(nodes_num)):
        cost_line = in_file.readline().split()
        costs[i][j] = float(cost_line[0])
        time_costs[i][j] += float(cost_line[1])

    result = dict()
    result['sources'] = [i for i in range(magazines_num)]
    result['dests'] =  [i for i in range(magazines_num, nodes_num)]
    result['costs'] = costs
    result['time_costs'] = time_costs
    result['weights'] = weights
    result['time_windows'] = time_windows

    in_file.close()
    return result

def create_test(in_path, out_path):
    test = read_full_test(in_path)
    out_file = open(out_path, 'w+')

    # Number of magazines. Magazines have numbers 0, 1, 2, ...
    out_file.write(str(len(test['sources'])) + '\n')

    # Number of destinations. Destinations have numbers (magazines_number), (magazines_number + 1), ...
    out_file.write(str(len(test['dests'])) + '\n')

    # Number of destinations lines. Weights, start and edn of time window.
    for dest in test['dests']:
        out_file.write(str(test['weights'][dest]) + ' ' + str(test['time_windows'][dest] - TIME_WINDOWS_RADIUS)
                + ' ' + str(test['time_windows'][dest] + TIME_WINDOWS_RADIUS) + '\n')

    n = len(test['sources']) + len(test['dests'])
    costs = test['costs']
    time_costs = test['time_costs']

    # Costs and time_costs between all sources and destinations.
    for (i, j) in product(range(n), range(n)):
        out_file.write(str(costs[i][j]) + ' ' + str(time_costs[i][j]) + '\n')

    out_file.close()
