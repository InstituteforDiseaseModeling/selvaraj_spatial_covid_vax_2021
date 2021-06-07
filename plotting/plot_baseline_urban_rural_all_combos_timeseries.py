import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import rcParams
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator

mpl.rcParams['pdf.fonttype'] = 42
rcParams.update({'font.size': 18})

type = 'covax_baseline_all_combos_20countries'
exp = 'covax_baseline_all_combos_20countries'
smoothing_window = 7

change_cases_file = '/Users/pselvaraj/Github/covid-dtk-scenarios/vaccine_efficacy_article/data/%s/%s_spatial_data_full.csv' % (type, type)
change_cases_file_processed = '/Users/pselvaraj/Github/covid-dtk-scenarios/vaccine_efficacy_article/data/%s/%s_spatial_data_final.csv' % (type, type)

os.makedirs(os.path.join(os.path.expanduser('~'), 'Github', 'covid-dtk-scenarios', 'vaccine_efficacy_article', 'figures',
                         type), exist_ok=True)

pops = {'Urban': 1.2e4, 'Rural': 2.8e4, 'Total': 4e4}

if not os.path.exists(change_cases_file_processed):
    df = pd.read_csv(change_cases_file)
    df = df[df['scenario'] == 'baseline']
    df = df[['Run_Number', 'R0', 'migration', 'Time', 'Urban', 'Rural', 'Total']]
    df_cumulative = pd.DataFrame()
    for gtemp, dfgtemp in df.groupby(['Run_Number', 'R0', 'migration']):
        dftemp = dfgtemp.copy()
        for channel in ['Urban', 'Rural', 'Total']:
            dftemp[channel + '_cumulative'] = np.array(dftemp[channel].cumsum())/sum(dftemp['Total'])*100
            dftemp[channel + '_cumulative_pop'] = np.array(dftemp[channel].cumsum()) / pops[channel]
        df_cumulative = pd.concat([df_cumulative, dftemp])
    df = df_cumulative.copy()

    if 'Unnamed: 0' in df.columns:
        del df['Unnamed: 0']

    # for n, (cd, df_cd) in enumerate(df_final.groupby('migration')):
    df_temp = pd.DataFrame()
    channels_of_interest = [c+a for c in ['Urban', 'Rural', 'Total'] for a in ['', '_cumulative', '_cumulative_pop']]
    smoothed_channels_of_interest = [c+a for c in ['Urban', 'Rural', 'Total'] for a in ['_smoothed', '_cumulative_smoothed', '_cumulative_pop_smoothed']]
    for i, (g, df_g) in enumerate(df.groupby(['R0', 'migration', 'Run_Number'])):
        df_smoothed = df_g.groupby(['R0', 'migration', 'Run_Number'])[channels_of_interest].rolling(smoothing_window, min_periods=1).mean().reset_index()
        df_smoothed['level_3'] = [i for i in range(len(df_smoothed))]
        df_smoothed.rename(columns={'level_3': 'Time'}, inplace=True)
        df_temp = pd.concat([df_temp, df_smoothed])
    df_temp2 = df.merge(df_temp, left_on=['Run_Number', 'R0', 'migration', 'Time'], right_on=['Run_Number', 'R0', 'migration', 'Time'], suffixes=['', '_smoothed'])
    df_final = df_temp2.groupby(['R0', 'migration', 'Time'])[channels_of_interest+smoothed_channels_of_interest].apply(np.mean).reset_index()
    df_std = df_temp2.groupby(['R0', 'migration', 'Time'])[channels_of_interest+smoothed_channels_of_interest].apply(np.std).reset_index()
    for channel in channels_of_interest+smoothed_channels_of_interest:
        df_final[channel + '_std'] = df_std[channel]
    df_final.to_csv(change_cases_file_processed)

else:
    df_final = pd.read_csv(change_cases_file_processed)
    if 'Unnamed: 0' in df_final.columns:
        del df_final['Unnamed: 0']

################################################ Plotting ################################################
migration_rates = list(df_final['migration'].unique())
r0 = list(df_final['R0'].unique())
scenarios = 'baseline'
width = 0.25

colors = ['xkcd:blue', 'xkcd:orange', 'xkcd:purple', 'xkcd:dark sea green',
          'xkcd:purple', 'xkcd:dark sea green', 'xkcd:red']

linestyles = [None, None] #'--']
mig = [0.0001, 0.0025, 0.025]
r0 = [2.0, 2.4, 2.8]
r0_labels = {2.0: 'Low', 2.4: 'Medium', 2.8: 'High'}
mig_labels = {0.0001: 'Low', 0.0025: 'Medium', 0.025: 'High'}
# df_final = df_final[df_final['R0'].isin(r0_reduced)]

for channel in ['Total_smoothed']:
    fig, axs = plt.subplots(nrows=len(r0), ncols=len(mig), figsize=(18, 15),
                            sharex=False, sharey=True, squeeze=True)
    for m, (st, df_st) in enumerate(df_final.groupby('R0')):
        for n, (u, df_u) in enumerate(df_st.groupby('migration')):

            axs[m, n].plot(df_u['Time'], df_u[channel], color='k', lw=2)
            axs[m, n].fill_between(df_u['Time'], df_u[channel] - df_u[channel + '_std'] * 1.96 / np.sqrt(43),
                                   df_u[channel] + df_u[channel + '_std'] * 1.96 / np.sqrt(43), color='k',
                                   alpha=0.3)

            df_cumsum = df_u['Total'].cumsum()
            spt_max = df_u['Total_smoothed'].values.argmax()
            sero_prevalence = sum(df_u['Total_smoothed'].iloc[0:spt_max]) / 4e4
            spt_max_1_2 = (abs(df_u['Total_smoothed'].iloc[0:spt_max] - df_u['Total_smoothed'].iloc[spt_max] / 2)).values.argmin()
            spt_max_3_2 = (abs(
                df_u['Total_smoothed'].iloc[spt_max:] - df_u['Total_smoothed'].iloc[spt_max] / 2)).values.argmin() + spt_max
            sero_prevalence_1_2 = sum(df_u['Total_smoothed'].iloc[0:spt_max_1_2]) / 4e4
            sero_prevalence_3_2 = sum(df_u['Total_smoothed'].iloc[0:spt_max_3_2]) / 4e4

            sero_prevalence_end = sum(df_u['Total_smoothed']) / 4e4
            axs[m, n].text(0.6, 0.47, "Peak = day %i" % spt_max, size=12, ha="center",
                           transform=axs[m, n].transAxes)
            axs[m, n].axvline(spt_max_1_2, color='r', linestyle='--')
            axs[m, n].axvline(spt_max_3_2, color='r', linestyle='--')
            axs[m, n].axvline(spt_max, color='g', linestyle='--')

            axs[0, n].set_title('%s migration' % mig_labels[mig[n]])
            axs[m, 0].set_ylabel('R0 = %s' % r0[m])

            if not 'cumulative' in channel:
                axs[m, n].set_ylim([0, 3.5e4])
                axs[0, n].set_yticks([0, 1e4, 2e4])
                axs[m, n].yaxis.set_minor_locator(MultipleLocator(2e3))
                axs[m, n].text(0.5, 0.6, "At peak = %0.1f%%" % sero_prevalence, size=12, ha="center",
                            transform=axs[m, n].transAxes)
                axs[m, n].text(0.75, 0.2, "At 2 years = %0.1f%%" % sero_prevalence_end, size=12, ha="center",
                            transform=axs[m, n].transAxes)
                axs[m, n].text(0.15, 0.1, "%0.1f%%" % sero_prevalence_1_2, size=12, ha="center",
                            transform=axs[m, n].transAxes)
                axs[m, n].text(0.35, 0.1, "%0.1f%%" % sero_prevalence_3_2, size=12, ha="center",
                            transform=axs[m, n].transAxes)
                fig.text(0.5, 0.95, 'New infections', ha='center', fontsize=18)
            else:
                axs[m, n].set_ylim([0, 100])
                axs[0, n].set_yticks([0, 20, 40, 60, 80, 100])
                axs[m, n].yaxis.set_minor_locator(MultipleLocator(20))
                fig.text(0.5, 0.95, 'New infections cumulative', ha='center', fontsize=18)
            axs[m, n].grid(b=True, which='minor', color='gray', linestyle='--', alpha=0.5)
            axs[m, n].grid(b=True, which='major', color='gray', linestyle='--', alpha=0.5)
            axs[m, n].set_xticks([0, spt_max_1_2, spt_max_3_2, 365, 730])
            axs[m, n].tick_params(axis='both', labelsize=10)
    fig.text(0.47, 0.15, 'Time', ha='center', fontsize=18)
    add = 'smooth'
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.95)
    fig_dir = os.path.join(os.path.expanduser('~'), 'Github', 'covid-dtk-scenarios', 'vaccine_efficacy_article', 'figures',
                            type, 'timeseries')
    os.makedirs(fig_dir, exist_ok=True)
    fig_name = os.path.join(fig_dir, '%s_timeseries_%s_base_%s_spatial.png' % (type, add, channel))
    plt.savefig(fig_name)
    # plt.show()
    plt.close('all')


# Plot urban and rural separately
pops = {'Urban': 1.6e4, 'Rural': 2.4e4}
sero_locs = {'Urban': 0.4, 'Rural': 0.6}
for j, channel_group in enumerate([['Urban_smoothed', 'Rural_smoothed'],
                                   ['Urban_cumulative_smoothed', 'Rural_cumulative_smoothed'],
                                   ['Urban_cumulative_pop_smoothed', 'Rural_cumulative_pop_smoothed']]):
    fig, axs = plt.subplots(nrows=len(r0), ncols=len(mig), figsize=(18, 15),
                                sharex=False, sharey=True, squeeze=True)
    for m, (st, df_st) in enumerate(df_final.groupby('R0')):
        for n, (u, df_u) in enumerate(df_st.groupby('migration')):
            for i, channel in enumerate(channel_group):
                if i == 0 and ('cumulative' not in channel):
                    axs[m, n].plot(df_u['Time'], df_u['Total_smoothed'], color='k', lw=2, alpha=0.2)
                elif i==0 and ('pop' not in channel):
                    axs[m, n].plot(df_u['Time'], df_u['Total_cumulative_smoothed'], color='k', lw=2, alpha=0.2)
                elif i==0 and ('pop' in channel):
                    axs[m, n].plot(df_u['Time'], df_u['Total_cumulative_pop_smoothed'], color='k', lw=2, alpha=0.2)

                axs[m, n].plot(df_u['Time'], df_u[channel], color=colors[i], lw=2)
                axs[m, n].fill_between(df_u['Time'], df_u[channel] - df_u[channel + '_std'] * 1.96 / np.sqrt(43),
                                       df_u[channel] + df_u[channel + '_std'] * 1.96 / np.sqrt(43), color=colors[i],
                                       alpha=0.3)

                channel_name = channel.split('_')[0]
                channel_sp = channel.split('_')[0] + '_' + channel.split('_')[-1]

                df_cumsum = df_u['Total'].cumsum()
                spt_max = df_u[channel_sp].values.argmax()
                sero_prevalence = sum(df_u[channel_sp].iloc[0:spt_max]) / pops[channel_name]

                if (df_u[channel_sp].iloc[spt_max]+2500)/25e3 > 1:
                    day_label_loc = (df_u[channel_sp].iloc[spt_max]-1000)/25e3
                else:
                    day_label_loc = (df_u[channel_sp].iloc[spt_max] + 5000) / 25e3
                axs[m, n].text(spt_max/730, day_label_loc, "Day %i" % spt_max, size=12, ha="center",
                               transform=axs[m, n].transAxes)
                axs[m, n].axvline(spt_max, color=colors[i], linestyle='--')

                axs[0, n].set_title('%s migration' % mig_labels[mig[n]])
                axs[m, 0].set_ylabel('R0 = %s' % r0[m])

                if not 'cumulative' in channel:
                    axs[m, n].set_ylim([0, 3.5e4])
                    axs[0, n].set_yticks([0, 1e4, 2e4])
                    axs[m, n].yaxis.set_minor_locator(MultipleLocator(2e3))
                    axs[m, n].text(spt_max / 730, (df_u[channel].iloc[spt_max] + 1000) / 25e3,
                                "%s peak = %0.1f%%" % (channel_name, sero_prevalence), size=12, ha="center",
                                transform=axs[m, n].transAxes)
                    # fig.text(0.47, 0.95, 'Urban & Rural new infections', ha='center', fontsize=18)
                else:
                    axs[m, n].set_ylim([0, 100])
                    axs[0, n].set_yticks([0, 20, 40, 60, 80, 100])
                    axs[m, n].yaxis.set_minor_locator(MultipleLocator(20))
                    # if 'pop' not in channel:
                    #     # fig.text(0.47, 0.95, 'Urban & Rural cumulative new infections', ha='center', fontsize=18)
                    # else:
                    #     fig.text(0.47, 0.95, 'Urban & Rural cumulative new infections with respect to sub-population',
                    #              ha='center', fontsize=18)
                axs[m, n].grid(b=True, which='minor', color='gray', linestyle='--', alpha=0.5)
                axs[m, n].grid(b=True, which='major', color='gray', linestyle='--', alpha=0.5)
                axs[m, n].set_xticks([0, 365, 730])
                axs[m, n].tick_params(axis='both', labelsize=10)
    fig.text(0.47, 0.15, 'Time', ha='center', fontsize=18)
    # fig.suptitle('Urban & Rural new infections')

    custom_lines_2 = [Line2D([0], [0], color='k', lw=2, alpha=0.2)] \
                     + [Line2D([0], [0], color=colors[i], lw=2) for i in range(2)]
    fig.legend(custom_lines_2, ['Total', 'Urban', 'Rural'], bbox_to_anchor=(0.6, 0.05), ncol=4)

    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.95)
    add = 'smooth'
    if j == 0:
        sum_type = ''
    elif j == 1:
        sum_type = 'cumulative'
    else:
        sum_type = 'cumulative_pop'
    fig_name = os.path.join(os.path.expanduser('~'), 'Github', 'covid-dtk-scenarios', 'vaccine_efficacy_article', 'figures',
                            type,
                            '%s_timeseries_%s_base_split_%s_spatial.png' % (type, add, sum_type))
    plt.savefig(fig_name)
    plt.close('all')
