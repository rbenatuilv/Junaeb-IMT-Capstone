import modules.graph as g
import modules.parameters as p
import pandas as pd
import sys


class UTSolver:
    """
    Class to solve the UT problem for a given dataset, using divide-and-conquer strategy.
    """

    def __init__(self, data: pd.DataFrame, min_racs, max_racs, profit_name: str = 'Profit', 
                 coords_labels: tuple[str] = ('X', 'Y'), racs_name: str = 'Raciones'):
        
        n = len(data)
        self.n = n

        self.profit = [data[profit_name][i] for i in range(n)]
        self.raciones = [data[racs_name][i] for i in range(n)]

        x_lab = coords_labels[0]
        y_lab = coords_labels[1]
        self.edges = g.MST([(data[x_lab][i], data[y_lab][i]) for i in range(n)])

        self.x = [data[x_lab][i] for i in range(n)]
        self.y = [data[y_lab][i] for i in range(n)]

        self.min_r = min_racs
        self.max_r = max_racs

        self.A = p.A
        self.B = p.B

        sys.setrecursionlimit(20000)

        self.initialize_auxs()

    def initialize_auxs(self):
        self.UT = [-1 for _ in range(self.n)]
        self.subv = [0 for _ in range(self.n)]
        self.subr = [0 for _ in range(self.n)]
        self.maxx = [0 for _ in range(self.n)] # Max in x of subtree below of v
        self.minx = [0 for _ in range(self.n)]
        self.maxy = [0 for _ in range(self.n)]
        self.miny = [0 for _ in range(self.n)]
        self.umaxx = [0 for _ in range(self.n)] # Max in x of subtree above of v
        self.uminx = [0 for _ in range(self.n)]
        self.umaxy = [0 for _ in range(self.n)]
        self.uminy = [0 for _ in range(self.n)]
        self.totalv = 0
        self.totalr = 0
        self.t = 0
        self.res = [-1, -1, -1]

    def get_compacity(self, v, p):
        """
        Get the compacity of a given subtree, using the ratio of the maximum 
        and minimum x and y coordinates as metric.
        """

        x1 = (self.maxx[v] - self.minx[v])
        y1 = (self.maxy[v] - self.miny[v])
        ratio1 = 0
        if min(x1, y1) != 0:
            ratio1 = max(x1, y1)/min(x1, y1) - 1

        ratio2 = 0
        maxx = self.umaxx[p]
        minx = self.uminx[p]
        maxy = self.umaxy[p]
        miny = self.uminy[p]

        for u in self.edges[p]:
            if self.subr[u] > self.subr[p] or u == v:
                continue
            maxx = max(maxx, self.maxx[u])
            minx = min(minx, self.minx[u])
            maxy = max(maxy, self.maxy[u])
            miny = max(miny, self.miny[u])

        x2 = maxx - minx
        y2 = maxy - miny
        ratio2 = 0

        if min(x2, y2) != 0:
            ratio2 = max(x2, y2)/min(x2, y2) - 1

        return ratio1 + ratio2
    
    def get_split_val(self, v, total):
        """
        Get the split value of a given subtree, using the ratio of values as metric.
        """

        v1 = self.subv[v]
        v2 = total - self.subv[v]
        ratio = 0
        if min(v1, v2) != 0:
            ratio = max(v1, v2)/min(v1, v2) - 1

        return ratio

    def get_subtree_metrics(self, v, p):
        """
        Get the metrics of a given subtree, such as the total value, the total number of rations,
        the maximum and minimum x and y coordinates, and the maximum and minimum x and y coordinates
        of the subtree without the current node.
        """
        
        self.subv[v] = self.profit[v]
        self.subr[v] = self.raciones[v]
        self.maxx[v] = self.x[v]
        self.minx[v] = self.x[v]
        self.maxy[v] = self.y[v]
        self.miny[v] = self.y[v]
        self.umaxx[v] = self.x[v]
        self.uminx[v] = self.x[v]
        self.umaxy[v] = self.y[v]
        self.uminy[v] = self.y[v]

        if p != -1:
            self.umaxx[v] = max(self.x[v], self.umaxx[p])
            self.uminx[v] = min(self.x[v], self.uminx[p])
            self.umaxy[v] = max(self.y[v], self.umaxy[p])
            self.uminy[v] = min(self.y[v], self.uminy[p])
        else:
            self.umaxx[v] = self.x[v]
            self.uminx[v] = self.x[v]
            self.umaxy[v] = self.y[v]
            self.uminy[v] = self.y[v]

        for u in self.edges[v]:
            if u == p:
                continue
            self.get_subtree_metrics(u, v)
            
            self.subv[v] += self.subv[u]
            self.subr[v] += self.subr[u]
            self.maxx[v] = max(self.maxx[v], self.maxx[u])
            self.minx[v] = min(self.minx[v], self.minx[u])
            self.maxy[v] = max(self.maxy[v], self.maxy[u])
            self.miny[v] = min(self.miny[v], self.miny[u])
        return

    def find_best_split(self, v, p):
        """
        Find the best split for a given tree, using ratio of values and compacity as metrics.
        """
    
        if self.subr[v] < self.min_r or len(self.edges[v]) == 0:
            return
    
        for u in self.edges[v]:
            if u == p:
                continue
            ratio_val = self.get_split_val(u, self.totalv)
            ratio_compacity = self.get_compacity(u, v)
            if self.A*ratio_val + self.B*ratio_compacity < self.res[0] and (self.totalr - self.subr[u]) >= self.min_r:
                self.res = [self.A*ratio_val + self.B*ratio_compacity, v, u]
            self.find_best_split(u, v)

    def assign_ut_to_nodes(self, v, p):
        """
        Assign UTs to the nodes of a given tree, when the size of the subtree is small enough.
        """
        self.UT[v] = self.t
        for u in self.edges[v]:
            if u == p:
                continue
            self.assign_ut_to_nodes(u, v)

    def rec_solve(self, root):
        """
        Solve recursively the UT problem for a given tree, finding the best split 
        and assigning UTs to the nodes when the size of the subtree is small enough.
        """

        self.get_subtree_metrics(root, -1)
    
        self.totalv = self.subv[root]
        self.totalr = self.subr[root]

        if self.totalr <= self.max_r:
            self.assign_ut_to_nodes(root, -1)
            print(f'UTs assigned: {self.t}', end='\r')
            self.t += 1
            return

        self.res = [3*self.totalv, -1, -1]
        self.find_best_split(root, -1)

        root1 = self.res[1]
        root2 = self.res[2]
        self.edges[root1].remove(root2)
        self.edges[root2].remove(root1)

        self.rec_solve(root1)
        self.rec_solve(root2)

    def solve(self):
        """
        Solve the UT problem for the dataset, using divide-and-conquer strategy.
        """
        for i in range(self.n):
            if self.UT[i] == -1:
                self.rec_solve(i)

