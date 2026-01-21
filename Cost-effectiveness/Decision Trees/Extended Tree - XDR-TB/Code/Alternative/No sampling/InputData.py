
from YLL_LE_Age_calc import *


# Common directory paths
base_path = '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/'
hm_output_path = base_path + 'HM/HM Output/'
cost_effectiveness_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'

# Read data
pred_data = pd.read_csv(hm_output_path + 'pred_obs_calibrated_model.csv')
cost_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptionsA.xlsx', 'Costs')
daly_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptionsA.xlsx', 'DALY')
LE_data = pd.read_csv(cost_effectiveness_path + 'LE_Moldova.csv')
prob_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptionsA.xlsx', 'Probabilities')
sens_spec_PM = hm_output_path + 'sens_spec_calibrated_model.csv'

# # Read probabilities, costs, and DALYs
# for index, row in prob_data.iterrows():
#     globals()[row['Probability Variable']] = row['Probability Value']
#
# for index, row in cost_data.iterrows():
#     globals()[row['Cost Variable']] = row['Cost Value']
#
# for index, row in daly_data.iterrows():
#     globals()[row['DALY Variable']] = row['DALY Value']

# Constants
GDP_moldova = 5714.43
LE_2019_Moldova = 70.94
FLQ_Res_prev = 1 - 0.812963

#Willingness to pay
wtp = GDP_moldova

# DALY calculation for each individual in the dataset
DALY_individual_Moldova = []

for i in range(len(pred_data['age'])):
    age_s = classify_age(pred_data['age'].iloc[i])
    sex_s = pred_data['sex'].iloc[i]
    DALY_individual_Moldova.append(filter_dataframe(LE_data, sex_s, age_s, 2019))

# # DALY calculation for each individual in the dataset
# DALY_individual_Moldova = [max(0, LE_2019_Moldova - age) for age in pred_data['age']]


if __name__ == "__main__":

    print('Length of the DALY_individual_Moldova:', len(DALY_individual_Moldova))
    print(DALY_individual_Moldova[64])