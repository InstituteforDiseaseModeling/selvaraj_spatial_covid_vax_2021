import pandas as pd
import numpy as np
import os

policy_file = os.path.join('data_input', 'combined_data.csv')


def custom_round(x, base=5):
    return int(base * round(float(x) / base))


def social_distancing_effect(countries: list = None, sd_bins=10):
    """
    :param countries: list of countries to consider for averaging social distancing effects
    :param sd_bins: minimum percentage difference in social distancing effect
    :return: dataframe of social distancing efficacy ('Index_value') and date of change to new efficacy
    """

    df = pd.read_csv(policy_file, encoding="ISO-8859-1")
    df = df[df['Country'].isin(countries)]
    df = df.groupby('Date_from_first_case')['Index_value'].apply(np.nanmean).reset_index()
    df.dropna(inplace=True)

    # round index_value to nearest 10
    df['Index_value'] = df['Index_value'].apply(lambda x: custom_round(x, base=sd_bins))

    df['Diff'] = df['Index_value'].diff()
    df = df[df['Diff'] != 0]
    df['Index_value'] = 1 - (df['Index_value'] / 100 * 1.0)

    # # Add extra line to open all settings
    df_add = pd.DataFrame.from_dict({'Date_from_first_case': [250], 'Index_value': [1], 'Diff': [100]})
    df = pd.concat([df, df_add])

    return df