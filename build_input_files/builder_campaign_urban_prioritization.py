"""
Prashanth Selvaraj
Apr 2021
"""

import json

import numpy as np

from vaccine_efficacy_article.build_input_files.aux_matrix_calc import mat_magic
from vaccine_efficacy_article.build_input_files.refdat_vaccine_dist import vaccine_availability_by_month


# ********************************************************************************

def campaignBuilder(params=dict(), filename='campaign.json'):
    # Dictionary to be written
    json_set = dict()

    # ***** Campaign file *****
    json_set['Campaign_Name'] = 'COMMENT_FIELD'
    json_set['Events'] = []
    json_set['Use_Defaults'] = 0

    # ***** Events *****

    # Contact pattern revision
    for k1 in range(2, 999):
        if ('trans_mat{:02d}_urban'.format(k1) not in params):
            break

        # Urban
        matmagic_pdict = {'arg_dist': params['trans_mat{:02d}_urban'.format(k1)],
                 'ctext_val': params['ctext_val'],
                 'countries': params['countries']}
        (_, _, matblock) = mat_magic(matmagic_pdict, area='Urban')
        pdict = {'startday': int(params['start_day_trans_mat{:02d}'.format(k1)][0]),
                 'matblock': matblock,
                 'nodes': [1]}
        json_set['Events'].extend(IV_MatrixSwap(pdict))

        # Rural
        matmagic_pdict = {'arg_dist': params['trans_mat{:02d}_rural'.format(k1)],
                          'ctext_val': params['ctext_val'],
                          'countries': params['countries']}
        (_, _, matblock) = mat_magic(matmagic_pdict, area='Rural')
        pdict = {'startday': int(params['start_day_trans_mat{:02d}'.format(k1)][0]),
                 'matblock': matblock,
                 'nodes': [i for i in range(2, 201)]}
        json_set['Events'].extend(IV_MatrixSwap(pdict))
    ##################################################################################################

    # Infection importation
    pdict = {'startday': params['importations_start_day'][0],
             'duration': params['importations_duration'][0],
             'amount': params['importations_daily_rate'][0]}
    json_set['Events'].extend(IV_ImportPressure(pdict))

    # Second infection importation
    pdict = {'startday': 270,
             'duration': 365,
             'amount': params['importations_daily_rate'][0]}
    json_set['Events'].extend(IV_ImportPressure(pdict))
    ##################################################################################################

    # Self-quarantine
    pdict = {'trigger': 'NewlySymptomatic',
             'startday': 15,
             'coverage': params['self_isolate_on_symp_frac'][0],
             'quality': params['self_isolate_effectiveness'][0],
             'delay': 0.00}
    json_set['Events'].extend(IV_Quarantine(pdict))
    ##################################################################################################

    # Age-dependent susceptibility
    pdict = {'startday': 10,
             'coverage': 1.00,
             'qual_acq': params['age_effect'][0] * 0.95,
             'qual_trn': params['age_effect'][0] * 0.95,
             'group_names': [{'Restrictions':
                                  ['Geographic:age00_riskLO']},
                             {'Restrictions':
                                  ['Geographic:age00_riskMD']},
                             {'Restrictions':
                                  ['Geographic:age00_riskHI']}]}
    json_set['Events'].extend(IV_MultiEffect(pdict))

    pdict = {'startday': 11,
             'coverage': 1.00,
             'qual_acq': params['age_effect'][0] * 0.75,
             'qual_trn': params['age_effect'][0] * 0.75,
             'group_names': [{'Restrictions':
                                  ['Geographic:age05_riskLO']},
                             {'Restrictions':
                                  ['Geographic:age05_riskMD']},
                             {'Restrictions':
                                  ['Geographic:age05_riskHI']}]}
    json_set['Events'].extend(IV_MultiEffect(pdict))

    pdict = {'startday': 12,
             'coverage': 1.00,
             'qual_acq': params['age_effect'][0] * 0.60,
             'qual_trn': params['age_effect'][0] * 0.60,
             'group_names': [{'Restrictions':
                                  ['Geographic:age10_riskLO']},
                             {'Restrictions':
                                  ['Geographic:age10_riskMD']},
                             {'Restrictions':
                                  ['Geographic:age10_riskHI']}]}
    json_set['Events'].extend(IV_MultiEffect(pdict))

    pdict = {'startday': 13,
             'coverage': 1.00,
             'qual_acq': params['age_effect'][0] * 0.35,
             'qual_trn': params['age_effect'][0] * 0.35,
             'group_names': [{'Restrictions':
                                  ['Geographic:age15_riskLO']},
                             {'Restrictions':
                                  ['Geographic:age15_riskMD']},
                             {'Restrictions':
                                  ['Geographic:age15_riskHI']}]}
    json_set['Events'].extend(IV_MultiEffect(pdict))
    ##################################################################################################

    # Urban-dependent susceptibility
    pdict = {'startday': 10,
             'coverage': 1.00,
             'qual_acq': params['urban_coverage'][0],
             'qual_trn': params['urban_coverage'][0],
             'nodes': [1]}

    json_set['Events'].extend(IV_GeoMultiEffect(pdict))

    # Rural dependent susceptibility
    pdict = {'startday': 10,
             'coverage': 1.00,
             'qual_acq': params['rural_coverage'][0],
             'qual_trn': params['rural_coverage'][0],
             'nodes': [i for i in range(2, 201)]}

    json_set['Events'].extend(IV_GeoMultiEffect(pdict))
    ###################################################################################################

    # Migration lockdown
    for k1 in range(2, 999):
        if ('migration_rest{:02d}'.format(k1) not in params):
            break

        if int(params['start_day_migration_rest{:02d}'.format(k1)][0]) < 320:
            pdict = {'startday': int(params['start_day_migration_rest{:02d}'.format(k1)][0]),
                     'duration': 365,
                     'efficacy': params['migration_rest{:02d}'.format(k1)][0],
                     # 'efficacy': 0,
                     # 'nodes': params['migration_rest{:02d}'.format(k1)[0]],
                     'nodes': None
                     }
        else:
            pdict = {'startday': int(params['start_day_migration_rest{:02d}'.format(k1)][0]),
                     'duration': 365,
                     'efficacy': params['migration_rest{:02d}'.format(k1)][0] * 10,
                     # 'efficacy': 0,
                     # 'nodes': params['migration_rest{:02d}'.format(k1)[0]],
                     'nodes': None
                     }
        json_set['Events'].extend(IV_Lockdown(pdict))

    ###################################################################################################


    # Vaccines
    if params['urban_prioritization'][0]:
        # indices for final_coverages to attribute to urban or rural prioritization
        if params['urban_prioritization'][0] == 1:
            j = 0
            k = 1
        else:
            j = 1
            k = 0
        for x, vax_group_name in enumerate(params['vaccine_group_names']):
            if params['vaccine_coverage2'][0] > 0:
                final_coverages, vax_distribution = vaccine_availability_by_month(params=params,
                                                                                  covax_distribution=True,
                                                                                  coverage=params['vaccine_coverage2'][0])
                pdict = {'startday': [i + params['start_day'][0] for i in vax_distribution],
                         'coverage_urban': list(final_coverages[j + x * 2, :]),
                         'coverage_rural': list(final_coverages[k + x * 2, :]),
                         'take': params['vaccine_take'][0],
                         'qual_acq': params['vaccine_qual_acq'][0],
                         'qual_trn': params['vaccine_qual_trans'][0],
                         'group_names': vax_group_name,
                         'vaccine_only_urb': params['vaccine_only_urb'][0],
                         'second_dose_effective_date': params['second_dose_effective_date'][0]}
                json_set['Events'].extend(IV_Vaccines_pfizer_2dose_up(pdict))

            if params['vaccine_coverage2'][0] < 1 and params['vaccine_coverage1'][0] > 0:
                final_coverages, vax_distribution = vaccine_availability_by_month(params=params,
                                                                                  covax_distribution=True,
                                                                                  coverage=params['vaccine_coverage1'][0])
                pdict = {'startday': [i + params['start_day'][0] for i in vax_distribution],
                         'coverage_urban': list(final_coverages[j + x * 2, :]),
                         'coverage_rural': list(final_coverages[k + x * 2, :]),
                         'take': params['vaccine_take'][0],
                         'qual_acq': params['vaccine_qual_acq'][0],
                         'qual_trn': params['vaccine_qual_trans'][0],
                         'group_names': vax_group_name,
                         'vaccine_only_urb': params['vaccine_only_urb'][0]}
                json_set['Events'].extend(IV_Vaccines_pfizer_1dose_up(pdict))

    else:
        covax_distribution = params['covax_distribution'][0]
        for x, vax_group_name in enumerate(params['vaccine_group_names']):
            if params['vaccine_coverage2'][0] > 0:
                final_coverages, vax_distribution = vaccine_availability_by_month(params=params,
                                                                                  covax_distribution=covax_distribution,
                                                                                  coverage=params['vaccine_coverage2'][0])
                pdict = { 'startday': [i + params['start_day'][0] for i in vax_distribution],
                         # 'startday': [i for i in vax_distribution],
                         'coverage': list(final_coverages[x]),
                         'take': params['vaccine_take'][0],
                         'qual_acq': params['vaccine_qual_acq'][0],
                         'qual_trn': params['vaccine_qual_trans'][0],
                         'group_names': vax_group_name,
                         'vaccine_only_urb': params['vaccine_only_urb'][0],
                         'second_dose_effective_date': params['second_dose_effective_date'][0]}
                json_set['Events'].extend(IV_Vaccines_pfizer_2dose(pdict))

            if params['vaccine_coverage2'][0] < 1 and params['vaccine_coverage1'][0] > 0:
                # if params['vaccine_coverage1'][0] == 0:
                #     pdict = {  # 'startday': [i for i in vax_distribution],
                #         'startday': [params['start_day'][0]],
                #         'coverage': [0],
                #         'take': params['vaccine_take'][0],
                #         'qual_acq': params['vaccine_qual_acq'][0],
                #         'qual_trn': params['vaccine_qual_trans'][0],
                #         'group_names': vax_group_name,
                #         'vaccine_only_urb': params['vaccine_only_urb'][0]}
                # else:
                final_coverages, vax_distribution = vaccine_availability_by_month(params=params,
                                                                                  covax_distribution=covax_distribution,
                                                                                  coverage=params['vaccine_coverage1'][
                                                                                      0])
                pdict = {  # 'startday': [i for i in vax_distribution],
                    'startday': [i + params['start_day'][0] for i in vax_distribution],
                    'coverage': list(final_coverages[x]),
                    'take': params['vaccine_take'][0],
                    'qual_acq': params['vaccine_qual_acq'][0],
                    'qual_trn': params['vaccine_qual_trans'][0],
                    'group_names': vax_group_name,
                    'vaccine_only_urb': params['vaccine_only_urb'][0]}
                json_set['Events'].extend(IV_Vaccines_pfizer_1dose(pdict))

    # return json_set

    #  ***** End file construction *****
    with open(filename, 'w') as fid01:
        json.dump(json_set, fid01, sort_keys=True)

    ###################################################################################################

# end-campaignBuilder

# ********************************************************************************

# Event observer
def IV_Quarantine(params=dict()):
    IVlist = list()

    IVdic = {'class': 'CampaignEvent',
             'Nodeset_Config': {'class': 'NodeSetAll'},
             'Start_Day': params['startday'],
             'Event_Coordinator_Config':
                 {'class': 'CommunityHealthWorkerEventCoordinator',
                  'Demographic_Coverage': 1.0,
                  'Target_Residents_Only': 0,
                  'Property_Restrictions': [],
                  'Node_Property_Restrictions': [],
                  'Property_Restrictions_Within_Node': [],
                  'Duration': 1000,
                  'Max_Distributed_Per_Day': 1e9,
                  'Waiting_Period': 1000.0,
                  'Days_Between_Shipments': 1000,
                  'Amount_In_Shipment': 0,
                  'Max_Stock': 1e9,
                  'Initial_Amount_Distribution':
                      'CONSTANT_DISTRIBUTION',
                  'Initial_Amount_Constant': 1e9,
                  'Target_Demographic': 'Everyone',
                  'Trigger_Condition_List': [params['trigger']],
                  'Intervention_Config':
                      {'class': 'SimpleVaccine',
                       'Dont_Allow_Duplicates': 0,
                       'Cost_To_Consumer': 0,
                       'Intervention_Name': 'QUARANTINE',
                       'Efficacy_Is_Multiplicative': 1,
                       'Disqualifying_Properties': [],
                       'New_Property_Value': '',
                       'Vaccine_Take': params['coverage'],
                       'Vaccine_Type': 'TransmissionBlocking',
                       'Waning_Config':
                           {'class': 'WaningEffectMapPiecewise',
                            'Initial_Effect': 1.0,
                            'Reference_Timer': 0.0,
                            'Expire_At_Durability_Map_End': 0,
                            'Durability_Map':
                                {
                                    'Times': [0.0, 1.0 + params['delay']],
                                    'Values': [0.0, params['quality']]
                                }
                            }
                       }
                  }
             }

    IVlist.append(IVdic)

    return IVlist


# ********************************************************************************

# Add protection
def IV_MultiEffect(params=dict()):
    IVlist = list()

    IVdic = {'class': 'CampaignEvent',
             'Nodeset_Config': {'class': 'NodeSetAll'},
             'Start_Day': params['startday'],
             'Event_Coordinator_Config':
                 {'class':
                      'StandardInterventionDistributionEventCoordinator',
                  'Demographic_Coverage': 1.0,
                  'Node_Property_Restrictions': [],
                  'Property_Restrictions_Within_Node':
                      params['group_names'],
                  'Number_Repetitions': 1,
                  'Timesteps_Between_Repetitions': 0,
                  'Target_Demographic': 'Everyone',
                  'Target_Residents_Only': 0,
                  'Property_Restrictions': [],
                  'Intervention_Config':
                      {'class': 'MultiEffectVaccine',
                       'Dont_Allow_Duplicates': 0,
                       'Cost_To_Consumer': 0,
                       'Intervention_Name': 'REDUCED_SUSCEPTIBILITY',
                       'Disqualifying_Properties': [],
                       'New_Property_Value': '',
                       'Vaccine_Take': params['coverage'],
                       'Acquire_Config':
                           {'class': 'WaningEffectConstant',
                            'Initial_Effect': params['qual_acq']
                            },
                       'Transmit_Config':
                           {'class': 'WaningEffectConstant',
                            'Initial_Effect': params['qual_trn']
                            },
                       'Mortality_Config':
                           {'class': 'WaningEffectConstant',
                            'Initial_Effect': 1.00
                            }
                       }
                  }
             }

    IVlist.append(IVdic)

    return IVlist

# ********************************************************************************

# Add protection
def IV_GeoMultiEffect(params=dict()):
    IVlist = list()

    nodeset_config = {'class': 'NodeSetNodeList', 'Node_List': params['nodes']}

    IVdic = {'class': 'CampaignEvent',
             'Nodeset_Config': nodeset_config,
             'Start_Day': 5,
             'Event_Coordinator_Config':
                 {'class':
                      'StandardInterventionDistributionEventCoordinator',
                  'Demographic_Coverage': 1.0,
                  'Node_Property_Restrictions': [],
                  'Property_Restrictions_Within_Node': [],
                  'Number_Repetitions': 1,
                  'Timesteps_Between_Repetitions': 0,
                  'Target_Demographic': 'Everyone',
                  'Target_Residents_Only': 0,
                  'Property_Restrictions': [],
                  'Intervention_Config':
                      {'class': 'MultiEffectVaccine',
                       'Dont_Allow_Duplicates': 0,
                       'Cost_To_Consumer': 0,
                       'Intervention_Name': 'REDUCED_GEO_SUSCEPTIBILITY',
                       'Disqualifying_Properties': [],
                       'New_Property_Value': '',
                       'Vaccine_Take': 1.0,
                       'Acquire_Config':
                           {'class': 'WaningEffectConstant',
                            'Initial_Effect': params['qual_acq']
                            },
                       'Transmit_Config':
                           {'class': 'WaningEffectConstant',
                            'Initial_Effect': params['qual_trn']
                            },
                       'Mortality_Config':
                           {'class': 'WaningEffectConstant',
                            'Initial_Effect': 1.00
                            }
                       }
                  }
             }

    IVlist.append(IVdic)

    return IVlist


# ********************************************************************************

# Contagion import
def IV_ImportPressure(params=dict()):
    IVlist = list()

    IVdic = {'class': 'CampaignEvent',
             'Nodeset_Config': {'class': 'NodeSetNodeList',
                                'Node_List': [1]},
             'Start_Day': params['startday'],
             'Event_Coordinator_Config':
                 {'class':
                      'StandardInterventionDistributionEventCoordinator',
                  'Demographic_Coverage': 1.0,
                  'Node_Property_Restrictions': [],
                  'Property_Restrictions_Within_Node': [],
                  'Number_Repetitions': 1,
                  'Timesteps_Between_Repetitions': 0,
                  'Target_Demographic': 'Everyone',
                  'Target_Residents_Only': 0,
                  'Property_Restrictions': [],
                  'Intervention_Config':
                      {'class': 'ImportPressure',
                       'Clade': 0,
                       'Genome': 0,
                       'Number_Cases_Per_Node': 0,
                       'Durations': [params['duration']],
                       'Import_Age': 12775,
                       'Daily_Import_Pressures': [params['amount']]
                       }
                  }
             }

    IVlist.append(IVdic)

    return IVlist


# ********************************************************************************

# HINT revision
def IV_MatrixSwap(params=dict()):
    IVlist = list()

    if (params['nodes']):
        nodsetdic = {'class': 'NodeSetNodeList', 'Node_List': params['nodes']}
    else:
        nodsetdic = {'class': 'NodeSetAll'}

    IVdic = {'class': 'CampaignEvent',
             'Nodeset_Config': nodsetdic,
             'Start_Day': params['startday'],
             'Event_Coordinator_Config':
                 {'class':
                      'StandardInterventionDistributionEventCoordinator',
                  'Demographic_Coverage': 1.0,
                  'Node_Property_Restrictions': [],
                  'Property_Restrictions_Within_Node': [],
                  'Number_Repetitions': 1,
                  'Timesteps_Between_Repetitions': 0,
                  'Target_Demographic': 'Everyone',
                  'Target_Residents_Only': 0,
                  'Property_Restrictions': [],
                  'Intervention_Config':
                      {'class': 'ChangeIPMatrix',
                       'Property_Name': 'Geographic',
                       'New_Matrix': params['matblock'].tolist()
                       }
                  }
             }

    IVlist.append(IVdic)

    return IVlist


# ********************************************************************************

# Vaccine delivery
def IV_Vaccines_pfizer_2dose(params=dict()):
    IVlist = list()

    if (params['vaccine_only_urb']):
        nodsetdic = {'class': 'NodeSetNodeList', 'Node_List': [1]}
    else:
        nodsetdic = {'class': 'NodeSetAll'}

    IVdic = {'class': 'CampaignEvent',
             'Nodeset_Config': nodsetdic,
             'Start_Day': 5,
             'Event_Coordinator_Config':
                 {'class': 'ReferenceTrackingEventCoordinatorCoarseTime',
                  'Time_Value_Map': {
                      'Times': params['startday'],
                      'Values': params['coverage']
                  },
                  'Node_Property_Restrictions': [],
                  'Property_Restrictions_Within_Node':
                      params['group_names'],
                  # 'Property_Restrictions_Within_Node': [],
                  'Number_Repetitions': 1,
                  'Timesteps_Between_Repetitions': 0,
                  'Target_Demographic': 'Everyone',
                  'Target_Residents_Only': 0,
                  'Property_Restrictions': [],
                  'Intervention_Config':{
                      "Disqualifying_Properties": [],
                      "Dont_Allow_Duplicates": 0,
                      "Intervention_List": [
                          {
                              'class': 'MultiEffectVaccine',
                               'Dont_Allow_Duplicates': 0,
                               'Cost_To_Consumer': 0,
                               'Intervention_Name': 'Multi_Intervention2dose',
                               'Disqualifying_Properties': [],
                               'New_Property_Value': 'InterventionStatus:Receive_2dose',
                               'Vaccine_Take': params['take'],
                               'Acquire_Config':
                                   {'class': 'WaningEffectMapLinear',
                                    'Initial_Effect': params['qual_acq'],
                                    "Reference_Timer": 0,
                                    "Expire_At_Durability_Map_End": 0,
                                    "Durability_Map": {
                                        "Times": [0, 10, params['second_dose_effective_date']-7,
                                                  params['second_dose_effective_date']],
                                        "Values": [0.0, 0.8, 0.8, 1.0]
                                    }
                                    },
                               'Transmit_Config':
                                   {'class': 'WaningEffectMapLinear',
                                    'Initial_Effect': params['qual_trn'],
                                    "Reference_Timer": 0,
                                    "Expire_At_Durability_Map_End": 0,
                                    "Durability_Map": {
                                        "Times": [0, 10, params['second_dose_effective_date']-7,
                                                  params['second_dose_effective_date']],
                                        "Values": [0.0, 0.8, 0.8, 1.0]
                                    }
                                    },
                               'Mortality_Config':
                                   {'class': 'WaningEffectConstant',
                                    'Initial_Effect': 1.00
                                    }
                               },
                          {
                              "Broadcast_Event": "GP_EVENT_000",
                              "Disqualifying_Properties": [],
                              "Dont_Allow_Duplicates": 0,
                              "Intervention_Name": 'BroadcastEvent',
                              "New_Property_Value": '',
                              "class": "BroadcastEvent"
                          }
                      ],
                      "Intervention_Name": 'Multi_Intervention2dose',
                      "New_Property_Value": '',
                      "class": "MultiInterventionDistributor",
                  }
                  }
             }

    IVlist.append(IVdic)

    return IVlist


def IV_Vaccines_pfizer_1dose(params=dict()):
    IVlist = list()

    if (params['vaccine_only_urb']):
        nodsetdic = {'class': 'NodeSetNodeList', 'Node_List': [1]}
    else:
        nodsetdic = {'class': 'NodeSetAll'}

    IVdic = {'class': 'CampaignEvent',
             'Nodeset_Config': nodsetdic,
             'Start_Day': 5,
             'Event_Coordinator_Config':
                 {'class': 'ReferenceTrackingEventCoordinatorCoarseTime',
                  'Time_Value_Map': {
                      'Times': params['startday'],
                      'Values': params['coverage']
                  },
                  'Node_Property_Restrictions': [],
                  'Property_Restrictions_Within_Node':
                      params['group_names'],
                  # 'Property_Restrictions_Within_Node': [],
                  'Number_Repetitions': 1,
                  'Timesteps_Between_Repetitions': 0,
                  'Target_Demographic': 'Everyone',
                  'Target_Residents_Only': 0,
                  'Property_Restrictions': [],
                  'Intervention_Config':{
                      "Disqualifying_Properties": [],
                      "Dont_Allow_Duplicates": 0,
                      "Intervention_List": [
                      {'class': 'MultiEffectVaccine',
                       'Dont_Allow_Duplicates': 0,
                       'Cost_To_Consumer': 0,
                       'Intervention_Name': 'Multi_Intervention1dose',
                       'Disqualifying_Properties': [],
                       'New_Property_Value': 'InterventionStatus:Receive_1dose',
                       'Vaccine_Take': params['take'],
                       'Acquire_Config':
                           {'class': 'WaningEffectMapLinear',
                            'Initial_Effect': params['qual_acq'],
                            "Reference_Timer": 0,
                            "Expire_At_Durability_Map_End": 0,
                            "Durability_Map": {
                                "Times": [0, 10],
                                "Values": [0.0, 0.8]
                            }
                            },
                       'Transmit_Config':
                           {'class': 'WaningEffectMapLinear',
                            'Initial_Effect': params['qual_trn'],
                            "Reference_Timer": 0,
                            "Expire_At_Durability_Map_End": 0,
                            "Durability_Map": {
                                "Times": [0, 10],
                                "Values": [0.0, 0.8]
                            }
                            },
                       'Mortality_Config':
                           {'class': 'WaningEffectConstant',
                            'Initial_Effect': 1.00
                            }
                       },
                          {
                              "Broadcast_Event": "GP_EVENT_001",
                              "Disqualifying_Properties": [],
                              "Dont_Allow_Duplicates": 0,
                              "Intervention_Name": 'BroadcastEvent',
                              "New_Property_Value": '',
                              "class": "BroadcastEvent"
                          }
                      ],
                      "Intervention_Name": 'Multi_Intervention1dose',
                      "New_Property_Value": '',
                      "class": "MultiInterventionDistributor",
                  }
                  }
             }

    IVlist.append(IVdic)

    return IVlist


def IV_Vaccines_pfizer_2dose_up(params=dict()):
    IVlist = list()

    for i, nodelist in enumerate([[1], [i for i in range(2, 201)]]):
        if len(nodelist) == 1:
            coverage = params['coverage_urban']
        else:
            coverage = params['coverage_rural']
        IVdic = {'class': 'CampaignEvent',
             'Nodeset_Config': {'class': 'NodeSetNodeList', 'Node_List': nodelist},
             'Start_Day': 5,
             'Event_Coordinator_Config':
                 {'class': 'ReferenceTrackingEventCoordinatorCoarseTime',
                  'Time_Value_Map': {
                      'Times': params['startday'],
                      'Values': coverage
                  },
                  'Node_Property_Restrictions': [],
                  'Property_Restrictions_Within_Node':
                      params['group_names'],
                  # 'Property_Restrictions_Within_Node': [],
                  'Number_Repetitions': 1,
                  'Timesteps_Between_Repetitions': 0,
                  'Target_Demographic': 'Everyone',
                  'Target_Residents_Only': 0,
                  'Property_Restrictions': [],
                  'Intervention_Config':{
                      "Disqualifying_Properties": [],
                      "Dont_Allow_Duplicates": 0,
                      "Intervention_List": [
                          {
                              'class': 'MultiEffectVaccine',
                               'Dont_Allow_Duplicates': 0,
                               'Cost_To_Consumer': 0,
                               'Intervention_Name': 'Multi_Intervention2doseup',
                               'Disqualifying_Properties': [],
                               'New_Property_Value': 'InterventionStatus:Receive_2dose',
                               'Vaccine_Take': params['take'],
                               'Acquire_Config':
                                   {'class': 'WaningEffectMapLinear',
                                    'Initial_Effect': params['qual_acq'],
                                    "Reference_Timer": 0,
                                    "Expire_At_Durability_Map_End": 0,
                                    "Durability_Map": {
                                        "Times": [0, 10, params['second_dose_effective_date']-7,
                                                  params['second_dose_effective_date']],
                                        "Values": [0.0, 0.8, 0.8, 1.0]
                                    }
                                    },
                               'Transmit_Config':
                                   {'class': 'WaningEffectMapLinear',
                                    'Initial_Effect': params['qual_trn'],
                                    "Reference_Timer": 0,
                                    "Expire_At_Durability_Map_End": 0,
                                    "Durability_Map": {
                                        "Times": [0, 10, params['second_dose_effective_date']-7,
                                                  params['second_dose_effective_date']],
                                        "Values": [0.0, 0.8, 0.8, 1.0]
                                    }
                                    },
                               'Mortality_Config':
                                   {'class': 'WaningEffectConstant',
                                    'Initial_Effect': 1.00
                                    }
                               },
                          {
                              "Broadcast_Event": "GP_EVENT_000",
                              "Disqualifying_Properties": [],
                              "Dont_Allow_Duplicates": 0,
                              "Intervention_Name": 'BroadcastEvent',
                              "New_Property_Value": '',
                              "class": "BroadcastEvent"
                          }
                      ],
                      "Intervention_Name": 'Multi_Intervention2doseup',
                      "New_Property_Value": '',
                      "class": "MultiInterventionDistributor",
                  }
                  }
             }

        IVlist.append(IVdic)

    return IVlist


def IV_Vaccines_pfizer_1dose_up(params=dict()):
    IVlist = list()

    for i, nodelist in enumerate([[1], [i for i in range(2, 201)]]):
        if len(nodelist) == 1:
            coverage = params['coverage_urban']
        else:
            coverage = params['coverage_rural']
        IVdic = {'class': 'CampaignEvent',
                 'Nodeset_Config': {'class': 'NodeSetNodeList', 'Node_List': nodelist},
                 'Start_Day': 5,
                 'Event_Coordinator_Config':
                     {'class': 'ReferenceTrackingEventCoordinatorCoarseTime',
                      'Time_Value_Map': {
                          'Times': params['startday'],
                          'Values': coverage
                      },
                      'Node_Property_Restrictions': [],
                      'Property_Restrictions_Within_Node':
                          params['group_names'],
                      # 'Property_Restrictions_Within_Node': [],
                      'Number_Repetitions': 1,
                      'Timesteps_Between_Repetitions': 0,
                      'Target_Demographic': 'Everyone',
                      'Target_Residents_Only': 0,
                      'Property_Restrictions': [],
                      'Intervention_Config':{
                          "Disqualifying_Properties": [],
                          "Dont_Allow_Duplicates": 0,
                          "Intervention_List": [
                          {'class': 'MultiEffectVaccine',
                           'Dont_Allow_Duplicates': 0,
                           'Cost_To_Consumer': 0,
                           'Intervention_Name': 'Multi_Intervention1doseup',
                           'Disqualifying_Properties': [],
                           'New_Property_Value': 'InterventionStatus:Receive_1dose',
                           'Vaccine_Take': params['take'],
                           'Acquire_Config':
                               {'class': 'WaningEffectMapLinear',
                                'Initial_Effect': params['qual_acq'],
                                "Reference_Timer": 0,
                                "Expire_At_Durability_Map_End": 0,
                                "Durability_Map": {
                                    "Times": [0, 10],
                                    "Values": [0.0, 0.8]
                                }
                                },
                           'Transmit_Config':
                               {'class': 'WaningEffectMapLinear',
                                'Initial_Effect': params['qual_trn'],
                                "Reference_Timer": 0,
                                "Expire_At_Durability_Map_End": 0,
                                "Durability_Map": {
                                    "Times": [0, 10],
                                    "Values": [0.0, 0.8]
                                }
                                },
                           'Mortality_Config':
                               {'class': 'WaningEffectConstant',
                                'Initial_Effect': 1.00
                                }
                           },
                              {
                                  "Broadcast_Event": "GP_EVENT_001",
                                  "Disqualifying_Properties": [],
                                  "Dont_Allow_Duplicates": 0,
                                  "Intervention_Name": 'BroadcastEvent',
                                  "New_Property_Value": '',
                                  "class": "BroadcastEvent"
                              }
                          ],
                          "Intervention_Name": 'Multi_Intervention1doseup',
                          "New_Property_Value": '',
                          "class": "MultiInterventionDistributor",
                      }
                      }
                 }

        IVlist.append(IVdic)

    return IVlist

# ********************************************************************************


# Migration restrictions
def IV_Lockdown(params=dict()):
    IVlist = list()

    if not params['nodes']:
        nodeset_config = {'class': 'NodeSetAll'}
    else:
        nodeset_config = {'class': 'NodeSetNodeList', 'Node_List': params['nodes']}

    IVdic = {
        'class': 'CampaignEvent',
        'Nodeset_Config': nodeset_config,
        'Start_Day': params['startday'],
        'Event_Coordinator_Config':
            {
                'class': 'StandardInterventionDistributionEventCoordinator',
                "Demographic_Coverage": 1,
                'Node_Property_Restrictions': [],
                'Number_Repetitions': 1,
                'Property_Restrictions_Within_Node': [],
                'Property_Restrictions': [],
                'Target_Demographic': 'Everyone',
                'Target_Residents_Only': 0,
                'Timesteps_Between_Repetitions': 0,
                "Intervention_Config": {
                    "class": "TravelRestriction",
                    'Intervention_Name': 'TravelRestriction',
                    "Migration_In_Modifier": params['efficacy'],
                    "Migration_Out_Modifier": params['efficacy'],
                    "Duration": params['duration'],
                    'Disqualifying_Properties': [],
                    "New_Property_Value": '',
                }
            }
    }

    IVlist.append(IVdic)

    return IVlist
