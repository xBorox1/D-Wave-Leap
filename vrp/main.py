from qubo_helper import Qubo
from tsp_problem import TSPProblem 
from vrp_problem import VRPProblem
from vrptw_problem import VRPTWProblem
from vrptw_solvers import *
from vrp_solvers import *
from itertools import product
import DWaveSolvers
import networkx as nx
import numpy as np
from input import *

CAPACITY = 1000

if __name__ == '__main__':

    for i in range(10):
        TEST = '../tests_vrp/exact/medium/medium-' + str(i) + '.test'
        test = read_test(TEST)

        # Problem parameters
        sources = test['sources']
        costs = test['costs']
        time_costs = test['time_costs']
        capacities = [50 for _ in range(3)]
        dests = test['dests']
        weigths = test['weights']
        time_windows = test['time_windows']

        only_one_const = 10000000.
        order_const = 1.
        capacity_const = 0.
        time_const = 0.

        problem = VRPTWProblem(sources, costs, time_costs, capacities, dests, weigths, time_windows)
        vrp_solver = SolutionPartitioningSolver(problem, DBScanSolver(problem, anti_noiser = True))
        solver = MergingTimeWindowsVRPTWSolver(problem, vrp_solver)


        result = solver.solve(only_one_const, order_const, capacity_const,
                solver_type = 'qbsolv', num_reads = 500)
        print(result.solution)
        print(result.check())
        print(result.total_cost())
        print(result.all_time_costs())
        print(result.all_weights())
