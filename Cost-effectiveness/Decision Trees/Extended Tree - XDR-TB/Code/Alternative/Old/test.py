import csv
import matplotlib.pyplot as plt
from DR_TB_Classes import *
import pandas as pd

# Read the CSV file with predictions, costs, dalys and probabilities
pred_data = pd.read_csv('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/HM Output/pred_obs_calibrated_model.csv')
cost_data = pd.read_excel('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Cost_DALY_Prob_asumptions.xlsx', 'Costs')
daly_data = pd.read_excel('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Cost_DALY_Prob_asumptions.xlsx', 'DALY')
prob_data = pd.read_excel('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Cost_DALY_Prob_asumptions.xlsx', 'Probabilities')
csv_file = '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/HM Output/sens_spec_calibrated_model.csv'

def largest_non_positive_threshold(data):
    for entry in reversed(data):
        if entry['NMB_s'] <= 0:
            return entry['threshold']
    return None  # If no non-positive 'NMB_s' value is found

# GBD per capita - Republic of Moldova
GBD_moldova = 5714.43
LE_2019_Moldova = 70.94

# FLQ Resistance prevalence
FLQ_Res_prev = 1-0.812963

# This calculates DALYs incurred for each individual in the Moldova dataset depending on age
DALY_individual_Moldova =[]

for age in pred_data['age']:
    if age >= LE_2019_Moldova:
        daly = 0 # The amount of DALYs incurred when the patient has live more than the life expectancy in 0

    else:
        daly = LE_2019_Moldova - age  # YLL

    DALY_individual_Moldova.append(daly)

# Probabilities
# This reads the probabilities from an excel file tab Probabilities
for index, row in prob_data.iterrows():
    var_name = row['Probability Variable']
    var_value = row['Probability Value']
    exec(f"{var_name} = {var_value}")

# Cost Tree
# This reads the costs from an excel file tab Costs
for index, row in cost_data.iterrows():
    var_name = row['Cost Variable']
    var_value = row['Cost Value']
    exec(f"{var_name} = {var_value}")


# Dalys Tree
# This reads the DALYs from an excel file tab DALY
for index, row in daly_data.iterrows():
    var_name = row['DALY Variable']
    var_value = row['DALY Value']
    exec(f"{var_name} = {var_value}")

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
C_FLQsus_cost = ChanceNode(name='C_FLQsus_cost', cost=0, future_nodes=[CC_FLQsus_cost, TF_FLQsus_cost, D_FLQsus_cost], probs=[Prob_CC_FLQsus, Prob_TF_FLQsus, Prob_D_FLQsus])
C_FLQres_cost = ChanceNode(name='C_FLQres_cost', cost=0, future_nodes=[CC_FLQres_cost, TF_FLQres_cost, D_FLQres_cost], probs=[Prob_CC_FLQres, Prob_TF_FLQres, Prob_D_FLQres])
C_DLM_cost = ChanceNode(name='C_DLM_cost', cost=Cost_DLM, future_nodes=[CC_DLM_cost, TF_DLM_cost, D_DLM_cost], probs=[Prob_CC_DLM, Prob_TF_DLM, Prob_D_DLM])

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

# FLQ Susceptible
# Chance Node
D_FLQ_res_cost = DecisionNode(name='D_FLQ_res_cost', cost=Cost_FLQ, future_nodes=[C_FLQsus_cost])
# Expected Costs
Exp_FLQ_res_cost = D_FLQ_res_cost.get_expected_costs()['C_FLQsus_cost']

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

    else:
        Exp_FLQ_DALY.append(Exp_FLQsus_DALY)
        Exp_DLM_DALY.append(Exp_D_DLM_DALY)
        Exp_FLQ_Cost.append(Exp_FLQ_sus_cost)
        StTreat_cost.append(Exp_FLQ_sus_cost)
        StTreat_DALY.append(Exp_FLQsus_DALY)

    ############ End Calculation ############


# Initiating the vectors
NMB_s_threshold = []
Daly_Tx_all_sum_threshold = []
Cost_Tx_all_sum_threshold = []
Treat_p_DLM_Pred_threshold = []
Treat_n_DLM_Pred_threshold = []
Daly_TruthEval_all_sum_threshold = []
Cost_TruthEval_all_sum_threshold = []

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
        C_FLQ_cost_p = ChanceNode(name='C_FLQ_cost_p', cost=Cost_FLQ, future_nodes=[C_FLQsus_cost, C_FLQres_cost], probs=[P_NR_P, P_R_P])
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

        # Standard Treatment
        # Chance Node
        C_FLQ_cost_s = ChanceNode(name='C_FLQ_cost_s', cost=Cost_FLQ, future_nodes=[C_FLQsus_cost, C_FLQres_cost],
                                  probs=[(1-FLQ_Res_prev), FLQ_Res_prev])
        # Decision Node
        D_cost_s = DecisionNode(name='D_cost_s', cost=0, future_nodes=[C_FLQ_cost_s])
        # Expected Cost
        Exp_FLQ_cost_s = D_cost_s.get_expected_costs()['C_FLQ_cost_s']

        ############ End Cost ############

        # This for loop iterate over the individuals of the dataset
        Exp_FLQ_daly_s = []
        Treat_DT_Pred = []
        Exp_DALY_DLM = []
        Daly_TruthEval_all =[]
        Cost_TruthEval_all = []

        # Count of patients that were prescribed DLM
        Treat_p_DLM_Pred = 0
        Treat_n_DLM_Pred = 0

        for DALY_Death, pred, exp_FLQ_DALY, exp_DLM_DALY, exp_FLQ_Cost in zip(DALY_individual_Moldova, pred_data['pred'], Exp_FLQ_DALY, Exp_DLM_DALY, Exp_FLQ_Cost):

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


            if pred > t:
                ### Positive DT ###
                # Chance Node
                C_FLQ_daly_p = ChanceNode(name='C_FLQ_daly_p', cost=DALY_FLQ, future_nodes=[C_FLQsus_DALY, C_FLQres_DALY], probs=[P_NR_P, P_R_P])
                # Decision Node
                D_daly_p = DecisionNode(name='D_daly_p', cost=0, future_nodes=[C_FLQ_daly_p, C_DLM_DALY])
                # Expected Costs
                Exp_FLQ_daly_p = D_daly_p.get_expected_costs()['C_FLQ_daly_p']
                Exp_DLM_daly_p = D_daly_p.get_expected_costs()['C_DLM_DALY']

                # Net Monetary Benefit
                NMB_p = GBD_moldova * (Exp_FLQ_daly_p - Exp_DLM_daly_p) - (Exp_DLM_cost_p - Exp_FLQ_cost_p)

                # Select Optimal Treatment
                if NMB_p > 0:
                    Treat_p_DLM_Pred += 1
                    Daly_TruthEval = exp_DLM_DALY
                    Cost_TruthEval = Exp_DLM_cost
                else:
                    Daly_TruthEval = exp_FLQ_DALY
                    Cost_TruthEval = exp_FLQ_Cost

                Daly_TruthEval_all.append(Daly_TruthEval)
                Cost_TruthEval_all.append(Cost_TruthEval)
                ### End Positive DT ###
            else:
                ### Negative DT ###
                # Chance Node
                C_FLQ_daly_n = ChanceNode(name='C_FLQ_daly_n', cost=DALY_FLQ, future_nodes=[C_FLQsus_DALY, C_FLQres_DALY], probs=[P_NR_N, P_R_N])
                # Decision Node
                D_daly_n = DecisionNode(name='D_daly_n', cost=0, future_nodes=[C_FLQ_daly_n, C_DLM_DALY])
                # Expected Costs
                Exp_FLQ_daly_n = D_daly_n.get_expected_costs()['C_FLQ_daly_n']
                Exp_DLM_daly_n = D_daly_n.get_expected_costs()['C_DLM_DALY']

                # Net Monetary Benefit
                NMB_n = GBD_moldova * (Exp_FLQ_daly_n - Exp_DLM_daly_n) - (Exp_DLM_cost_n - Exp_FLQ_cost_n)

                # Select Optimal Treatment
                if NMB_n > 0:
                    Treat_n_DLM_Pred += 1
                    Daly_TruthEval = exp_DLM_DALY
                    Cost_TruthEval = Exp_DLM_cost
                else:
                    Daly_TruthEval = exp_FLQ_DALY
                    Cost_TruthEval = exp_FLQ_Cost

                Daly_TruthEval_all.append(Daly_TruthEval)
                Cost_TruthEval_all.append(Cost_TruthEval)
                ### End Negative DT ###

            # Standard Treatment
            # Chance Node
            C_FLQ_daly_s = ChanceNode(name='C_FLQ_daly_s', cost=DALY_FLQ, future_nodes=[C_FLQsus_DALY, C_FLQres_DALY],
                                      probs=[(1-FLQ_Res_prev), FLQ_Res_prev])
            # Decision Node
            D_daly_s = DecisionNode(name='D_daly_s', cost=0, future_nodes=[C_FLQ_daly_s])
            # Expected Cost
            Exp_FLQ_daly_s.append(D_daly_s.get_expected_costs()['C_FLQ_daly_s'])

            # Everyone receives DLM
            if pred > t:
                Exp_DALY_DLM.append(Exp_DLM_daly_p)
            else:
                Exp_DALY_DLM.append(Exp_DLM_daly_n)

            ############ End DALY ############

        Treat_p_DLM_Pred_threshold.append({'threshold': t, 'N_p_DLM_Treat': Treat_p_DLM_Pred})
        Treat_n_DLM_Pred_threshold.append({'threshold': t, 'N_n_DLM_Treat': Treat_n_DLM_Pred})

        # Summing up the DALYs and costs for the DT + Pred Model -using truth outcome
        Daly_TruthEval_all_sum = sum(Daly_TruthEval_all)
        Daly_TruthEval_all_sum_threshold.append({'threshold': t, 'DALY': Daly_TruthEval_all_sum})
        Cost_TruthEval_all_sum = sum(Cost_TruthEval_all)
        Cost_TruthEval_all_sum_threshold.append({'threshold': t, 'Cost': Cost_TruthEval_all_sum})

        # Summing up the DALYs for the standard treatment
        Exp_FLQ_daly_s_sum = sum(Exp_FLQ_daly_s) # The total DALYs of the satandard treatment is the sum of individual DAlYs
        Exp_FLQ_cost_s_sum = Exp_FLQ_cost_s * pred_data.shape[0] # The cost of the same for each individual, therefore the total cost is the individual cost multiplied by number of individuals

        # Summing up the DALYs for everyone on DLM
        Exp_DALY_DLM_sum = sum(
            Exp_DALY_DLM)  # The total DALYs of the satandard treatment is the sum of individual DAlYs

        # Net Monetary benefit - Optimal treatment versus Standard Treatment
        NMB_s = GBD_moldova * (sum(StTreat_DALY)/540 - Daly_TruthEval_all_sum/540) - (Cost_TruthEval_all_sum/540 - sum(StTreat_cost)/540)
        NMB_s_threshold.append({'threshold': t, 'NMB_s': NMB_s})

thresholds = [item['threshold'] for item in NMB_s_threshold]
NMB_s_plot = [item['NMB_s'] for item in NMB_s_threshold]

plt.plot(thresholds, NMB_s_plot, linewidth=2)
# Add a vertical line at the last threshold for each NMB is negative or zero
plt.xlabel('Threshold')
plt.ylabel('Change in NMB')
plt.title('Threshold vs Change in NMB')
plt.grid(True)
#plt.savefig(r'/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_St_Treat_Opt_Treat.png')
plt.show()

# Everyone on FLQ
FLQ_Cost = sum(StTreat_cost)/540
FLQ_DALY = sum(StTreat_DALY)/540

# Decision model
# Extract DALY, Cost, and threshold values from the lists
daly_values = [entry['DALY'] for entry in Daly_TruthEval_all_sum_threshold]
cost_values = [entry['Cost'] for entry in Cost_TruthEval_all_sum_threshold]
threshold_values = [entry['threshold'] for entry in Cost_TruthEval_all_sum_threshold]

Increase_DTPMall_Cost = [(cost / 540) - FLQ_Cost for cost in cost_values]
Increase_DTPMall_DALY = [FLQ_DALY - (daly / 540) for daly in daly_values]


plt.scatter(Increase_DTPMall_DALY, Increase_DTPMall_Cost, label='DT + PM - All Threshold')
# Plot a point at the origin labeled FLQ
plt.scatter(0, 0, color='red', label='FLQ')

# Select the indices of the thresholds you want to annotate
selected_indices = [400, 450, 490, 500, 510]  # Example: annotate every other threshold

#Annotate points with their threshold values for the selected indices
for i in selected_indices:
    plt.text(Increase_DTPMall_DALY[i], Increase_DTPMall_Cost[i], str(threshold_values[i]), fontsize=8)

plt.text(0, 0, 'FLQ', verticalalignment='bottom', horizontalalignment='right')
# Label axes and add a legend
plt.xlabel('Increase in health')
plt.ylabel('Increase in Cost')
plt.grid(True)
plt.legend()
plt.show()