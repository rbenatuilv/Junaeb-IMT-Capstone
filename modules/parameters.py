import geopandas as gpd
import os
import pickle


# Params for plotting
path_regs = os.path.join(os.getcwd(), 'modules', 'aux_data', 'regions.pkl')

try:
    with open(path_regs, 'rb') as file:
        REGS = pickle.load(file)
except FileNotFoundError:
    path_gpd = os.path.join(os.getcwd(), 'modules', 'aux_data', 'Regiones')
    REGS = gpd.read_file(path_gpd)
    with open(path_regs, 'wb') as file:
        pickle.dump(REGS, file)


path_regs_cont = os.path.join(os.getcwd(), 'modules', 'aux_data', 'regions_cont.pkl')
try:
    with open(path_regs, 'rb') as file:
        REGS_CONT = pickle.load(file)
except FileNotFoundError:
    path_gpd = os.path.join(os.getcwd(), 'modules', 'aux_data', 'Regiones_cont')
    REGS_CONT = gpd.read_file(path_gpd)
    with open(path_regs_cont, 'wb') as file:
        pickle.dump(REGS_CONT, file)


# Params for UT solver
MAXSZ = 250
MINSZ = 50

# Params for cost calculation
BENEF_RACION = 845
COST_RACION = 725
SUELDO_MANIP = 358000
RATIO_MANIP = 70
DIAS_ESCOLARES = 180

# Params for TSP solver
COMP_COMMAND = ["g++", "modules/aux_scripts/TSP.cpp", "-o", "TSP"]
RUN_COMMAND = ["./TSP"]
MAX_DIST = 200000  # Maxima distancia en metros
MAX_N = 12  # Máxima cantidad de colegios
VEHICLE_COST = 800000 * 10  # Costo fijo de tener una furgoneta (anual)
MAX_SAMPLE = 10  # Número de ejemplos por cada colegio

metro_litro = 10000
precio_litro = 1300
viajes = 90  # Al año
CONV_FACTOR = (precio_litro * viajes) / (metro_litro)  # Factor de conversión a pesos