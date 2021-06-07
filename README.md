# selvaraj_spatial_covid_vax_2021

Please see README files in each subdirectory for description of files and how to run simulations.

Requirements: 
dtk-tools package. This is available upon request from support@idmod.org

COMPS system for HPC job management Email support@idmod.org

Code to analyze completed simulations is in ./analyzers.

Code to build model input files is in ./build_input_files.

Data for contact matrices and age pyramids are in ./data_input.

Executable and model parameter schema are in ./exe.

Plotting code is in ./plotting.

run_age_priority_vaccine_sims.py - creates and runs simulations for different age prioritization scenarios.

run_baseline_all_combos.py - creates and runs simulations for baseline scenarios with different R0 and migration rates.

run_coverage_timing_comparison.py - creates and runs simulations to evaluate trade off between coverage and timing of vaccine deployment.

run_spatial_priority_vaccine_sims.py - creates and runs simulations for different spatial prioritization schemes for vaccine distribution (random, urban first, rural first)