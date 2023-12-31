import pandas as pd
import modules.parameters as p
from tqdm import tqdm
import modules.graph as graph
import modules.geo as geo


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
    check = {}

    for i in tqdm(range(n), desc='Checking and joining duplicate schools'):
        where = -1
        
        point = (data[x_label][i], data[y_label][i])
        if point in check:
            where = check[point]

        if where == -1:
            x.append(data[x_label][i])
            y.append(data[y_label][i])
            rbds.append([int(data[rbd_label][i])])
            check[point] = len(x) - 1
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


def get_ut_profits(data, ut_label: str = 'UT'):
    """
    Returns a list of the profits for each UT.
    """

    n = len(data)
    k = max(data[ut_label][i] for i in range(n)) + 1

    UT = [data[ut_label][i] for i in range(n)]

    profit = [0 for _ in range(k)]
    raciones = [0 for _ in range(k)]

    for i in range(n):
        profit[UT[i]] += data['Profit'][i]
        raciones[UT[i]] += data['Raciones'][i]


    new_data = {ut_label: [i for i in range(k)], 'Profit': profit, 'Raciones': raciones}

    return pd.DataFrame(new_data)


def obtain_stats(df_schools: pd.DataFrame, df_ut_profits: pd.DataFrame,
                 coords_labels: tuple[str] = ('X', 'Y'), ut_label: str = 'UT'):
    """
    Calculates the average, maximum and minimum rate of profit between UTs.
    """
    
    x_label = coords_labels[0]
    y_label = coords_labels[1]

    uts = df_ut_profits[ut_label].unique()
    UT = [df_schools[ut_label][i] for i in range(len(df_schools))]

    ut_edges = [[] for _ in range(len(uts))]

    points = [(df_schools[x_label][i], df_schools[y_label][i]) 
              for i in range(len(df_schools))]

    schools_edges = graph.get_adj_list(points)

    for i in range(len(df_schools)):
        for j in schools_edges[i]:

            dist = geo.convert_to_meters(graph.distance(points[i], points[j]))

            if UT[j] not in ut_edges[UT[i]] and UT[i] != UT[j] and dist < 150000:
                ut_edges[UT[i]].append(UT[j])

    sumdiff = 0
    maxdiff = 0
    mindiff = 100000
    contar = 0

    profit = [df_ut_profits['Profit'][i] for i in range(len(df_ut_profits))]

    for i in range(len(ut_edges)):
        for j in ut_edges[i]:
            sumdiff += max(profit[i], profit[j]) / min(profit[i], profit[j])
            contar += 1
            maxdiff = max(maxdiff, max(profit[i], profit[j]) / min(profit[i], profit[j]))
            mindiff = min(mindiff, max(profit[i], profit[j]) / min(profit[i], profit[j]))

    print(f'En promedio, el beneficio económico entre UTs vecinas presenta una razón de {round(sumdiff / contar, 3)}')
    print(f'La razón más alta que se presenta entre UTs vecinas es {round(maxdiff, 3)}')
    print(f'La menor razón que se presenta entre UTs vecinas es {round(mindiff, 3)}')

    return sumdiff / contar, maxdiff, mindiff


def save_data(data: pd.DataFrame, path: str):
    """
    Save the dataset to an excel file.
    """
    data.to_excel(path, index=False)
