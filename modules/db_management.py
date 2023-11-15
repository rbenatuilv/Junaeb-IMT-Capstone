import pandas as pd
import modules.parameters as p
from tqdm import tqdm


def join_duplicate_schools(data: pd.DataFrame, coords_labels: tuple[str] = ('X, Y'), 
                           rbd_label: str = 'RBD') -> pd.DataFrame:
    """
    Join duplicated geographical points in the dataset. Returns a new dataset, where
    the RBD column has lists of RBDs for repeated locations.
    """
    n = len(data)

    x_label = coords_labels[0]
    y_label = coords_labels[1]

    rbds = []
    x = []
    y = []

    for i in tqdm(range(n), desc='Checking and joining duplicate schools'):
        where = -1
        for j in range(len(x)):
            if x[j] == data[x_label][i] and y[j] == data[y_label][i]:
                where = j
        if where == -1:
            x.append(data[x_label][i])
            y.append(data[y_label][i])
            rbds.append([int(data[rbd_label][i])])
        else:
            rbds[where].append(int(data[rbd_label][i]))
    
    new_data = pd.DataFrame({x_label: x, y_label: y, rbd_label: rbds})
    return new_data


def add_food_rations_and_costs(data: pd.DataFrame, rations: pd.DataFrame, 
                     rbd_label: str = 'RBD'):
    """
    Add the food rations and costs to the duplicates-free dataset. Modifies 
    the dataset in place, adding the columns 'Manipuladora', 'Beneficio', 
    'Alimentos' and 'Raciones'.
    """

    n = len(data)

    indice = {rations[rbd_label][i]: i for i in range(len(rations))}

    beneficio = [0 for _ in range(n)]
    manipuladoras = [0 for _ in range(n)]
    costo = [0 for _ in range(n)]
    raciones = [0 for _ in range(n)]

    for i in tqdm(range(n), desc='Calculating food rations and costs'):
        for rbd in data[rbd_label][i]:
            ix = indice[rbd]
            raciones[i] += int(rations['A'][ix])
            raciones[i] += int(rations['D'][ix])
            raciones[i] += int(rations['T'][ix])
            raciones[i] += int(rations['O'][ix])
            raciones[i] += int(rations['C'][ix])

        beneficio[i] = p.BENEF_RACION * raciones[i]
        costo[i] = p.COST_RACION * raciones[i]
        raciones[i] = raciones[i] // p.DIAS_ESCOLARES
        manipuladoras[i] = p.SUELDO_MANIP * (((raciones[i] // 2) // p.DIAS_ESCOLARES + 
                                              (p.RATIO_MANIP - 1)) // p.RATIO_MANIP)

    data['Manipuladora'] = manipuladoras
    data['Beneficio'] = beneficio
    data['Alimentos'] = costo
    data['Raciones'] = raciones


def add_profit(data: pd.DataFrame, profit_label: str = 'Profit', logist_label: str = 'Logistica'):
    """
    Add the profit column to the dataset. Modifies the dataset in place, adding the column
    'Profit'.
    """

    try:
        data[logist_label]
    except KeyError:
        print(f'The dataset does not have a column named {logist_label}')
        return

    n = len(data)

    profit = [0 for _ in range(n)]

    for i in range(n):
        profit[i] = data['Beneficio'][i] - data['Logistica'][i] - data['Manipuladora'][i] - data['Alimentos'][i]

    data[profit_label] = profit


def ut_assignation(data: pd.DataFrame, schools: pd.DataFrame):
    """
    Assigns UTs to each school in the schools dataset, using the 
    UTs dataset. Returns a new schools dataset, where the UT column 
    has the UT for each school.
    """

    try:
        data['UT']
    except KeyError:
        print('The dataset does not have a column named UT')
        return

    rbds = data['RBD']
    uts = data['UT']

    new_rbds = []
    new_uts = []

    for UT, rbd in zip(uts, rbds):
        for r in rbd:
            new_rbds.append(r)
            new_uts.append(UT)

    new_data = pd.DataFrame({'RBD': new_rbds, 'UT': new_uts})

    return schools.merge(new_data, on='RBD')


def save_data(data: pd.DataFrame, path: str):
    """
    Save the dataset to an excel file.
    """
    data.to_excel(path, index=False)
