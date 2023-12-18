from pandas import read_parquet
from pyarrow import Table
from pyarrow.parquet import write_table
from parametros import factor_entero, MAXD

data = read_parquet('data_final.parquet')
n = len(data)
k = max(data['UT'][i] for i in range(n)) + 1
print(k)

UT = [data['UT'][i] for i in range(n)]
maxi = 0
for u in UT:
    maxi = max(maxi, u)

profit = [0 for _ in range(k)]

for i in range(n):
    profit[UT[i]] = profit[UT[i]] + data['Profit'][i]//1000000

mini = 100000000000000000
maxi = 0
media = 0
for i in range(k):
    media = media + profit[i]
    mini = min(mini, profit[i])
    maxi = max(maxi, profit[i])
media = media/k
print(profit)
print(sum(profit))

edges = [[] for _ in range(k)]

for i in range(n):
    for j in data['Aristas'][i]:
        if UT[j] not in edges[UT[i]] and UT[i] != UT[j] and (abs(data['X'][i] - data['X'][j]) + abs(data['Y'][i] - data['Y'][j])) < factor_entero*MAXD:
            edges[UT[i]].append(UT[j])

sumdiff = 0
maxdiff = 0
mindiff = 100000
contar = 0

for i in range(k):
    for j in edges[i]:
        print(max(profit[i], profit[j]), min(profit[i], profit[j]))
        sumdiff = sumdiff + max(profit[i], profit[j])/min(profit[i], profit[j])
        contar = contar + 1
        maxdiff = max(maxdiff, max(profit[i], profit[j])/min(profit[i], profit[j]))
        mindiff = min(mindiff, max(profit[i], profit[j])/min(profit[i], profit[j]))

print(sumdiff/contar)
print(maxdiff)
print(mindiff)

#print(maxi/mini, maxdiff)

