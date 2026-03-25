from DR_TB_XTree import *

np.random.seed(5)

par_samplesize = 200
par_sampler = ParameterSampler(FLQ_Res_prev, prob_data_prior, cost_data_prior, dalyweight_data_prior,
                               dalylength_data_prior, sideeffectdaly_data_prior, sideeffectfreq_data_prior,
                               sideeffectlength_data_prior, nsamples=par_samplesize)

preliminary_DALY = Preliminary_DALY(mainpm_pred_data, LE_data)

# DALY_individual_Moldova = [
#     0 if age > LE_2019_Moldova else LE_2019_Moldova - age
#     for age in mainpm_pred_data['age']
# ]

print(DALY_individual_Moldova)
#DALY_individual_Moldova = preliminary_DALY.compute_daly_individual()

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
print(f"Parameter sampling concluded.")

# # Generate the sequence from 0 to 1 with a step of 0.0025
# threshold_values = np.arange(0, 1.0025, 0.0025)

mainpm_pred_data_sorted = mainpm_pred_data.sort_values(by='predicted').reset_index(drop=True)

# Calculate the average of two consecutive values in the sorted 'prediction' column
threshold_values = (mainpm_pred_data_sorted['predicted'].shift(-1) + mainpm_pred_data_sorted['predicted']) / 2
# Drop the last NaN value caused by the shift
threshold_values = threshold_values.dropna().reset_index(drop=True)

# Create the DataFrame
allthresholds = pd.DataFrame({'threshold': threshold_values})
print(allthresholds)

# WTP
wtp = np.arange(0.5, 3.5, 0.5) * GDP_moldova
i = 1

start_time_wtp = time.time()

for wtp_value in wtp:

    # for wtp_value in wtp:  # Use a different variable name here
    #wtp_value = GDP_moldova

    start_time_wtp = time.time()

    drtb_instance = DRTuberculosisDT(par_sampler, DALY_individual_Moldova, pm_performance, mainpm_pred_data, diseaseprev_sampled_par, prob_sampled_par, cost_sampled_par, dalyweight_sampled_par, dalylength_sampled_par, sideeffectdaly_sampled_par, sideeffectfreq_sampled_par, sideeffectlength_sampled_par, par_samplesize, wtp_value,random_seed)

    ############ Preliminary Costs and DALY Calculation ############
    # Calculated expected costs and DALYs for each treatment depending on FLQ susceptibility
    preliminary_daly_costs = preliminary_DALY.calculate_pre_daly_cost_s(par_sampler, mainpm_pred_data, DALY_individual_Moldova, diseaseprev_sampled_par, prob_sampled_par, cost_sampled_par,
                                           dalyweight_sampled_par, dalylength_sampled_par,
                                        sideeffectdaly_sampled_par,
                                                       sideeffectfreq_sampled_par,
                                                       sideeffectlength_sampled_par,
                                           wtp_value, par_samplesize)

############ End Preliminary Costs and ############

    ### Calibrated
    # PMDT - Platt Calibration - Adjusted method
    # PMDT_sampled = drtb_instance.dr_tb_pmdt_s_opt(allthresholds, DALY_individual_Moldova, preliminary_daly_costs, correction = "OptCorr_Adj")
    # file_path_PMDT_sampled = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM Boostrap/Optimism Correction/Adjusted/Test/' + f'PMDT_wtp{i}bootstrapping_samplesize200.xlsx'

    # PMDT - Beta Calibration - Adjusted method
    # PMDT_sampled = drtb_instance.dr_tb_pmdt_s_opt(allthresholds, DALY_individual_Moldova, preliminary_daly_costs, correction = "OptCorr_Adj")
    # file_path_PMDT_sampled = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/Input_V10/' + f'PMDT_wtp{i}bootstrapping_samplesize200.xlsx'

    # PM input Only - Platt Calibration
    # PMDT_sampled = drtb_instance.dr_tb_pmdt_predonly(DALY_individual_Moldova, preliminary_daly_costs)
    # file_path_PMDT_sampled = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/' + f'PMDT_wtp{i}bootstrapping_samplesize200.xlsx'

    # PM input Only - Beta Calibration
    # PMDT_sampled = drtb_instance.dr_tb_pmdt_predonly(DALY_individual_Moldova, preliminary_daly_costs)
    # file_path_PMDT_sampled = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM input Only/Input_V10/' + f'PMDT_wtp{i}bootstrapping_samplesize200_modLE.xlsx'

    # PMDT - Platt Calibration- Method 632
    # PMDT_sampled = drtb_instance.dr_tb_pmdt_s_opt(allthresholds, DALY_individual_Moldova, preliminary_daly_costs, corr
    # ection = "Method632")
    # file_path_PMDT_sampled = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/Method 632/' + f'PMDT_wtp{i}bootstrapping_samplesize200.xlsx'

    # PM without DM - Platt Calibration
    # PMDT_sampled = drtb_instance.dr_tb_pm_s(allthresholds, DALY_individual_Moldova, preliminary_daly_costs)
    # file_path_PMDT_sampled = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM without DM/Test/' + f'PMDT_wtp{i}bootstrapping_samplesize200.xlsx'

    # PM without DM - Beta Calibration
    # PMDT_sampled = drtb_instance.dr_tb_pm_s(allthresholds, DALY_individual_Moldova, preliminary_daly_costs)
    # file_path_PMDT_sampled = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM without DM/Input_V10/' + f'PMDT_wtp{i}bootstrapping_samplesize200.xlsx'

    # DT without PM
    # PMDT_sampled = drtb_instance.dr_tb_dt_s(preliminary_daly_costs, DALY_individual_Moldova)
    # file_path_PMDT_sampled = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/DT Only/Input_V10/' + f'DT_wtp{i}bootstrapping_samplesize200.xlsx'


    ### Not Calibrated

    # PMDT - No Calibration - Adjusted method
    # PMDT_sampled = drtb_instance.dr_tb_pmdt_s_opt(allthresholds, DALY_individual_Moldova, preliminary_daly_costs, correction = "OptCorr_Adj")
    # file_path_PMDT_sampled = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM Bootstrap/Input_V10/' + f'PMDT_wtp{i}bootstrapping_samplesize200.xlsx'

    # PM input Only - No Calibration
    # PMDT_sampled = drtb_instance.dr_tb_pmdt_predonly(DALY_individual_Moldova, preliminary_daly_costs)
    # file_path_PMDT_sampled = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM input Only/Input_V10/' + f'PMDT_wtp{i}bootstrapping_samplesize200.xlsx'

    # PM input Only - No Calibration
    # PMDT_sampled = drtb_instance.dr_tb_pmdt_predonly(DALY_individual_Moldova, preliminary_daly_costs)
    # file_path_PMDT_sampled = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM input Only/Input_V10/ModLE/' + f'PMDT_wtp{i}bootstrapping_samplesize200_ModLE.xlsx'

    # # PM without DM - No Calibration
    # PMDT_sampled = drtb_instance.dr_tb_pm_s(allthresholds, DALY_individual_Moldova, preliminary_daly_costs)
    # file_path_PMDT_sampled = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM without DM/Input_V10/' + f'PMDT_wtp{i}bootstrapping_samplesize200.xlsx'



    # Save the DataFrame to an Excel file
    PMDT_sampled.to_excel(
        file_path_PMDT_sampled,
        index=False)

    elapsed_time_wtp = time.time() - start_time_wtp
    print(f"WTP {i} done. Total WTP running time: {elapsed_time_wtp / 60:.2f} minutes.")

    i += 1
