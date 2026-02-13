import csv
import matplotlib.pyplot as plt
from DR_TB_Classes import *
import pandas as pd

# Read the CSV file with predictions
pred_data = pd.read_csv('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/HM Output/pred_obs_calibrated_model.csv')

# Costs
CostFLQ = 200
CostDLM_FLQ = 700
CostDLM = 300

# Terminal nodes

# Positive tree
T1_p = TerminalNode(name='T1_p', cost=CostFLQ)
T2_p = TerminalNode(name='T2_p', cost=CostDLM_FLQ)
T3_p = TerminalNode(name='T3_p', cost=CostDLM)

# Negative tree
T1_n = TerminalNode(name='T1_n', cost=CostFLQ)
T2_n = TerminalNode(name='T2_n', cost=CostDLM_FLQ)
T3_n = TerminalNode(name='T3_n', cost=CostDLM)

# Not calibrated mode
#csv_file = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/HM Output/sens_spec_adjusted.csv'
# Calibrated model
csv_file = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/HM Output/sens_spec_calibrated_model.csv'

cost_threshold = []
cost_FLQ_P = []
cost_FLQ_N = []

with open(csv_file, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        P_NR_P = float(row['P_NR_P'])
        P_R_P = float(row['P_R_P'])
        P_NR_N = float(row['P_NR_N'])
        P_R_N = float(row['P_R_N'])
        t = float(row['threshold'])

        # Positive tree
        # Chance nodes
        C_FLQ_p = ChanceNode(name='C_FLQ_p', cost=0, future_nodes=[T1_p, T2_p], probs=[P_NR_P, P_R_P])
        # create D1
        D_p = DecisionNode(name='D_p', cost=0, future_nodes=[C_FLQ_p, T3_p])
        # Calculating minimum cost
        if D_p.get_expected_costs()['C_FLQ_p'] > D_p.get_expected_costs()['T3_p']:
            C_p = D_p.get_expected_costs()['T3_p']
        else:
            C_p = D_p.get_expected_costs()['C_FLQ_p']

        cost_FLQ_P.append(D_p.get_expected_costs()['C_FLQ_p'])

        # Negative tree
        # Chance nodes
        C_FLQ_n = ChanceNode(name='C_FLQ_n', cost=0, future_nodes=[T1_n, T2_n], probs=[P_NR_N, P_R_N])
        # create D1
        D_n = DecisionNode(name='D_n', cost=0, future_nodes=[C_FLQ_n, T3_n])
        # Calculating minimum cost
        if D_n.get_expected_costs()['C_FLQ_n'] > D_n.get_expected_costs()['T3_n']:
            C_n = D_n.get_expected_costs()['T3_n']
        else:
            C_n = D_n.get_expected_costs()['C_FLQ_n']

        cost_FLQ_N.append(D_n.get_expected_costs()['C_FLQ_n'])

        cost = 0
        for prediction in pred_data['pred']:
            if prediction > t:
                cost = cost + C_p
            else:
                cost = cost + C_n

        cost_threshold.append({'threshold': t, 'cost': cost})

# Cost with standard treatment
FLQ_R_prev = 0.19 # Assumed prevalence of FLQ resistance
C_Std_Treat = ((1-FLQ_R_prev)*CostFLQ + FLQ_R_prev*CostDLM_FLQ) * 540 # Cost of standard treatment

# cost_threshold is the list of dictionaries
thresholds = [item['threshold'] for item in cost_threshold]
costs = [item['cost'] for item in cost_threshold]

# Plotting the threshold versus cost
plt.scatter(thresholds, costs)
plt.xlabel('Threshold')
plt.ylabel('Cost')
plt.title('Threshold vs Cost')
plt.grid(True)
# Draw a horizontal line at y = 10
plt.axhline(y=C_Std_Treat, color='r', linestyle='--', label='Cost of standard treatment')

# Not calibrated model
#plt.savefig(r'/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Simple Tree/Output/DR_TB_HM_simpleDT_averagecost.png')
# Calibrated model
plt.savefig(r'/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Simple Tree/Output/DR_TB_HM_simpleDT_averagecost_betacalibratedmodel.png')

plt.show()
plt.scatter(thresholds, cost_FLQ_P)
plt.xlabel('Threshold')
plt.ylabel('Cost')
plt.title('Cost of FLQ chance node - P > t')
plt.grid(True)

plt.show()

plt.scatter(thresholds, cost_FLQ_N)
plt.xlabel('Threshold')
plt.ylabel('Cost')
plt.title('Cost of FLQ chance node - P <= t')
plt.grid(True)

plt.show()