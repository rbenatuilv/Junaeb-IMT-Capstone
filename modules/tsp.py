import subprocess
from numpy.random import choice
import pandas as pd
import modules.parameters as p
import modules.graph as g
import modules.geo as geo
from tqdm import tqdm
import heapq


class TSPApprox:
    def __init__(self, data: pd.DataFrame, coords_labels: tuple[str] = ('X, Y'),
                 compile: bool = True):
        self.data = data
        self.x_label = coords_labels[0]
        self.y_label = coords_labels[1]
        self.points = [(data[self.x_label][i], data[self.y_label][i]) 
                       for i in range(len(data))]
        self.adj_list = g.get_adj_list(self.points)

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
    
    def get_options_dijkstra(self, node: int, mode: str = 'manhattan') -> tuple[list[int], list[float]]:
        """
        Obtains the list of nearby nodes within the maximum distance, using
        Dijkstra's algorithm.
        """
       
        visited = dict()
        heap = [(0, node)]

        while heap:
            dist, next = heapq.heappop(heap)
            if next in visited:
                continue
            visited[next] = dist

            for neigh in self.adj_list[next]:
                if neigh not in visited:
                    d = g.distance(self.points[node], self.points[neigh], mode=mode)
                    if d <= self.maxd:
                        heapq.heappush(heap, (d, neigh))

            if len(visited) > 2 * self.maxn + 1:
                break

        visited.pop(node)
        visited = list(visited.items())
        visited.sort(key=lambda x: x[1])
        visited = visited[:2 * self.maxn + 1]

        tot_prob = sum([1 / x[1] for x in visited])
        probs = [(1 / x[1]) / tot_prob for x in visited]
        visited = [x[0] for x in visited]

        return visited, probs


    def get_options(self, node: int, mode: str = 'manhattan') -> tuple[list[int], list[float]]:
        """
        Obtains the list of nearby nodes within the maximum distance.
        Naive version.
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
            dist.append([g.distance(point, other_point, mode=mode), other])
        
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

            options, prob = self.get_options_djikstra(node)

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
