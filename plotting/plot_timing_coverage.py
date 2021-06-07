import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import rcParams
from matplotlib.patches import Patch
import seaborn as sns

mpl.rcParams['pdf.fonttype'] = 42
rcParams.update({'font.size': 16})

# type = 'pulsed_phased'
type = 'covax_timing_coverage'

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

colors = ['YlGnBu', 'YlOrBr', 'Blues']
titles = {2: 'Low', 2.4: 'Medium', 2.8: 'High'}

# Build 3
fig, axs = plt.subplots(nrows=len(scenarios), ncols=3, figsize=(14, 7))
# Use medium migration and R0
df_final = df_final[(df_final['R0'] == 2.4) & (df_final['migration'] == 0.0025)]

# Plot only 50% coverage case
for s, channel in enumerate(['Infections', 'Severe', 'Mortality']):
    if 'Infections' in channel:
        ch_title = 'Infections averted'
    elif 'Severe' in channel:
        ch_title = 'Severe cases averted'
    elif 'Mortality' in channel:
        ch_title = 'Deaths averted'
    for x, (group_plot, df_gp) in enumerate(df_final.groupby(['scenario', 'target_group'])):
            sc = group_plot[0] # scenario
            tp = group_plot[1]  # target_group

            k = scenarios.index(sc)
            i = target_group.index(tp)

            if 'Infections' in channel:
                vmax = 0.15*100
            elif 'Severe' in channel:
                vmax = 0.3*100
            elif 'Mortality' in channel:
                vmax = 0.5*100

            dftemp = df_gp.pivot('vaccine_coverage_1st_dose', 'start_day', channel+'_change')
            dftemp = (dftemp * 100).apply(np.ceil)

            if k == 0:
                g1 = sns.heatmap(dftemp, ax=axs[k, s], cmap=colors[s], vmin=0, vmax=vmax, cbar=None, annot=True,
                                 fmt="0.1f", annot_kws={"fontsize":10})
            else:
                cbar_ax = fig.add_axes([.1+0.283*s, .1, .2, .03])
                g1 = sns.heatmap(dftemp, ax=axs[k, s], cmap=colors[s], cbar_kws={"orientation": "horizontal"},
                                 cbar_ax=cbar_ax, vmin=0, vmax=vmax, annot=True, fmt="0.1f", annot_kws={"fontsize": 10})
                cbar = g1.collections[0].colorbar
                cbar.set_ticks([0, vmax/4, vmax/2, 3*vmax/4, vmax])
                cbar.set_ticklabels(['0%', '', str(int(round(vmax/2, 1)))+'%',
                                     '', str(int(round(vmax, 1)))+'%'])
            g1.invert_yaxis()

            if k == 1 and s == 1:
                g1.set(xlabel='Start day')
            else:
                g1.set(xlabel=None)

            if k == 0:
                g1.set(xticklabels=[])
                g1.set(title=ch_title)
            if s > 0:
                g1.set(yticklabels=[])
            else:
                g1.set(yticklabels=['20%', '', '40%', '', '60%', '', '80%'])
            g1.set(ylabel=None)



    # custom_lines_2 = [Patch(color=colors[n]) for n in range(3)]
    # # custom_lines_2 += [Patch(color='w', hatch='*')]
    # fig.legend(custom_lines_2, ['%s' % tg.replace('_', ' ').capitalize() for tg in target_group],
    #            bbox_to_anchor=(0.7, 0.1), ncol=3)
    #
    fig.text(0.93, 0.7, scenario_labels[0].capitalize(), ha='center', fontsize=16)
    fig.text(0.93, 0.32, scenario_labels[1].capitalize(), ha='center', fontsize=16)
    fig.text(0.02, 0.38, 'Vaccine coverage', ha='center', fontsize=18, rotation=90)

plt.suptitle('Lost time does not make up for greater coverage later')
plt.tight_layout()
plt.subplots_adjust(left=0.08, bottom=0.23, right=0.88)
fig_name = os.path.join(fig_dir, 'covax_timing_coverage.png')
plt.xticks(rotation=90)
plt.savefig(fig_name)
# plt.show()
# plt.close('all')
