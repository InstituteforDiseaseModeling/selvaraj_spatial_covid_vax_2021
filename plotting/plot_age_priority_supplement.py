import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import rcParams
from matplotlib.patches import Patch

mpl.rcParams['pdf.fonttype'] = 42
rcParams.update({'font.size': 16})

# type = 'pulsed_phased'
type = 'covax_age_priority_all'

fig_dir = os.path.join('./figures', type)
os.makedirs(fig_dir, exist_ok=True)

settings = ['Urban_', 'Rural_', '']
channels = ['Infections', 'Severe', 'Mortality']
data_channels = [s + c for s in settings for c in channels]

filename = os.path.join('./data', '%s' % type, '%s_event_recorder_summarized.csv' % type)
if not os.path.exists(filename):
    df = pd.read_csv(os.path.join('./data', '%s' % type, '%s_event_recorder_full.csv' % type))

    df = df.groupby(['Run_Number', 'start_day', "vaccine_coverage_1st_dose", 'scenario', 'target_group',
                     'migration', 'R0'])[data_channels].apply(np.sum).reset_index()

    channels_all = ["vaccine_coverage_1st_dose", "scenario", "start_day", 'target_group', 'migration', 'R0'] + \
               data_channels
    df = df[['Run_Number'] + channels_all]

    df_baseline = df[df['scenario'] == 'baseline']
    df = df[df['scenario'].isin(['acquisition_blocking', 'disease_blocking'])]

    # Compare with baseline
    df_new = pd.DataFrame()
    for i, (g, df_g) in enumerate(df.groupby(['Run_Number', 'start_day', "vaccine_coverage_1st_dose", 'scenario',
                                              'target_group', 'migration', 'R0'])):
        dftemp = df_g.copy()
        for c in data_channels:
            baseline = df_baseline[(df_baseline['Run_Number'] == g[0]) & (df_baseline['migration'] == g[-2])
                                   & (df_baseline['R0'] == g[-1])][c].values[0]
            dftemp[c+'_change'] = 1 - df_g['%s' % c] / baseline
        dftemp = dftemp[["vaccine_coverage_1st_dose", "scenario", "start_day", 'target_group',
                             'migration', 'R0'] + [s + c + '_change' for s in settings for c in channels]]
        df_new = pd.concat([df_new, dftemp])

    # Cleaning up and saving file
    for j, (channel) in enumerate(data_channels):
        df_new = df_new[(df_new[channel+'_change'] <= 1) & (df_new[channel+'_change'] >= -1)]
    df_final = df_new.groupby(["vaccine_coverage_1st_dose", 'target_group',
                               "start_day", "scenario", 'migration',
                               'R0'])[[s + c + '_change' for s in settings for c in channels]].apply(np.mean).reset_index()
    df_std = df_new.groupby(["vaccine_coverage_1st_dose", 'target_group',
                             "start_day", "scenario", 'migration',
                             'R0'])[[s + c + '_change' for s in settings for c in channels]].apply(np.std).reset_index()
    for channel in [s + c + '_change' for s in settings for c in channels]:
        df_final[channel+'_std'] = df_std[channel]

    df_final.to_csv(filename)

else:
    df_final = pd.read_csv(filename)
    if 'Unnamed: 0' in df_final.columns:
        del df_final['Unnamed: 0']

if 'Unnamed: 0' in df_final.columns:
    del df_final['Unnamed: 0']

################################################ Plotting ################################################
start_day = list(df_final['start_day'].unique())
target_group = list(df_final['target_group'].unique())
vaccine_coverage_1stdose = list(df_final['vaccine_coverage_1st_dose'].unique())
r0 = list(df_final['R0'].unique())
migration = list(df_final['migration'].unique())
mig_labels = dict(zip(migration, ['Low', 'Medium', 'High']))

coverage_labels = ['%i%%' % (c*100) for c in vaccine_coverage_1stdose]

urban_labels = ['Random', 'Old first', 'Young first']
num_seeds = 20
width = 0.25
bar_locs = [[i-width for i in range(1, len(vaccine_coverage_1stdose)+1)],
            [i for i in range(1, len(vaccine_coverage_1stdose)+1)],
            [i+width for i in range(1, len(vaccine_coverage_1stdose)+1)]]

scenarios = list(df_final['scenario'].unique())
scenario_labels = ['%s\n%s' %(s.split('_')[0], s.split('_')[1]) for s in scenarios]

colors = ['xkcd:purple', 'xkcd:sky blue', 'xkcd:light red']
titles = {2: 'Low', 2.4: 'Medium', 2.8: 'High'}


# Build 3
for y, (major_group_plot, df_major_group) in enumerate(df_final.groupby(['vaccine_coverage_1st_dose',
                                                                         'migration', 'R0'])):
    # Plot only 50% coverage case
    fig, axs = plt.subplots(nrows=len(scenarios), ncols=3, figsize=(14, 7))

    for s, channel in enumerate(['Infections', 'Severe', 'Mortality']):
        if 'Infections' in channel:
            ch_title = 'Infections averted'
        elif 'Severe' in channel:
            ch_title = 'Severe cases averted'
        elif 'Mortality' in channel:
            ch_title = 'Deaths averted'
        for x, (group_plot, df_gp) in enumerate(df_major_group.groupby(['scenario', 'target_group'])):
                sc = group_plot[0] # scenario
                tp = group_plot[1]  # target_group

                k = scenarios.index(sc)
                i = target_group.index(tp)

                axs[k, s].plot(df_gp['start_day'], df_gp[channel+'_change'], color=colors[i])
                axs[k, s].fill_between(df_gp['start_day'], df_gp[channel + '_change'] - df_gp[channel + '_change_std'],
                                       df_gp[channel + '_change'] + df_gp[channel + '_change_std'],
                                       color=colors[i], alpha=0.6)

                axs[k, s].grid(b=True, which='major', color='gray', linestyle='--', alpha=0.3)

                axs[k, s].set_xticks(start_day)
                axs[k, s].set_xlim([30, 180])
                if k == 1:
                    axs[k, s].set_xticklabels(start_day)
                else:
                    axs[k, s].set_xticklabels(['']*len(start_day))

                if k == 0:
                    axs[k, s].set_title(ch_title, fontsize=18)
                if k == 1 and s == 1:
                    axs[k, s].set_xlabel('Start day of vaccine campaign', fontsize=18)

                if 'Infections' in channel:
                    axs[k, s].set_ylim([0, 0.2])
                    axs[k, s].set_yticks([0, 0.075, 0.15, 0.225, 0.3])
                    axs[k, s].set_yticklabels(['0', '', '15%', '', '30%'])
                elif 'Severe' in channel:
                    axs[k, s].set_ylim([0, 0.5])
                    axs[k, s].set_yticks([0, 0.125, 0.25, 0.375, 0.5])
                    axs[k, s].set_yticklabels(['0', '', '25%', '', '50%'])
                elif 'Mortality' in channel:
                    axs[k, s].set_ylim([0, 0.6])
                    axs[k, s].set_yticks([0, 0.15, 0.3, 0.45, 0.6])
                    axs[k, s].set_yticklabels(['0', '', '30%', '', '60%'])

        custom_lines_2 = [Patch(color=colors[n]) for n in range(3)]
        # custom_lines_2 += [Patch(color='w', hatch='*')]
        fig.legend(custom_lines_2, ['%s' % tg.replace('_', ' ').capitalize() for tg in target_group],
                   bbox_to_anchor=(0.7, 0.1), ncol=3)

        fig.text(0.93, 0.7, scenario_labels[0].capitalize(), ha='center', fontsize=16)
        fig.text(0.93, 0.32, scenario_labels[1].capitalize(), ha='center', fontsize=16)
        fig.text(0.02, 0.3, 'Decrease compared to baseline', ha='center', fontsize=18, rotation=90)

    plt.suptitle('Coverage - %i%%, R0 - %0.1f, %s migration' % (major_group_plot[0]*100, major_group_plot[2],
                                                               mig_labels[major_group_plot[1]]))
    plt.subplots_adjust(left=0.08, bottom=0.2, right=0.88)
    fig_name = os.path.join(fig_dir, 'covax_age_priority_cov_%0.1f_mig_%0.4f_r0_%0.1f.png' % (major_group_plot[0],
                                                                                              major_group_plot[1],
                                                                                              major_group_plot[2]))
    plt.savefig(fig_name)
    # plt.show()
    # plt.close('all')
