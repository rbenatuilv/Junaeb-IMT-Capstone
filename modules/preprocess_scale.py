import pandas as pd
import numpy as np
import os
import pickle
import statsmodels.api as sm

def xlxs_to_pickle(folder : str='Data', 
                   xlxs_path : str='Copia de PAE_2019.xlsx', 
                   pickle_path : str='DATA_JUNAEB2019.pkl'):

    path = os.path.join(folder, xlxs_path)
    data = pd.read_excel(path)

    path_pickle = os.path.join(folder, pickle_path)
    with open(path_pickle, 'wb') as archivo:
        pickle.dump(data, archivo)
    return

def open_pickle(folder : str='Data', 
                pickle_path : str='DATA_JUNAEB2019.pkl'):
    path_pickle = os.path.join(folder, pickle_path)
    path = os.path.join(path_pickle)
    with open(path, 'rb') as file:
        data = pickle.load(file)
    return data



def basic_preprocess(data):
    data = data.rename(columns = {'InstituciÃ³n':'Institución', 'Ute':'UT_2019'})
    data['Servicio'] = data['Servicio'].str.strip()
    data = data[data['Institución'] == 'JU'] # Seleccionar data JUNAEB
    return data

    

def rbd_metrics_calc(data, schools):
    rbds = list(schools.RBD.values)
    services = data.Servicio.unique()

    raciones = {ser: [] for ser in services}
    raciones['UT_2019'] = []
    raciones['empresa'] = []
    precios = {ser: [] for ser in services}
    total_pagado = {ser: [] for ser in services}
    unitary_prices = {ser: [] for ser in services} # auxiliar para gráficar

    for rbd in rbds:
        selected_data = data[data['Rbd'] == rbd]
        hay_servicio = False
        for ser in services:
            if ser in selected_data['Servicio'].unique():
                hay_servicio = True
                raciones_servicio = selected_data[selected_data['Servicio'] == ser]['TotalRacEqAsigMes']
                precios_servicio = selected_data[selected_data['Servicio'] == ser]['Precio']
                pagado_servicio = (precios_servicio*raciones_servicio).sum()

                if raciones_servicio.sum() != 0:
                    raciones[ser].append(raciones_servicio.sum())
                    precios[ser].append(pagado_servicio/raciones_servicio.sum()) # Promedio ponderado de precio_por_racion
                    total_pagado[ser].append(pagado_servicio)
                    unitary_prices[ser].append((pagado_servicio/raciones_servicio.sum(), raciones_servicio.sum()))
                else:
                    raciones[ser].append(0)
                    precios[ser].append(0)
                    total_pagado[ser].append(0)
                    unitary_prices[ser].append((0,0))
            else:
                raciones[ser].append(0)
                precios[ser].append(0)
                total_pagado[ser].append(0)
                unitary_prices[ser].append((0,0))
        
        if hay_servicio:
            raciones['empresa'].append(selected_data['RUTEmpresa'].values[0])
            raciones['UT_2019'].append(selected_data['UT_2019'].values[0])
        else:
            raciones['empresa'].append(-1)
            raciones['UT_2019'].append(-1)
                
    raciones['RBD'] = list(rbds)
    precios['RBD'] = list(rbds)
    total_pagado['RBD'] = list(rbds)
    unitary_prices['RBD'] = list(rbds)

    return raciones, total_pagado



def join_metrics(raciones, total_pagado, ruteo):
    restr1 = np.all(raciones.drop('empresa', axis=1).max()*10 < 2**64)
    restr2 = np.all(total_pagado.max()*10 < 2**64)
    if restr1 or restr2:
        raise ValueError("Values are greater than int64 supports")
    
    raciones['raciones_sum'] = raciones.drop(['RBD', 'UT_2019', 'empresa'], axis=1).sum(axis=1)
    total_pagado['pagado_sum'] = total_pagado.drop('RBD', axis=1).sum(axis=1)
    sum_df = pd.merge(raciones[['raciones_sum', 'RBD', 'UT_2019', 'empresa']], 
                      total_pagado[['pagado_sum', 'RBD']], on='RBD')
    
    raciones_con_ruteo = sum_df.join(ruteo[['RBD', 'value', 'UTE', 'Region', 'x', 'y']].set_index('RBD'), on='RBD', how='left')
    data_sum_x_ut = raciones_con_ruteo[raciones_con_ruteo['UT_2019'] != -1]
    data_sum_x_ut = data_sum_x_ut[['raciones_sum', 'pagado_sum', 'value', 'empresa']].groupby(by=['empresa']).sum()

    restr1 = np.all(data_sum_x_ut.max() < 2**64)
    restr2 = np.all(data_sum_x_ut.max() < 2**64)
    if restr1 or restr2:
        raise ValueError("Values are greater than int64 supports")
    
    return data_sum_x_ut
    

def adjusted_unitary_price(data):
    alpha = 1
    data['pagado_ajustado'] = (data['pagado_sum'] - alpha * data['value'] )/data['raciones_sum']
    return data

def adjust_weighted_ols(data):
    x = data[['raciones_sum']]
    y = data['pagado_ajustado']

    # Fit a model to estimate the residuals
    model_ols = sm.OLS(y, sm.add_constant(x)).fit()
    residuals = model_ols.resid

    # Model the relationship between variance and predictor variable
    # You can choose a different functional form based on your observations
    variance_model = sm.OLS(np.abs(residuals), sm.add_constant(x)).fit()
    predicted_variance = variance_model.predict(sm.add_constant(x))

    # Create weights based on the inverse of the predicted variance
    weights = 1.0 / np.sqrt(predicted_variance)

    # Fit a WLS model
    wls_model = sm.WLS(y, sm.add_constant(x), weights=weights)

    # Fit the model
    wls_results = wls_model.fit()

    # Print the summary
    return wls_results.params
    print(wls_results.summary(alpha=0.1))
    
folder = 'Data'
xlxs_path = 'Copia de PAE_2019.xlsx'
pickle_path = 'DATA_JUNAEB2019.pkl'
schools_path = 'Colegios(Continental)2020.xlsx'

xlxs_to_pickle(folder, xlxs_path, pickle_path)
data = open_pickle(folder, pickle_path)
data = basic_preprocess(data)

path = os.path.join(folder, schools_path)
schools = pd.read_excel(path)

raciones, total_pagado = rbd_metrics_calc(data, schools)

folder = 'Solution1'
ruteo_path = 'colegios_final.csv'
path = os.path.join(folder, ruteo_path)
ruteo = pd.read_csv(path)

data_sum_x_ut = join_metrics(raciones, total_pagado, ruteo)
data_sum_x_ut = adjusted_unitary_price(data_sum_x_ut)
params_ols = adjust_weighted_ols(data_sum_x_ut)
