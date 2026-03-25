import pandas as pd
from YLL_LE_Age_calc import *

# Common directory paths
base_path = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/'
hm_output_path = base_path + 'LR/Output/Optimism Corrected/'
cost_effectiveness_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'
Input_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'
Output_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/'

# Read data

#Platt Calibration
# booststrap_pred_data = pd.read_csv(hm_output_path + 'LR_bootstrap_PlattCalibration.csv')
# mainpm_pred_data = pd.read_csv(hm_output_path + 'LR_MainPM_PlattCalibration.csv')
#Beta Calibration
# booststrap_pred_data = pd.read_csv(hm_output_path + 'LR_bootstrap_BetaCalibration.csv')
# mainpm_pred_data = pd.read_csv(hm_output_path + 'LR_MainPM_BetaCalibration.csv')
# #No Calibration
booststrap_pred_data = pd.read_csv(hm_output_path + 'LR_bootstrap_nocalibration.csv')
mainpm_pred_data = pd.read_csv(hm_output_path + 'LR_MainPM_nocalibration.csv')

prob_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_assumptions_V10.xlsx', 'Probabilities')
cost_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_assumptions_V10.xlsx', 'Costs')
dalyweight_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_assumptions_V10.xlsx', 'DALY Weight')
dalylength_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_assumptions_V10.xlsx', 'DALY Length')
sideeffectdaly_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_assumptions_V10.xlsx', 'Side Effects DALY')
sideeffectfreq_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_assumptions_V10.xlsx', 'Side Effects Frequency')
sideeffectlength_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_assumptions_V10.xlsx', 'Side Effects Length')

LE_data = pd.read_csv(cost_effectiveness_path + 'LE_Moldova.csv')

# Constants
GDP_moldova = 5714.43
LE_2019_Moldova = 70.94
FLQ_Res_prev = 1 - 0.812963