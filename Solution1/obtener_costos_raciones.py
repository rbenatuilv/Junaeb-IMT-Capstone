from pandas import read_excel, read_parquet
from pyarrow import Table
from pyarrow.parquet import write_table

beneficio_racion = 845
costo_racion = 725
sueldo_manipuladora = 358000
ratio_manipuladora = 70
dias_escolares = 180

data = read_excel('Raciones_totales.xlsx')
data2 = read_parquet('data_final.parquet')

n = len(data2)

indice = {data['RBD'][i]: i for i in range(len(data))}

beneficio = [0 for _ in range(n)]
manipuladoras = [0 for _ in range(n)]
costo = [0 for _ in range(n)]
raciones = [0 for _ in range(n)]

for i in range(n):
    for rbd in data2['RBD'][i]:
        ix = indice[rbd]
        raciones[i] = raciones[i] + int(data['A'][ix])
        raciones[i] = raciones[i] + int(data['D'][ix])
        raciones[i] = raciones[i] + int(data['T'][ix])
        raciones[i] = raciones[i] + int(data['O'][ix])
        raciones[i] = raciones[i] + int(data['C'][ix])

for i in range(n):
    beneficio[i] = beneficio_racion*raciones[i]
    costo[i] = costo_racion*raciones[i]
    raciones[i] = raciones[i]//dias_escolares
    manipuladoras[i] = sueldo_manipuladora*(((raciones[i]//2)//dias_escolares + (ratio_manipuladora - 1))//ratio_manipuladora)

data2['Manipuladora'] = manipuladoras
data2['Beneficio'] = beneficio
data2['Alimentos'] = costo
data2['Raciones'] = raciones

write_table(Table.from_pandas(data2), 'data_final.parquet')