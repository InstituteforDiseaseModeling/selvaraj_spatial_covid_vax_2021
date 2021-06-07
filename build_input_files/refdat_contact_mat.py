import numpy as np
import rdata
import os

cm_direc = os.path.join('data_input', 'prem_contact_matrices')

country_short = {'Angola': 'AGO', 'Benin': 'BEN', 'Botswana': 'BWA', 'Burkina Faso': 'BFA', 'Burundi': 'BDI',
                 'Cameroon': 'CMR', 'Central African Republic': 'CAF', 'Chad': 'TCD', 'Ivory Coast': 'CIV',
                 'DRC': 'COD', 'Eritrea': 'ERI', 'Ethiopia': 'ETH', 'Gabon': 'GAB', 'Gambia': 'GMB', 'Ghana': 'GHA',
                 'Guinea': 'GIN', 'Guinea-Bissau': 'GNB', 'Kenya': 'KEN', 'Lesotho': 'LSO', 'Liberia': 'LBR',
                 'Madagascar': 'MDG', 'Malawi': 'MWI', 'Mali': 'MLI', 'Mauritania': 'MRT', 'Mozambique': 'MOZ',
                 'Namibia': 'NAM', 'Niger': 'NER', 'Nigeria': 'NGA', 'Rwanda': 'RWA', 'Senegal': 'SEN',
                 'Sierra Leone': 'SLE', 'South Africa': 'ZAF', 'Tanzania': 'TZA', 'Togo': 'TGO', 'Uganda': 'UGA',
                 'Zambia': 'ZMB', 'Zimbabwe': 'ZWE'}


def find_median_contact_matrix(arg_key=str(), countries: list = None, area='Rural'):

    cm_home = np.zeros((16, 16, len(countries)))
    cm_school = np.zeros((16, 16, len(countries)))
    cm_work = np.zeros((16, 16, len(countries)))
    cm_community = np.zeros((16, 16, len(countries)))

    parsed = rdata.parser.parse_file(os.path.join(cm_direc, area, 'contact_home_%s.rdata' % area.lower()))
    wb_home = rdata.conversion.convert(parsed)
    parsed = rdata.parser.parse_file(os.path.join(cm_direc, area, 'contact_school_%s.rdata' % area.lower()))
    wb_school = rdata.conversion.convert(parsed)
    parsed = rdata.parser.parse_file(os.path.join(cm_direc, area, 'contact_work_%s.rdata' % area.lower()))
    wb_work = rdata.conversion.convert(parsed)
    parsed = rdata.parser.parse_file(os.path.join(cm_direc, area, 'contact_others_%s.rdata' % area.lower()))
    wb_community = rdata.conversion.convert(parsed)

    for i, country in enumerate(countries):
        country = country_short[country]
        cm01_home = wb_home['contact_home'][country]
        cm01_school = wb_school['contact_school'][country]
        cm01_work = wb_work['contact_work'][country]
        cm01_community = wb_community['contact_others'][country]

        cm_home[:, :, i] = cm01_home
        cm_work[:, :, i] = cm01_work
        cm_school[:, :, i] = cm01_school
        cm_community[:, :, i] = cm01_community

    cm_home = np.mean(cm_home, axis=2)
    cm_work = np.mean(cm_work, axis=2)
    cm_school = np.mean(cm_school, axis=2)
    cm_community = np.mean(cm_community, axis=2)

    mat_home = dict()
    mat_work = dict()
    mat_school = dict()
    mat_community = dict()
    mat_home['AFRO:REP'] = cm_home
    mat_work['AFRO:REP'] = cm_work
    mat_school['AFRO:REP'] = cm_school
    mat_community['AFRO:REP'] = cm_community

    narg_key1 = arg_key
    while len(narg_key1) > 0 and narg_key1 not in mat_home:
        narg_key1 = narg_key1.rsplit(':', 1)[0]

    return mat_home[narg_key1], mat_work[narg_key1], mat_school[narg_key1], mat_community[narg_key1]