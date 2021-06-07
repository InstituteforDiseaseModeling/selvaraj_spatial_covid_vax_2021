"""
Prashanth Selvaraj
Apr 2021
"""

import os
import sys
import argparse

sys.path.append(os.path.dirname(__file__))

from simtools.Analysis.AnalyzeManager import AnalyzeManager
from report_event_analyzer import EventAnalyzer

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Running analyzer')
    parser.add_argument("--experiment_id_dict", default=None, type=str, help="Experiment id dictionary")
    args = parser.parse_args()

    experiments = eval(args.experiment_id_dict)
    # experiments = {'Test': 'd1f7ffc1-a374-ea11-a2c5-c4346bcb1550'}

    ages = [a for a in range(0, 80, 5)]
    mortality_rates = [0.0000161, 0.0000161, 0.0000695, 0.0000695, 0.000309, 0.000309, 0.000844, 0.000844,
                       0.00161, 0.00161, 0.00595, 0.00595, 0.0193, 0.0193, 0.0428, 0.0578]
    severe_rates = [0.00050, 0.00050, 0.00165, 0.00165, 0.00720, 0.00720, 0.02080, 0.02080,
                    0.03430, 0.03430, 0.07650, 0.07650, 0.13280, 0.13280, 0.21, 0.21]
    mortality_dict = dict(zip(ages, mortality_rates))
    severe_dict = dict(zip(ages, severe_rates))

    nodes = [i for i in range(1, 201)]
    node_labels = ['Urban'] + ['Rural'] * 200
    geo_dict = dict(zip(nodes, node_labels))

    property_report_channels = ['New Infections']
    new_channels = []
    mortality_rates_dict = {}
    for channel in property_report_channels:
        for age in [a for a in range(0, 80, 5)]:
            for group in ['riskHI', 'riskMD', 'riskLO']:
                for int in ['InterventionStatus:Receive_1dose', 'InterventionStatus:Receive_2dose',
                            'InterventionStatus:None']:
                    if age < 10:
                        new_channel_names = '%s:Geographic:age0%i_%s,%s' % (channel, age, group, int)
                    else:
                        new_channel_names = '%s:Geographic:age%i_%s,%s' % (channel, age, group, int)
                    mortality_rates_dict.update({new_channel_names: mortality_dict[age]})
                    new_channels.append(new_channel_names)

    inset_chart_channels = ['New Infections', 'Infectious Population']

    # # Spatial priority
    # sweep_vars = ["covax_distribution", 'migration', "R0", 'Run_Number', 'scenario', 'start_day',
    #               'urban_prioritization', "vaccine_coverage_1st_dose"]

    # Age priority
    sweep_vars = ["covax_distribution", 'migration', "R0", 'Run_Number', 'scenario', 'start_day', 'target_group',
                  "vaccine_coverage_1st_dose"]

    for expt_name, exp_id in experiments.items():
        am = AnalyzeManager(exp_list=exp_id,
                            analyzers=[
                                EventAnalyzer(expt_name=expt_name,
                                              severe_rates_by_age=severe_dict,
                                              mortality_rates_by_age=mortality_dict,
                                              geo_dict=geo_dict,
                                              sweep_variables=sweep_vars,
                                              ),
                            ]
                            )
        print(am.experiments)
        am.analyze()
