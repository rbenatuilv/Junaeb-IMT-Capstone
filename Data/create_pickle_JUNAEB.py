import pickle
import pandas as pd
import os


folder = 'Consolidado2020'
meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
ruta_pickle = 'DATA_JUNAEB.pkl'

data = dict()
for mes in meses:
    print(f'Creating dataframe: {mes}')
    path = os.path.join(folder, f'{mes}_JUNAEB.xlsx')
    data[mes[:3]] = pd.read_excel(path)

with open(ruta_pickle, 'wb') as archivo:
    pickle.dump(data, archivo)
