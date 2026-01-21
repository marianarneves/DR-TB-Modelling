from DR_TB_XTree_parsample import *

np.random.seed(5)

# WTP
# wtp = np.arange(2, 3, 0.5) * GDP_moldova
wtp = 1. * GDP_moldova

# Number of parameter samples
par_samplesize = 10

sampler = ParameterSampler(cost_data_prior, dalyweight_data, dalylength_data, nsamples=par_samplesize)

# Sampling from the prior costs
cost_sampled_par = sampler.sample_cost_parameters()
# Sampling from the prior daly weights
dalyweight_sampled_par = sampler.sample_dalyweight_parameters()
# Sampling from the prior daly length
dalylength_sampled_par = sampler.sample_dalylength_parameters()

############ Preliminary Costs and DALY Calculation ############
# Calculated expected costs and DALYs for ach treatment depending on FLQ susceptibility
preliminary_daly_costs = calculate_pre_daly_cost_s(pred_data, DALY_individual_Moldova, prob_data, cost_sampled_par,
                                                   dalyweight_sampled_par, dalylength_sampled_par,
                                                   wtp, par_samplesize)
############ End Preliminary Costs and ############

PMDT_sampled = dr_tb_pmdt_s(sens_spec_PM, pred_data, DALY_individual_Moldova, preliminary_daly_costs, prob_data,
                            cost_sampled_par,
                            dalyweight_sampled_par,
                            dalylength_sampled_par, wtp, par_samplesize=par_samplesize)

# Create a dynamic file path
file_path_PMDT_sampled = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Tests/Test parameter sampling/' + f'testoopcomp.xlsx'
# Save the DataFrame to an Excel file
PMDT_sampled.to_excel(
    file_path_PMDT_sampled,
    index=False)

#
# par_samplesize = 10
# sampler = ParameterSampler(cost_data_prior, dalyweight_data, dalylength_data, nsamples=par_samplesize)
#
# i = 2
#
# for wtp_value in wtp:  # Use a different variable name here
#     print(wtp_value)
#     # Sampling from the prior costs
#     cost_sampled_par = sampler.sample_cost_parameters()
#     # Sampling from the prior daly weights
#     dalyweight_sampled_par = sampler.sample_dalyweight_parameters()
#     # Sampling from the prior daly length
#     dalylength_sampled_par = sampler.sample_dalylength_parameters()
#
#     ############ Preliminary Costs and DALY Calculation ############
#     # Calculated expected costs and DALYs for each treatment depending on FLQ susceptibility
#     preliminary_daly_costs = calculate_pre_daly_cost_s(pred_data, DALY_individual_Moldova, prob_data, cost_sampled_par,
#                                                        dalyweight_sampled_par, dalylength_sampled_par,
#                                                        wtp_value, par_samplesize)
#     ############ End Preliminary Costs and ############
#
#     PMDT_sampled = dr_tb_pmdt_s(sens_spec_PM, pred_data, DALY_individual_Moldova, preliminary_daly_costs, prob_data,
#                                 cost_sampled_par,
#                                 dalyweight_sampled_par,
#                                 dalylength_sampled_par, wtp_value, par_samplesize=par_samplesize)
#
#     # Create a dynamic file path
#     file_path_PMDT_sampled = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Tests/Test parameter sampling/' + f'PMDT_10samples_wtp{i}test.xlsx'
#     # Save the DataFrame to an Excel file
#     PMDT_sampled.to_excel(
#         file_path_PMDT_sampled,
#         index=False)
#
#     i += 1