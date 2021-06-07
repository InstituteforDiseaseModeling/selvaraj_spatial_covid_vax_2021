"""
Prashanth Selvaraj
Apr 2021
"""
import json, io, os

import numpy                    as    np
import scipy.spatial.distance   as    spspd

from vaccine_efficacy_article.build_input_files.aux_matrix_calc import mat_magic


# ********************************************************************************

def demographicsBuilder(params=dict(), demographics_fn='demographics.json', dir='.'):
    # Get HINT matrix - urban
    pdict = {'arg_dist': params['trans_mat01_urban'],
             'ctext_val': params['ctext_val'],
             'countries': params['countries']}
    (age_pyr_urban, age_names, mat_block_urban) = mat_magic(pdict, area='Urban')

    # Get HINT matrix - urban
    pdict = {'arg_dist': params['trans_mat01_rural'],
             'ctext_val': params['ctext_val'],
             'countries': params['countries']}
    (age_pyr_rural, age_names, mat_block_rural) = mat_magic(pdict, area='Rural')

    # *****  Dictionary of parameters to be written *****

    json_set = dict()

    # ***** Detailed node attributes *****

    # Add node list
    json_set['Nodes'] = list()

    # Generate nodes
    totpop = params['totpop'][0]
    num_nodes = params['num_nodes'][0]
    mrcoeff = params['migration_coeff'][0]
    frac_rural = params['frac_rural'][0]
    pop_pow = params['pop_power'][0]

    # Generate node sizes
    nsizes = np.exp(-np.log(np.random.rand(num_nodes - 1)) / pop_pow)
    nsizes = frac_rural * nsizes / np.sum(nsizes)
    nsizes = np.minimum(nsizes, 100 / totpop)
    nsizes = frac_rural * nsizes / np.sum(nsizes)
    nsizes = np.insert(nsizes, 0, 1 - frac_rural)
    npops = ((np.round(totpop * nsizes, 0)).astype(int)).tolist()

    # Generate node lattice
    ucellb = np.array([[1.0, 0.0], [-0.5, 0.86603]])
    nlocs = np.random.rand(num_nodes, 2)
    nlocs[0, :] = 0.5
    nlocs = np.round(np.matmul(nlocs, ucellb), 4)

    # Add nodes to demographics
    for k1 in range(len(npops)):
        nodeDic = dict()
        nodeDic['NodeID'] = k1 + 1
        nodeDic['NodeAttributes'] = {'InitialPopulation': npops[k1],
                                     'Latitude': nlocs[k1, 1],
                                     'Longitude': nlocs[k1, 0]}
        json_set['Nodes'].append(nodeDic)

        if k1 == 0:
            ipdict = dict()
            ipdict['Property'] = 'Geographic'
            ipdict['Values'] = age_names
            ipdict['Initial_Distribution'] = age_pyr_urban.tolist()
            # ipdict['Transitions'] = list()
            ipdict['TransmissionMatrix'] = {'Matrix': mat_block_urban.tolist(),
                                            'Route': 'Contact'}

            json_set['Nodes'][0]['IndividualProperties'] = [ipdict]

            ipdict = dict()
            ipdict['Property'] = 'InterventionStatus'
            ipdict['Values'] = ['None', 'Receive_1dose', 'Receive_2dose']
            ipdict['Initial_Distribution'] = [1, 0, 0]

            json_set['Nodes'][0]['IndividualProperties'].append(ipdict)

    # ***** Metadata and default attributes *****

    # Create metadata dictionary
    json_set['Metadata'] = {'IdReference': 'covid-custom'}

    # Create defaults dictionary
    json_set['Defaults'] = {'IndividualAttributes': dict(),
                            'IndividualProperties': list(),
                            'NodeAttributes': dict()}

    # Add default node attributes
    nadict = dict()

    nadict['BirthRate'] = 0.0
    nadict['Airport'] = 0
    nadict['Region'] = 1
    nadict['Seaport'] = 0

    json_set['Defaults']['NodeAttributes'].update(nadict)

    # Add default individual properties
    ipdict = dict()

    ipdict['Property'] = 'Geographic'
    ipdict['Values'] = age_names
    ipdict['Initial_Distribution'] = age_pyr_rural.tolist()
    # ipdict['Transitions'] = list()
    ipdict['TransmissionMatrix'] = {'Matrix': mat_block_rural.tolist(),
                                    'Route': 'Contact'}

    json_set['Defaults']['IndividualProperties'].append(ipdict)

    # Vaccine tags
    ipdict = dict()
    ipdict['Property'] = 'InterventionStatus'
    ipdict['Values'] = ['None', 'Receive_1dose', 'Receive_2dose']
    ipdict['Initial_Distribution'] = [1, 0, 0]

    json_set['Defaults']['IndividualProperties'].append(ipdict)

    # ***** Write demographics files *****
    with open(demographics_fn, 'w')  as fid01:
        json.dump(json_set, fid01, sort_keys=True)

########################################################################################################################
    # ***** Write migration files *****
    migJson = {'Metadata': {'IdReference': 'covid-custom', 'NodeCount': num_nodes,
                            'DatavalueCount': 30}, 'NodeOffsets': ''.join(['{:0>8s}{:0>8s}'.format(hex(k1)[2:], hex(k1 * 360)[2:])
                                                                           for k1 in range(num_nodes)])}

    with open(os.path.join(dir, 'regional_migration_%0.4f.bin.json' % mrcoeff), 'w') as fid01:
        json.dump(migJson, fid01, sort_keys=True)

    # Calculate inter-node distances on periodic grid
    nlocs = np.tile(nlocs, (9, 1))
    nlocs[0 * num_nodes:1 * num_nodes, :] += [0.0, 0.0]
    nlocs[1 * num_nodes:2 * num_nodes, :] += [1.0, 0.0]
    nlocs[2 * num_nodes:3 * num_nodes, :] += [-1.0, 0.0]
    nlocs[3 * num_nodes:4 * num_nodes, :] += [0.0, 0.0]
    nlocs[4 * num_nodes:5 * num_nodes, :] += [1.0, 0.0]
    nlocs[5 * num_nodes:6 * num_nodes, :] += [-1.0, 0.0]
    nlocs[6 * num_nodes:7 * num_nodes, :] += [0.0, 0.0]
    nlocs[7 * num_nodes:8 * num_nodes, :] += [1.0, 0.0]
    nlocs[8 * num_nodes:9 * num_nodes, :] += [-1.0, 0.0]
    nlocs[0 * num_nodes:1 * num_nodes, :] += [0.0, 0.0]
    nlocs[1 * num_nodes:2 * num_nodes, :] += [0.0, 0.0]
    nlocs[2 * num_nodes:3 * num_nodes, :] += [0.0, 0.0]
    nlocs[3 * num_nodes:4 * num_nodes, :] += [-0.5, 0.86603]
    nlocs[4 * num_nodes:5 * num_nodes, :] += [-0.5, 0.86603]
    nlocs[5 * num_nodes:6 * num_nodes, :] += [-0.5, 0.86603]
    nlocs[6 * num_nodes:7 * num_nodes, :] += [0.5, -0.86603]
    nlocs[7 * num_nodes:8 * num_nodes, :] += [0.5, -0.86603]
    nlocs[8 * num_nodes:9 * num_nodes, :] += [0.5, -0.86603]
    distgrid = spspd.squareform(spspd.pdist(nlocs))
    nborlist = np.argsort(distgrid, axis=1)

    outbytes = io.BytesIO()
    for k1 in range(num_nodes):
        for k2 in range(1, 31):
            if distgrid.shape[0] > k2:
                tnode = int(np.mod(nborlist[k1, k2], num_nodes)) + 1
            else:
                tnode = 0
            # end-if
            outbytes.write(tnode.to_bytes(4, byteorder='little'))
        # end-k2
        for k2 in range(1, 31):
            if distgrid.shape[0] > k2:
                idnode = nborlist[k1, k2]
                tnode = int(np.mod(nborlist[k1, k2], num_nodes))
                migrat = mrcoeff * npops[tnode] / np.sum(npops) / (distgrid[k1, idnode])
                val = np.array([migrat], dtype=np.float64)
            else:
                val = np.array([0.0], dtype=np.float64)
            # end-if
            outbytes.write(val.tobytes())
        # end-k2
    # end-k1
    with open(os.path.join(dir, 'regional_migration_%0.4f.bin' % mrcoeff), 'wb') as fid01:
        fid01.write(outbytes.getvalue())

# end-demographicsBuilder

# *******************************************************************************