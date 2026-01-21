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
_moldova = 5714.43
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
D_DLM_cost = DecisionNode(name='D_DLM_cost', cost=Cost_FLQ, future_nodes=[C_DLM_cost])
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


PM_Cost_threshold = []
PM_DALY_threshold = []

with open(csv_file, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        t = float(row['threshold'])

        Cost = []
        DALY = []

        for i, pred in enumerate(pred_data['pred']):
            if pred > t:
                Cost.append(Exp_FLQ_Cost[i])
                DALY.append(Exp_FLQ_DALY[i])
            else:
                Cost.append(Exp_DLM_cost)
                DALY.append(Exp_DLM_DALY[i])

        PM_Cost_threshold.append({'threshold': t, 'Cost': sum(Cost)})
        PM_DALY_threshold.append({'threshold': t, 'DALY': sum(DALY)})


thresholds = [item['threshold'] for item in PM_Cost_threshold]
PM_Cost_threshold_costvalues = [item['Cost'] for item in PM_Cost_threshold]
PM_DALY_threshold_dalyvalues = [item['DALY'] for item in PM_DALY_threshold]

# Plot Cost
plt.subplot(2, 1, 1)  # Create subplot 1 (top)
plt.plot(thresholds, PM_Cost_threshold_costvalues)
plt.xlabel('Threshold')
plt.ylabel('Cost')
plt.title('Threshold vs Cost')
plt.grid(True)

# Plot DALY
plt.subplot(2, 1, 2)  # Create subplot 2 (bottom)
plt.plot(thresholds, PM_DALY_threshold_dalyvalues)
plt.xlabel('Threshold')
plt.ylabel('DALY')
plt.title('Threshold vs DALY')
plt.grid(True)

plt.tight_layout()  # Adjust subplot parameters to give specified padding
plt.show()

# Comparing with strategy everyone on FLQ
# Everyone on FLQ
FLQ_Cost = sum(StTreat_cost)/540
FLQ_DALY = sum(StTreat_DALY)/540

# Increase from Prediction Model alone compared to everyone in FLQ
Increase_DTPMalone_Cost = [(cost/ 540) - FLQ_Cost for cost in PM_Cost_threshold_costvalues]
Increase_DTPMalone_DALY = [FLQ_DALY - (daly / 540) for daly in PM_DALY_threshold_dalyvalues]

# Plot Cost
plt.subplot(2, 1, 1)  # Create subplot 1 (top)
plt.plot(thresholds, Increase_DTPMalone_Cost)
plt.xlabel('Threshold')
plt.ylabel('Change in Cost')
plt.title('Threshold vs Change in Cost')
plt.grid(True)

# Plot DALY
plt.subplot(2, 1, 2)  # Create subplot 2 (bottom)
plt.plot(thresholds, Increase_DTPMalone_DALY)
plt.xlabel('Threshold')
plt.ylabel('Change in DALY')
plt.title('Threshold vs Change in DALY')
plt.grid(True)

plt.tight_layout()  # Adjust subplot parameters to give specified padding
plt.show()



########## Comparing with strategy of everyone on FLQ ##########

#Cost Everyone on DLM
DLM_DALY = sum(Exp_DLM_DALY)/540
DLM_Cost = Exp_DLM_cost

# Everyone FLQ against Everyone in DLM
Increase_DLM_Cost = DLM_Cost - FLQ_Cost
Increase_DLM_DALY = FLQ_DALY - DLM_DALY

##### Plotting cost against DALYs #####
plt.figure(figsize=(8, 6))  # Set the figure size
plt.scatter(Increase_DTPMalone_DALY, Increase_DTPMalone_Cost, color='blue', label='Prediction Model vs FLQ', s=100)  # Scatter plot for PM vs FLQ
plt.scatter(Increase_DLM_DALY, Increase_DLM_Cost, color='#FFD700', label='Everyone on DLW vs Standard Treatment', marker='X',  s=100)  # Scatter plot for DLM vs FLQ

# Adding FLQ and DLM points
plt.scatter(0, 0, color='red', label='FLQ', marker='o', s=100)  # FLQ point

plt.title('Prediction Model vs Standard Treatment')  # Title of the plot
plt.xlabel('Improve in Health')  # Label for y-axis
plt.ylabel('Increase in Cost')  # Label for x-axis
plt.grid(True)  # Enable grid
plt.legend()  # Show legend
plt.show()  # Display the plot
##### End Plotting cost against DALYs #####