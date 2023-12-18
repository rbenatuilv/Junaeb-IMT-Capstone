import geopandas as gpd
import os
import pickle
import platform


# Params for UT solver
MAXSZ = 250
MINSZ = 50
MAXR = 60000
MINR = 15000
A = 1
B = 0

# Params for cost calculation
BENEF_RACION = 925
COST_RACION = 740
SUELDO_MANIP = 358000
RATIO_MANIP = 70
DIAS_ESCOLARES = 180

# Params for TSP solver
MAX_DIST = 200000  # Maxima distancia en metros
MAX_N = 12  # Máxima cantidad de colegios
VEHICLE_COST = 800000 * 10  # Costo fijo de tener una furgoneta (anual)
MAX_SAMPLE = 10  # Número de ejemplos por cada colegio

metro_litro = 10000
precio_litro = 1300
viajes = 90  # Al año
CONV_FACTOR = (precio_litro * viajes) / (metro_litro)  # Factor de conversión a pesos


# Params for compiler
cpp_file = os.path.join(os.getcwd(), 'modules', 'aux_scripts', 'TSP.cpp')
if platform.system() == 'Darwin':
    COMP_COMMAND = ["clang++", "-o", cpp_file, "TSP"]
else:
    COMP_COMMAND = ["g++", cpp_file, "-o", "TSP"]

RUN_COMMAND = ["./TSP"]


# Params for plotting
path_regs = os.path.join(os.getcwd(), 'modules', 'aux_data', 'regions.pkl')

try:
    with open(path_regs, 'rb') as file:
        REGS = pickle.load(file)
except FileNotFoundError:
    path_gpd1 = os.path.join(os.getcwd(), 'modules', 'aux_data', 'Regiones')
    REGS = gpd.read_file(path_gpd1).to_crs(epsg=4326)
    with open(path_regs, 'wb') as file:
        pickle.dump(REGS, file)


path_regs_cont = os.path.join(os.getcwd(), 'modules', 'aux_data', 'regions_cont.pkl')
try:
    with open(path_regs_cont, 'rb') as file:
        REGS_CONT = pickle.load(file)
except FileNotFoundError:
    path_gpd2 = os.path.join(os.getcwd(), 'modules', 'aux_data', 'Regiones_cont')
    REGS_CONT = gpd.read_file(path_gpd2).to_crs(epsg=4326)
    with open(path_regs_cont, 'wb') as file:
        pickle.dump(REGS_CONT, file)