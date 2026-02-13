import pandas as pd
from YLL_LE_Age_calc import *

# Common directory paths
base_path = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/'
hm_output_path = base_path + 'HM/HM Output/Bootstrap/Bootstrap PM - optimism corrected/'
cost_effectiveness_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'
Input_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'
Ouput_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/'

# Read data
booststrap_pred_data = pd.read_csv(hm_output_path + 'HM_bootstrap_calibrated_predictions.csv')
mainpm_pred_data = pd.read_csv(hm_output_path + 'HM_mainPM_calibrated_predictions.csv')
prob_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'Probabilities')
cost_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'Costs')
dalyweight_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'DALY Weight')
dalylength_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'DALY Lenght')
LE_data = pd.read_csv(cost_effectiveness_path + 'LE_Moldova.csv')

# Constants
GDP_moldova = 5714.43
LE_2019_Moldova = 70.94
FLQ_Res_prev = 1 - 0.812963

# DALY calculation for each individual in the dataset
DALY_individual_Moldova = []

for i in range(len(mainpm_pred_data['age'])):
    age_s = classify_age(mainpm_pred_data['age'].iloc[i])
    sex_s = mainpm_pred_data['sex'].iloc[i]
    DALY_individual_Moldova.append(filter_dataframe(LE_data, sex_s, age_s, 2019))

# # DALY calculation for each individual in the dataset
# DALY_individual_Moldova = [max(0, LE_2019_Moldova - age) for age in pred_data['age']]


if __name__ == "__main__":

    print('Length of the DALY_individual_Moldova:', len(DALY_individual_Moldova))
    print(DALY_individual_Moldova[64])