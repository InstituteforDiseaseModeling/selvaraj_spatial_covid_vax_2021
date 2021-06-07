"""
Prashanth Selvaraj
Apr 2021
"""
import os
import json

from vaccine_efficacy_article.build_input_files.builder_campaign_urban_prioritization import campaignBuilder
from vaccine_efficacy_article.params import *


def  create_simulation(cb, seed=0, importation_rate=1.2, r0=2.4, acq_coverage1=0.0, acq_coverage2=0.0,
                         dis_coverage1=0.0, dis_coverage2=0.0, urban=1, age=15,
                      filename='', start_day=250, covax_distribution=0, urban_prioritization=0,
                      roundtrip_probability=0.0, roundtrip_duration=0.0, tg='random',
                      **kwargs):
    scenario = ''
    coverage1 = 0
    coverage2 = 0

    if acq_coverage1 == 0 and dis_coverage1 == 0:
        scenario = 'baseline'
    elif acq_coverage1:
        scenario = 'acquisition_blocking'
        coverage1 = acq_coverage1
        coverage2 = acq_coverage2
        # cb.set_param("Demographics_Filenames", [demo_fn])
    elif dis_coverage1:
        scenario = 'disease_blocking'
        coverage1 = dis_coverage1
        coverage2 = dis_coverage2
        # cb.set_param("Demographics_Filenames", [demo_fn])

        # I don't include the frac_rural multipliers here so that the sim tags are easier to match up during analysis

    with open(filename) as f:
        campaign = json.load(f)
    cb.add_input_file('campaign.json', campaign)

    cb.campaign.Use_Defaults = False
    cb.set_param('Simulation_Duration', 730)
    cb.set_param('Run_Number', seed)
    cb.set_param('Base_Infectivity_Exponential', r0 / 8.0)
    cb.set_param('Regional_Migration_Roundtrip_Duration', roundtrip_duration)
    cb.set_param('Regional_Migration_Roundtrip_Probability', roundtrip_probability)

    tags_dict = {'Run_Number': seed, 'R0': r0, 'importations_daily_rate': importation_rate,
                 'vaccine_coverage_1st_dose': coverage1, 'vaccine_coverage_2nd_dose': coverage2,
                 'urban_only': urban, 'scenario': scenario, 'start_day': start_day,
                 'covax_distribution': covax_distribution, 'urban_prioritization': urban_prioritization,
                 'roundtrip_probability': roundtrip_probability, 'roundtrip_duration': roundtrip_duration,
                 'target_group': tg}

    if 'demo_fn' in kwargs:
        demo_fn = kwargs.pop('demo_fn', False)
        cb.set_param("Demographics_Filenames", [demo_fn])
        mig_rates = eval(demo_fn.split('_')[-1].split('.json')[0])
        cb.set_param("Regional_Migration_Filename",
                     demo_fn.replace("covax_demographics", "regional_migration").replace(".json", ".bin"))
        tags_dict.update({'migration': mig_rates})

    if 'urban_coverage' in kwargs:
        urban_coverage = kwargs.pop('urban_coverage', False)
        tags_dict.update({'urban_coverage': urban_coverage})

    if 'rural_coverage' in kwargs:
        rural_coverage = kwargs.pop('rural_coverage', False)
        tags_dict.update({'rural_coverage': rural_coverage})

    return tags_dict


def create_campaign_file(importation_rate=1.2, acq_coverage1=0.0, acq_coverage2=0.0,
                         dis_coverage1=0.0, dis_coverage2=0.0, take=1.0,
                         start_day=250, modified_inputs_path='', countries: list = None,
                         covax_distribution=False, urban_prioritization=0, urban_coverage=0, rural_coverage=0,
                         target_groups: list = [15]):
    params = create_params_dict(countries=countries, covax_distribution=True)
    params['importations_daily_rate'] = [importation_rate]
    params['vaccine_take'] = [take]
    params['start_day'] = [start_day]
    params['covax_distribution'] = [covax_distribution]
    params['vaccine_only_urb'] = [0]
    params['urban_prioritization'] = [urban_prioritization]
    params['urban_coverage'] = [urban_coverage]
    params['rural_coverage'] = [rural_coverage]
    params['target_groups'] = [target_groups]
    acq2 = acq_coverage1*acq_coverage2 # acquisition blocking vaccine coverage in two dose group
    acq1 = acq_coverage1 * (1 - acq_coverage2)

    dis2 = dis_coverage1 * dis_coverage2  # acquisition blocking vaccine coverage in two dose group
    dis1 = dis_coverage1 * (1 - dis_coverage2)

    tg = 'random'
    if len(target_groups) > 1 and target_groups[0] == 15:
        tg = 'old_first'
    elif len(target_groups) > 1 and target_groups[0] > 15:
        tg = 'young_first'


    final_vaccine_groups = []
    target_groups = list(reversed(params['target_groups'][0]))
    # while None in vaccine_groups:
    for i, target_group in enumerate(target_groups):
        vaccine_groups = []
        if len(target_groups) > 1:
            if target_groups[1] < target_groups[0]:
                if i == 0:
                    for j in range(target_groups[i], 76, 5):
                        vaccine_groups += [{'Restrictions': ['Geographic:age%02d_riskHI' % j]},
                                           {'Restrictions': ['Geographic:age%02d_riskMD' % j]},
                                           {'Restrictions': ['Geographic:age%02d_riskLO' % j]}]
                else:
                    for j in range(target_groups[i], target_groups[i - 1], 5):
                        vaccine_groups += [{'Restrictions': ['Geographic:age%02d_riskHI' % j]},
                                           {'Restrictions': ['Geographic:age%02d_riskMD' % j]},
                                           {'Restrictions': ['Geographic:age%02d_riskLO' % j]}]
                final_vaccine_groups += [vaccine_groups]
            else:
                if i == len(target_groups) - 1:
                    for j in range(target_groups[i], 76, 5):
                        vaccine_groups += [{'Restrictions': ['Geographic:age%02d_riskHI' % j]},
                                           {'Restrictions': ['Geographic:age%02d_riskMD' % j]},
                                           {'Restrictions': ['Geographic:age%02d_riskLO' % j]}]
                else:
                    for j in range(target_groups[i], target_groups[i+1], 5):
                        vaccine_groups += [{'Restrictions': ['Geographic:age%02d_riskHI' % j]},
                                           {'Restrictions': ['Geographic:age%02d_riskMD' % j]},
                                           {'Restrictions': ['Geographic:age%02d_riskLO' % j]}]
                final_vaccine_groups += [vaccine_groups]
        else:
            for j in range(target_groups[i], 76, 5):
                vaccine_groups += [{'Restrictions': ['Geographic:age%02d_riskHI' % j]},
                                   {'Restrictions': ['Geographic:age%02d_riskMD' % j]},
                                   {'Restrictions': ['Geographic:age%02d_riskLO' % j]}]
            final_vaccine_groups += [vaccine_groups]

    filename = os.path.join(modified_inputs_path, 'campaign.json')
    params['vaccine_group_names'] = final_vaccine_groups

    if acq_coverage1 == 0 and dis_coverage1 == 0:
        scenario = 'baseline'
        coverage = acq_coverage1
        params['vaccine_coverage1'] = [0]
        params['vaccine_coverage2'] = [0]
        # filename = os.path.join(modified_inputs_path, scenario, 'campaign_%0.1f_u%0.1f,r%0.1f.json'
        #                         % (coverage, urban_coverage, rural_coverage))
        filename = os.path.join(modified_inputs_path, scenario, 'campaign_%0.2f.json'
                                % (coverage))
    elif acq_coverage1:
        scenario = 'acquisition_blocking'
        params['vaccine_qual_trans'] = [0]
        params['vaccine_qual_acq'] = params['vaccine_qual_acq']
        params['vaccine_coverage1'] = [acq1]
        params['vaccine_coverage2'] = [acq2]
        coverage1 = acq_coverage1
        coverage2 = acq_coverage2
        filename = os.path.join(modified_inputs_path, scenario, 'campaign_1d_%0.2f_2d_%0.2f_%i_%i_%i_%s.json'
                                % (coverage1, coverage2, start_day, covax_distribution*1,
                                   urban_prioritization, tg))
    elif dis_coverage1:
        scenario = 'disease_blocking'
        params['vaccine_qual_acq'] = [0]
        params['vaccine_coverage1'] = [dis1]
        params['vaccine_coverage2'] = [dis2]
        coverage1 = dis_coverage1
        coverage2 = dis_coverage2
        filename = os.path.join(modified_inputs_path, scenario, 'campaign_1d_%0.2f_2d_%0.2f_%i_%i_%i_%s.json'
                                % (coverage1, coverage2, start_day, covax_distribution*1,
                                   urban_prioritization, tg))

    if not os.path.exists(filename):
        campaignBuilder(params=params, filename=filename)

    return None
