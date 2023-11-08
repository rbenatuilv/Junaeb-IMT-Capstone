import subprocess
from pandas import read_parquet
from numpy.random import choice
from pyarrow import Table
from pyarrow.parquet import write_table

data = read_parquet('data_final.parquet')

compile_command = ["g++", "TSP.cpp", "-o", "TSP"]
run_command = ["./TSP"]
compile_process = subprocess.run(compile_command, stdout = subprocess.PIPE)

MAXD = 200000 #Maxima distancia en metros
MAXN = 12 #Máxima cantidad de colegios
C = 10*800000 #Costo fijo de tener una furgoneta
K = 10 #Número de ejemplos por cada colegio
metro_litro = 10*10**3
precio_litro = 1300
viajes = 90
factor_entero = 10**5
factor = (precio_litro*viajes)/(metro_litro*factor_entero) #Factor de conversión a pesos

n = len(data)
suma = [0 for _ in range(n)]
cant = [0 for _ in range(n)]
cost = [0 for _ in range(n)]

for i in range(n):

    if (100*i)//n != (100*(i-1))//n:
        print(f"{(100*i)//n}%")

    dis = []
    options = []
    prob = []

    for j in range(n):
        if i == j:
            continue
        dis.append([abs(data['X'][i] - data['X'][j]) + abs(data['Y'][i] - data['Y'][j]), j])
    
    dis.sort()

    for j in range(2*MAXN + 1):
        if dis[j][0] <= factor_entero*MAXD:
            options.append(dis[j][1])

    suma_prob = 0
    for j in range(2*MAXN + 1):
        if dis[j][0] <= factor_entero*MAXD:
            prob.append(factor_entero/dis[j][0])
            suma_prob = suma_prob + factor_entero/dis[j][0]

    if len(prob) == 0:
        suma[i] = C
        cant[i] = 1
        continue

    for j in range(len(prob)):
        prob[j] = prob[j]/suma_prob

    N = min(MAXN - 1, len(options))
    
    for j in range(K):

        sample = choice(options, size = N, replace = False, p = prob)

        entrada = str(N+1) + "\n"
        entrada = entrada + str(int(data['X'][i])) + " " + str(int(data['Y'][i])) + "\n"
        for u in sample:
            entrada = entrada + str(int(data['X'][u])) + " " + str(int(data['Y'][u])) + "\n"
        run_process = subprocess.run(run_command, input = entrada.encode(), stdout = subprocess.PIPE)
        res = (int(run_process.stdout.decode())*factor + C)/N
        suma[i] += res
        cant[i] += 1

        for u in sample:
            suma[u] += res
            cant[u] += 1

for i in range(n):
    if cant[i] > 0:
        cost[i] = int(suma[i]/cant[i])

data['Logistica'] = cost

write_table(Table.from_pandas(data), 'data_final.parquet')