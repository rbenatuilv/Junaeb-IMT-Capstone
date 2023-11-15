import matplotlib.pyplot as plt
import modules.parameters as p
import geopandas as gpd


def plot_region(reg_number: int, 
                ax: plt.Axes = None, 
                title: str = None):
    """
    Plot a Chilean region given its number.
    """
    regs = p.REGS_CONT
    reg = regs[regs['codregion'] == reg_number]
    
    plot = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))
        plot = True
    reg.boundary.plot(ax=ax, color='k', linewidth=1)

    if title is None:
        title = reg['Region'].values[0]

    ax.set_title(title)

    if plot:
        plt.show()
        print(f'Plotted: Region {reg["Region"].values[0]}')
    else:
        return ax


def plot_regions(reg_numbers: list[int] = None, 
                 ax: plt.Axes = None, 
                 title: str = None, **args):
    """
    Plot Chilean regions given a list of numbers. If list is None, plot all regions.
    """
    regs = p.REGS_CONT

    plot = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))
        plot = True

    if reg_numbers is None:
        reg_numbers = list(range(1, 17))
    regs[regs['codregion'].isin(reg_numbers)].boundary.plot(ax=ax, color='k' ,**args)

    if title is None:
        title = 'Regiones'

    ax.set_title(title)

    if plot:
        plt.show()
        print('Plotted')
    else:
        return ax


def single_plot_uts(reg_number, schools, crs: str = 'EPSG:4326', 
                    ax: plt.Axes = None, title: str = None, 
                    save: bool = False, folder: str = None, **args):
    """
    Plot the UTs of a single region.
    """
    schools = schools[schools['Region'] == reg_number]

    geo = gpd.points_from_xy(schools['Longitud'], schools['Latitud'])
    geo_data = gpd.GeoDataFrame(schools, geometry=geo, crs=crs)

    plot = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))
        plot = True

    geo_data.plot(ax=ax, column='UT', **args)
    plot_region(reg_number, ax=ax, title=title)

    ax.set_axis_off()    

    if plot:
        if save:
            path = f'{folder}/UTs_R{reg_number}.png'
            plt.savefig(path, dpi=300)
        else:
            plt.show()
        print(f'Plotted: UTs of Region {reg_number}')
    else:
        return ax


def total_plot_uts(schools, subplots: tuple[int], 
                   crs: str = 'EPSG:4326', 
                   save: bool = False, folder: str = None, **args):
    """
    Plot the UTs of all regions.
    """
    reg_numbers = schools['Region'].unique()

    fig, axes = plt.subplots(*subplots, figsize=(20, 20))
    axes = axes.flatten()

    for i, reg_number in enumerate(reg_numbers):
        single_plot_uts(reg_number, schools, crs=crs, ax=axes[i], **args)

    # Save the plot
    if save:
        path = f'{folder}/UTs.png'
        plt.savefig(path, dpi=300)
    else:
        plt.show()
    print('Plotted: UTs of all regions')
