"""
Prashanth Selvaraj
Apr 2021
"""
import pandas as pd
import numpy as np
import os

ap_direc = os.path.join('data_input', 'age_pyramids')


def find_age_pyramid(arg_key=str(), countries: list = None, area='Rural'):
    ap_total = np.zeros((16, ))
    df = pd.read_csv(os.path.join(ap_direc, 'URPAS_2014_ALL_processed.csv'))
    df = df[df['AreaType']==area]
    age_cols = ["%02d-%02d" % (a, a + 4) for a in range(0, 76, 5)]
    for i, country in enumerate(countries):

        # print('%s-%s' % (country, area))
        df_country = df[df['LocationName']==country]
        age_pyr_country = np.array(df_country[age_cols]) * df_country['Total'].values
        ap_total += age_pyr_country[0, :]

    age_pyr_x = list(range(0, 80, 5))
    age_pyr_y = dict()
    age_pyr_y['AFRO:REP'] = (ap_total / sum(ap_total)).tolist()

    narg_key1 = arg_key
    while len(narg_key1) > 0 and narg_key1 not in age_pyr_y:
        narg_key1 = narg_key1.rsplit(':', 1)[0]

    # return ap_total/sum(ap_total)
    return age_pyr_x, age_pyr_y[narg_key1]