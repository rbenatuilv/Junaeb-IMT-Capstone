import modules.graph as g
import modules.parameters as p
import pandas as pd


def solve(root: int, edges: list[int], profit: list, uts: list[int], 
          current_ut: list[int], subval: list, subsize: list[int]):
    """
    Solve recursively the UT problem for a given tree, finding the best split 
    and assigning UTs to the nodes when the size of the subtree is small enough.
    """

    g.get_subtree_metrics(root, -1, edges, profit, subval, subsize)
    
    totalv = subval[root]
    totalsz = subsize[root]

    if totalsz <= p.MAXSZ:
        g.assign_ut_to_nodes(root, -1, edges, uts, current_ut[0])
        print(f'Assigned UT {current_ut[0]} to {totalsz} schools')

        current_ut[0] += 1
        return

    res = [3*totalv, -1, -1]
    g.find_best_split(root, -1, edges, subval, subsize, totalv, res)

    root1 = res[1]
    root2 = res[2]
    edges[root1].remove(root2)
    edges[root2].remove(root1)

    solve(root1, edges, profit, uts, current_ut, subval, subsize)
    solve(root2, edges, profit, uts, current_ut, subval, subsize)


def ut_solver(data: pd.DataFrame, col_name: str = 'Profit', 
              coords_labels: tuple[str] = ('X, Y')) -> list[int]:
    """
    Solve the UT problem for a given dataset, using divide-and-conquer strategy.
    """
    x = coords_labels[0]
    y = coords_labels[1]

    n = len(data)
    profit = [data[col_name][i] for i in range(n)]
    points = [(data[x][i], data[y][i]) for i in range(n)]

    root = 0
    edges = g.MST(points)
    uts = [-1 for _ in range(n)]
    current_ut = [0]
    subval = [0 for _ in range(n)]
    subsize = [0 for _ in range(n)]

    solve(root, edges, profit, uts, current_ut, subval, subsize)

    return uts
