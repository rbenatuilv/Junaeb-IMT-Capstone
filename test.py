import modules.pretty_plot as pp
import pandas as pd
import geopandas as gpd
from tqdm import tqdm

import modules.db_management as dbm
import modules.graph as g
import modules.tsp as tsp

from modules.find_neighs import get_closest, get_closest_intersect, get_closest_djikstra


##################### Efficiency test ###################

coords_labels = ['Longitud', 'Latitud']
schools = dbm.join_duplicate_schools(pd.read_excel('Data/Colegios(Continental)2020.xlsx'), coords_labels=coords_labels)

geometry = gpd.points_from_xy(schools['Longitud'], schools['Latitud'])
geo_schools = gpd.GeoDataFrame(schools, geometry=geometry, crs='EPSG:4326')

n = len(schools)

tester = tsp.TSPApprox(schools, coords_labels=coords_labels, compile=False)

r = range(100)

list1 = []
for node in tqdm(r):
    list1.append((node, tester.get_options(node, mode='euclidean')[0]))


# list2 = []
x_label = coords_labels[0]
y_label = coords_labels[1]

points = [(schools[x_label][i], schools[y_label][i]) for i in range(len(schools))]
adj_list = g.get_adj_list(points)

# for node in tqdm(range(n)):
#     list2.append(get_closest(points, adj_list, node, 25)[0])


list3 = []
for node in tqdm(r):
    list3.append((node, get_closest_djikstra(points, adj_list, node, 25, mode='euclidean')[0]))


# opt1 = list1[0]
# # opt2 = list2[0]
# opt3 = list3[0]

# print(opt1)
# # print(opt2)
# print(opt3)

for e1, e2 in zip(list1, list3):
    if e1[1] != e2[1]:
        print(e1)
        print(e2)
        print()
