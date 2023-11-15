from pandas import read_csv, DataFrame
from pyarrow import Table
from pyarrow.parquet import write_table

data = read_csv('colegios_final.csv')
n = len(data)

RBD = []
x = []
y = []
geo = []

for i in range(n):
    where = -1
    for j in range(len(x)):
        if x[j] == data['x'][i] and y[j] == data['y'][i]:
            where = j
    if where == -1:
        x.append(int(data['x'][i]))
        y.append(int(data['y'][i]))
        RBD.append([int(data['RBD'][i])])
        geo.append(data['geometry'][i])
    else:
        RBD[where].append(int(data['RBD'][i]))

data2 = DataFrame()
data2['RBD'] = RBD
data2['X'] = x
data2['Y'] = y
data2['geometry'] = geo

write_table(Table.from_pandas(data2), 'data_final.parquet')
