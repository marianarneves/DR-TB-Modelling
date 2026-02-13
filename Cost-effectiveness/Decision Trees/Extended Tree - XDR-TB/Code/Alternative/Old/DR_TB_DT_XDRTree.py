import csv
import matplotlib.pyplot as plt
import pandas as pd
from DR_TB_Classes import *

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

# Functions
def largest_non_positive_threshold(data):
    for entry in reversed(data):
        if entry['NMB_s'] <= 0:
            return entry['threshold']
    return None

# Constants
GDP_moldova = 5714.43
LE_2019_Moldova = 70.94
FLQ_Res_prev = 1 - 0.812963

# DALY calculation for each individual in the dataset
DALY_individual_Moldova = [max(0, LE_2019_Moldova - age) if age < LE_2019_Moldova else 0 for age in pred_data['age']]

# Read probabilities, costs, and DALYs
for index, row in prob_data.iterrows():
    globals()[row['Probability Variable']] = row['Probability Value']

for index, row in cost_data.iterrows():
    globals()[row['Cost Variable']] = row['Cost Value']

for index, row in daly_data.iterrows():
    globals()[row['DALY Variable']] = row['DALY Value']

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

# Initiating the vectors
NMB_s_threshold = []
NMB_s_individual_threshold =[]
Daly_Tx_all_sum_threshold = []
Cost_Tx_all_sum_threshold = []
Treat_p_DLM_Pred_threshold = []
Treat_n_DLM_Pred_threshold = []

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
        Daly_Tx_all = []
        Cost_Tx_all = []
        Exp_FLQ_daly_s = []
        Treat_DT_Pred = []
        Exp_DALY_DLM = []

        # Count of patients that were prescribed DLM
        Treat_p_DLM_Pred = 0
        Treat_n_DLM_Pred = 0

        for DALY_Death, pred in zip(DALY_individual_Moldova, pred_data['pred']):

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
                NMB_p = GDP_moldova * (Exp_FLQ_daly_p - Exp_DLM_daly_p) - (Exp_DLM_cost_p - Exp_FLQ_cost_p)

                # Select Optimal Treatment
                if NMB_p > 0:
                    Daly_Tx = Exp_DLM_daly_p
                    Cost_Tx = Exp_DLM_cost_p
                    Treat_p_DLM_Pred += 1
                else:
                    Daly_Tx = Exp_FLQ_daly_p
                    Cost_Tx = Exp_FLQ_cost_p


                Daly_Tx_all.append(Daly_Tx)
                Cost_Tx_all.append(Cost_Tx)
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
                NMB_n = GDP_moldova * (Exp_FLQ_daly_n - Exp_DLM_daly_n) - (Exp_DLM_cost_n - Exp_FLQ_cost_n)

                # Select Optimal Treatment
                if NMB_n > 0:
                    Daly_Tx = Exp_DLM_daly_n
                    Cost_Tx = Exp_DLM_cost_n
                    Treat_n_DLM_Pred += 1
                else:
                    Daly_Tx = Exp_FLQ_daly_n
                    Cost_Tx = Exp_FLQ_cost_n

                Daly_Tx_all.append(Daly_Tx)
                Cost_Tx_all.append(Cost_Tx)
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

        # Summing up the DALYs and costs for the DT + Pred Model
        Daly_Tx_all_sum = sum(Daly_Tx_all)
        Daly_Tx_all_sum_threshold.append({'threshold': t, 'DALY': Daly_Tx_all_sum})
        Cost_Tx_all_sum = sum(Cost_Tx_all)
        Cost_Tx_all_sum_threshold.append({'threshold': t, 'Cost': Cost_Tx_all_sum})

        # Summing up the DALYs for the standard treatment
        Exp_FLQ_daly_s_sum = sum(Exp_FLQ_daly_s) # The total DALYs of the satandard treatment is the sum of individual DAlYs
        Exp_FLQ_cost_s_sum = Exp_FLQ_cost_s * pred_data.shape[0] # The cost of the same for each individual, therefore the total cost is the individual cost multiplied by number of individuals

        # Summing up the DALYs for everyone on DLM
        Exp_DALY_DLM_sum = sum(
            Exp_DALY_DLM)  # The total DALYs of the satandard treatment is the sum of individual DAlYs
        # print(Exp_DALY_DLM_sum)
        # Exp_FLQ_cost_s_sum = Exp_FLQ_cost_s * pred_data.shape[
        #     0]  # The cost of the same for each individual, therefore the total cost is the individual cost multiplied by number of individuals

        # Net Monetary benefit - Optimal treatment versus Standard Treatment
        NMB_s = GDP_moldova * (Exp_FLQ_daly_s_sum - Daly_Tx_all_sum) - (Cost_Tx_all_sum - Exp_FLQ_cost_s_sum)
        NMB_s_threshold.append({'threshold': t, 'NMB_s': NMB_s})
        # Net Monetary benefit - Optimal treatment versus Standard Treatment
        NMB_s_individual = GDP_moldova * (Exp_FLQ_daly_s_sum/540 - Daly_Tx_all_sum/540) - (Cost_Tx_all_sum/540 - Exp_FLQ_cost_s_sum/540)
        NMB_s_individual_threshold.append({'threshold': t, 'NMB_s_individual': NMB_s_individual})

        # print(NMB_s)

# for entry in NMB_s_threshold:
#     print("Threshold:", entry['threshold'])

# Find the dictionary with the maximum NMB_s value
max_threshold_dict = max(NMB_s_threshold, key=lambda x: x['NMB_s'])
max_threshold = max_threshold_dict['threshold']

def find_daly_for_threshold(threshold_list, threshold_value):
    for entry in threshold_list:
        if entry['threshold'] == threshold_value:
            return entry['DALY']
    return None  # If the threshold is not found in the list

def find_cost_for_threshold(threshold_list, threshold_value):
    for entry in threshold_list:
        if entry['threshold'] == threshold_value:
            return entry['Cost']
    return None  # If the threshold is not found in the list

max_daly = find_daly_for_threshold(Daly_Tx_all_sum_threshold, max_threshold)
max_cost = find_cost_for_threshold(Cost_Tx_all_sum_threshold, max_threshold)

# Print or use the maximum threshold
# print("Threshold for maximum NMB_s:", max_threshold)
# # Print or use the maximum DALY and Cost values
# print("DALY for maximum NMB_s threshold:", max_daly)
# print("Cost for maximum NMB_s threshold:", max_cost)

# Other thresholds:

daly_025 = find_daly_for_threshold(Daly_Tx_all_sum_threshold, 0.250805097)
cost_025 = find_cost_for_threshold(Cost_Tx_all_sum_threshold, 0.250805097)

print(daly_025)
print(cost_025)

daly_057 = find_daly_for_threshold(Daly_Tx_all_sum_threshold,0.578355192)
cost_057 = find_cost_for_threshold(Cost_Tx_all_sum_threshold, 0.578355192)

print(daly_057)
print(cost_057)

Cost_Truth = 1402.8626407407407
DALY_truth = 0.6014665782407407

#Cost Everyone on DLM
DLM_Cost = 2346.246
DLM_DALY = 1.786247361111111

# Everyone on FLQ
FLQ_Cost = 1226.433962328
FLQ_DALY = 1.188207647758889

# DT + Prediction Model for which NMB is the maximun
DTPM_Cost = 719074.4600369144/540
DTPM_DALY = 581.4890628643827/540

# Everyone FLQ against Everyone in DLM
Increase_DLM_Cost = DLM_Cost - FLQ_Cost
Increase_DLM_DALY =  FLQ_DALY - DLM_DALY

# Ground truth against Everyone FLQ
Increase_Truth_Cost = Cost_Truth - FLQ_Cost
Increase_Truth_DALY = FLQ_DALY - DALY_truth

# DT+PM against Everyone FLQ
Increase_DTPM_Cost = DTPM_Cost - FLQ_Cost
Increase_DTPM_DALY = FLQ_DALY - DTPM_DALY

#Decision model
# Decision model
# Extract DALY, Cost, and threshold values from the lists
daly_values = [entry['DALY'] for entry in Daly_Tx_all_sum_threshold]
cost_values = [entry['Cost'] for entry in Cost_Tx_all_sum_threshold]
threshold_values = [entry['threshold'] for entry in Daly_Tx_all_sum_threshold]

Increase_DTPMall_Cost = [(cost / 540) - FLQ_Cost for cost in cost_values]
Increase_DTPMall_DALY = [FLQ_DALY - (daly / 540) for daly in daly_values]

plt.scatter(Increase_Truth_DALY, Increase_Truth_Cost, label='Truth')
plt.scatter(Increase_DTPMall_DALY, Increase_DTPMall_Cost, label='DT + PM - All Threshold')
plt.scatter(Increase_DTPM_DALY, Increase_DTPM_Cost, label='DT + PM')
# Plot a point at the origin labeled FLQ
plt.scatter(0, 0, color='black', label='FLQ')

# Select the indices of the thresholds you want to annotate
selected_indices = [400, 450, 490,  500, 510]  # Example: annotate every other threshold

# Annotate points with their threshold values for the selected indices
for i in selected_indices:
    plt.text(Increase_DTPMall_DALY[i], Increase_DTPMall_Cost[i], str(threshold_values[i]), fontsize=8)

# Draw a dashed line between DLM and FLQ points
# plt.plot([0, Increase_DALY], [0, Increase_Cost], color='gray', linestyle='--')
plt.text(0, 0, 'FLQ', verticalalignment='bottom', horizontalalignment='right')
# Label axes and add a legend
plt.xlabel('Increase in health')
plt.ylabel('Increase in Cost')
plt.grid(True)
plt.legend()
plt.show()


plt.scatter(Increase_Truth_DALY, Increase_Truth_Cost, label='Truth')
plt.scatter(Increase_DTPMall_DALY, Increase_DTPMall_Cost, label='DT + PM - All Threshold')
plt.scatter(Increase_DTPM_DALY, Increase_DTPM_Cost, label='DT + PM')
# Plot a point at the origin labeled FLQ
plt.scatter(0, 0, color='black', label='FLQ')
# Draw a dashed line between DLM and FLQ points
# plt.plot([0, Increase_DALY], [0, Increase_Cost], color='gray', linestyle='--')
plt.text(0, 0, 'FLQ', verticalalignment='bottom', horizontalalignment='right')
# Label axes and add a legend
plt.xlabel('Increase in health')
plt.ylabel('Increase in Cost')
plt.grid(True)
plt.legend()
plt.show()


print(Exp_DLM_cost_n)
print(Exp_DALY_DLM_sum/540)
print(Exp_FLQ_cost_s_sum/540)
print(Exp_FLQ_daly_s_sum/540)

# Everyone FLQ against Everyone in DLM
Increase_Cost = 540*Exp_DLM_cost_n - Exp_FLQ_cost_s_sum
Increase_DALY = Exp_DALY_DLM_sum - Exp_FLQ_daly_s_sum

# Plot Increase_Cost vs Increase_DALY
plt.scatter(Increase_DALY, Increase_Cost, label='DLM')
# Plot a point at the origin labeled FLQ
plt.scatter(0, 0, color='red', label='FLQ')
# Draw a dashed line between DLM and FLQ points
plt.plot([0, Increase_DALY], [0, Increase_Cost], color='gray', linestyle='--')
plt.text(0, 0, 'FLQ', verticalalignment='bottom', horizontalalignment='right')
# Label axes and add a legend
plt.xlabel('Change in DALY')
plt.ylabel('Change in Cost')
plt.grid(True)
plt.legend()
plt.show()


lt_NI = largest_non_positive_threshold(NMB_s_threshold)
# print(lt_NI)

thresholds = [item['threshold'] for item in NMB_s_threshold]
NMB_s_plot = [item['NMB_s'] for item in NMB_s_threshold]

plt.plot(thresholds, NMB_s_plot, linewidth=2)
# Add a vertical line at the last threshold for each NMB is negative or zero
plt.axvline(x=lt_NI, color='red', linestyle='--')  # Customize the color, linestyle, and linewidth as needed
plt.xlabel('Threshold')
plt.ylabel('Change in NMB')
plt.title('Threshold vs Change in NMB')
plt.grid(True)
plt.savefig(r'/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_St_Treat_Opt_Treat.png')
plt.show()

thresholds = [item['threshold'] for item in NMB_s_threshold]
NMB_s_individual_threshold_plot = [item['NMB_s_individual'] for item in NMB_s_individual_threshold]

plt.plot(thresholds, NMB_s_individual_threshold_plot, linewidth=2)
# Add a vertical line at the last threshold for each NMB is negative or zero
plt.axvline(x=lt_NI, color='red', linestyle='--')  # Customize the color, linestyle, and linewidth as needed
plt.xlabel('Threshold')
plt.ylabel('Change in NMB')
plt.title('Threshold vs Change in NMB')
plt.grid(True)
plt.show()

thresholds = [item['threshold'] for item in Daly_Tx_all_sum_threshold]
NMB_s_plot2 = [element * 2 for element in NMB_s_plot]
Daly_TX_threshold_plot = [item['DALY'] for item in Daly_Tx_all_sum_threshold]
Daly_TX_threshold_plot2 = [element * 1000 for element in Daly_TX_threshold_plot]
Cost_TX_threshold_plot = [item['Cost'] for item in Cost_Tx_all_sum_threshold]


# Plot the first line with a red color
plt.plot(thresholds, NMB_s_plot2, label='NBM', color='black', linewidth=2)
# Plot the first line with a red color
plt.plot(thresholds, Daly_TX_threshold_plot2, label='DALY', color='red', linewidth=2)
# Plot the second line with a blue color
plt.plot(thresholds, Cost_TX_threshold_plot, label='Cost', color='blue', linewidth=2)
# Add a legend to the plot
plt.xlabel('Threshold')
plt.ylabel('DALY')
# Add a legend to the plot
plt.legend()
plt.title('Threshold vs NMB, DALY and Cost')
plt.grid(True)
plt.show()

plt.scatter(Daly_TX_threshold_plot, Cost_TX_threshold_plot, label='DALY', color='red', linewidth=2)
plt.xlabel('DALY')
plt.ylabel('Costs')
plt.title('Costs vs DALY')
plt.grid(True)
plt.show()

# plt.scatter(Daly_TX_threshold_plot, Cost_TX_threshold_plot, label='DALY', color=['blue' if t > 0.10653436 else 'red' for t in thresholds], linewidth=2)
# plt.xlabel('DALY')
# plt.ylabel('Costs')
# plt.title('Costs vs DALY')
# plt.grid(True)
# plt.show()

thresholds = [item['threshold'] for item in Daly_Tx_all_sum_threshold]
Daly_TX_threshold_plot = [item['DALY'] for item in Daly_Tx_all_sum_threshold]

plt.scatter(thresholds, Daly_TX_threshold_plot)
plt.xlabel('Threshold')
plt.ylabel('DALY')
plt.title('Threshold vs DALY')
plt.grid(True)
plt.show()


thresholds = [item['threshold'] for item in Cost_Tx_all_sum_threshold]
Cost_TX_threshold_plot = [item['Cost'] for item in Cost_Tx_all_sum_threshold]

plt.scatter(thresholds, Cost_TX_threshold_plot)
plt.xlabel('Threshold')
plt.ylabel('Cost')
plt.title('Threshold vs Cost')
plt.grid(True)
plt.show()


# Number of individuals whose optimal treatment is DLM
thresholds = [item['threshold'] for item in Treat_p_DLM_Pred_threshold]
Treat_p_DLM_Pred_plot = [item['N_p_DLM_Treat'] for item in Treat_p_DLM_Pred_threshold]
Treat_n_DLM_Pred_plot = [item['N_n_DLM_Treat'] for item in Treat_n_DLM_Pred_threshold]

# Plot the first line with a red color
plt.plot(thresholds, Treat_p_DLM_Pred_plot, label='Class FLQ Res', color='red', linewidth=2)
# Plot the second line with a blue color
plt.plot(thresholds, Treat_n_DLM_Pred_plot, label='Class FLQ Sus', color='blue', linewidth=2)
# Add a legend to the plot
plt.legend()
plt.xlabel('Threshold')
plt.ylabel('Number of patients')
plt.title('Number of patients whose optimal treatment is DLM')
plt.grid(True)

plt.savefig(r'/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/N_patients_DLM_threshold.png')


# Show the plot
plt.show()
