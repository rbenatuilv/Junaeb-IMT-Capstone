import modules.pretty_plot as pp
import pandas as pd
import geopandas as gpd
from tqdm import tqdm

import modules.db_management as dbm
import modules.geo as geo
import modules.tsp as tsp



##################### Load data #########################

# schools = pd.read_excel('(TEST) Colegios(Continental)2020(UTs).xlsx')

# pp.single_plot_uts(7, schools, legend=True, markersize=10, marker='x', cmap='tab20')

##################### Efficiency test ###################

coords_labels = ['Longitud', 'Latitud']
schools = dbm.join_duplicate_schools(pd.read_excel('Data/Colegios(Continental)2020.xlsx'), coords_labels=coords_labels)

geometry = gpd.points_from_xy(schools['Longitud'], schools['Latitud'])
geo_schools = gpd.GeoDataFrame(schools, geometry=geometry, crs='EPSG:4326')

n = len(schools)

tester = tsp.TSPApprox(schools, coords_labels=coords_labels, compile=False)

list1 = []
for node in tqdm(range(n)):
    list1.append(tester.get_options(node))

print(list1)

list2 = []
for node in tqdm(range(n)):
    list2.append(tester.get_options_optimized(node))

print(list2)

print(list1 == list2)