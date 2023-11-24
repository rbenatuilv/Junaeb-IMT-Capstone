import modules.tsp as tsp
import modules.ut_solver as ut
import modules.db_management as dbm
import modules.pretty_plot as pp
import modules.parameters as p
import modules.requirements as req

import pandas as pd
import os
import signal
from time import sleep


TEST = False  # Set to True to test the code with a single region (7)

#################### Data parameters ######################

parent_folder = 'Data'
rations_folder = 'Raciones'

schools_file = 'Colegios(Continental)2020.xlsx'
rations_file = 'Raciones_totales.xlsx'

coords_labels = ['Longitud', 'Latitud']


#################### Interrupt handler ####################

def handle_interrupt(signal, frame):
    print('\n\nInterrupted by user. Exiting...\n')
    exit(0)

signal.signal(signal.SIGINT, handle_interrupt)

#################### Check requirements ##################

print('\n' + 'JUNAEB UT CREATOR'.center(100, '-') + '\n')

print('CHECKING REQUIREMENTS...\n')

req.check_import_requirements()
req.check_data_requirements(parent_folder=parent_folder, 
                            schools_file=schools_file,
                            rations_folder=rations_folder, 
                            rations_file=rations_file)

print('Done!\n')

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

print('\nSOLVING TSPs...\n')
tsp_solver = tsp.TSPApprox(data, coords_labels=coords_labels)
data['Logistica'] = tsp_solver.solve()

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

regs = schools['Region'].unique()

if not os.path.exists('plots'):
    os.makedirs('plots')

for r in regs:
    pp.single_plot_uts(r, schools, save=True, folder='plots', test=TEST,
                       cmap='tab20', legend=True, markersize=10, marker='x')

pp.total_plot_uts(schools, (4, 4), save=True, folder='plots', test=TEST,
                  cmap='tab20', legend=True, markersize=1, marker='x')

print('\nDone!\n')

#########################################################