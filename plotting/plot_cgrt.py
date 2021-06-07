import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Patch
import matplotlib as mpl
import pandas as pd
import numpy as np
import os

mpl.rcParams['pdf.fonttype'] = 42
rcParams.update({'font.size': 16})


countries = ['Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon', 'Central African Republic',
                 'Chad', 'Ivory Coast', 'DRC', 'Eritrea', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea',
                 'Guinea-Bissau', 'Kenya', 'Lesotho', 'Liberia', 'Madagascar', 'Malawi', 'Mali', 'Mauritania',
                 'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda', 'Senegal', 'Sierra Leone',
                 'South Africa', 'Tanzania', 'Togo', 'Uganda', 'Zambia', 'Zimbabwe']

policy_file = os.path.join('./data_input', 'combined_data.csv')


def social_distancing_effect(countries: list = None):
    """
    :param countries: list of countries to consider for averaging social distancing effects
    :return: dataframe of social distancing efficacy ('Index_value') and date of change to new efficacy
    """

    df = pd.read_csv(policy_file, encoding="ISO-8859-1")
    df = df[df['Country'].isin(countries)]
    dfmean = df.groupby('Date_from_first_case')['Index_value'].apply(np.nanmean).reset_index()
    dfmean.dropna(inplace=True)
    dfmean['Country'] = ['All']*len(dfmean)
    df = df[['Date_from_first_case', 'Index_value', 'Country']]
    df = pd.concat([df, dfmean])

    return df


if __name__ == '__main__':
    plt.rcdefaults()
    fig, ax = plt.subplots()

    # Example data
    df = social_distancing_effect(countries)
    for c, df_c in df.groupby(['Country']):
        if c == 'All':
            color = 'r'
            alpha = 1.0
        else:
            color = 'k'
            alpha = 0.2
        ax.plot(df_c['Date_from_first_case'], df_c['Index_value'], color=color, alpha=alpha, linewidth=2)
    ax.set_yticks([0, 25, 50, 75])
    ax.set_yticklabels(['0', '25%', '50%', '75%'])
    ax.set_xticks([0, 100, 200, 300, 400])
    ax.set_ylabel('Oxford CGRT containment and health index')
    ax.set_xlabel('Days since first case')

    custom_lines_2 = [Patch(color='r', alpha=1), Patch(color='k', alpha=0.2)]
    fig.legend(custom_lines_2, ['Mean', 'Individual country'],
               bbox_to_anchor=(0.5, 0.27), ncol=1, fontsize=12)
    plt.title('Government response to COVID-19 in SSA countries')
    plt.savefig('./figures/oxford_cgrt_fig.png')
