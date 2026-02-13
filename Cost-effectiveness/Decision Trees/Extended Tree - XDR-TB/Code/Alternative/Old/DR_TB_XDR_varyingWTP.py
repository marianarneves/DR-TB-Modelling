import csv
import matplotlib.pyplot as plt
import pandas as pd
from DR_TB_Classes import *
import numpy as np
from scipy.stats import t

# Common directory paths
base_path = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/'
hm_output_path = base_path + 'HM/HM Output/'
cost_effectiveness_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/'

# Read data
pred_data = pd.read_csv(hm_output_path + 'pred_obs_calibrated_model.csv')
cost_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions.xlsx', 'Costs')
daly_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions.xlsx', 'DALY')
prob_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions.xlsx', 'Probabilities')
csv_file = hm_output_path + 'sens_spec_calibrated_model.csv'

# Constants
GDP_moldova = 5714.43
LE_2019_Moldova = 70.94
FLQ_Res_prev = 1 - 0.812963

#wtp
wtp_2019_Moldova = np.arange(0.5, 3.5, 0.5) * GDP_moldova

# DALY calculation for each individual in the dataset
DALY_individual_Moldova = [max(0, LE_2019_Moldova - age) for age in pred_data['age']]

# Read probabilities, costs, and DALYs
for index, row in prob_data.iterrows():
    globals()[row['Probability Variable']] = row['Probability Value']

for index, row in cost_data.iterrows():
    globals()[row['Cost Variable']] = row['Cost Value']

for index, row in daly_data.iterrows():
    globals()[row['DALY Variable']] = row['DALY Value']

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

# Terminal nodes - Dalys
CC_FLQsus_DALY = TerminalNode(name='CC_FLQsus_DALY', cost=DALY_CC_FLQsus)
TF_FLQsus_DALY = TerminalNode(name='TF_FLQsus_DALY', cost=DALY_TF_FLQsus)
CC_FLQres_DALY = TerminalNode(name='CC_FLQres_DALY', cost=DALY_CC_FLQres)
TF_FLQres_DALY = TerminalNode(name='TF_FLQres_DALY', cost=DALY_TF_FLQres)
CC_DLM_DALY = TerminalNode(name='CC_DLM_DALY', cost=DALY_CC_DLM)
TF_DLM_DALY = TerminalNode(name='TF_DLM_DALY', cost=DALY_TF_DLM)

############ Decision nodes and expected value - Cost ############

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
D_DLM_cost = DecisionNode(name='D_DLM_cost', cost=Cost_DLM, future_nodes=[C_DLM_cost])
# Expected Costs
Exp_DLM_cost = D_DLM_cost.get_expected_costs()['C_DLM_cost']

############ End Cost ############


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

    if obs == 1:
        Exp_FLQ_DALY.append(Exp_FLQres_DALY)
        Exp_DLM_DALY.append(Exp_D_DLM_DALY)
        Exp_FLQ_Cost.append(Exp_FLQ_res_cost)
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
        StTreat_cost.append(Exp_FLQ_sus_cost)
        StTreat_DALY.append(Exp_FLQsus_DALY)
        StTreat_NMB.append(GDP_moldova * Exp_FLQsus_DALY + Exp_FLQ_sus_cost)
        StTreat_cost_sus.append(Exp_FLQ_sus_cost)
        StTreat_DALY_sus.append(Exp_FLQsus_DALY)
        StTreat_NMB_sus.append(GDP_moldova * Exp_FLQsus_DALY + Exp_FLQ_sus_cost)


############ End DALY Calculation ############


# Saving individual to calculate confidence intervals
NMB_avg_r_eachind = []
NMB_avg_s_eachind = []
NMB_avg_sd_r_eachind = []
NMB_avg_sd_s_eachind = []
NMB_avg_sd_eachind = []
WTP_each_ind = []
NMB_avg_sd_r_loweric_eachind = []
NMB_avg_sd_r_upperic_eachind = []
NMB_avg_sd_s_loweric_eachind = []
NMB_avg_sd_s_upperic_eachind = []
NMB_avg_sd_loweric_eachind = []
NMB_avg_sd_upperic_eachind = []

with open(csv_file, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        P_NR_P = float(row['P_NR_P'])
        P_R_P = float(row['P_R_P'])
        P_NR_N = float(row['P_NR_N'])
        P_R_N = float(row['P_R_N'])
        threshold = float(row['threshold'])
        positive = float(row['positive'])
        negative = float(row['negative'])

        ############ Cost ############

        NMB_avg_r = []
        NMB_avg_sd_r = []
        NMB_avg_s = []
        NMB_avg_sd_s = []
        NMB_avg_sd = []

        for wtp in wtp_2019_Moldova:

            # Positive Tree
            # Chance Node
            C_FLQ_cost_p = ChanceNode(name='C_FLQ_cost_p', cost=Cost_FLQ, future_nodes=[C_FLQsus_cost, C_FLQres_cost],
                                      probs=[P_NR_P, P_R_P])
            # Decision Node
            D_cost_p = DecisionNode(name='D_cost_p', cost=0, future_nodes=[C_FLQ_cost_p, C_DLM_cost])
            # Expected Costs
            Exp_FLQ_cost_p = D_cost_p.get_expected_costs()['C_FLQ_cost_p']
            Exp_DLM_cost_p = D_cost_p.get_expected_costs()['C_DLM_cost']

            # Negative Tree
            # Chance Node
            C_FLQ_cost_n = ChanceNode(name='C_FLQ_cost_n', cost=Cost_FLQ, future_nodes=[C_FLQsus_cost, C_FLQres_cost],
                                      probs=[P_NR_N, P_R_N])
            # Decision Node
            D_cost_n = DecisionNode(name='D_cost_n', cost=0, future_nodes=[C_FLQ_cost_n, C_DLM_cost])
            # Expected Costs
            Exp_FLQ_cost_n = D_cost_n.get_expected_costs()['C_FLQ_cost_n']
            Exp_DLM_cost_n = D_cost_n.get_expected_costs()['C_DLM_cost']

            ############ End Cost ############

            # Confuosion Matrix
            TP_DTPM = 0
            FN_DTPM = 0
            TN_DTPM = 0
            FP_DTPM = 0


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

                if pred > threshold:
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
                    NMB_p = wtp * (Exp_FLQ_daly_p - Exp_DLM_daly_p) - (Exp_DLM_cost_p - Exp_FLQ_cost_p)

                    # Select Optimal Treatment
                    if NMB_p > 0:
                        Daly_Tx_truth = Exp_DLM_DALY[i]
                        Cost_Tx_truth = Exp_DLM_cost
                        Daly_Tx_truth_sd = StTreat_DALY[i] - Exp_DLM_DALY[i]
                        Cost_Tx_truth_sd = Exp_DLM_cost - StTreat_cost[i]

                        if obs == 1:
                            NMB_avg_r.append(wtp * (Exp_DLM_DALY[i]) + (Exp_DLM_cost))
                            NMB_avg_sd_r.append(
                               wtp * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (Exp_DLM_cost - StTreat_cost[i]))
                            NMB_avg_sd.append(
                                 wtp * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (
                                            Exp_DLM_cost - StTreat_cost[i]))
                        else:
                            NMB_avg_s.append(
                               wtp * (Exp_DLM_DALY[i]) + (Exp_DLM_cost))
                            NMB_avg_sd_s.append(
                                wtp * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (
                                            Exp_DLM_cost - StTreat_cost[i]))
                            NMB_avg_sd.append(
                               wtp * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (
                                            Exp_DLM_cost - StTreat_cost[i]))
                    else:
                        Daly_Tx_truth = Exp_FLQ_DALY[i]
                        Cost_Tx_truth = Exp_FLQ_Cost[i]
                        Daly_Tx_truth_sd = StTreat_DALY[i] - Exp_FLQ_DALY[i]
                        Cost_Tx_truth_sd = Exp_FLQ_Cost[i] - StTreat_cost[i]

                        if obs == 1:
                            NMB_avg_r.append(
                              wtp * (Exp_FLQ_DALY[i]) + (Exp_FLQ_Cost[i]))
                            NMB_avg_sd_r.append(
                                wtp * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (Exp_FLQ_Cost[i]- StTreat_cost[i]))
                            NMB_avg_sd.append(
                                wtp * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (Exp_FLQ_Cost[i]- StTreat_cost[i]))
                        else:
                            NMB_avg_s.append(
                               wtp * (Exp_FLQ_DALY[i]) + (Exp_FLQ_Cost[i]))
                            NMB_avg_sd_s.append(
                                wtp * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (Exp_FLQ_Cost[i] - StTreat_cost[i]))
                            NMB_avg_sd.append(
                               wtp * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (Exp_FLQ_Cost[i] - StTreat_cost[i]))


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
                    NMB_n = wtp * (Exp_FLQ_daly_n - Exp_DLM_daly_n) - (Exp_DLM_cost_n - Exp_FLQ_cost_n)

                    # Select Optimal Treatment
                    if NMB_n > 0:
                        Daly_Tx_truth = Exp_DLM_DALY[i]
                        Cost_Tx_truth = Exp_DLM_cost
                        Daly_Tx_truth_sd = StTreat_DALY[i] - Exp_DLM_DALY[i]
                        Cost_Tx_truth_sd = Exp_DLM_cost - StTreat_cost[i]

                        if obs == 1:
                            NMB_avg_r.append(
                               wtp * (Exp_DLM_DALY[i]) + (Exp_DLM_cost))
                            NMB_avg_sd_r.append(
                                wtp * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (
                                            Exp_DLM_cost - StTreat_cost[i]))
                            NMB_avg_sd.append(
                               wtp * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (
                                            Exp_DLM_cost - StTreat_cost[i]))
                        else:
                            NMB_avg_s.append(
                                wtp * (Exp_DLM_DALY[i]) + (Exp_DLM_cost))
                            NMB_avg_sd_s.append(
                                wtp * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (Exp_DLM_cost - StTreat_cost[i]))
                            NMB_avg_sd.append(
                               wtp * (StTreat_DALY[i] - Exp_DLM_DALY[i]) - (Exp_DLM_cost - StTreat_cost[i]))
                    else:
                        Daly_Tx_truth = Exp_FLQ_DALY[i]
                        Cost_Tx_truth = Exp_FLQ_Cost[i]
                        Daly_Tx_truth_sd = StTreat_DALY[i] - Exp_FLQ_DALY[i]
                        Cost_Tx_truth_sd = Exp_FLQ_Cost[i] - StTreat_cost[i]

                        if obs == 1:
                            NMB_avg_r.append(
                                wtp * (Exp_FLQ_DALY[i]) + (Exp_FLQ_Cost[i]))
                            NMB_avg_sd_r.append(
                               wtp * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (
                                            Exp_FLQ_Cost[i] - StTreat_cost[i]))
                            NMB_avg_sd.append(
                               wtp * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (
                                            Exp_FLQ_Cost[i] - StTreat_cost[i]))

                        else:
                            NMB_avg_s.append(wtp * (Exp_FLQ_DALY[i]) + (Exp_FLQ_Cost[i]))
                            NMB_avg_sd_s.append(
                               wtp * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (
                                            Exp_FLQ_Cost[i] - StTreat_cost[i]))
                            NMB_avg_sd.append(wtp * (StTreat_DALY[i] - Exp_FLQ_DALY[i]) - (
                                            Exp_FLQ_Cost[i] - StTreat_cost[i]))

                    ### End Negative DT ###

            NMB_avg_r_eachind.append(
                {'threshold': threshold, 'WTP': wtp, 'NMB': np.mean(NMB_avg_r)})
            NMB_avg_sd_r_eachind.append(
                {'threshold': threshold, 'WTP': wtp, 'NMB': np.mean(NMB_avg_sd_r)})
            NMB_avg_sd_r_loweric_eachind.append(
                {'threshold': threshold, 'WTP': wtp, 'NMB': np.mean(NMB_avg_sd_r) - t.ppf(0.975, 101-1) * (np.std(NMB_avg_sd_r, ddof=1) / np.sqrt(101))})
            NMB_avg_sd_r_upperic_eachind.append(
                {'threshold': threshold, 'WTP': wtp,
                 'NMB': np.mean(NMB_avg_sd_r) + t.ppf(0.975, 101-1) * (np.std(NMB_avg_sd_r, ddof=1) / np.sqrt(101))})
            NMB_avg_s_eachind.append(
                {'threshold': threshold, 'WTP': wtp, 'NMB': np.mean(NMB_avg_s)})
            NMB_avg_sd_s_eachind.append(
                {'threshold': threshold, 'WTP': wtp, 'NMB': np.mean(NMB_avg_sd_s)})
            NMB_avg_sd_s_loweric_eachind.append(
                {'threshold': threshold, 'WTP': wtp,
                 'NMB': np.mean(NMB_avg_sd_s) - t.ppf(0.975, 439-1) * (np.std(NMB_avg_sd_s, ddof=1) / np.sqrt(439))})
            NMB_avg_sd_s_upperic_eachind.append(
                {'threshold': threshold, 'WTP': wtp,
                 'NMB': np.mean(NMB_avg_sd_s) + t.ppf(0.975, 439-1) * (np.std(NMB_avg_sd_s, ddof=1) / np.sqrt(439))})
            NMB_avg_sd_eachind.append(
                {'threshold': threshold, 'WTP': wtp, 'NMB': np.mean(NMB_avg_sd)})
            NMB_avg_sd_loweric_eachind.append(
                {'threshold': threshold, 'WTP': wtp,
                 'NMB': np.mean(NMB_avg_sd) - t.ppf(0.975, 540-1) * (np.std(NMB_avg_sd, ddof=1) / np.sqrt(540))})
            NMB_avg_sd_upperic_eachind.append(
                {'threshold': threshold, 'WTP': wtp,
                 'NMB': np.mean(NMB_avg_sd) + t.ppf(0.975, 540-1) * (np.std(NMB_avg_sd, ddof=1) / np.sqrt(540))})


# NMB for resistant and susceptible people with Condidence intervals
# Extracting all threshold elements
threshold = [item["threshold"] for item in NMB_avg_r_eachind]
wtp_values = [item["WTP"] for item in NMB_avg_r_eachind]
NMB_avg_r_eachind_values = [item["NMB"] for item in NMB_avg_r_eachind]
NMB_avg_sd_r_eachind_values = [item["NMB"] for item in NMB_avg_sd_r_eachind]
NMB_avg_s_eachind_values = [item["NMB"] for item in NMB_avg_s_eachind]
NMB_avg_sd_s_eachind_values = [item["NMB"] for item in NMB_avg_sd_s_eachind]
NMB_avg_sd_eachind_values = [item["NMB"] for item in NMB_avg_sd_eachind]
NMB_avg_sd_r_loweric_eachind_values = [item["NMB"] for item in NMB_avg_sd_r_loweric_eachind]
NMB_avg_sd_r_upperic_eachind_values = [item["NMB"] for item in NMB_avg_sd_r_upperic_eachind]
NMB_avg_sd_s_loweric_eachind_values = [item["NMB"] for item in NMB_avg_sd_s_loweric_eachind]
NMB_avg_sd_s_upperic_eachind_values = [item["NMB"] for item in NMB_avg_sd_s_upperic_eachind]
NMB_avg_sd_loweric_eachind_values = [item["NMB"] for item in NMB_avg_sd_loweric_eachind]
NMB_avg_sd_upperic_eachind_values = [item["NMB"] for item in NMB_avg_sd_upperic_eachind]

data_DT_NMB_avg_eachind = {
    "Threshold": threshold,
    "WTP": wtp_values,
    "NMB_avg_r": NMB_avg_r_eachind_values,
    "NMB_avg_sd_r": NMB_avg_sd_r_eachind_values,
    "NMB_avg_sd_r_loweric": NMB_avg_sd_r_loweric_eachind_values,
    "NMB_avg_sd_r_upperic": NMB_avg_sd_r_upperic_eachind_values,
    "NMB_avg_s": NMB_avg_s_eachind_values,
    "NMB_avg_sd_s": NMB_avg_sd_s_eachind_values,
    "NMB_avg_sd_s_loweric": NMB_avg_sd_s_loweric_eachind_values,
    "NMB_avg_sd_s_upperic": NMB_avg_sd_s_upperic_eachind_values,
    "NMB_avg": NMB_avg_sd_eachind_values,
    "NMB_avg_sd_loweric": NMB_avg_sd_loweric_eachind_values,
    "NMB_avg_sd_upperic": NMB_avg_sd_upperic_eachind_values
}

# Convert the dictionary to a pandas DataFrame
df_DT_NMB_avg_eachind = pd.DataFrame(data_DT_NMB_avg_eachind)

# Save the DataFrame to an Excel file
df_DT_NMB_avg_eachind.to_excel("/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_sus_res_varWTP.xlsx", index=False)
