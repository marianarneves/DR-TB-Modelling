from DR_TB_XTree_parsample import *

np.random.seed(5)

# WTP
wtp = np.arange(0.5, 3.5, 0.5) * GDP_moldova
i = 1

par_samplesize = 500
par_sampler = ParameterSampler(FLQ_Res_prev, cost_data_prior, dalyweight_data, dalylength_data, nsamples=par_samplesize)
pm_performance = PMPerformance(booststrap_pred_data, par_sampler)

# Sampling from the prior costs
cost_sampled_par = par_sampler.sample_cost_parameters()
# Sampling from the prior daly weights
dalyweight_sampled_par = par_sampler.sample_dalyweight_parameters()
# Sampling from the prior daly length
dalylength_sampled_par = par_sampler.sample_dalylength_parameters()
# Sampling from the prior disease prevalence
diseaseprev_sampled_par = par_sampler.sample_disease_prevalence()

# Generate the sequence from 0 to 1 with a step of 0.0025
threshold_values = np.arange(0, 1.0025, 0.0025)

# Create the DataFrame
allthresholds = pd.DataFrame({'threshold': threshold_values})

for wtp_value in wtp:  # Use a different variable name here

    start_time_wtp = time.time()

    drtb_instance = DRTuberculosisDT(par_sampler, DALY_individual_Moldova, pm_performance, mainpm_pred_data, diseaseprev_sampled_par, prob_data, cost_sampled_par, dalyweight_sampled_par, dalylength_sampled_par, par_samplesize, wtp_value)

    ############ Preliminary Costs and DALY Calculation ############
    # Calculated expected costs and DALYs for each treatment depending on FLQ susceptibility
    preliminary_daly_costs = calculate_pre_daly_cost_s(par_sampler, mainpm_pred_data, DALY_individual_Moldova, diseaseprev_sampled_par, prob_data, cost_sampled_par,
                                                       dalyweight_sampled_par, dalylength_sampled_par,
                                                       wtp_value, par_samplesize)

    ############ End Preliminary Costs and ############

    PMDT_sampled = drtb_instance.dr_tb_pmdt_s(allthresholds, DALY_individual_Moldova, preliminary_daly_costs)

    # Create a dynamic file path
    file_path_PMDT_sampled = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Tests/Test PM bootstrapping/500 samples - parallel/' + f'PMDT_1000_wtp{i}_bootstrapping_calpred.xlsx'
    # Save the DataFrame to an Excel file
    PMDT_sampled.to_excel(
        file_path_PMDT_sampled,
        index=False)

    elapsed_time_wtp = time.time() - start_time_wtp
    print(f"WTP {i} done. Total WTP running time: {elapsed_time_wtp / 60:.2f} minutes.")

    i+=1

