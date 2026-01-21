import sys
import numpy as np
import pandas as pd

# Add each folder to the system path
sys.path.append('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Code/Main/Optimism correction')

from YLL_LE_Age_calc import *
from SampleParameters import *

np.random.seed(5)

# Add each folder to the system path
sys.path.append('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Code/Main/Optimism correction')

# Common directory paths
base_path = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/'
hm_output_path = base_path + 'LR/Output/Optimism Corrected/'
cost_effectiveness_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'
Input_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'
Output_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/'

# Read data

#Data containing age
mainpm_pred_data = pd.read_csv(hm_output_path + 'LR_MainPM_BetaCalibration.csv')

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
wtp_value = 1 * GDP_moldova

# DALY calculation for each individual in the dataset
DALY_individual_Moldova = []

for i in range(len(mainpm_pred_data['age'])):
    age_s = classify_age(mainpm_pred_data['age'].iloc[i])
    sex_s = mainpm_pred_data['sex'].iloc[i]
    DALY_individual_Moldova.append(filter_dataframe(LE_data, sex_s, age_s, 2019))

par_samplesize = 200
par_sampler = ParameterSampler(FLQ_Res_prev, prob_data_prior, cost_data_prior, dalyweight_data_prior,
                               dalylength_data_prior, sideeffectdaly_data_prior, sideeffectfreq_data_prior,
                               sideeffectlength_data_prior, nsamples=par_samplesize)

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
