from pandas import read_parquet
from pyarrow import Table
from pyarrow.parquet import write_table

data = read_parquet('data_final.parquet')

n = len(data)

profit = [0 for _ in range(n)]

for i in range(n):
    profit[i] = data['Beneficio'][i] - data['Logistica'][i] - data['Manipuladora'][i] - data['Alimentos'][i]

data['Profit'] = profit

write_table(Table.from_pandas(data), 'data_final.parquet')