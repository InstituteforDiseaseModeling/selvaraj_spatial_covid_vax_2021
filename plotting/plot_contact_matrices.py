import openpyxl as oxl
import numpy as np
import matplotlib as mpl
import os

import matplotlib.pyplot as plt
from vaccine_efficacy_article.build_input_files.refdat_contact_mat import find_median_contact_matrix

mpl.rcParams['pdf.fonttype'] = 42

fig_dir = os.path.join(os.path.expanduser('~'), 'Github', 'covid-dtk-scenarios', 'vaccine_efficacy_article',
                         'figures')
os.makedirs(fig_dir, exist_ok=True)


def plot_all_settings(mat_home, mat_work, mat_schl, mat_comm, country):

    max = np.max([np.max(mat_home), np.max(mat_comm), np.max(mat_schl), np.max(mat_work)])
    norm = 5

    fig, axs = plt.subplots(2, 2, figsize=(6, 6))

    axs[0, 0].imshow(mat_home.T, cmap='Blues', origin='lower', vmin=0, vmax=max / norm)
    axs[0, 0].set_title('Home')

    axs[0, 1].imshow(mat_work.T, cmap='Blues', origin='lower', vmin=0, vmax=max / norm)
    axs[0, 1].set_title('Work')

    axs[1, 0].imshow(mat_schl.T, cmap='Blues', origin='lower', vmin=0, vmax=max / norm)
    axs[1, 0].set_title('School')

    axs[1, 1].imshow(mat_comm.T, cmap='Blues', origin='lower', vmin=0, vmax=max / norm)
    axs[1, 1].set_title('Community')

    for i in range(2):
        for j in range(2):
            axs[i, j].set_yticks(ticks=[-0.5 + i for i in range(0, 20, 2)])
            axs[i, j].set_yticklabels([10 * i for i in range(0, 10)])
            axs[i, j].set_xticks(ticks=[-0.5 + i for i in range(0, 20, 2)])
            axs[i, j].set_xticklabels([10 * i for i in range(0, 10)])
            axs[i, j].set_xlim([-0.5, 15.5])
            axs[i, j].set_ylim([-0.5, 15.5])
    fig.text(0.5, 0.005, 'Age group of individual', ha='center')
    fig.text(0.005, 0.5, 'Age group of contacts', va='center', rotation='vertical')
    plt.subplots_adjust(top=0.8, bottom=0.2, left=0.2, right=0.8)
    plt.suptitle(country, fontsize=16)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, '%s_contacts_layer.pdf' % country))
    plt.show()


def plot_total_matrix(mat_total, country):

    max = np.max([np.max(mat_total)])
    norm = 5

    plt.figure(figsize=(4, 4))
    plt.imshow(mat_total.T, cmap='Blues', origin='lower', vmin=0, vmax=max / norm)
    plt.xticks(ticks=[-0.5 + i for i in range(0, 20, 2)], labels=[10 * i for i in range(0, 10)])
    plt.yticks(ticks=[-0.5 + i for i in range(0, 20, 2)], labels=[10 * i for i in range(0, 10)])
    plt.xlim([-0.5, 15.5])
    plt.ylim([-0.5, 15.5])
    plt.xlabel('Age group of individual')
    plt.ylabel('Age group of contacts')
    plt.title(country, fontsize=14)
    plt.savefig(os.path.join(fig_dir, '%s_contacts_layer_total.pdf' % country))
    plt.show()


if __name__ == '__main__':

    countries = ['Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon', 'Central African Republic',
                 'Chad', 'Ivory Coast', 'DRC', 'Eritrea', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea',
                 'Guinea-Bissau', 'Kenya', 'Lesotho', 'Liberia', 'Madagascar', 'Malawi', 'Mali', 'Mauritania',
                 'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda', 'Senegal', 'Sierra Leone',
                 'South Africa', 'Tanzania', 'Togo', 'Uganda', 'Zambia', 'Zimbabwe']

    mat_home_r, mat_work_r, mat_school_r, mat_community_r = \
        find_median_contact_matrix(arg_key='AFRO:REP', countries=countries, area='Rural')
    mat_total_r = mat_home_r + mat_work_r + mat_school_r + mat_community_r

    mat_home_u, mat_work_u, mat_school_u, mat_community_u = \
        find_median_contact_matrix(arg_key='AFRO:REP', countries=countries, area='Urban')
    mat_total_u = mat_home_u + mat_work_u + mat_school_u + mat_community_u

    plot_all_settings(mat_home=mat_home_r, mat_comm=mat_community_r, mat_schl=mat_school_r, mat_work=mat_work_r,
                      country='Rural')
    plot_all_settings(mat_home=mat_home_u, mat_comm=mat_community_u, mat_schl=mat_school_u, mat_work=mat_work_u,
                      country='Urban')
    plot_total_matrix(mat_total_r, country='Rural')
    plot_total_matrix(mat_total_u, country='Urban')