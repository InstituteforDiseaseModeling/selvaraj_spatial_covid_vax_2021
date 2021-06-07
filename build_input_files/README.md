aux_matrix_calc.py contains functions for creating normalized contact matrices 

builder_campaign.py contains functions for each campaign type (e.g. change in contact matrices due to govt. policies, 
acquisition or disease blocking vaccine distribution, age appropriate tranmission multipliers) 

builder_config.py contains default config param values

builder_demographics.py contains functions for building the demographics and migration files

helper_functions.py has functions to create a simulation based on different param values from a sweep as well as to 
write out a campaign file specific to that simulation

refdat_age_pyr.py contains a function to calculate the age pyramid of all the countries in the country list provided

refdat_contact_mat.py contains a function to calculate the median contact matrix for all the countries listed

refdat_policy_effect.py contains a function to calculate multipliers for the contact matrices depending on govt. policies
in place. This data was obtained from https://www.bsg.ox.ac.uk/research/research-projects/coronavirus-government-response-tracker
 
refdat_vaccine_dist.py contains a function to distribute vaccines per the COVAX timeline. This data was obtained from 
https://www.gavi.org/news/document-library/covax-global-supply-forecast