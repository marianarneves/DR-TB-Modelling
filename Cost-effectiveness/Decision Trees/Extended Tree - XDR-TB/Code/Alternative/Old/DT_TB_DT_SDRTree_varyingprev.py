import csv
import matplotlib.pyplot as plt
import pandas as pd
from DR_TB_Classes import *

# Common directory paths
base_path = '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/'
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
Daly_Tx_all_sum_threshold = []
Cost_Tx_all_sum_threshold = []
Treat_p_DLM_Pred_threshold = []
Treat_n_DLM_Pred_threshold = []
Exp_FLQ_cost_s_sum_prev =[]
Exp_FLQ_daly_s_sum_prev =[]

# Define the step size
step_size = 0.01

# Define the vector from 0 to 1 with step size 0.01
vector = [i * step_size for i in range(int(1/step_size) + 1)]

# Iterate over the vector
for value in vector:

    FLQ_Res_prev = 1-value

    ############ Cost ############
    # Standard Treatment
    # Chance Node
    C_FLQ_cost_s = ChanceNode(name='C_FLQ_cost_s', cost=Cost_FLQ, future_nodes=[C_FLQsus_cost, C_FLQres_cost],
                              probs=[(1-FLQ_Res_prev), FLQ_Res_prev])
    # Decision Node
    D_cost_s = DecisionNode(name='D_cost_s', cost=0, future_nodes=[C_FLQ_cost_s])
    # Expected Cost
    Exp_FLQ_cost_s = D_cost_s.get_expected_costs()['C_FLQ_cost_s']

    # DLM
    D_cost = DecisionNode(name='D_cost', cost=0, future_nodes=[C_DLM_cost])
    # Expected Costs
    Exp_DLM_cost = D_cost.get_expected_costs()['C_DLM_cost']
    ############ End Cost ############


    # This for loop iterate over the individuals of the dataset
    Exp_FLQ_daly_s = []
    Treat_DT_Pred = []
    Exp_DALY_DLM = []
    Exp_daly_truth = []
    Exp_cost_truth = []

    for DALY_Death, obs in zip(DALY_individual_Moldova, pred_data['obs']):

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

        # Standard Treatment
        # Chance Node
        C_FLQ_daly_s = ChanceNode(name='C_FLQ_daly_s', cost=DALY_FLQ, future_nodes=[C_FLQsus_DALY, C_FLQres_DALY],
                                  probs=[(1-FLQ_Res_prev), FLQ_Res_prev])
        # Decision Node
        D_daly_s = DecisionNode(name='D_daly_s', cost=0, future_nodes=[C_FLQ_daly_s])
        # Expected Cost
        Exp_FLQ_daly_s.append(D_daly_s.get_expected_costs()['C_FLQ_daly_s'])

        # Everyone receives DLM
        # Decision Node
        D_daly = DecisionNode(name='D_daly', cost=0, future_nodes=[C_DLM_DALY])
        # Expected Costs
        Exp_DALY_DLM.append(D_daly.get_expected_costs()['C_DLM_DALY'])


        # Using the groud truth

        if obs == 1:
            Exp_daly_truth.append(D_daly.get_expected_costs()['C_DLM_DALY'])
            Exp_cost_truth.append(Exp_DLM_cost)
        else:
            # Decision Node
            D_daly_FLQ_truth = DecisionNode(name='D_daly_FLQ_truth', cost=DALY_FLQ, future_nodes=[C_FLQsus_DALY])
            # Expected Cost
            Exp_daly_truth.append(D_daly_FLQ_truth.get_expected_costs()['C_FLQsus_DALY'])
            # Decision Node
            D_cost_FLQ_truth = DecisionNode(name='D_cost_FLQ_truth', cost=Cost_FLQ, future_nodes=[C_FLQsus_cost])
            Exp_cost_truth.append(D_cost_FLQ_truth.get_expected_costs()['C_FLQsus_cost'])

        ############ End DALY ############

    # Summing up the DALYs for the standard treatment
    Exp_FLQ_daly_s_sum = sum(Exp_FLQ_daly_s) # The total DALYs of the satandard treatment is the sum of individual DAlYs
    Exp_FLQ_daly_s_sum_prev.append({'Prev': FLQ_Res_prev, 'DALY_FLQ': Exp_FLQ_daly_s_sum})
    Exp_FLQ_cost_s_sum = Exp_FLQ_cost_s * pred_data.shape[0] # The cost of the same for each individual, therefore the total cost is the individual cost multiplied by number of individuals
    Exp_FLQ_cost_s_sum_prev.append({'Prev': FLQ_Res_prev, 'Cost_FLQ': Exp_FLQ_cost_s_sum})

# Summing up the DALYs for everyone on DLM
Exp_DALY_DLM_sum = sum(Exp_DALY_DLM)  # The total DALYs of the satandard treatment is the sum of individual DAlYs
    # print(Exp_DALY_DLM_sum)
    # Exp_FLQ_cost_s_sum = Exp_FLQ_cost_s * pred_data.shape[
    #     0]  # The cost of the same for each individual, therefore the total cost is the individual cost multiplied by number of individuals

# Summing up for the ground truth
DALY_truth = sum(Exp_daly_truth)/540
Cost_Truth = sum(Exp_cost_truth)/540
print(DALY_truth)
print(Cost_Truth)

# print(540*Exp_DLM_cost)
# print(Exp_DALY_DLM_sum)
# print(Exp_FLQ_daly_s_sum_prev)
# print(Exp_FLQ_cost_s_sum_prev)

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

# Plot Increase_Cost vs Increase_DALY
plt.scatter(Increase_DLM_DALY, Increase_DLM_Cost, label='DLM')
plt.scatter(Increase_Truth_DALY, Increase_Truth_Cost, label='Truth')
plt.scatter(Increase_DTPM_DALY, Increase_DTPM_Cost, label='DT + PM')
# Plot a point at the origin labeled FLQ
plt.scatter(0, 0, color='red', label='FLQ')
# Draw a dashed line between DLM and FLQ points
# plt.plot([0, Increase_DALY], [0, Increase_Cost], color='gray', linestyle='--')
plt.text(0, 0, 'FLQ', verticalalignment='bottom', horizontalalignment='right')
# Label axes and add a legend
plt.xlabel('Increase in health')
plt.ylabel('Increase in Cost')
plt.grid(True)
plt.legend()
plt.show()


#
# Prev = [item['Prev'] for item in Exp_FLQ_daly_s_sum_prev]
# Exp_FLQ_daly_plot = [item['DALY_FLQ'] for item in Exp_FLQ_daly_s_sum_prev]
#
# plt.plot(Prev, Exp_FLQ_daly_plot, linewidth=2)
# plt.axhline(y=Exp_DALY_DLM_sum, color='red', linestyle='--', label='DALY DLM')
# plt.xlabel('FLQ Res Prev')
# plt.ylabel('DALY')
# plt.title('FLQ Resistance Prevalence vs DALY')
# plt.legend()
# plt.grid(True)
# plt.show()
#
# Prev = [item['Prev'] for item in Exp_FLQ_cost_s_sum_prev]
# Exp_FLQ_Cost_plot = [item['Cost_FLQ'] for item in Exp_FLQ_cost_s_sum_prev]
#
# plt.scatter(Prev, Exp_FLQ_Cost_plot, linewidth=2)
# plt.axhline(y=540*Exp_DLM_cost, color='red', linestyle='--', label='Cost DLM')
# plt.xlabel('FLQ Res Prev')
# plt.ylabel('Cost')
# plt.title('FLQ Resistance Prevalence vs Cost')
# plt.legend()
# plt.grid(True)
# plt.show()
#
