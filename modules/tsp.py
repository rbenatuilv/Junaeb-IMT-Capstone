import subprocess
from numpy.random import choice
import pandas as pd
import modules.parameters as p
import modules.graph as g
import modules.geo as geo
from tqdm import tqdm
from queue import PriorityQueue


class TSPApprox:
    def __init__(self, data: pd.DataFrame, coords_labels: tuple[str] = ('X, Y'),
                 compile: bool = True):
        self.data = data
        self.x_label = coords_labels[0]
        self.y_label = coords_labels[1]

        self.maxd = geo.convert_to_degrees(p.MAX_DIST)
        self.maxn = p.MAX_N
        self.vehicle_cost = p.VEHICLE_COST
        self.max_samples = p.MAX_SAMPLE
        self.conv_factor = p.CONV_FACTOR
        self.int_factor = 10**7

        self.compile_command = p.COMP_COMMAND
        self.run_command = p.RUN_COMMAND

        if compile:
            self.tsp_compile()
    
    def tsp_compile(self):
        """
        Compiles the C++ code.
        """
        print('Compiling TSP solver...')
        self.compile_process = subprocess.run(self.compile_command, 
                                              stdout = subprocess.PIPE)
    
    def tsp_run(self, input: str) -> str:
        """
        Runs the C++ code with the given input. 
        Returns the output as a string.
        """
        self.run_process = subprocess.run(self.run_command, 
                                          input = input.encode(), 
                                          stdout = subprocess.PIPE)
        return int(self.run_process.stdout.decode())
    
    def get_options_optimized(self, node: int) -> tuple[list[int], list[float]]:
        n = len(self.data)
        dist = PriorityQueue()
        options = []
        prob = []

        point = (self.data[self.x_label][node], self.data[self.y_label][node])

        for other in range(n):
            if node == other:
                continue
            other_point = (self.data[self.x_label][other],
                            self.data[self.y_label][other])
            distance = g.distance(point, other_point)
            if distance <= self.maxd:
                dist.put((distance, other))

        suma_prob = 0
        for _ in range(min(2*self.maxn + 1, dist.qsize())):
            distance, other = dist.get()
            options.append(other)
            prob.append(1 / distance)
            suma_prob += 1 / distance

        if len(prob) == 0:
            return [], []

        for j in range(len(prob)):
            prob[j] = prob[j] / suma_prob

        return options, prob


    def get_options(self, node: int) -> tuple[list[int], list[float]]:
        """
        Obtains the list of nearby nodes within the maximum distance.
        """
        n = len(self.data)
        dist = []
        options = []
        prob = []

        point = (self.data[self.x_label][node], self.data[self.y_label][node])

        for other in range(n):
            if node == other:
                continue
            other_point = (self.data[self.x_label][other],
                            self.data[self.y_label][other])
            dist.append([g.distance(point, other_point), other])
        
        dist.sort(key=lambda x: x[0])

        suma_prob = 0
        for j in range(2*self.maxn + 1):
            try:
                if dist[j][0] <= self.maxd:
                    options.append(dist[j][1])
                    prob.append(1 / dist[j][0])
                    suma_prob += 1 / dist[j][0]
            except IndexError:
                break

        if len(prob) == 0:
            return [], []

        for j in range(len(prob)):
            prob[j] = prob[j] / suma_prob

        return options, prob
    
    def tsp_sample(self, node: int, sample: list[int]) -> float:
        """
        Solves the TSP problem for a given node and sample. Returns
        the cost of the solution, divided by the number of nodes in the
        sample.
        """

        n = len(sample)
        point = (int(self.data[self.x_label][node] * self.int_factor), 
                 int(self.data[self.y_label][node] * self.int_factor))
        point = [str(x) for x in point]

        entrada = str(n + 1) + "\n"
        entrada += " ".join(point) + "\n"

        for u in sample:
            other_point = (int(self.data[self.x_label][u] * self.int_factor),
                           int(self.data[self.y_label][u] * self.int_factor))
            other_point = [str(x) for x in other_point]

            entrada += " ".join(other_point) + "\n"

        ans = geo.convert_to_meters(self.tsp_run(entrada) / self.int_factor)
        return (ans * self.conv_factor + self.vehicle_cost) / n
    
    def solve(self) -> list[float]:
        """
        Solves the TSP approximation for each node in the dataset, using
        the given parameters. Returns a list with the cost of the solution
        for each node (logistic costs).
        """
        n = len(self.data)
        cant = [0 for _ in range(n)]
        suma = [0 for _ in range(n)]

        for node in tqdm(range(n), desc='Calculating TSP approximations'):

            options, prob = self.get_options(node)

            if not options:
                cant[node] = 1
                suma[node] = self.vehicle_cost
                continue

            sample_size = min(self.maxn - 1, len(options))

            for _ in range(self.max_samples):
                sample = choice(options, size = sample_size, replace = False, p = prob)

                cost = self.tsp_sample(node, sample)
                cant[node] += 1
                suma[node] += cost

                for neigh in sample:
                    cant[neigh] += 1
                    suma[neigh] += cost
        
        return [suma[i] / cant[i] if cant[i] > 0 else 0 for i in range(n)]
