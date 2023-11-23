import modules.tsp as tsp
import modules.ut_solver as ut
import modules.db_management as dbm
import modules.pretty_plot as pp
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt


##################### Load data #########################

print('LOADING DATA...\n')

parent_folder = 'Data'
rations_folder = 'Raciones'

schools_file = 'Colegios(Continental)2020.xlsx'
rations_file = 'Raciones_totales.xlsx'

print('Loading schools data...', end='')
path_schools = os.path.join(parent_folder, schools_file)
schools = pd.read_excel(path_schools)

# Use this line to filter by region (testing purposes)
# schools = schools[schools['Region'] == 7].reset_index(drop=True)

print('Done!')

print('Loading rations data...', end='')
path_rations = os.path.join(parent_folder, rations_folder, rations_file)
rations = pd.read_excel(path_rations)
print('Done!\n')

coords_labels = ['Longitud', 'Latitud']

#################### Data management ####################

print('PROCESSING DATA...\n')

data = dbm.join_duplicate_schools(schools, coords_labels=coords_labels)
dbm.add_food_rations_and_costs(data, rations)

#################### TSP solver #########################

print('\nSOLVING TSPs...\n')
tsp_solver = tsp.TSPApprox(data, coords_labels=coords_labels)
data['Logistica'] = tsp_solver.solve()

###################### Profit ###########################

print('\nADDING PROFITS...', end='')

dbm.add_profit(data)

print('Done!\n')

#################### UT solver ##########################

print('SOLVING UTs...')

data['UT'] = ut.ut_solver(data, coords_labels=coords_labels)

print('\nDone!\n')

################### UT assignation ######################

print('ASSIGNING UTs...', end='')

schools = dbm.ut_assignation(data, schools)

print('Done!\n')

#################### Save data ##########################

print('SAVING DATA...', end='')
path = os.path.join('Colegios2020(UTs).xlsx')
dbm.save_data(schools, path)
print('Done!\n')

#################### Plotting ###########################

print('PLOTTING...\n')

regs = schools['Region'].unique()

if not os.path.exists('plots'):
    os.makedirs('plots')

for r in regs:
    pp.single_plot_uts(r, schools, save=True, folder='plots', 
                       cmap='tab20', legend=True, markersize=10, marker='x')

pp.total_plot_uts(schools, (4, 4), save=True, folder='plots', 
                  cmap='tab20', legend=True, markersize=1, marker='x')

print('\nDone!\n')

#########################################################