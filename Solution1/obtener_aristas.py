from numpy import array
from scipy.spatial import Delaunay
from pandas import read_parquet
from pyarrow import Table
from pyarrow.parquet import write_table


data = read_parquet('data_final.parquet')
n = len(data)

points = array([[data['X'][i], data['Y'][i]] for i in range(n)])

tri = Delaunay(points)

edges = [[] for _ in range(n)]

for u in tri.simplices:
    if u[1] not in edges[u[0]]:
        edges[u[0]].append(u[1])
    if u[2] not in edges[u[0]]:
        edges[u[0]].append(u[2])
    if u[0] not in edges[u[1]]:
        edges[u[1]].append(u[0])
    if u[2] not in edges[u[1]]:
        edges[u[1]].append(u[2])
    if u[0] not in edges[u[2]]:
        edges[u[2]].append(u[0])
    if u[1] not in edges[u[2]]:
        edges[u[2]].append(u[1])

data['Aristas'] = edges
write_table(Table.from_pandas(data), 'data_final.parquet')