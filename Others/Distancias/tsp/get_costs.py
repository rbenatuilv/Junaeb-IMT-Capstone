import subprocess
from pandas import read_csv
from random import sample

compile_command = ["g++", "TSP.cpp", "-o", "TSP"]
run_command = ["./TSP"]
compile_process = subprocess.run(compile_command, stdout = subprocess.PIPE)

MAXN = 12 #Máxima cantidad de colegios
#MAXR = 5000 #Máxima cantidad de raciones
MAXD = 1006065184946015 #Máxima distancia entre el colegio de inicio
#C = 600000 #Costo fijo de tener una furgoneta
K = 10 #Número de ejemplos por cada colegio
#factor = (10**10) #Factor de conversión a pesos

data = read_csv("colegios_filtrados.csv")
n = len(data)

x = [int(10**10*data.loc[i, 'x']) for i in range(n)]
y = [int(10**10*data.loc[i, 'y']) for i in range(n)]
sum = [0 for _ in range(n)]
num = [0 for _ in range(n)]

#for i in range(n):
for i in range(3):

    population = []
    for j in range(n):
        if i == j:
            continue
        population.append([abs(x[i] - x[j]) + abs(y[i] - y[j]), j])
    population.sort()

    options = []

    for j in range(2*MAXN):
        options.append(population[j][1])

    for j in range(K):

        schools = [i] + sample(options, MAXN - 1)

        entrada = str(len(schools)) + "\n"
        for u in schools:
            entrada = entrada + str(x[u]) + " " + str(y[u]) + "\n"

        run_process = subprocess.run(run_command, input = entrada.encode(), stdout = subprocess.PIPE)
        #res = (int(run_process.stdout.decode()) + C)/len(schools)
        res = int(run_process.stdout.decode())/len(schools)

        for u in schools:
            sum[u] = sum[u] + res
            num[u] = num[u] + 1

#for i in range(n):
for i in range(3):
    data.loc[i, 'values'] = int(sum[i]/num[i])

data.to_csv("colegios_final.csv")
