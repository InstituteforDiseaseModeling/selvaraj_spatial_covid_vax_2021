import numpy as np

from vaccine_efficacy_article.build_input_files.refdat_age_pyr import find_age_pyramid


def vaccine_availability_by_month(covax_distribution=True, coverage=0, **kwargs):

    if covax_distribution:

        cumulative_vax = [1, 39, 88, 131, 198, 385, 582, 775, 961, 1233, 1501, 1768]
        monthly_vax = [cumulative_vax[0]] + [cumulative_vax[i + 1] - cumulative_vax[i] for i in
                                             range(0, len(cumulative_vax) - 1)]
        monthly_vax_percentage = [mv / sum(monthly_vax) for mv in monthly_vax]
        monthly_vax_percentage_adjusted = [0]*12
        monthly_vax_percentage_adjusted[0] = monthly_vax_percentage[0]
        for i in range(1, 12):
            monthly_vax_percentage_adjusted[i] = monthly_vax_percentage[i]/(1-sum(monthly_vax_percentage[:i]))
        cumulative_monthly_vax_percentage = np.array([cv / sum(monthly_vax) for cv in cumulative_vax])

        distribution_date = [i for i in range(0, 334, 30)]

        if 'params' in kwargs:
            params = kwargs.pop('params', False)
            frac_rural = params['frac_rural'][0]

            cumulative_monthly_vax_percentage[:] *= coverage

            ctext_val = params['ctext_val'][0]
            countries = params['countries']

            (age_rng, age_pyr) = find_age_pyramid(arg_key=ctext_val, countries=countries)
            age_index = age_rng.index(min(params['target_groups'][0]))

            age_pyr = [a / sum(age_pyr[age_index:]) for a in age_pyr[age_index:]]
            age_rng = age_rng[age_index:]

            target_groups = params['target_groups'][0]
            target_groups_indices = [age_rng.index(tg) for tg in target_groups]
            new_age_pyr = [0] * len(target_groups)

            for i in range(len(target_groups_indices)):
                if len(target_groups_indices) > 1:
                    if target_groups_indices[1] > target_groups_indices[0]:
                        if i < len(target_groups_indices) - 1:
                            new_age_pyr[i] = sum(age_pyr[target_groups_indices[i]:target_groups_indices[i + 1]])
                        else:
                            new_age_pyr[i] = sum(age_pyr[target_groups_indices[i]:])
                    else:
                        if i == 0:
                            new_age_pyr[i] = sum(age_pyr[target_groups_indices[i]:])
                        else:
                            new_age_pyr[i] = sum(age_pyr[target_groups_indices[i]:target_groups_indices[i - 1]])
                else:
                    new_age_pyr[i] = sum(age_pyr[target_groups_indices[i]:])

            new_age_pyr = list(reversed(new_age_pyr))

            final_age_coverages = np.zeros((len(new_age_pyr), 12))
            for i, nap in enumerate(new_age_pyr):
                age_coverage, cumulative_monthly_vax_percentage = \
                    age_cumulative_coverage(cumulative_monthly_vax_percentage=cumulative_monthly_vax_percentage,
                                            divisor=nap)

                final_age_coverages[i, :] = age_coverage

            if params['urban_prioritization'][0]:
                if params['urban_prioritization'][0] == 1:
                    urban_divisor = 1 - frac_rural

                elif params['urban_prioritization'][0] == 2:
                    urban_divisor = frac_rural

                else:
                    urban_divisor = 1

                final_geo_coverages = np.zeros((len(new_age_pyr) * 2, 12))
                for i, nap in enumerate(new_age_pyr):
                    first_loc_coverage, second_loc_coverage = \
                        geo_cumulative_coverage(cumulative_monthly_vax_percentage=final_age_coverages[i, :],
                                                divisor=urban_divisor)

                    final_geo_coverages[i * 2] = first_loc_coverage
                    final_geo_coverages[i * 2 + 1] = second_loc_coverage

                return final_geo_coverages, distribution_date

            else:
                return final_age_coverages, distribution_date

    else:
        cumulative_monthly_vax_percentage = np.array([1])
        distribution_date = [0]

    return cumulative_monthly_vax_percentage, distribution_date


def age_cumulative_coverage(cumulative_monthly_vax_percentage, divisor):
    coverage = np.array([cmvp / divisor
                             for cmvp in cumulative_monthly_vax_percentage])
    item = next((x for x in coverage if x > 1.0), None)
    if item:
        index = np.where(coverage == item)[0][0]
        cumulative_monthly_vax_percentage[index:] = cumulative_monthly_vax_percentage[index:] - divisor
        cumulative_monthly_vax_percentage[:index] = 0
        coverage[coverage > 1.0] = 1.0
    else:
        cumulative_monthly_vax_percentage[:] = 0

    return coverage, cumulative_monthly_vax_percentage


def geo_cumulative_coverage(cumulative_monthly_vax_percentage, divisor):
    coverage = np.array([cmvp / divisor
                             for cmvp in cumulative_monthly_vax_percentage])
    second_loc_coverage = coverage.copy()
    item = next((x for x in coverage if x > 1.0), None)
    if item:
        index = np.where(coverage == item)[0][0]
        second_loc_coverage[coverage < 1.0] = 0
        second_loc_coverage[index:] = (np.array(cumulative_monthly_vax_percentage)[index:] - divisor) / (1 - divisor)
        coverage[coverage > 1.0] = 1.0
    else:
        second_loc_coverage[:] = 0

    return coverage, second_loc_coverage

