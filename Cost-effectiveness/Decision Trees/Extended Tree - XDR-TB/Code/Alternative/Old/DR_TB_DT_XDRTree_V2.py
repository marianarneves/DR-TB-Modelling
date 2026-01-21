import csv
import matplotlib.pyplot as plt
import pandas as pd
from DR_TB_Classes import *
import numpy as np

# Common directory paths
base_path = '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/'
hm_output_path = base_path + 'HM/HM Output/'
cost_effectiveness_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'

# Read data
pred_data = pd.read_csv(hm_output_path + 'pred_obs_calibrated_model.csv')
cost_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions.xlsx', 'Costs')
daly_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions.xlsx', 'DALY')
prob_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions.xlsx', 'Probabilities')
csv_file = hm_output_path + 'sens_spec_calibrated_model.csv'

# Read probabilities, costs, and DALYs
for index, row in prob_data.iterrows():
    globals()[row['Probability Variable']] = row['Probability Value']

for index, row in cost_data.iterrows():
    globals()[row['Cost Variable']] = row['Cost Value']

for index, row in daly_data.iterrows():
    globals()[row['DALY Variable']] = row['DALY Value']

# Constants
GDP_moldova = 5714.43
LE_2019_Moldova = 70.94
FLQ_Res_prev = 1 - 0.812963


############ Cost ############

# Terminal nodes - Costs
CC_FLQsus_cost = TerminalNode(name='CC_FLQsus_cost', cost=Cost_CC_FLQsus)
TF_FLQsus_cost = TerminalNode(name='TF_FLQsus_cost', cost=Cost_TF_FLQsus)
D_FLQsus_cost = TerminalNode(name='D_FLQsus_cost', cost=Cost_D_FLQsus)
CC_FLQres_cost = TerminalNode(name='CC_FLQres_cost', cost=Cost_CC_FLQres)
TF_FLQres_cost = TerminalNode(name='TF_FLQres_cost', cost=Cost_TF_FLQres)
D_FLQres_cost = TerminalNode(name='D_FLQres_cost', cost=Cost_D_FLQres)
CC_DLM_cost = TerminalNode(name='CC_DLM_cost', cost=Cost_CC_DLM)
TF_DLM_cost = TerminalNode(name='TF_DLM_cost', cost=Cost_TF_DLM)
D_DLM_cost = TerminalNode(name='D_DLM_cost', cost=Cost_D_DLM)

# Chance nodes - Costs
C_FLQsus_cost = ChanceNode(name='C_FLQsus_cost', cost=0, future_nodes=[CC_FLQsus_cost, TF_FLQsus_cost, D_FLQsus_cost],
                           probs=[Prob_CC_FLQsus, Prob_TF_FLQsus, Prob_D_FLQsus])
C_FLQres_cost = ChanceNode(name='C_FLQres_cost', cost=0, future_nodes=[CC_FLQres_cost, TF_FLQres_cost, D_FLQres_cost],
                           probs=[Prob_CC_FLQres, Prob_TF_FLQres, Prob_D_FLQres])
C_DLM_cost = ChanceNode(name='C_DLM_cost', cost=Cost_DLM, future_nodes=[CC_DLM_cost, TF_DLM_cost, D_DLM_cost],
                        probs=[Prob_CC_DLM, Prob_TF_DLM, Prob_D_DLM])

#Decision nodes and expected value - Costs

# FLQ Susceptible
# Chance Node
D_FLQ_sus_cost = DecisionNode(name='D_FLQ_sus_cost', cost=Cost_FLQ, future_nodes=[C_FLQsus_cost])
# Expected Costs
Exp_FLQ_sus_cost = D_FLQ_sus_cost.get_expected_costs()['C_FLQsus_cost']

# FLQ Resistant
# Chance Node
D_FLQ_res_cost = DecisionNode(name='D_FLQ_res_cost', cost=Cost_FLQ, future_nodes=[C_FLQres_cost])
# Expected Costs
Exp_FLQ_res_cost = D_FLQ_res_cost.get_expected_costs()['C_FLQres_cost']

# DLM
# Chance Node
D_DLM_cost = DecisionNode(name='D_DLM_cost', cost=0, future_nodes=[C_DLM_cost])
# Expected Costs
Exp_DLM_cost = D_DLM_cost.get_expected_costs()['C_DLM_cost']

############ End Cost ############

############ DALYs ############

# Terminal nodes - Dalys
CC_FLQsus_DALY = TerminalNode(name='CC_FLQsus_DALY', cost=DALY_CC_FLQsus)
TF_FLQsus_DALY = TerminalNode(name='TF_FLQsus_DALY', cost=DALY_TF_FLQsus)
CC_FLQres_DALY = TerminalNode(name='CC_FLQres_DALY', cost=DALY_CC_FLQres)
TF_FLQres_DALY = TerminalNode(name='TF_FLQres_DALY', cost=DALY_TF_FLQres)
CC_DLM_DALY = TerminalNode(name='CC_DLM_DALY', cost=DALY_CC_DLM)
TF_DLM_DALY = TerminalNode(name='TF_DLM_DALY', cost=DALY_TF_DLM)

############ End DALYs ############


############ DALY Calculation ############

Exp_FLQ_DALY = []
Exp_DLM_DALY = []
Exp_FLQ_Cost = []
StTreat_cost = []
StTreat_DALY = []
StTreat_NMB = []
StTreat_cost_res = []
StTreat_DALY_res = []
StTreat_NMB_res = []
StTreat_cost_sus = []
StTreat_DALY_sus = []
StTreat_NMB_sus = []
FLQ_NMB = []
DLM_NMB = []

# DALY calculation for each individual in the dataset
DALY_individual_Moldova = [max(0, LE_2019_Moldova - age) for age in pred_data['age']]

for DALY_Death, obs in zip(DALY_individual_Moldova, pred_data['obs']):

    ############ DALY ############

    # Terminal Nodes
    D_FLQsus_DALY = TerminalNode(name='D_FLQsus_DALY', cost=DALY_Death)
    D_FLQres_DALY = TerminalNode(name='D_FLQres_DALY', cost=DALY_Death)
    D_DLM_DALY = TerminalNode(name='D_DLM_DALY', cost=DALY_Death)

    # Chance nodes - DALYs
    C_FLQsus_DALY = ChanceNode(name='C_FLQsus_DALY', cost=DALY_FLQ,
                               future_nodes=[CC_FLQsus_DALY, TF_FLQsus_DALY, D_FLQsus_DALY],
                               probs=[Prob_CC_FLQsus, Prob_TF_FLQsus, Prob_D_FLQsus])
    C_FLQres_DALY = ChanceNode(name='C_FLQres_DALY', cost=DALY_FLQ,
                               future_nodes=[CC_FLQres_DALY, TF_FLQres_DALY, D_FLQres_DALY],
                               probs=[Prob_CC_FLQres, Prob_TF_FLQres, Prob_D_FLQres])
    C_DLM_DALY = ChanceNode(name='C_DLM_DALY', cost=DALY_DLM,
                            future_nodes=[CC_DLM_DALY, TF_DLM_DALY, D_DLM_DALY],
                            probs=[Prob_CC_DLM, Prob_TF_DLM, Prob_D_DLM])

    # Decision nodes and Expected Values
    D_FLQsus_DALY = DecisionNode(name='D_FLQsus_DALY', cost=0, future_nodes=[C_FLQsus_DALY])
    Exp_FLQsus_DALY = D_FLQsus_DALY.get_expected_costs()['C_FLQsus_DALY']
    D_FLQres_DALY = DecisionNode(name='D_FLQres_DALY', cost=0, future_nodes=[C_FLQres_DALY])
    Exp_FLQres_DALY = D_FLQres_DALY.get_expected_costs()['C_FLQres_DALY']
    D_DLM_DALY = DecisionNode(name='D_DLM_DALY', cost=0, future_nodes=[C_DLM_DALY])
    Exp_D_DLM_DALY = D_DLM_DALY.get_expected_costs()['C_DLM_DALY']

    DLM_NMB.append(GDP_moldova * Exp_D_DLM_DALY + Exp_DLM_cost)

    if obs == 1:
        Exp_FLQ_DALY.append(Exp_FLQres_DALY)
        Exp_DLM_DALY.append(Exp_D_DLM_DALY)
        Exp_FLQ_Cost.append(Exp_FLQ_res_cost)
        FLQ_NMB.append(GDP_moldova * Exp_FLQres_DALY + Exp_FLQ_res_cost)
        StTreat_cost.append(Exp_FLQ_res_cost)
        StTreat_DALY.append(Exp_FLQres_DALY)
        StTreat_NMB.append(GDP_moldova * Exp_FLQres_DALY + Exp_FLQ_res_cost)
        StTreat_cost_res.append(Exp_FLQ_res_cost)
        StTreat_DALY_res.append(Exp_FLQres_DALY)
        StTreat_NMB_res.append(GDP_moldova * Exp_FLQres_DALY + Exp_FLQ_res_cost)

    else:
        Exp_FLQ_DALY.append(Exp_FLQsus_DALY)
        Exp_DLM_DALY.append(Exp_D_DLM_DALY)
        Exp_FLQ_Cost.append(Exp_FLQ_sus_cost)
        FLQ_NMB.append(GDP_moldova * Exp_FLQsus_DALY + Exp_FLQ_sus_cost)
        StTreat_cost.append(Exp_FLQ_sus_cost)
        StTreat_DALY.append(Exp_FLQsus_DALY)
        StTreat_NMB.append(GDP_moldova * Exp_FLQsus_DALY + Exp_FLQ_sus_cost)
        StTreat_cost_sus.append(Exp_FLQ_sus_cost)
        StTreat_DALY_sus.append(Exp_FLQsus_DALY)
        StTreat_NMB_sus.append(GDP_moldova * Exp_FLQsus_DALY + Exp_FLQ_sus_cost)

data_DT_NMB = {
    "DLM_NMB": DLM_NMB,
    "FLQ_NMB": FLQ_NMB
}

# Convert the dictionary to a pandas DataFrame
df_DT_NMB = pd.DataFrame(data_DT_NMB)
# Save the DataFrame to an Excel file
df_DT_NMB.to_excel("/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Code/DR_TB_DT_MDRTree test/Test/DLM_NMB_old.xlsx", index=False)



############ End DALY Calculation ############

# Initiating the vectors
NMB_s_threshold = []
Treat_p_DLM_Pred_threshold = []
Treat_n_DLM_Pred_threshold = []
Treat_DLM_threshold = []
Treat_DLM_res_threshold = []
Treat_DLM_sus_threshold = []

Daly_Tx_truth_all_threshold = []
Cost_Tx_truth_all_threshold = []

# Performance of PM + DT
TP_DTPM_threshold = []
FP_DTPM_threshold = []
FN_DTPM_threshold = []
TN_DTPM_threshold = []

# Testing outcome specific thresholds
Exp_FLQ_DALY_ind_thre = []
Exp_FLQ_Cost_ind_thre = []
Exp_DLM_DALY_ind_thre = []
Exp_DLM_Cost_ind_thre = []
NMB_ind_thre = []
PMDTPM_classification_ind_thre =[]
PM_classification_ind_thre = []
prediction_ind_thre = []
observed_ind_thre = []
threshold_ind_thre = []
patient_ind_thre = []
Daly_Tx_truth_all_ind_thre = []
Cost_Tx_truth_all_ind_thre = []
StTreat_cost_ind_thre = []
StTreat_DALY_ind_thre = []

#Checking the Expected cost and DALY in each tree
Exp_FLQ_DALY_p_ind_thre = []
Exp_FLQ_Cost_p_ind_thre = []
Exp_DLM_DALY_p_ind_thre = []
Exp_DLM_Cost_p_ind_thre = []
Exp_FLQ_DALY_n_ind_thre = []
Exp_FLQ_Cost_n_ind_thre = []
Exp_DLM_DALY_n_ind_thre = []
Exp_DLM_Cost_n_ind_thre = []

#Checking the Expected cost and DALY in each susceptibility profile
Daly_Tx_truth_avg_r_threshold = []
Cost_Tx_truth_avg_r_threshold = []
NMB_avg_r_threshold = []
Daly_Tx_truth_avg_s_threshold = []
Cost_Tx_truth_avg_s_threshold = []
NMB_avg_s_threshold = []

Daly_Tx_truth_avg_sd_r_threshold = []
Cost_Tx_truth_avg_sd_r_threshold = []
NMB_avg_sd_r_threshold = []
Daly_Tx_truth_avg_sd_s_threshold = []
Cost_Tx_truth_avg_sd_s_threshold = []
NMB_avg_sd_s_threshold = []

#Average cost and DALY
Daly_Tx_truth_ind_threshold = []
Cost_Tx_truth_ind_threshold = []
Daly_Tx_truth_ind_sd_threshold = []
Cost_Tx_truth_ind_sd_threshold = []

#Cost, DALY , NMB each branch by threshold
Exp_FLQ_Cost_ResClass_thre = []
Exp_FLQ_DALY_ResClass_thre = []
Exp_FLQ_Cost_SusClass_thre = []
Exp_FLQ_DALY_SusClass_thre = []
Exp_DLM_Cost_thre = []
Exp_DLM_DALY_SusClass_thre = []
Exp_DLM_DALY_ResClass_thre = []
NMB_ResClass_thre = []
NMB_SusClass_thre = []
NMB_FLQ_ResClass_thre = []
NMB_DLM_ResClass_thre = []
NMB_FLQ_SusClass_thre = []
NMB_DLM_SusClass_thre = []
NMB_PMDT_threshold = []

# Saving individual to calculate confidence intervals
NMB_avg_r_eachind = []
NMB_avg_s_eachind = []
NMB_avg_sd_r_eachind = []
NMB_avg_sd_s_eachind = []
NMB_avg_sd_eachind = []

with open(csv_file, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        P_NR_P = float(row['P_NR_P'])
        P_R_P = float(row['P_R_P'])
        P_NR_N = float(row['P_NR_N'])
        P_R_N = float(row['P_R_N'])
        t = float(row['threshold'])
        positive = float(row['positive'])
        negative = float(row['negative'])

        ############ Cost ############

        # Positive Tree
        # Chance Node
        C_FLQ_cost_p = ChanceNode(name='C_FLQ_cost_p', cost=Cost_FLQ, future_nodes=[C_FLQsus_cost, C_FLQres_cost],
                                  probs=[P_NR_P, P_R_P])
        # Decision Node
        D_cost_p = DecisionNode(name='D_cost_p', cost=0, future_nodes=[C_FLQ_cost_p, C_DLM_cost])
        # Expected Costs
        Exp_FLQ_cost_p = D_cost_p.get_expected_costs()['C_FLQ_cost_p']
        Exp_DLM_cost_p = D_cost_p.get_expected_costs()['C_DLM_cost']

        # Expected cost
        Exp_FLQ_Cost_p_ind_thre.append({'threshold': t, 'Cost_FLQ_p': Exp_FLQ_cost_p})
        Exp_DLM_Cost_p_ind_thre.append({'threshold': t, 'Cost_DLM_p': Exp_DLM_cost_p})

        # Negative Tree
        # Chance Node
        C_FLQ_cost_n = ChanceNode(name='C_FLQ_cost_n', cost=Cost_FLQ, future_nodes=[C_FLQsus_cost, C_FLQres_cost],
                                  probs=[P_NR_N, P_R_N])
        # Decision Node
        D_cost_n = DecisionNode(name='D_cost_n', cost=0, future_nodes=[C_FLQ_cost_n, C_DLM_cost])
        # Expected Costs
        Exp_FLQ_cost_n = D_cost_n.get_expected_costs()['C_FLQ_cost_n']
        Exp_DLM_cost_n = D_cost_n.get_expected_costs()['C_DLM_cost']

        # Expected cost
        Exp_FLQ_Cost_n_ind_thre.append({'threshold': t, 'Cost_FLQ_n': Exp_FLQ_cost_n})
        Exp_DLM_Cost_n_ind_thre.append({'threshold': t, 'Cost_DLM_n': Exp_DLM_cost_n})

        # Saving cost each branch
        Exp_FLQ_Cost_ResClass_thre.append({'threshold': t, 'Cost': Exp_FLQ_cost_p})
        Exp_FLQ_Cost_SusClass_thre.append({'threshold': t, 'Cost': Exp_FLQ_cost_n})
        Exp_DLM_Cost_thre.append({'threshold': t, 'Cost': Exp_DLM_cost_p})

        ############ End Cost ############

        # Save DALY and Costs
        Daly_Tx_truth_all = []
        Cost_Tx_truth_all = []

        Daly_Tx_truth_sd_all = []
        Cost_Tx_truth_sd_all = []

        # Count of patients that were prescribed DLM
        Treat_p_DLM_Pred = 0 # People who are classified FLQ resistant and received DLM
        Treat_n_DLM_Pred = 0 # People who are classified FLQ susceptible and received DLM
        Treat_DLM = 0 # Overall people receiving DLM
        Treat_DLM_res =0 # People who are FLQ resistant and received DLM
        Treat_DLM_sus =0 # People who are FLQ susceptible and received DLM

        # Confiosion Matrix
        TP_DTPM = 0
        FN_DTPM = 0
        TN_DTPM = 0
        FP_DTPM = 0

        # Checking the Expected cost and DALY in each susceptibility profile
        Daly_Tx_truth_avg_r = []
        Cost_Tx_truth_avg_r = []
        NMB_avg_r = []
        Daly_Tx_truth_avg_s = []
        Cost_Tx_truth_avg_s = []
        NMB_avg_s = []
        Daly_Tx_truth_avg_sd_r = []
        Cost_Tx_truth_avg_sd_r = []
        NMB_avg_sd_r = []
        Daly_Tx_truth_avg_sd_s = []
        Cost_Tx_truth_avg_sd_s = []
        NMB_avg_sd_s = []

        #Saving DALY for each branch
        Exp_FLQ_DALY_ResClass = []
        Exp_FLQ_DALY_SusClass = []
        Exp_DLM_DALY_SusClass = []
        Exp_DLM_DALY_ResClass = []
        NMB_ResClass = []
        NMB_SusClass = []
        NMB_FLQ_ResClass = []
        NMB_DLM_ResClass = []
        NMB_FLQ_SusClass = []
        NMB_DLM_SusClass = []


        for i, (DALY_Death, pred, obs) in enumerate(zip(DALY_individual_Moldova, pred_data['pred'], pred_data['obs'])):

            ############ DALY ############

            # Terminal Nodes
            D_FLQsus_DALY = TerminalNode(name='D_FLQsus_DALY', cost=DALY_Death)
            D_FLQres_DALY = TerminalNode(name='D_FLQres_DALY', cost=DALY_Death)
            D_DLM_DALY = TerminalNode(name='D_DLM_DALY', cost=DALY_Death)

            # Chance nodes - DALYs
            C_FLQsus_DALY = ChanceNode(name='C_FLQsus_DALY', cost=0,
                                       future_nodes=[CC_FLQsus_DALY, TF_FLQsus_DALY, D_FLQsus_DALY],
                                       probs=[Prob_CC_FLQsus, Prob_TF_FLQsus, Prob_D_FLQsus])
            C_FLQres_DALY = ChanceNode(name='C_FLQres_Daly', cost=0,
                                       future_nodes=[CC_FLQres_DALY, TF_FLQres_DALY, D_FLQres_DALY],
                                       probs=[Prob_CC_FLQres, Prob_TF_FLQres, Prob_D_FLQres])
            C_DLM_DALY = ChanceNode(name='C_DLM_DALY', cost=DALY_DLM,
                                    future_nodes=[CC_DLM_DALY, TF_DLM_DALY, D_DLM_DALY],
                                    probs=[Prob_CC_DLM, Prob_TF_DLM, Prob_D_DLM])

            threshold_ind_thre.append(t)
            patient_ind_thre.append(i)

            if pred > t:
                ### Positive DT ###
                # Chance Node
                C_FLQ_daly_p = ChanceNode(name='C_FLQ_daly_p', cost=DALY_FLQ,
                                          future_nodes=[C_FLQsus_DALY, C_FLQres_DALY], probs=[P_NR_P, P_R_P])
                # Decision Node
                D_daly_p = DecisionNode(name='D_daly_p', cost=0, future_nodes=[C_FLQ_daly_p, C_DLM_DALY])
                # Expected Costs
                Exp_FLQ_daly_p = D_daly_p.get_expected_costs()['C_FLQ_daly_p']
                Exp_DLM_daly_p = D_daly_p.get_expected_costs()['C_DLM_DALY']

                # Net Monetary Benefit
                NMB_p = GDP_moldova * (Exp_FLQ_daly_p - Exp_DLM_daly_p) - (Exp_DLM_cost_p - Exp_FLQ_cost_p)

                Exp_FLQ_Cost_ind_thre.append(Exp_FLQ_cost_p)
                Exp_FLQ_DALY_ind_thre.append(Exp_FLQ_daly_p)
                Exp_DLM_DALY_ind_thre.append(Exp_DLM_daly_p)
                Exp_DLM_Cost_ind_thre.append(Exp_DLM_cost_p)
                NMB_ind_thre.append(NMB_p)
                PM_classification_ind_thre.append(1)
                prediction_ind_thre.append(pred)

                # Saving DALY each branch
                Exp_FLQ_DALY_ResClass.append(Exp_FLQ_daly_p)
                Exp_DLM_DALY_ResClass.append(Exp_DLM_daly_p)
                NMB_ResClass.append(NMB_p)
                NMB_FLQ_ResClass.append(GDP_moldova * Exp_FLQ_daly_p + Exp_FLQ_cost_p)
                NMB_DLM_ResClass.append(GDP_moldova * Exp_DLM_daly_p + Exp_DLM_cost_p)

                if obs ==1:
                    observed_ind_thre.append(1)
                else:
                    observed_ind_thre.append(0)

                # Select Optimal Treatment
                if NMB_p > 0:
                    Treat_DLM += 1
                    Treat_p_DLM_Pred += 1
                    Daly_Tx_truth = Exp_DLM_DALY[i]
                    Cost_Tx_truth = Exp_DLM_cost
                    Daly_Tx_truth_sd = StTreat_DALY[i] - Exp_DLM_DALY[i]
                    Cost_Tx_truth_sd = Exp_DLM_cost - StTreat_cost[i]

                    PMDTPM_classification_ind_thre.append(1)
                    if obs == 1:
                        Treat_DLM_res += 1
                        TP_DTPM += 1
                        Daly_Tx_truth_avg_r.append(Exp_DLM_DALY[i])
                        Cost_Tx_truth_avg_r.append(Exp_DLM_cost)
                        NMB_avg_r.append(
                            GDP_moldova * (Exp_DLM_DALY[i]) + (Exp_DLM_cost))
                        NMB_avg_r_eachind.append({'threshold': t, 'NMB':  GDP_moldova * (Exp_DLM_DALY[i]) + (Exp_DLM_cost)})
                        Daly_Tx_truth_avg_sd_r.append(StTreat_DALY[i] - Exp_DLM_DALY[i])
                        Cost_Tx_truth_avg_sd_r.append(Exp_DLM_cost - StTreat_cost[i])
                        NMB_avg_sd_r.append(GDP_moldova * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (Exp_DLM_cost - StTreat_cost[i]))
                        NMB_avg_sd_r_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (Exp_DLM_cost - StTreat_cost[i])})
                        NMB_avg_sd_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (
                                        Exp_DLM_cost - StTreat_cost[i])})
                    else:
                        Treat_DLM_sus += 1
                        FP_DTPM += 1
                        Daly_Tx_truth_avg_s.append(Exp_DLM_DALY[i])
                        Cost_Tx_truth_avg_s.append(Exp_DLM_cost)
                        NMB_avg_s.append(
                            GDP_moldova * (Exp_DLM_DALY[i]) + (Exp_DLM_cost))
                        NMB_avg_s_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (Exp_DLM_DALY[i]) + (Exp_DLM_cost)})
                        Daly_Tx_truth_avg_sd_s.append(StTreat_DALY[i] - Exp_DLM_DALY[i])
                        Cost_Tx_truth_avg_sd_s.append(Exp_DLM_cost - StTreat_cost[i])
                        NMB_avg_sd_s.append(GDP_moldova * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (Exp_DLM_cost - StTreat_cost[i]))
                        NMB_avg_sd_s_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (
                                        Exp_DLM_cost - StTreat_cost[i])})
                        NMB_avg_sd_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (
                                        Exp_DLM_cost - StTreat_cost[i])})
                else:
                    Daly_Tx_truth = Exp_FLQ_DALY[i]
                    Cost_Tx_truth = Exp_FLQ_Cost[i]
                    Daly_Tx_truth_sd = StTreat_DALY[i] - Exp_FLQ_DALY[i]
                    Cost_Tx_truth_sd = Exp_FLQ_Cost[i] - StTreat_cost[i]

                    PMDTPM_classification_ind_thre.append(0)
                    if obs == 1:
                        FN_DTPM += 1
                        Daly_Tx_truth_avg_r.append(Exp_FLQ_DALY[i])
                        Cost_Tx_truth_avg_r.append(Exp_FLQ_Cost[i])
                        NMB_avg_r.append(GDP_moldova * (Exp_FLQ_DALY[i]) + (Exp_FLQ_Cost[i]))
                        NMB_avg_r_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (Exp_FLQ_DALY[i]) + (Exp_FLQ_Cost[i])})
                        Daly_Tx_truth_avg_sd_r.append(StTreat_DALY[i] - Exp_FLQ_DALY[i])
                        Cost_Tx_truth_avg_sd_r.append(Exp_FLQ_Cost[i] - StTreat_cost[i])
                        NMB_avg_sd_r.append(GDP_moldova * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (Exp_FLQ_Cost[i]- StTreat_cost[i]))
                        NMB_avg_sd_r_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (Exp_FLQ_Cost[i]- StTreat_cost[i])})
                        NMB_avg_sd_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (Exp_FLQ_Cost[i]- StTreat_cost[i])})
                    else:
                        TN_DTPM += 1
                        Daly_Tx_truth_avg_s.append(Exp_FLQ_DALY[i])
                        Cost_Tx_truth_avg_s.append(Exp_FLQ_Cost[i])
                        NMB_avg_s.append(GDP_moldova * (Exp_FLQ_DALY[i]) + (Exp_FLQ_Cost[i]))
                        NMB_avg_s_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (Exp_FLQ_DALY[i]) + (Exp_FLQ_Cost[i])})
                        Daly_Tx_truth_avg_sd_s.append(StTreat_DALY[i] - Exp_FLQ_DALY[i])
                        Cost_Tx_truth_avg_sd_s.append(Exp_FLQ_Cost[i] - StTreat_cost[i])
                        NMB_avg_sd_s.append(
                            GDP_moldova * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (Exp_FLQ_Cost[i] - StTreat_cost[i]))
                        NMB_avg_sd_s_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (Exp_FLQ_Cost[i] - StTreat_cost[i])})
                        NMB_avg_sd_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (Exp_FLQ_Cost[i] - StTreat_cost[i])})


                ### End Positive DT ###
            else:
                ### Negative DT ###
                # Chance Node
                C_FLQ_daly_n = ChanceNode(name='C_FLQ_daly_n', cost=DALY_FLQ,
                                          future_nodes=[C_FLQsus_DALY, C_FLQres_DALY], probs=[P_NR_N, P_R_N])
                # Decision Node
                D_daly_n = DecisionNode(name='D_daly_n', cost=0, future_nodes=[C_FLQ_daly_n, C_DLM_DALY])
                # Expected Costs
                Exp_FLQ_daly_n = D_daly_n.get_expected_costs()['C_FLQ_daly_n']
                Exp_DLM_daly_n = D_daly_n.get_expected_costs()['C_DLM_DALY']

                # Net Monetary Benefit
                NMB_n = GDP_moldova * (Exp_FLQ_daly_n - Exp_DLM_daly_n) - (Exp_DLM_cost_n - Exp_FLQ_cost_n)

                Exp_FLQ_Cost_ind_thre.append(Exp_FLQ_cost_n)
                Exp_FLQ_DALY_ind_thre.append(Exp_FLQ_daly_n)
                Exp_DLM_DALY_ind_thre.append(Exp_DLM_daly_n)
                Exp_DLM_Cost_ind_thre.append(Exp_DLM_cost_n)
                NMB_ind_thre.append(NMB_n)
                PM_classification_ind_thre.append(0)
                prediction_ind_thre.append(pred)

                # Saving DALY each branch
                Exp_FLQ_DALY_SusClass.append(Exp_FLQ_daly_n)
                Exp_DLM_DALY_SusClass.append(Exp_DLM_daly_n)
                NMB_SusClass.append(NMB_n)
                NMB_FLQ_SusClass.append(GDP_moldova * Exp_FLQ_daly_n + Exp_FLQ_cost_n)
                NMB_DLM_SusClass.append(GDP_moldova * Exp_DLM_daly_n + Exp_DLM_cost_n)

                if obs == 1:
                    observed_ind_thre.append(1)
                else:
                    observed_ind_thre.append(0)

                # Select Optimal Treatment
                if NMB_n > 0:
                    Treat_DLM_res += 1
                    Treat_DLM += 1
                    Treat_n_DLM_Pred += 1
                    Daly_Tx_truth = Exp_DLM_DALY[i]
                    Cost_Tx_truth = Exp_DLM_cost
                    Daly_Tx_truth_sd = StTreat_DALY[i] - Exp_DLM_DALY[i]
                    Cost_Tx_truth_sd = Exp_DLM_cost - StTreat_cost[i]

                    PMDTPM_classification_ind_thre.append(1)
                    if obs == 1:
                        Treat_DLM_sus += 1
                        TP_DTPM += 1
                        Daly_Tx_truth_avg_r.append(Exp_DLM_DALY[i])
                        Cost_Tx_truth_avg_r.append(Exp_DLM_cost)
                        NMB_avg_r.append(
                            GDP_moldova * (Exp_DLM_DALY[i]) + (Exp_DLM_cost))
                        NMB_avg_r_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (Exp_DLM_DALY[i]) + (Exp_DLM_cost)})
                        Daly_Tx_truth_avg_sd_r.append(StTreat_DALY[i] - Exp_DLM_DALY[i])
                        Cost_Tx_truth_avg_sd_r.append(Exp_DLM_cost - StTreat_cost[i])
                        NMB_avg_sd_r.append(GDP_moldova * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (Exp_DLM_cost - StTreat_cost[i]))
                        NMB_avg_sd_r_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (
                                        Exp_DLM_cost - StTreat_cost[i])})
                        NMB_avg_sd_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (
                                        Exp_DLM_cost - StTreat_cost[i])})
                    else:
                        FP_DTPM += 1
                        Daly_Tx_truth_avg_s.append(Exp_DLM_DALY[i])
                        Cost_Tx_truth_avg_s.append(Exp_DLM_cost)
                        NMB_avg_s.append(
                            GDP_moldova * (Exp_DLM_DALY[i]) + (Exp_DLM_cost))
                        NMB_avg_s_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (Exp_DLM_DALY[i]) + (Exp_DLM_cost)})
                        Daly_Tx_truth_avg_sd_s.append(StTreat_DALY[i] - Exp_DLM_DALY[i])
                        Cost_Tx_truth_avg_sd_s.append(Exp_DLM_cost - StTreat_cost[i])
                        NMB_avg_sd_s.append(GDP_moldova * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (Exp_DLM_cost - StTreat_cost[i]))
                        NMB_avg_sd_s_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (Exp_DLM_cost - StTreat_cost[i])})
                        NMB_avg_sd_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (Exp_DLM_cost - StTreat_cost[i])})
                else:
                    Daly_Tx_truth = Exp_FLQ_DALY[i]
                    Cost_Tx_truth = Exp_FLQ_Cost[i]
                    Daly_Tx_truth_sd = StTreat_DALY[i] - Exp_FLQ_DALY[i]
                    Cost_Tx_truth_sd = Exp_FLQ_Cost[i] - StTreat_cost[i]
                    PMDTPM_classification_ind_thre.append(0)
                    if obs == 1:
                        FN_DTPM += 1
                        Daly_Tx_truth_avg_r.append(Exp_FLQ_DALY[i])
                        Cost_Tx_truth_avg_r.append(Exp_FLQ_Cost[i])
                        NMB_avg_r.append(GDP_moldova * (Exp_FLQ_DALY[i]) + (Exp_FLQ_Cost[i]))
                        NMB_avg_r_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (Exp_FLQ_DALY[i]) + (Exp_FLQ_Cost[i])})
                        Daly_Tx_truth_avg_sd_r.append(StTreat_DALY[i] - Exp_FLQ_DALY[i])
                        Cost_Tx_truth_avg_sd_r.append(Exp_FLQ_Cost[i] - StTreat_cost[i])
                        NMB_avg_sd_r.append(GDP_moldova * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (Exp_FLQ_Cost[i]- StTreat_cost[i]))
                        NMB_avg_sd_r_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (
                                        Exp_FLQ_Cost[i] - StTreat_cost[i])})
                        NMB_avg_sd_eachind.append(
                            {'threshold': t, 'NMB':  GDP_moldova * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (
                                        Exp_FLQ_Cost[i] - StTreat_cost[i])})

                    else:
                        TN_DTPM += 1
                        Daly_Tx_truth_avg_s.append(Exp_FLQ_DALY[i])
                        Cost_Tx_truth_avg_s.append(Exp_FLQ_Cost[i])
                        NMB_avg_s.append(GDP_moldova * (Exp_FLQ_DALY[i]) + (Exp_FLQ_Cost[i]))
                        NMB_avg_s_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (Exp_FLQ_DALY[i]) + (Exp_FLQ_Cost[i])})
                        Daly_Tx_truth_avg_sd_s.append(StTreat_DALY[i] - Exp_FLQ_DALY[i])
                        Cost_Tx_truth_avg_sd_s.append(Exp_FLQ_Cost[i]- StTreat_cost[i])
                        NMB_avg_sd_s.append(GDP_moldova * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (Exp_FLQ_Cost[i]- StTreat_cost[i]))
                        NMB_avg_sd_s_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (
                                        Exp_FLQ_Cost[i] - StTreat_cost[i])})
                        NMB_avg_sd_eachind.append(
                            {'threshold': t, 'NMB': GDP_moldova * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (
                                        Exp_FLQ_Cost[i] - StTreat_cost[i])})

                ### End Negative DT ###

            #print(NMB_avg_r)
            # All costs and DAlYs at this threshold
            Daly_Tx_truth_all.append(Daly_Tx_truth)
            Cost_Tx_truth_all.append(Cost_Tx_truth)

            Daly_Tx_truth_all_ind_thre.append(Daly_Tx_truth)
            Cost_Tx_truth_all_ind_thre.append(Cost_Tx_truth)

            StTreat_cost_ind_thre.append(StTreat_cost[i])
            StTreat_DALY_ind_thre.append(StTreat_DALY[i])

            #Compared to Standard Treatment
            Daly_Tx_truth_sd_all.append(Daly_Tx_truth_sd)
            Cost_Tx_truth_sd_all.append(Cost_Tx_truth_sd)

        # Saving DALY each branch
        Exp_FLQ_DALY_ResClass_thre.append({'threshold': t, 'DALY': sum(Exp_FLQ_DALY_ResClass)/(positive*540)})
        Exp_DLM_DALY_ResClass_thre.append({'threshold': t, 'DALY': sum(Exp_DLM_DALY_ResClass)/(positive*540)})
        NMB_ResClass_thre.append({'threshold': t, 'NMB': sum(NMB_ResClass)/(positive*540)})
        NMB_FLQ_ResClass_thre.append({'threshold': t, 'NMB': sum(NMB_FLQ_ResClass)/(positive*540)})
        NMB_DLM_ResClass_thre.append({'threshold': t, 'NMB': sum(NMB_DLM_ResClass)/(positive*540)})

        Exp_FLQ_DALY_SusClass_thre.append({'threshold': t, 'DALY': sum(Exp_FLQ_DALY_SusClass)/(negative*540)})
        Exp_DLM_DALY_SusClass_thre.append({'threshold': t, 'DALY': sum(Exp_DLM_DALY_SusClass) / (negative*540)})
        NMB_SusClass_thre.append({'threshold': t, 'NMB': sum(NMB_SusClass)/(negative*540)})
        NMB_FLQ_SusClass_thre.append({'threshold': t, 'NMB': sum(NMB_FLQ_SusClass)/(negative*540)})
        NMB_DLM_SusClass_thre.append({'threshold': t, 'NMB': sum(NMB_DLM_SusClass)/(negative*540)})

        ############ End DALY ############

        TP_DTPM_threshold.append({'threshold': t, 'TP_DTPM': TP_DTPM})
        FP_DTPM_threshold.append({'threshold': t, 'FP_DTPM': FP_DTPM})
        FN_DTPM_threshold.append({'threshold': t, 'FN_DTPM': FN_DTPM})
        TN_DTPM_threshold.append({'threshold': t, 'TN_DTPM': TN_DTPM})

        Treat_p_DLM_Pred_threshold.append({'threshold': t, 'N_p_DLM_Treat': Treat_p_DLM_Pred})
        Treat_n_DLM_Pred_threshold.append({'threshold': t, 'N_n_DLM_Treat': Treat_n_DLM_Pred})

        Treat_DLM_threshold.append({'threshold': t, 'DLM_Treat': Treat_DLM/540}) # Overall percentage of people precribed DLM
        Treat_DLM_res_threshold.append({'threshold': t, 'DLM_Treat': Treat_DLM_res/101}) # Percentage of FLQ resistant people precribed DLM
        Treat_DLM_sus_threshold.append({'threshold': t, 'DLM_Treat': Treat_DLM_sus/439}) # Percentage of FLQ susceptible people precribed DLM

        # Summing up the DALYs and costs for the DT + Pred Model considering truth
        Daly_Tx_truth_all_sum = sum(Daly_Tx_truth_all)
        Daly_Tx_truth_all_threshold.append({'threshold': t, 'DALY': Daly_Tx_truth_all_sum})
        Cost_Tx_truth_all_sum = sum(Cost_Tx_truth_all)
        Cost_Tx_truth_all_threshold.append({'threshold': t, 'Cost': Cost_Tx_truth_all_sum})

        # Net Monetary benefit - Optimal treatment versus Standard Treatment
        NMB_s = GDP_moldova * (sum(StTreat_DALY) / 540 - Daly_Tx_truth_all_sum / 540) - (
                Cost_Tx_truth_all_sum / 540 - sum(StTreat_cost) / 540)
        NMB_s_threshold.append({'threshold': t, 'NMB_s': NMB_s})
        NMB_PMDT = GDP_moldova * Daly_Tx_truth_all_sum / 540 + (
                Cost_Tx_truth_all_sum / 540)
        NMB_PMDT_threshold.append({'threshold': t, 'NMB_PMDT': NMB_PMDT})

        # Overall Individual Costs and DALYs
        Daly_Tx_truth_ind_threshold.append({'threshold': t, 'DALY': Daly_Tx_truth_all_sum/540})
        Cost_Tx_truth_ind_threshold.append({'threshold': t, 'Cost': Cost_Tx_truth_all_sum/540})
        Daly_Tx_truth_ind_sd_threshold.append({'threshold': t, 'DALY': sum(Daly_Tx_truth_sd_all) / 540})
        Cost_Tx_truth_ind_sd_threshold.append({'threshold': t, 'Cost': sum(Cost_Tx_truth_sd_all) / 540})

        # Costs and DALYs depending on susceptibility
        Daly_Tx_truth_avg_r_threshold.append({'threshold': t, 'DALY': sum(Daly_Tx_truth_avg_r)/101})
        Cost_Tx_truth_avg_r_threshold.append({'threshold': t, 'Cost': sum(Cost_Tx_truth_avg_r)/101})
        NMB_avg_r_threshold.append({'threshold': t, 'NMB_r': sum(NMB_avg_r)/101})
        Daly_Tx_truth_avg_s_threshold.append({'threshold': t, 'DALY': sum(Daly_Tx_truth_avg_s)/439})
        Cost_Tx_truth_avg_s_threshold.append({'threshold': t, 'Cost': sum(Cost_Tx_truth_avg_s)/439})
        NMB_avg_s_threshold.append({'threshold': t, 'NMB_s': sum(NMB_avg_s)/439})

        Daly_Tx_truth_avg_sd_r_threshold.append({'threshold': t, 'DALY': sum(Daly_Tx_truth_avg_sd_r)/101})
        Cost_Tx_truth_avg_sd_r_threshold.append({'threshold': t, 'Cost': sum(Cost_Tx_truth_avg_sd_r)/101})
        NMB_avg_sd_r_threshold.append({'threshold': t, 'NMB_r': sum(NMB_avg_sd_r)/101})
        Daly_Tx_truth_avg_sd_s_threshold.append({'threshold': t, 'DALY': sum(Daly_Tx_truth_avg_sd_s)/439})
        Cost_Tx_truth_avg_sd_s_threshold.append({'threshold': t, 'Cost': sum(Cost_Tx_truth_avg_sd_s)/439})
        NMB_avg_sd_s_threshold.append({'threshold': t, 'NMB_s': sum(NMB_avg_sd_s)/439})


# # Everyone on FLQ
# FLQ_Cost = sum(StTreat_cost) / 540
# FLQ_DALY = sum(StTreat_DALY) / 540
#
# #### Increase in Cost and Health ####
# # Extract DALY, Cost, and threshold values from the lists
# daly_values = [entry['DALY'] for entry in Daly_Tx_truth_all_threshold]
# cost_values = [entry['Cost'] for entry in Cost_Tx_truth_all_threshold]
# threshold_values = [entry['threshold'] for entry in Cost_Tx_truth_all_threshold]
#
# Increase_DTPMall_Cost = [(cost / 540) - FLQ_Cost for cost in cost_values]
# Increase_DTPMall_DALY = [FLQ_DALY - (daly / 540) for daly in daly_values]
#
# plt.scatter(Increase_DTPMall_DALY, Increase_DTPMall_Cost, label='DT + PM - All Threshold')
# # Plot a point at the origin labeled FLQ
# plt.scatter(0, 0, color='black', label='FLQ')
#
# # Select the indices of the thresholds you want to annotate
# selected_indices = [400, 450, 490, 500, 510]  # Example: annotate every other threshold
#
# # Annotate points with their threshold values for the selected indices
# for i in selected_indices:
#     plt.text(Increase_DTPMall_DALY[i], Increase_DTPMall_Cost[i], str(threshold_values[i]), fontsize=8)
#
# # Draw a dashed line between DLM and FLQ points
# # plt.plot([0, Increase_DALY], [0, Increase_Cost], color='gray', linestyle='--')
# plt.text(0, 0, 'FLQ', verticalalignment='bottom', horizontalalignment='right')
# # Label axes and add a legend
# plt.xlabel('Increase in health')
# plt.ylabel('Increase in Cost')
# plt.grid(True)
# plt.legend()
# plt.show()
# #### End Increase in Cost and Health ####
#
#### Net Monetary Benefit ####
thresholds = [item['threshold'] for item in NMB_s_threshold]
NMB_s_plot = [item['NMB_s'] for item in NMB_s_threshold]

plt.plot(thresholds, NMB_s_plot, linewidth=2)
# Add a vertical line at the last threshold for each NMB is negative or zero
plt.xlabel('Threshold')
plt.ylabel('Change in NMB')
plt.title('Threshold vs Change in NMB')
plt.grid(True)
plt.savefig(r'/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Figures/NMB_St_Treat_Opt_Treat_Individual.png')
plt.show()

# # PM + DT performance
# # Extracting all threshold elements
# threshold = [item["threshold"] for item in TP_DTPM_threshold]
# TP_DTPM_values = [item["TP_DTPM"] for item in TP_DTPM_threshold]
# FP_DTPM_values = [item["FP_DTPM"] for item in FP_DTPM_threshold]
# FN_DTPM_values = [item["FN_DTPM"] for item in FN_DTPM_threshold]
# TN_DTPM_values = [item["TN_DTPM"] for item in TN_DTPM_threshold]
# Daly_Tx_truth_all_threshold_values = [item["DALY"] for item in Daly_Tx_truth_all_threshold]
# Cost_Tx_truth_all_threshold_values = [item["Cost"] for item in Cost_Tx_truth_all_threshold]
#
# data_PMDT = {
#     "NMB_change": NMB_s_plot,
#     "Threshold": threshold,
#     "TP_DTPM": TP_DTPM_values,
#     "FP_DTPM": FP_DTPM_values,
#     "FN_DTPM": FN_DTPM_values,
#     "TN_DTPM": TN_DTPM_values,
#     "Daly_Tx_truth_all": Daly_Tx_truth_all_threshold_values,
#     "Cost_Tx_truth_all": Cost_Tx_truth_all_threshold_values,
#     "StTreat_DALY": np.full(len(NMB_s_plot), sum(StTreat_DALY)),
#     "StTreat_Cost": np.full(len(NMB_s_plot), sum(StTreat_cost))
# }
#
# # Convert the dictionary to a pandas DataFrame
# df_PMDT = pd.DataFrame(data_PMDT)
#
# # Save the DataFrame to an Excel file
# df_PMDT.to_excel("/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/PMDT_performance.xlsx", index=False)

#
# data_PMDT_ind_thre = {
#     "Patient": patient_ind_thre,
#     "observed": observed_ind_thre,
#     "prediction": prediction_ind_thre,
#     "PM_classification" : PM_classification_ind_thre,
#     "threshold": threshold_ind_thre,
#     "Exp_FLQ_DALY": Exp_FLQ_DALY_ind_thre,
#     "Exp_FLQ_Cost": Exp_FLQ_Cost_ind_thre,
#     "Exp_DLM_DALY": Exp_DLM_DALY_ind_thre,
#     "Exp_DLM_Cost": Exp_DLM_Cost_ind_thre,
#     "NMB": NMB_ind_thre,
#     "PMDTPM_classification": PMDTPM_classification_ind_thre,
#     "Daly_Tx_truth": Daly_Tx_truth_all_ind_thre,
#     "Cost_Tx_truth": Cost_Tx_truth_all_ind_thre,
#     "StTreat_cost": StTreat_cost_ind_thre,
#     "StTreat_DALY": StTreat_DALY_ind_thre
# }
#
# # Convert the dictionary to a pandas DataFrame
# df_PMDT_ind_thre = pd.DataFrame(data_PMDT_ind_thre)
#
# # Save the DataFrame to an Excel file
# df_PMDT_ind_thre.to_excel("/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/PMDT_individual_performance.xlsx", index=False)
#


# # PM + DT performance
# # Extracting all threshold elements
# threshold = [item["threshold"] for item in Exp_FLQ_Cost_p_ind_thre]
# Exp_FLQ_Cost_p_ind_thre_values = [item["Cost_FLQ_p"] for item in Exp_FLQ_Cost_p_ind_thre]
# Exp_FLQ_Cost_n_ind_thre_values = [item["Cost_FLQ_n"] for item in Exp_FLQ_Cost_n_ind_thre]
# Exp_DLM_Cost_p_ind_thre_values = [item["Cost_DLM_p"] for item in Exp_DLM_Cost_p_ind_thre]
# Exp_DLM_Cost_n_ind_thre_values = [item["Cost_DLM_n"] for item in Exp_DLM_Cost_n_ind_thre]
#
# data_DT_eachtree_costs = {
#     "Threshold": threshold,
#     "FLQ_Cost_p": Exp_FLQ_Cost_p_ind_thre_values,
#     "DLM_Cost_p": Exp_DLM_Cost_p_ind_thre_values,
#     "FLQ_Cost_n": Exp_FLQ_Cost_n_ind_thre_values,
#     "DLM_Cost_n": Exp_DLM_Cost_n_ind_thre_values,
# }
#
# # Convert the dictionary to a pandas DataFrame
# df_DT_eachtree_costs = pd.DataFrame(data_DT_eachtree_costs)
#
# # Save the DataFrame to an Excel file
# df_DT_eachtree_costs.to_excel("/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/PMDT_cost_pos_neg_DT.xlsx", index=False)
#
# # Cost and DALY depending on FLQ susceptibility
#
# # Extracting all threshold elements
# threshold = [item["threshold"] for item in Daly_Tx_truth_avg_r_threshold]
# Daly_Tx_truth_avg_r_values = [item["DALY"] for item in Daly_Tx_truth_avg_r_threshold]
# Cost_Tx_truth_avg_r_values = [item["Cost"] for item in Cost_Tx_truth_avg_r_threshold]
# NMB_avg_r_values = [item["NMB_r"] for item in NMB_avg_r_threshold]
# Daly_Tx_truth_avg_s_values = [item["DALY"] for item in Daly_Tx_truth_avg_s_threshold]
# Cost_Tx_truth_avg_s_values = [item["Cost"] for item in Cost_Tx_truth_avg_s_threshold]
# NMB_avg_s_values = [item["NMB_s"] for item in NMB_avg_s_threshold]
# Daly_Tx_truth_avg_sd_r_values = [item["DALY"] for item in Daly_Tx_truth_avg_sd_r_threshold]
# Cost_Tx_truth_avg_sd_r_values = [item["Cost"] for item in Cost_Tx_truth_avg_sd_r_threshold]
# NMB_avg_sd_r_values = [item["NMB_r"] for item in NMB_avg_sd_r_threshold]
# Daly_Tx_truth_avg_sd_s_values = [item["DALY"] for item in Daly_Tx_truth_avg_sd_s_threshold]
# Cost_Tx_truth_avg_sd_s_values = [item["Cost"] for item in Cost_Tx_truth_avg_sd_s_threshold]
# NMB_avg_sd_s_values = [item["NMB_s"] for item in NMB_avg_sd_s_threshold]
# Daly_Tx_truth_ind_threshold_values = [item["DALY"] for item in Daly_Tx_truth_ind_threshold]
# Cost_Tx_truth_ind_threshold_values = [item["Cost"] for item in Cost_Tx_truth_ind_threshold]
# Daly_Tx_truth_ind_sd_threshold_values = [item["DALY"] for item in Daly_Tx_truth_ind_sd_threshold]
# Cost_Tx_truth_ind_sd_threshold_values = [item["Cost"] for item in Cost_Tx_truth_ind_sd_threshold]
# NMB_s_threshold_values = [item["NMB_s"] for item in NMB_s_threshold]
# NMB_PMDT_threshold_values = [item["NMB_PMDT"] for item in NMB_PMDT_threshold]
# Treat_DLM_threshold_values = [item["DLM_Treat"] for item in Treat_DLM_threshold]
# Treat_DLM_res_threshold_values = [item["DLM_Treat"] for item in Treat_DLM_res_threshold]
# Treat_DLM_sus_threshold_values = [item["DLM_Treat"] for item in Treat_DLM_sus_threshold]
# Exp_FLQ_DALY_ResClass_thre_values = [item["DALY"] for item in Exp_FLQ_DALY_ResClass_thre]
# Exp_DLM_DALY_ResClass_thre_values = [item["DALY"] for item in Exp_DLM_DALY_ResClass_thre]
# NMB_ResClass_thre_values = [item["NMB"] for item in NMB_ResClass_thre]
# Exp_FLQ_DALY_SusClass_thre_values = [item["DALY"] for item in Exp_FLQ_DALY_SusClass_thre]
# Exp_DLM_DALY_SusClass_thre_values = [item["DALY"] for item in Exp_DLM_DALY_SusClass_thre]
# NMB_SusClass_thre_values = [item["NMB"] for item in NMB_SusClass_thre]
# Exp_FLQ_Cost_ResClass_thre_values = [item["Cost"] for item in Exp_FLQ_Cost_ResClass_thre]
# Exp_FLQ_Cost_SusClass_thre_values = [item["Cost"] for item in Exp_FLQ_Cost_SusClass_thre]
# Exp_DLM_Cost_thre_values = [item["Cost"] for item in Exp_DLM_Cost_thre]
# NMB_FLQ_ResClass_thre_values = [item["NMB"] for item in NMB_FLQ_ResClass_thre]
# NMB_DLM_ResClass_thre_values = [item["NMB"] for item in NMB_DLM_ResClass_thre]
# NMB_FLQ_SusClass_thre_values = [item["NMB"] for item in NMB_FLQ_SusClass_thre]
# NMB_DLM_SusClass_thre_values = [item["NMB"] for item in NMB_DLM_SusClass_thre]
#
# data_DT_sus_res = {
#     "Threshold": threshold,
#     "Daly_Tx_truth_avg_r": Daly_Tx_truth_avg_r_values,
#     "Cost_Tx_truth_avg_r": Cost_Tx_truth_avg_r_values,
#     "NMB_avg_r": NMB_avg_r_values,
#     "Daly_Tx_truth_avg_s": Daly_Tx_truth_avg_s_values,
#     "Cost_Tx_truth_avg_s": Cost_Tx_truth_avg_s_values,
#     "NMB_avg_s": NMB_avg_s_values,
#     "Daly_Tx_truth_avg_sd_r": Daly_Tx_truth_avg_sd_r_values,
#     "Cost_Tx_truth_avg_sd_r": Cost_Tx_truth_avg_sd_r_values,
#     "NMB_avg_sd_r": NMB_avg_sd_r_values,
#     "Daly_Tx_truth_avg_sd_s": Daly_Tx_truth_avg_sd_s_values,
#     "Cost_Tx_truth_avg_sd_s": Cost_Tx_truth_avg_sd_s_values,
#     "NMB_avg_sd_s": NMB_avg_sd_s_values,
#     "Daly_Tx_truth": Daly_Tx_truth_ind_threshold_values,
#     "Cost_Tx_truth": Cost_Tx_truth_ind_threshold_values,
#     "Daly_Tx_truth_sd": Daly_Tx_truth_ind_sd_threshold_values,
#     "Cost_Tx_truth_sd": Cost_Tx_truth_ind_sd_threshold_values,
#     "NMB_PMDT": NMB_PMDT_threshold_values,
#     "NMB": NMB_s_threshold_values,
#     "StTreat_cost": [sum(StTreat_cost)/540] *len(threshold),
#     "StTreat_DALY": [sum(StTreat_DALY)/540] *len(threshold),
#     "StTreat_NMB": [sum(StTreat_NMB)/540] *len(threshold),
#     "StTreat_cost_res": [sum(StTreat_cost_res)/101] *len(threshold),
#     "StTreat_DALY_res": [sum(StTreat_DALY_res)/101] *len(threshold),
#     "StTreat_NMB_res": [sum(StTreat_NMB_res)/101] *len(threshold),
#     "StTreat_cost_sus": [sum(StTreat_cost_sus)/439] *len(threshold),
#     "StTreat_DALY_sus": [sum(StTreat_DALY_sus)/439] *len(threshold),
#     "StTreat_NMB_sus": [sum(StTreat_NMB_sus)/439] *len(threshold),
#     "Treat_DLM": Treat_DLM_threshold_values,
#     "Treat_DLM_res": Treat_DLM_res_threshold_values,
#     "Treat_DLM_sus": Treat_DLM_sus_threshold_values,
#     "Exp_FLQ_DALY_ResClass": Exp_FLQ_DALY_ResClass_thre_values,
#     "Exp_FLQ_Cost_ResClass": Exp_FLQ_Cost_ResClass_thre_values,
#     "NMB_ResClass": NMB_ResClass_thre_values,
#     "Exp_FLQ_DALY_SusClass": Exp_FLQ_DALY_SusClass_thre_values,
#     "Exp_FLQ_Cost_SusClass": Exp_FLQ_Cost_SusClass_thre_values,
#     "NMB_SusClass": NMB_SusClass_thre_values,
#     "Exp_DLM_DALY_ResClass": Exp_DLM_DALY_ResClass_thre_values,
#     "Exp_DLM_DALY_SusClass": Exp_DLM_DALY_SusClass_thre_values,
#     "Exp_DLM_Cost": Exp_DLM_Cost_thre_values,
#     "NMB_FLQ_ResClass": NMB_FLQ_ResClass_thre_values,
#     "NMB_DLM_ResClass": NMB_DLM_ResClass_thre_values,
#     "NMB_FLQ_SusClass": NMB_FLQ_SusClass_thre_values,
#     "NMB_DLM_SusClass": NMB_DLM_SusClass_thre_values,
#
# }
#
# # Convert the dictionary to a pandas DataFrame
# df_DT_sus_res = pd.DataFrame(data_DT_sus_res)
#
# # Save the DataFrame to an Excel file
# df_DT_sus_res.to_excel("/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/PMDT_sus_res.xlsx", index=False)
#
#
# # NMB for resistant and susceptible people with Condidence intervals
# # Extracting all threshold elements
# threshold = [item["threshold"] for item in NMB_avg_r_eachind]
# NMB_avg_r_eachind_values = [item["NMB"] for item in NMB_avg_r_eachind]
# NMB_avg_sd_r_eachind_values = [item["NMB"] for item in NMB_avg_sd_r_eachind]
#
# print(len(NMB_avg_sd_r_eachind_values))
#
# data_DT_NMB_avg_r_eachind = {
#     "Threshold": threshold,
#     "NMB_avg_r": NMB_avg_r_eachind_values,
#     "NMB_avg_sd_r": NMB_avg_sd_r_eachind_values
# }
#
# # Convert the dictionary to a pandas DataFrame
# df_DT_NMB_avg_r_eachind = pd.DataFrame(data_DT_NMB_avg_r_eachind)
#
# # Save the DataFrame to an Excel file
# df_DT_NMB_avg_r_eachind.to_excel("/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_avg_r_eachind.xlsx", index=False)
#
# # NMB for resistant and susceptible people with Condidence intervals
# # Extracting all threshold elements
# threshold = [item["threshold"] for item in NMB_avg_s_eachind]
# NMB_avg_s_eachind_values = [item["NMB"] for item in NMB_avg_s_eachind]
# NMB_avg_sd_s_eachind_values = [item["NMB"] for item in NMB_avg_sd_s_eachind]
#
# data_DT_NMB_avg_s_eachind = {
#     "Threshold": threshold,
#     "NMB_avg_s": NMB_avg_s_eachind_values,
#     "NMB_avg_sd_s": NMB_avg_sd_s_eachind_values
# }
#
# # Convert the dictionary to a pandas DataFrame
# df_DT_NMB_avg_s_eachind = pd.DataFrame(data_DT_NMB_avg_s_eachind)
#
# # Save the DataFrame to an Excel file
# df_DT_NMB_avg_s_eachind.to_excel("/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_avg_s_eachind.xlsx", index=False)
#
# # NMB for resistant and susceptible people with Condidence intervals
# # Extracting all threshold elements
# threshold = [item["threshold"] for item in NMB_avg_sd_eachind]
# NMB_avg_sd_eachind_values = [item["NMB"] for item in NMB_avg_sd_eachind]
#
# data_DT_NMB_avg_eachind = {
#     "Threshold": threshold,
#     "NMB_avg": NMB_avg_sd_eachind_values
# }
#
# # Convert the dictionary to a pandas DataFrame
# df_DT_NMB_avg_eachind = pd.DataFrame(data_DT_NMB_avg_eachind)
#
# # Save the DataFrame to an Excel file
# df_DT_NMB_avg_eachind.to_excel("/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_avg_eachind.xlsx", index=False)
