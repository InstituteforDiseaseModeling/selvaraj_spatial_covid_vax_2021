"""
Ghana DTK COVID-19 run file
"""
#
import sys

from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from simtools.SetupParser import SetupParser
from simtools.ModBuilder import ModBuilder, ModFn
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory

from vaccine_efficacy_article.build_input_files.builder_config import configBuilder
from vaccine_efficacy_article.build_input_files.builder_demographics import demographicsBuilder
from vaccine_efficacy_article.build_input_files.helper_functions import create_campaign_file, create_simulation
from vaccine_efficacy_article.params import create_params_dict

import os

sys.path.append(os.pardir)


if __name__ == "__main__":

    exp_name = 'covax_spatial_priority'
    countries = ['Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon', 'Central African Republic',
                 'Chad', 'Ivory Coast', 'DRC', 'Eritrea', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea',
                 'Guinea-Bissau', 'Kenya', 'Lesotho', 'Liberia', 'Madagascar', 'Malawi', 'Mali', 'Mauritania',
                 'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda', 'Senegal', 'Sierra Leone',
                 'South Africa', 'Tanzania', 'Togo', 'Uganda', 'Zambia', 'Zimbabwe']

    # Setup basic simulation parameters
    num_seeds = 20

    # Initialize setup parser
    SetupParser.default_block = "HPC"
    SetupParser.init(selected_block=SetupParser.default_block)

    # Instantiate config builder
    modified_inputs_path = os.path.join(os.getcwd(), 'input_files', exp_name)
    os.makedirs(modified_inputs_path, exist_ok=True)

    for scenario in ['acquisition_blocking', 'disease_blocking', 'baseline']:
        os.makedirs(os.path.join(modified_inputs_path, scenario), exist_ok=True)

    params = create_params_dict(countries=countries)
    config_file = configBuilder(params=params, dir=modified_inputs_path)
    cb = DTKConfigBuilder.from_files(config_file)

    demographics_fn = os.path.join(modified_inputs_path, 'covax_demographics.json')
    if not os.path.exists(demographics_fn):
        demographicsBuilder(params=params, demographics_fn=demographics_fn, dir=modified_inputs_path)

    cb.set_param("Demographics_Filenames", [os.path.join(exp_name, 'covax_demographics.json')])
    cb.set_param("Regional_Migration_Filename", os.path.join(exp_name, 'regional_migration_%0.4f.bin'
                                                             % params['migration_coeff'][0]))

    cb.set_param("Report_Event_Recorder", 1)
    cb.set_param("Report_Event_Recorder_Events", ['NewInfection'])
    # cb.set_param("Report_Event_Recorder_Events", ['Immigrating', 'Emigrating'])
    cb.set_param("Report_Event_Recorder_Ignore_Events_In_List", 0)
    cb.set_param("Report_Event_Recorder_Individual_Properties", ['InterventionStatus', 'Geographic'])
    cb.set_param("logLevel_default", 'ERROR')

    cb.set_param('Enable_Spatial_Output', 1)
    cb.set_param('Spatial_Output_Channels', ['New_Infections', 'Population'])
    # cb.set_param("Enable_Event_DB", 0)

    importation_rate = [2.0]
    repro_number = [2.0, 2.2, 2.4, 2.6, 2.8, 3.0]
    coverage_1stdose = [0.5]
    coverage_2nddose = [1.0]  # This coverage is multiplied by coverage_1stdose values
    covax_distribution = [1]
    urban_prioritization = [0, 1, 2]          # 0 - no prioritization in time, 1 - urban priority, 2 - rural priority
    migration_rates = [1e-4, 1e-3, 2.5e-3, 1e-2, 2.5e-2]
    start_day = [90]
    target_groups = [[15, 50, 60, 70]]

    # Write campaign files
    # if not os.path.exists(modified_inputs_path):
    for scen in ['disease', 'acquire']:
        for c1 in coverage_1stdose:
            for c2 in coverage_2nddose:
                for s in start_day:
                    for cd in covax_distribution:
                        for up in urban_prioritization:
                            for target_group in target_groups:
                                if scen == 'acquire':
                                    create_campaign_file(importation_rate=importation_rate[0], acq_coverage1=c1,
                                                         acq_coverage2=c2,
                                                         start_day=s, modified_inputs_path=modified_inputs_path,
                                                         countries=countries, covax_distribution=cd,
                                                         urban_prioritization=up, target_groups=target_group)
                                else:
                                    create_campaign_file(importation_rate=importation_rate[0], dis_coverage1=c1,
                                                         dis_coverage2=c2,
                                                         start_day=s, modified_inputs_path=modified_inputs_path,
                                                         countries=countries, covax_distribution=cd,
                                                         urban_prioritization=up, target_groups=target_group)

    for scen in ['baseline']:
        for i in importation_rate:
            create_campaign_file(importation_rate=i,
                                 modified_inputs_path=modified_inputs_path,
                                 covax_distribution=0,
                                 countries=countries, target_groups=[15, 50])

    # Build demographics files
    for mig in migration_rates:
        demographics_fn = os.path.join(modified_inputs_path, 'covax_demographics_%0.4f.json' % mig)
        if not os.path.exists(demographics_fn):
            params['migration_coeff'] = [mig]
            demographicsBuilder(params=params, demographics_fn=demographics_fn, dir=modified_inputs_path)

    # Build out list of scenarios
    acq_blocking_scenario = [
        [
            ModFn(create_simulation, seed=seed, r0=r0, importation_rate=ir, acq_coverage1=c1, acq_coverage2=c2,
                  start_day=s, covax_distribution=cd, urban_prioritization=up, tg=tg,
                  filename=os.path.join(modified_inputs_path, 'acquisition_blocking',
                                        'campaign_1d_%0.2f_2d_%0.2f_%i_%i_%i_%s.json'
                                        % (c1, c2, s, cd, up, tg)),
                  demo_fn=os.path.join(exp_name, 'covax_demographics_%0.4f.json' % mig),
                  roundtrip_probability=rtp, roundtrip_duration=rtd)
        ]
        for seed in range(num_seeds)
        for ir in importation_rate
        for r0 in repro_number
        for mig in migration_rates
        for c1 in coverage_1stdose
        for c2 in coverage_2nddose
        for s in start_day
        for cd in covax_distribution
        for up in urban_prioritization
        for tg in ['old_first']
        for rtp in [0.8]  # round trip probability
        for rtd in [7]  # round trip duration
    ]

    dis_blocking_scenario = [
        [
            ModFn(create_simulation, seed=seed, r0=r0, importation_rate=ir, dis_coverage1=c1, dis_coverage2=c2,
                  start_day=s, covax_distribution=cd, urban_prioritization=up, tg=tg,
                  filename=os.path.join(modified_inputs_path, 'disease_blocking',
                                        'campaign_1d_%0.2f_2d_%0.2f_%i_%i_%i_%s.json'
                                        % (c1, c2, s, cd, up, tg)),
                  demo_fn=os.path.join(exp_name, 'covax_demographics_%0.4f.json' % mig),
                  roundtrip_probability=rtp, roundtrip_duration=rtd)
        ]
        for seed in range(num_seeds)
        for ir in importation_rate
        for r0 in repro_number
        for mig in migration_rates
        for c1 in coverage_1stdose
        for c2 in coverage_2nddose
        for s in start_day
        for cd in covax_distribution
        for up in urban_prioritization
        for tg in ['old_first']
        for rtp in [0.8]  # round trip probability
        for rtd in [7]  # round trip duration
    ]

    baseline = [
        [
            ModFn(create_simulation, seed=seed, r0=r0, importation_rate=ir, acq_coverage1=c,
                  filename=os.path.join(modified_inputs_path, 'baseline',
                                        'campaign_%0.2f.json' % c),
                  demo_fn = os.path.join(exp_name, 'covax_demographics_%0.4f.json' % mig),
                  roundtrip_probability=rtp, roundtrip_duration=rtd)
    ]
        for seed in range(num_seeds)
        for ir in importation_rate
        for r0 in repro_number
        for mig in migration_rates
        for rtp in [0.8]  # round trip probability
        for rtd in [7]  # round trip duration
        for c in [0.0]
    ]

    builder = ModBuilder.from_list(acq_blocking_scenario + dis_blocking_scenario + baseline)
    # builder = ModBuilder.from_list(baseline)
    # builder = ModBuilder.from_list(acq_blocking_scenario)

    # Run locally or on HPC
    run_sim_args = {'config_builder': cb,
                    'exp_name': exp_name,
                    'exp_builder': builder}

    exp_manager = ExperimentManagerFactory.from_cb(cb)
    exp_manager.run_simulations(**run_sim_args)
    exp_manager.wait_for_finished(verbose=False)
