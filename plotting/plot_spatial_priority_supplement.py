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
type = 'covax_spatial_priority'

fig_dir = os.path.join(os.path.expanduser('~'), 'Github', 'covid-dtk-scenarios',
                         'vaccine_efficacy_article', 'figures', type)
os.makedirs(fig_dir, exist_ok=True)

settings = ['Urban_', 'Rural_', '']
channels = ['Infections', 'Severe', 'Mortality']
data_channels = [s + c for s in settings for c in channels]

filename = os.path.join(os.path.expanduser('~'), 'Github', 'covid-dtk-scenarios',
                         'vaccine_efficacy_article', 'data', '%s' % type, '%s_event_recorder_summarized.csv' % type)
if not os.path.exists(filename):
    df = pd.read_csv(os.path.join(os.path.expanduser('~'), 'Github', 'covid-dtk-scenarios',
                                  'vaccine_efficacy_article', 'data', '%s' % type, '%s_event_recorder_full.csv' % type))
    df = df.groupby(['Run_Number', 'start_day', "vaccine_coverage_1st_dose", 'scenario', 'target_group', 'migration',
                     'R0', 'urban_prioritization'])[data_channels].apply(np.sum).reset_index()

    channels_all = ["vaccine_coverage_1st_dose", "scenario", "start_day", 'target_group', 'migration', 'R0',
                    'urban_prioritization'] + \
               data_channels
    df = df[['Run_Number'] + channels_all]

    df_baseline = df[df['scenario'] == 'baseline']
    df = df[df['scenario'].isin(['acquisition_blocking', 'disease_blocking'])]

    # Compare with baseline
    df_new = pd.DataFrame()
    for i, (g, df_g) in enumerate(df.groupby(['Run_Number', 'start_day', "vaccine_coverage_1st_dose", 'scenario',
                                              'target_group', 'migration', 'R0', 'urban_prioritization'])):
        dftemp = df_g.copy()
        for c in data_channels:
            baseline = df_baseline[(df_baseline['Run_Number'] == g[0]) & (df_baseline['migration'] == g[-3])
                                   & (df_baseline['R0'] == g[-2])][c].values[0]
            dftemp[c+'_change'] = 1 - df_g['%s' % c] / baseline
        dftemp = dftemp[["vaccine_coverage_1st_dose", "scenario", "start_day", 'target_group', 'migration',
                         'urban_prioritization', 'R0'] + [s + c + '_change' for s in settings for c in channels]]
        df_new = pd.concat([df_new, dftemp])

    # Cleaning up and saving file
    for j, (channel) in enumerate(data_channels):
        df_new = df_new[(df_new[channel+'_change'] <= 1) & (df_new[channel+'_change'] >= -1)]
    df_final = df_new.groupby(["vaccine_coverage_1st_dose", 'target_group',
                               "start_day", "scenario", 'migration', 'R0',
                               'urban_prioritization'])[[s + c + '_change' for s in settings for c in channels]].apply(np.mean).reset_index()
    df_std = df_new.groupby(["vaccine_coverage_1st_dose", 'target_group',
                             "start_day", "scenario", 'migration',  'R0',
                             'urban_prioritization'])[[s + c + '_change' for s in settings for c in channels]].apply(np.std).reset_index()
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
df_final = df_final[df_final['migration'].isin([0.0001, 0.0025, 0.025])]
df_final = df_final[df_final['R0'].isin([2.0, 2.4, 2.8])]
df_final = df_final[df_final['urban_prioritization'].isin([1, 2])]

start_day = list(df_final['start_day'].unique())
# target_group = list(df_final['target_group'].unique())
vaccine_coverage_1stdose = list(df_final['vaccine_coverage_1st_dose'].unique())
r0 = list(df_final['R0'].unique())
migration = list(df_final['migration'].unique())
urban_rural = list(df_final['urban_prioritization'].unique())
mig_labels = dict(zip(migration, ['Low', 'Medium', 'High']))

coverage_labels = ['%i%%' % (c*100) for c in vaccine_coverage_1stdose]

urban_labels = ['Random', 'Old first', 'Young first']
num_seeds = 20
width = 0.2
bar_locs = [[1+i*width for i in range(-3, 3)],
            [3+i*width for i in range(-3, 3)],
            [5+i*width for i in range(-3, 3)]]
offset = [-0.1, 0, 0.1]

scenarios = list(df_final['scenario'].unique())
scenario_labels = ['%s\n%s' %(s.split('_')[0], s.split('_')[1]) for s in scenarios]

colors = ['#208380', '#d71b5a', '#2b3e8a']
titles = {2: 'Low', 2.4: 'Medium', 2.8: 'High'}
r0_mig = dict(zip(r0, migration))

df_final = df_final[['scenario', 'vaccine_coverage_1st_dose', 'start_day', 'R0', 'migration', 'urban_prioritization',
                     'Infections_change', 'Severe_change', 'Mortality_change', 'Infections_change_std',
                     'Severe_change_std', 'Mortality_change_std']]

# Plot only 50% coverage case
# df_final = df_final[df_final['R0'] == 2.4]
for s, channel in enumerate(['Infections', 'Severe', 'Mortality']):

    for q, (scen, df_scen) in enumerate(df_final.groupby(['scenario'])):

        fig, axs = plt.subplots(nrows=len(r0), ncols=len(migration), figsize=(14, 7))

        for m, (r, df_r) in enumerate(df_scen.groupby(['R0'])):

            for n, (mig, df_m) in enumerate(df_r.groupby(['migration'])):

                for x, (group_plot, df_gp) in enumerate(df_m.groupby(['vaccine_coverage_1st_dose', 'start_day',
                                                                     'urban_prioritization'])):
                    vc = group_plot[0]  # vaccine_coverage
                    st = group_plot[1]  # start day
                    up = group_plot[2]  # urban prioritization

                    ch_title = 'Migration = %s' % mig
                    sub_bar_loc = urban_rural.index(up) + start_day.index(st) * 2
                    bar_loc = bar_locs[vaccine_coverage_1stdose.index(vc)][sub_bar_loc] + offset[start_day.index(st)]

                    axs[m, n].bar(bar_loc, df_gp[channel + '_change'],
                                  yerr=df_gp[channel + '_change_std'] * 1.96 / np.sqrt(num_seeds),
                                  width=width, color=colors[urban_rural.index(up)],
                                  alpha=(0.3 + 0.3 * start_day.index(st)))

                    axs[m, n].grid(b=True, which='major', color='gray', linestyle='--', alpha=0.3)

                    axs[m, n].set_xticks([1, 3, 5])
                    # axs[m, n].set_xlim([30, 180])
                    if m == 2:
                        axs[m, n].set_xticklabels(['%s%%' % int(i*100) for i in vaccine_coverage_1stdose])
                    else:
                        axs[m, n].set_xticklabels([''] * len(vaccine_coverage_1stdose))

                    if m==2 and n==1:
                        axs[m, n].set_xlabel('Vaccine coverage')

                    if m == 0:
                        axs[m, n].set_title(ch_title, fontsize=18)
                    # if n == 1 and m == 2:
                    #     axs[m, n].set_xlabel('Decrease compared to baseline', fontsize=18)

                    if 'Infections' in channel:
                        axs[m, n].set_ylim([0, 0.3])
                        axs[m, n].set_yticks([0, 0.075, 0.15, 0.225, 0.3])
                        axs[m, n].set_yticklabels(['0', '', '15%', '', '30%'])
                    elif 'Severe' in channel:
                        axs[m, n].set_ylim([0, 0.4])
                        axs[m, n].set_yticks([0, 0.125, 0.25, 0.375, 0.5])
                        axs[m, n].set_yticklabels(['0', '', '25%', '', '50%'])
                    elif 'Mortality' in channel:
                        axs[m, n].set_ylim([0, 0.6])
                        axs[m, n].set_yticks([0, 0.175, 0.35, 0.525, 0.7])
                        axs[m, n].set_yticklabels(['0', '', '35%', '', '70%'])

        custom_lines_2 = [Patch(color=colors[n]) for n in range(2)]
        # custom_lines_2 += [Patch(color='w', hatch='*')]
        fig.legend(custom_lines_2, ['%s' % up.replace('_', ' ').capitalize() for up in ['Urban', 'Rural']],
                   bbox_to_anchor=(0.47, 0.1), ncol=2)

        custom_lines_3 = [Patch(color='k', alpha=0.3 * (1 + n)) for n in range(3)]
        # custom_lines_2 += [Patch(color='w', hatch='*')]
        fig.legend(custom_lines_3, ['%s' % st for st in start_day],
                   bbox_to_anchor=(0.8, 0.12), ncol=3, title='Start Day')

        fig.text(0.93, 0.75, 'R0 = %0.1f' % r0[0], ha='center', fontsize=16)
        fig.text(0.93, 0.5, 'R0 = %0.1f' % r0[1], ha='center', fontsize=16)
        fig.text(0.93, 0.25, 'R0 = %0.1f' % r0[2], ha='center', fontsize=16)
        fig.text(0.02, 0.3, 'Decrease compared to baseline', ha='center', fontsize=18, rotation=90)

        plt.suptitle('%s - %s' % (channel, scen.replace('_', ' ').capitalize()))
        plt.subplots_adjust(left=0.08, bottom=0.2, right=0.88)
        fig_name = os.path.join(fig_dir, 'covax_spatial_priority_supplement_%s_%s.png' % (channel, scen))
        plt.savefig(fig_name)
        # plt.show()
        # plt.close('all')
