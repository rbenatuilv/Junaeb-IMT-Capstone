import modules.requirements as req
import os
import signal


TEST = False  # Set to True to test the code with a single region (7)
SAVE_LOGISTICS = True  # Set to True to save the logistics of each school
USE_LOGISTICS = False  # Set to True to use the logistics of each school

#################### Data parameters ######################

parent_folder = 'Data'
rations_folder = 'Raciones'

schools_file = 'Colegios(Continental)2020.xlsx'
rations_file = 'Raciones_totales_2019.xlsx'

coords_labels = ['Longitud', 'Latitud']

#################### Interrupt handler ####################

def handle_interrupt(signal, frame):
    print('\n\nInterrupted by user. Exiting...\n')
    exit(0)

signal.signal(signal.SIGINT, handle_interrupt)

#################### Check requirements ##################

print('\n' + 'JUNAEB UT CREATOR'.center(80, '-') + '\n')

print('CHECKING REQUIREMENTS...\n')

req.check_import_requirements()
req.check_data_requirements(parent_folder=parent_folder, 
                            schools_file=schools_file,
                            rations_folder=rations_folder, 
                            rations_file=rations_file)

print('Done!\n')


import modules.tsp as tsp
import modules.ut_solver as ut
import modules.db_management as dbm
import modules.pretty_plot as pp
import modules.parameters as p
import pandas as pd


##################### Load data #########################

print('LOADING DATA...\n')

print('Loading schools data...', end='')
path_schools = os.path.join(parent_folder, schools_file)
schools = pd.read_excel(path_schools)

if TEST:
    schools = schools[schools['Region'] == 7].reset_index(drop=True)

print('Done!')

print('Loading rations data...', end='')
path_rations = os.path.join(parent_folder, rations_folder, rations_file)
rations = pd.read_excel(path_rations)
print('Done!\n')

#################### Data management ####################

print('PROCESSING DATA...\n')

data = dbm.join_duplicate_schools(schools, coords_labels=coords_labels)
dbm.add_food_rations_and_costs(data, rations)

#################### TSP solver #########################

if not USE_LOGISTICS:
    print('\nSOLVING TSPs...\n')
    tsp_solver = tsp.TSPApprox(data, coords_labels=coords_labels)
    data['Logistica'] = tsp_solver.solve()

    if SAVE_LOGISTICS:
        dbm.save_data(data[['Logistica']], 'logistics.xslx')

else:
    print('\nLOADING LOGISTICS...', end='')
    data['Logistica'] = pd.read_excel('logistics.xslx')['Logistica']
    print('Done!\n')

###################### Profit ###########################

print('\nADDING PROFITS...', end='')

dbm.add_profit(data)

print('Done!\n')

#################### UT solver ##########################

print('SOLVING UTs...\n')

ut_solver = ut.UTSolver(data, min_racs=p.MINR, max_racs=p.MAXR, coords_labels=coords_labels)
ut_solver.solve()

data['UT'] = ut_solver.UT

print('\nDone!\n')

################### UT assignation ######################

print('ASSIGNING UTs...', end='')

schools = dbm.ut_assignation(data, schools)

print('Done!\n')

#################### Save data ##########################

print('SAVING DATA...', end='')

if TEST:
    path = os.path.join('(TEST) Colegios2020(UTs).xlsx')
else:
    path = os.path.join('Colegios2020(UTs).xlsx')

dbm.save_data(schools, path)
print('Done!\n')

#################### Plotting ###########################

print('PLOTTING...\n')

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

colors1 = plt.cm.Dark2(np.linspace(0,1))
colors2 = plt.cm.tab10(np.linspace(0,1))
colors3 = plt.cm.Set1(np.linspace(0,1))

colors = np.vstack((colors1, colors2, colors3, colors1, colors2, colors3))
mymap = mcolors.LinearSegmentedColormap.from_list('my_colormap', colors)

regs = schools['Region'].unique()

if not os.path.exists('plots'):
    os.makedirs('plots')

for r in regs:
    pp.single_plot_uts(r, schools, save=True, folder='plots', test=TEST,
                       cmap=mymap, legend=True, markersize=20, marker='x')

pp.total_plot_uts(schools, (4, 4), save=True, folder='plots', test=TEST,
                  cmap=mymap, legend=True, markersize=2, marker='x')

print('\nDone!\n')

#########################################################