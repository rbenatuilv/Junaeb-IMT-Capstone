import subprocess
from geopandas import read_parquet
from numpy.random import choice

data = read_parquet('colegios.parquet')

compile_command = ["g++", "TSP.cpp", "-o", "TSP"]
run_command = ["./TSP"]
compile_process = subprocess.run(compile_command, stdout = subprocess.PIPE)

MAXN = 12 #Máxima cantidad de colegios
C = 800000 #Costo fijo de tener una furgoneta
K = 10 #Número de ejemplos por cada colegio
metro_litro = 10*10**3
precio_litro = 1300
viajes_mes = 14
factor_entero = 10**5
factor = (precio_litro*viajes_mes)/(metro_litro*factor_entero) #Factor de conversión a pesos

n = len(data)
suma = [0 for _ in range(n)]
cant = [0 for _ in range(n)]

for i in range(n):

    options = data['closest'][i]
    prob = data['prob'][i]
    N = min(MAXN - 1, len(options))
    
    for j in range(K):

        sample = choice(options, size = N, replace = False, p = prob)

        entrada = str(N+1) + "\n"
        entrada = entrada + str(int(data['x'][i]/10)) + " " + str(int(data['y'][i]/10)) + "\n"
        for u in sample:
            entrada = entrada + str(int(data['x'][u]/10)) + " " + str(int(data['y'][u]/10)) + "\n"
        run_process = subprocess.run(run_command, input = entrada.encode(), stdout = subprocess.PIPE)
        res = (int(run_process.stdout.decode())*factor + C)/N

        suma[i] += res
        cant[i] += 1

        for u in sample:
            suma[u] += res
            cant[u] += 1

for i in range(n):
    data['value'][i] = int(suma[i]/cant[i])

data.to_csv("colegios_final.csv")