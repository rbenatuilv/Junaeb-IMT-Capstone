import signal



def check_import_requirements():
    """
    Check if all the required modules are installed.
    """
    try:
        import pandas as pd
        import geopandas as gpd
        import numpy as np
        import matplotlib.pyplot as plt
        import tqdm

    except ImportError:
        print('Some modules are missing. Please run the following command:')
        print('pip install -r requirements.txt')
        exit(1)


def check_data_requirements(parent_folder: str = 'Data', schools_file: str = 'Colegios(Continental)2020.xlsx',
                            rations_folder: str = 'Raciones', rations_file: str = 'Raciones_totales.xlsx',):
    """
    Check if all the required data is present.
    """
    import os

    required_files = [
        os.path.join(os.getcwd(), parent_folder, schools_file),
        os.path.join(os.getcwd(), parent_folder, rations_folder, rations_file)
    ]

    for file in required_files:
        if not os.path.isfile(file):
            print(f'File {file} not found. Please check the data folder.')
            exit(1)
