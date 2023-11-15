import modules.pretty_plot as pp
import pandas as pd


##################### Load data #########################

schools = pd.read_excel('(TEST) Colegios(Continental)2020(UTs).xlsx')

pp.single_plot_uts(7, schools, legend=True, markersize=10, marker='x', cmap='tab20')