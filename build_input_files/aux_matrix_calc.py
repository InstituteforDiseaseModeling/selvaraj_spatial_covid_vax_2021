"""
Prashanth Selvaraj
Apr 2021
"""

from vaccine_efficacy_article.build_input_files.refdat_contact_mat import find_median_contact_matrix
from vaccine_efficacy_article.build_input_files.refdat_age_pyr import find_age_pyramid
import numpy as np


# ********************************************************************************

def mat_magic(params: dict = None, area='Rural'):
    arg_dist = params['arg_dist'][0]
    ctext_val = params['ctext_val'][0]
    countries = params['countries']

    # Distribution of R0 (must be normalized)
    R0x = [0.35, 0.50, 0.15]  # New style
    R0y = [3.0 / 5.0, 1.0, 29.0 / 15.0]

    # Age pyramid
    (age_rng, age_pyr) = find_age_pyramid(arg_key=ctext_val, countries=countries, area=area)

    # Unscaled contact matrices
    mat_home, mat_work, mat_school, mat_community = find_median_contact_matrix(ctext_val, countries=countries, area=area)

    # Linear algebra, the best kind of algebra
    age_pyr = np.array(age_pyr)

    # Calculate HINT matrix with distancing
    mat_tot = arg_dist[0] * mat_home + arg_dist[1] * mat_work + arg_dist[2] * mat_school + arg_dist[3] * mat_community

    # Calculate R0 normalization value
    R0_ref = np.dot(np.dot(age_pyr, mat_tot), age_pyr)

    # Category labels
    names_big = list()
    names_big.extend(['age{:02d}_riskLO'.format(k1) for k1 in age_rng])
    names_big.extend(['age{:02d}_riskMD'.format(k1) for k1 in age_rng])
    names_big.extend(['age{:02d}_riskHI'.format(k1) for k1 in age_rng])

    # Category fractions
    age_big = np.hstack((R0x[0] * age_pyr, R0x[1] * age_pyr, R0x[2] * age_pyr))

    # Tile matrix
    mat_tall = np.tile(mat_tot, (3, 1))
    mat_big = np.hstack((R0y[0] * mat_tall, R0y[1] * mat_tall, R0y[2] * mat_tall)) / R0_ref

    # Diagnostics
    # print(np.dot(np.dot(age_big,mat_big),age_big))

    return (age_big, names_big, mat_big)
