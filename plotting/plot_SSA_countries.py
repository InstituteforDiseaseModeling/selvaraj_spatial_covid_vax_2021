import numpy as np
import pandas as pd
import copy
import matplotlib.rcsetup
import seaborn as sns
import sys
import os
import matplotlib.pyplot as plt

import scipy.stats
from datetime import date

import geopandas as gpd

filename = './World_Countries__Generalized_.shp'

if __name__ == '__main__':

    # load data and join with map shapefiles
    data = gpd.read_file(filename)
    countries = ['Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon', 'Central African Republic',
                 'Chad', 'Côte d\'Ivoire', 'Congo DRC', 'Eritrea', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea',
                 'Guinea-Bissau', 'Kenya', 'Lesotho', 'Liberia', 'Madagascar', 'Malawi', 'Mali', 'Mauritania',
                 'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda', 'Senegal', 'Sierra Leone',
                 'South Africa', 'Tanzania', 'Togo', 'Uganda', 'Zambia', 'Zimbabwe']
    countries_all = ['Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon',
                     'Central African Republic', 'Chad', 'Côte d\'Ivoire', 'Congo', 'Congo DRC', 'Djibouti', 'Egypt',
                     'Eritrea', 'Ethiopia', 'Equatorial Guinea',
                     'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 'Kenya', 'Lesotho', 'Liberia', 'Libya',
                     'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Morocco', 'Mozambique', 'Namibia', 'Niger',
                     'Nigeria', 'Rwanda', 'Senegal', 'Sierra Leone', 'South Africa', 'Sudan', 'Tanzania', 'Togo',
                     'Tunisia', 'Uganda', 'Western Sahara', 'Zambia', 'Zimbabwe']
    data_all = data[data['COUNTRY'].isin(countries_all)]
    data_selected = data[data['COUNTRY'].isin(countries)]

    fig = plt.gcf()
    ax = fig.add_subplot(111)
    data_all.plot(column='Best', linewidth=0.5, ax=ax, color='xkcd:white', edgecolor='k',
                       legend=True)
    data_selected.plot(column='Best', linewidth=0.1, ax=ax, color='xkcd:blue', edgecolor='0.8',
                     legend=True)
    plt.savefig('./figures/SSA.png')
    plt.show()