from DR_TB_XTree import *

# Constants
GDP_moldova = 5714.43
FLQ_Res_prev = 1 - 0.812963


## YLL_LE
externaldata = pd.read_csv('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/DT Only/Input_V10/Test age x NMB/PIDEMp/YLLcontinuous_input.csv')


#Testing the relationship between age and optimal treatment
#YLL Continuous
# DALY_individual_Moldova = list(range(101)) * 2
# YLL_LE
DALY_individual_Moldova = [
    0 if age > LE_2019_Moldova else LE_2019_Moldova - age
    for age in externaldata['age']
]

preliminary_DALY = Preliminary_DALY(mainpm_pred_data, LE_data)

# WTP
wtp_value = 1 * GDP_moldova

i = 1

par_samplesize = 200
par_sampler = ParameterSampler(FLQ_Res_prev, prob_data_prior, cost_data_prior, dalyweight_data_prior,
                               dalylength_data_prior, sideeffectdaly_data_prior, sideeffectfreq_data_prior,
                               sideeffectlength_data_prior, nsamples=par_samplesize)
pm_performance = PMPerformance(mainpm_pred_data, booststrap_pred_data, par_sampler)

print(f"Parameter sampling starts.")
# Sampling from the prior probabilities
prob_sampled_par = par_sampler.sample_prob_parameters()
# Sampling from the prior costs
cost_sampled_par = par_sampler.sample_cost_parameters()
# Sampling from the prior daly weights
dalyweight_sampled_par = par_sampler.sample_dalyweight_parameters()
# Sampling from the prior daly length
dalylength_sampled_par = par_sampler.sample_dalylength_parameters()
# Sampling from the prior disease prevalence
diseaseprev_sampled_par = par_sampler.sample_disease_prevalence()
# Sampling from the prior daly weights
sideeffectdaly_sampled_par = par_sampler.sample_sideeffectdaly_parameters()
# Sampling from the prior daly length
sideeffectfreq_sampled_par = par_sampler.sample_sideeffectfreq_parameters()
# Sampling from the prior disease prevalence
sideeffectlength_sampled_par = par_sampler.sample_sideeffectlength_parameters()
print(f"Parameter sampling finished.")


mainpm_pred_data_sorted = mainpm_pred_data.sort_values(by='predicted').reset_index(drop=True)

# Calculate the average of two consecutive values in the sorted 'prediction' column
threshold_values = (mainpm_pred_data_sorted['predicted'].shift(-1) + mainpm_pred_data_sorted['predicted']) / 2
# Drop the last NaN value caused by the shift
threshold_values = threshold_values.dropna().reset_index(drop=True)

# Create the DataFrame
allthresholds = pd.DataFrame({'threshold': threshold_values})

#YLL Continuous inputdata
#externaldata = pd.read_csv('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/DT Only/Input_V10/Test age x NMB/PIDEMc/MainPM_dummy_YLL_pos_neg.csv')

drtb_instance = DRTuberculosisDT(par_sampler, DALY_individual_Moldova, pm_performance, externaldata, diseaseprev_sampled_par, prob_sampled_par, cost_sampled_par, dalyweight_sampled_par, dalylength_sampled_par, sideeffectdaly_sampled_par, sideeffectfreq_sampled_par, sideeffectlength_sampled_par, par_samplesize, wtp_value)

############ Preliminary Costs and DALY Calculation ############
# Calculated expected costs and DALYs for each treatment depending on FLQ susceptibility
preliminary_daly_costs = preliminary_DALY.calculate_pre_daly_cost_s(par_sampler, externaldata, DALY_individual_Moldova, diseaseprev_sampled_par, prob_sampled_par, cost_sampled_par,
                                       dalyweight_sampled_par, dalylength_sampled_par,
                                       sideeffectdaly_sampled_par,
                                       sideeffectfreq_sampled_par,
                                       sideeffectlength_sampled_par,
                                       wtp_value, par_samplesize)


############ End Preliminary Costs and ############

PMDT_sampled = drtb_instance.dr_tb_dt_s(preliminary_daly_costs, DALY_individual_Moldova)

print("Column names individually:")
for col in PMDT_sampled.columns:
    print(col)

# # Export test file
file_path_PMDT_sampled = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/DT Only/Input_V10/Test age x NMB/PIDEMp/' + f'PIDEMp_YLLcontinuous_test_output_2.xlsx'
# Save the DataFrame to an Excel file
PMDT_sampled.to_excel(
    file_path_PMDT_sampled,
    index=False)
#
# ####
#
# PMDT_sampled = drtb_instance.dr_tb_pmdt_s_opt(allthresholds, DALY_individual_Moldova, preliminary_daly_costs,
#                                               correction="OptCorr_Adj")
#
# # # Export test file
# file_path_PMDT_sampled = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/DT Only/Input_V10/Test age x NMB/PIDEMc/' + f'PIDEMc_test_output.xlsx'
# # Save the DataFrame to an Excel file
# PMDT_sampled.to_excel(
#     file_path_PMDT_sampled,
#     index=False)