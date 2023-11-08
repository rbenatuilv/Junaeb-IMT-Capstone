from pandas import read_parquet
from pyarrow import Table
from pyarrow.parquet import write_table
from parametros import MAXSZ, MINSZ

def find(u, padre):
    if u == padre[u]:
        return u
    padre[u] = find(padre[u], padre)
    return padre[u]

def union(u, v, padre, largo):

    u = find(u, padre)
    v = find(v, padre)

    if u == v:
        return
    
    if largo[u] >= largo[v]:
        padre[v] = u
        largo[u] += largo[v]
    else:
        padre[u] = v
        largo[v] += largo[u]
    
    return


def MST(data):
    n = len(data)
    padre = [i for i in range(n)]
    largo = [1 for _ in range(n)]
    aristas = []
    edges = [[] for _ in range(n)]

    for i in range(n):
        for j in data['Aristas'][i]:
            aristas.append([abs(data['X'][i] - data['X'][j]) + abs(data['Y'][i] - data['Y'][j]), i, j])

    aristas.sort()

    for u in aristas:
        if find(u[1], padre) != find(u[2], padre):
            union(u[1], u[2], padre, largo)
            edges[u[1]].append(u[2])
            edges[u[2]].append(u[1])

    return edges

def dfs(v, p, edges, profit, subv, subsz):
    subv[v] = profit[v]
    subsz[v] = 1
    for u in edges[v]:
        if u == p:
            continue
        dfs(u, v, edges, profit, subv, subsz)
        subv[v] = subv[v] + subv[u]
        subsz[v] = subsz[v] + subsz[u]
    return

def dfs2(v, p, edges, subv, subsz, totalv, res):
    
    if subsz[v] < MINSZ or len(edges[v]) == 0:
        return
    
    for u in edges[v]:
        if u == p:
            continue
        if abs((totalv - subv[u]) - subv[u]) < res[0]:
            res[0] = abs((totalv - subv[u]) - subv[u])
            res[1] = v
            res[2] = u
        dfs2(u, v, edges, subv, subsz, totalv, res)

    return res

def dfs3(v, p, edges, UT, t):
    UT[v] = t[0]
    for u in edges[v]:
        if u == p:
            continue
        dfs3(u, v, edges, UT, t)

def solve(edges, profit, UT, t, root, subv, subsz):

    dfs(root, -1, edges, profit, subv, subsz)
    
    totalv = subv[root]
    totalsz = subsz[root]

    if totalsz <= MAXSZ:
        dfs3(root, -1, edges, UT, t)
        t[0] = t[0] + 1
        return

    res = [3*totalv, -1, -1]
    dfs2(root, -1, edges, subv, subsz, totalv, res)

    root1 = res[1]
    root2 = res[2]
    edges[root1].remove(root2)
    edges[root2].remove(root1)

    solve(edges, profit, UT, t, root1, subv, subsz)
    solve(edges, profit, UT, t, root2, subv, subsz)

    return

data = read_parquet('data_final.parquet')

n = len(data)

profit = [data['Profit'][i] for i in range(n)]
nodos = [i for i in range(n)]
UT = [-1 for _ in range(n)]
subv = [0 for _ in range(n)]
subsz = [0 for _ in range(n)]
edges = MST(data)
t = [0]

solve(edges, profit, UT, t, 0, subv, subsz)

data['UT'] = UT
write_table(Table.from_pandas(data), 'data_final.parquet')