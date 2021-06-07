"""
Prashanth Selvaraj
Apr 2021
"""

import os
import re
import pandas as pd
import numpy as np
from simtools.Analysis.AnalyzeManager import AnalyzeManager
from simtools.Analysis.BaseAnalyzers import BaseAnalyzer
from simtools.SetupParser import SetupParser


class EventAnalyzer(BaseAnalyzer):

    def __init__(self, expt_name, report_names=["ReportEventRecorder"],
                 sweep_variables=None, working_dir=".", plotting=False, severe_rates_by_age=None,
                 mortality_rates_by_age=None,
                 geo_dict=None):
        super(EventAnalyzer, self).__init__(working_dir=working_dir,
                                        filenames=["output/{name}.csv".format(name=name)
                                                      for name in report_names]
                                           )
        self.sweep_variables = sweep_variables or ['Run_Number']
        self.reports = report_names
        self.expt_name = expt_name
        self.severe_rates_by_age = severe_rates_by_age
        self.mortality_rates_by_age = mortality_rates_by_age
        self.geo_dict = geo_dict
        self.output_fname = os.path.join(self.working_dir, "%s_event_recorder_data.csv" % self.expt_name)
        self.output_fname_full = os.path.join(self.working_dir, "%s_event_recorder_full.csv" % self.expt_name)
        self.fig_dir = self.working_dir
        self.plotting = plotting

    def select_simulation_data(self, data, simulation):
        simdata = []

        for report in self.reports:

            datatemp = data["output/{name}.csv".format(name=report)]

            datatemp = datatemp[['Time', 'Node_ID', 'Individual_ID', 'Event_Name', 'Geographic', 'InterventionStatus']]
            datatemp['Age'] = datatemp['Geographic'].apply(lambda x: int(re.search(r'\d+', x).group()))
            datatemp['Node_ID'] = datatemp['Node_ID'].apply(lambda x: self.geo_dict[x])
            df_infection = datatemp[datatemp['Event_Name'].isin(['NewInfection'])]

            df_severe = pd.DataFrame()
            df_mortality = pd.DataFrame()
            for g, df_g in df_infection.groupby(['Age', 'Node_ID']):
                number = (
                    df_g.groupby(['Age', 'Node_ID'])['Event_Name'].agg(['count']).values[0][0] * self.severe_rates_by_age[g[0]])
                if number < 0.05:
                    number = 0
                else:
                    number = int(np.ceil(number))
                df_severe = pd.concat(
                    [df_severe, df_g[df_g['Individual_ID'].isin(list(df_g['Individual_ID'].sample(number)))]])
                mortality_number = (
                    df_g.groupby(['Age', 'Node_ID'])['Event_Name'].agg(['count']).values[0][0] *
                    self.mortality_rates_by_age[g[0]])
                if mortality_number < 0.05:
                    mortality_number = 0
                else:
                    mortality_number = int(np.ceil(mortality_number))
                df_mortality = pd.concat(
                    [df_mortality, df_g[df_g['Individual_ID'].isin(list(df_g['Individual_ID'].sample(mortality_number)))]])

            df_severe = df_severe[df_severe['InterventionStatus'] == 'None']
            df_mortality = df_mortality[df_mortality['InterventionStatus'] == 'None']

            df_final = df_infection.groupby(['Age', 'Node_ID'])['InterventionStatus'].agg(['count']).reset_index()
            df_final = pd.pivot_table(df_final, values='count', index=['Age'], columns='Node_ID').reset_index()
            df_final_severe = df_severe.groupby(['Age', 'Node_ID'])['InterventionStatus'].agg(['count'])[
                'count'].reset_index()
            df_final_severe = pd.pivot_table(df_final_severe, values='count', index=['Age'],
                                             columns='Node_ID').reset_index()
            df_final_mortality = df_mortality.groupby(['Age', 'Node_ID'])['InterventionStatus'].agg(['count'])[
                'count'].reset_index()
            df_final_mortality = pd.pivot_table(df_final_mortality, values='count', index=['Age'],
                                             columns='Node_ID').reset_index()
            df_final_mortality.rename(columns={'Rural': 'Rural_Mortality', 'Urban': 'Urban_Mortality'}, inplace=True)

            df_final = pd.merge(df_final, df_final_severe, on=['Age'], suffixes=['_Infections', '_Severe'])
            df_final = pd.merge(df_final, df_final_mortality, on=['Age'], how='left')
            df_final.fillna(0, inplace=True)
            df_final['Infections'] = df_final['Rural_Infections'] + df_final['Urban_Infections']
            df_final['Severe'] = df_final['Rural_Severe'] + df_final['Urban_Severe']
            if 'Rural_Mortality' not in df_final.columns:
                df_final['Rural_Mortality'] = [0]*len(df_final)
            if 'Urban_Mortality' not in df_final.columns:
                df_final['Urban_Mortality'] = [0]*len(df_final)
            df_final['Mortality'] = df_final['Rural_Mortality'] + df_final['Urban_Mortality']

            simdata.append(df_final)

        simdata = pd.concat(simdata)
        # print("Finished simulation" )

        for sweep_var in self.sweep_variables:
            if sweep_var in simulation.tags.keys():
                simdata[sweep_var] = simulation.tags[sweep_var]
            else:
                simdata[sweep_var] = 0
        return simdata

    def finalize(self, all_data):

        data_sets_per_experiment = {}

        # for simulation, associated_data in all_data.items():
        print('Done with analysis')
        for simulation, associated_data in all_data.items():
            experiment_name = simulation.experiment.exp_name
            if experiment_name not in data_sets_per_experiment:
                data_sets_per_experiment[experiment_name] = []

            data_sets_per_experiment[experiment_name].append(associated_data)
        print("Finalizing \n")
        for experiment_name, data_sets in data_sets_per_experiment.items():

            new_channels = ['Infections', 'Severe', 'Mortality']
            for c in ['Infections', 'Severe', 'Mortality']:
                for add in ['Rural_', 'Urban_']:
                    new_channels += [add + c]

            print("about to concatenate \n")
            d = pd.concat(data_sets).reset_index(drop=True)
            d.to_csv(self.output_fname_full)
            print("Concatenated\n")

            self.sweep_variables.remove('Run_Number')
            d_mean = d.groupby(self.sweep_variables)[new_channels].apply(np.mean).reset_index()
            d_std = d.groupby(self.sweep_variables)[new_channels].apply(np.std).reset_index()
            for channel in new_channels:
                d_mean[channel + '_std'] = d_std[channel]
            d_mean.to_csv(self.output_fname, index=False)


if __name__ == "__main__":

    projectdir = os.path.join(os.path.expanduser('~'), 'Dropbox (IDM)', 'COVID-19', 'emod-simulations',
                              'PS')
    os.makedirs(projectdir, exist_ok=True)

    SetupParser.default_block = 'HPC'
    SetupParser.init()

    out_dir = os.path.join(projectdir, 'sim_data')

    experiments = {"Test": "92a480da-6cac-eb11-a2e3-c4346bcb7275"}

    ages = [a for a in range(0, 80, 5)]
    severe_rates = [0.00050, 0.00050, 0.00165, 0.00165, 0.00720, 0.00720, 0.02080, 0.02080,
                    0.03430, 0.03430, 0.07650, 0.07650, 0.13280, 0.13280, 0.21, 0.21]
    mortality_rates = [0.0000161, 0.0000161, 0.0000695, 0.0000695, 0.000309, 0.000309, 0.000844, 0.000844,
                       0.00161, 0.00161, 0.00595, 0.00595, 0.0193, 0.0193, 0.0428, 0.0578]
    severe_dict = dict(zip(ages, severe_rates))
    mortality_dict = dict(zip(ages, mortality_rates))

    nodes = [i for i in range(1, 201)]
    node_labels = ['Urban'] + ['Rural'] * 200
    geo_dict = dict(zip(nodes, node_labels))

    for expt_name, exp_id in experiments.items():
        am = AnalyzeManager(exp_list=exp_id,
                            analyzers=[
                                EventAnalyzer(working_dir=out_dir,
                                                expt_name=expt_name,
                                              severe_rates_by_age=severe_dict,
                                              mortality_rates_by_age=mortality_dict,
                                              geo_dict=geo_dict,
                                                report_names = ['ReportEventRecorder'],
                                                sweep_variables=["Run_Number"])
                                       ],
                            force_analyze=False)

        print(am.experiments)
        am.analyze()