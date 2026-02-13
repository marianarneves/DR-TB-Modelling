import csv
import matplotlib.pyplot as plt
from DR_TB_Classes import *

# Average cost - DT

# Add probability of events
SE_FLQ = 0.12 # Side effects with FLQ
NSE_FLQ = 1 - SE_FLQ  # No side effects with FLQ
SE_DLM = 0.05 # Side effects with DLM
NSE_DLM = 1 - SE_DLM # No side effects with DLM
TPR = 0.75 # True Positive Rate for the threshold using the prediction model
FPR = 1 - TPR # False Positive Rate for the threshold using the prediction model
TNR = 0.6 # True Negative Rate for the threshold using the prediction model
FNR = 1 - TNR # False Negative Rate for the threshold using the prediction model
ExT_FLQ_NSE = 0.98 # Treatment Extension with FLQ and no side effects
Death_FLQ_NSE = 1 - ExT_FLQ_NSE # Death with FLQ  and no side effects
ExT_FLQ_SE = 0.98 # Treatment Extension with FLQ and side effects
Death_FLQ_SE = 1 - ExT_FLQ_SE # Death with FLQ  and side effects
ExT_DLM_NSE = 0.97 # Treatment Extension with DLM with no side effects
Death_DLM_NSE = 1 - ExT_DLM_NSE # Death with DLM with no side effects
ExT_DLM_SE = 0.97 # Treatment Extension with DLM with side effects
Death_DLM_SE = 1 - ExT_DLM_SE # Death with DLM ith side effects
FLQ_Resistant_NSE = 0.97 # FLQ resistance with no side effects
Not_FLQ_Resistant_NSE = 1 - FLQ_Resistant_NSE # No FLQ resistance with no side effects
FLQ_Resistant_SE = 0.97 # FLQ resistance with side effects
Not_FLQ_Resistant_SE = 1 - FLQ_Resistant_SE # No FLQ resistance with side effects
DLM_Resistant_NSE = 0.97 # DLM resistance with no side effects
Not_DLM_Resistant_NSE = 1 - DLM_Resistant_NSE # No DLM resistance with no side effects
DLM_Resistant_SE = 0.97 # DLM resistance with side effects
Not_DLM_Resistant_SE = 1 - DLM_Resistant_SE # No DLM resistance with side effects

# create the terminal nodes
T1 = TerminalNode(name='T1', cost=0)
T2 = TerminalNode(name='T2', cost=100)
T3 = TerminalNode(name='T3', cost=0)
T4 = TerminalNode(name='T4', cost=1000)
T5 = TerminalNode(name='T5', cost=0)
T6 = TerminalNode(name='T6', cost=100)
T7 = TerminalNode(name='T7', cost=0)
T8 = TerminalNode(name='T8', cost=1000)
T9 = TerminalNode(name='T9', cost=0)
T10 = TerminalNode(name='T10', cost=100)
T11 = TerminalNode(name='T11', cost=0)
T12 = TerminalNode(name='T12', cost=1000)
T13 = TerminalNode(name='T13', cost=0)
T14 = TerminalNode(name='T14', cost=100)
T15 = TerminalNode(name='T15', cost=0)
T16 = TerminalNode(name='T16', cost=1000)

# create C14
C14 = ChanceNode(name='C14', cost=0, future_nodes=[T14, T15], probs=[DLM_Resistant_SE, Not_DLM_Resistant_SE])
# create C13
C13 = ChanceNode(name='C13', cost=0, future_nodes=[T10, T11], probs=[DLM_Resistant_NSE, Not_DLM_Resistant_NSE])
# create C12
C12 = ChanceNode(name='C12', cost=0, future_nodes=[T6, T7], probs=[FLQ_Resistant_SE, Not_FLQ_Resistant_SE])
# create C12
C11 = ChanceNode(name='C11', cost=0, future_nodes=[T2, T3], probs=[FLQ_Resistant_NSE, Not_FLQ_Resistant_NSE])
# create C10
C10 = ChanceNode(name='C10', cost=0, future_nodes=[C14, T6], probs=[ExT_DLM_SE, Death_DLM_SE])
# create C9
C9 = ChanceNode(name='C9', cost=0, future_nodes=[C13, T12], probs=[ExT_DLM_NSE, Death_DLM_NSE])
# create C8
C8 = ChanceNode(name='C8', cost=0, future_nodes=[C12, T8], probs=[ExT_FLQ_SE, Death_FLQ_SE])
# create C7
C7 = ChanceNode(name='C7', cost=0, future_nodes=[C11, T4], probs=[ExT_FLQ_NSE, Death_FLQ_NSE])

# Create expected costs list
D1_expected_costs = []
# Initialize list to store weighted average costs
weighted_average_costs = []

csv_file="C:/Users/mraniereneves/OneDrive - Yale University/Yale/TB/Republic of Moldova data/sens_spec.csv"

with open(csv_file, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        TPR = float(row['sensitivity'])
        TNR = float(row['specificity'])

        # Calculate FPR and FNR based on TPR and TNR
        FPR = 1 - TPR
        FNR = 1 - TNR

        # create C6
        C6 = ChanceNode(name='C6', cost=0, future_nodes=[T13, C10], probs=[TNR, FNR])
        # create C5
        C5 = ChanceNode(name='C5', cost=0, future_nodes=[T9, C9], probs=[TNR, FNR])
        # create C4
        C4 = ChanceNode(name='C4', cost=0, future_nodes=[T5, C8], probs=[TPR, FPR])
        # create C3
        C3 = ChanceNode(name='C3', cost=0, future_nodes=[T1, C7], probs=[TPR, FPR])
        # create C2
        C2 = ChanceNode(name='C2', cost=0, future_nodes=[C5, C6], probs=[SE_DLM, NSE_DLM])
        # create C1
        C1 = ChanceNode(name='C1', cost=0, future_nodes=[C3, C4], probs=[SE_FLQ, NSE_FLQ])
        # create D1
        D1 = DecisionNode(name='D1', cost=0, future_nodes=[C1, C2])

        D1_expected_costs.append(D1.get_expected_costs())

        # Get the values from the CSV for positive and negative
        positive_value = float(row['positive'])
        negative_value = float(row['negative'])

        weighted_cost = negative_value * D1.get_expected_costs()['C1'] + positive_value * D1.get_expected_costs()['C2']

        weighted_average_costs.append([float(row['threshold']),weighted_cost])


#######

# create C6
C6 = ChanceNode(name='C6', cost=0, future_nodes=[T13, C10], probs=[0, 0])
# create C5
C5 = ChanceNode(name='C5', cost=0, future_nodes=[T9, C9], probs=[0,  0])
# create C4
C4 = ChanceNode(name='C4', cost=0, future_nodes=[T5, C8], probs=[0.8, 0.2])
# create C3
C3 = ChanceNode(name='C3', cost=0, future_nodes=[T1, C7], probs=[0.8, 0.2])
# create C2
C2 = ChanceNode(name='C2', cost=0, future_nodes=[C5, C6], probs=[SE_DLM, NSE_DLM])
# create C1
C1 = ChanceNode(name='C1', cost=0, future_nodes=[C3, C4], probs=[SE_FLQ, NSE_FLQ])
# create D1
D1 = DecisionNode(name='D1', cost=0, future_nodes=[C1, C2])

no_pm = D1.get_expected_costs()['C1']


# Extract the first and second elements from each sublist
first_elements = [sublist[0] for sublist in weighted_average_costs]
second_elements = [sublist[1] for sublist in weighted_average_costs]

# Plot the first element versus the second element
plt.plot(first_elements, second_elements, 'o')
plt.xlabel('Threshold')
plt.ylabel('Weighted Average Cost')
plt.title('Weighted Average Cost of TB treatment with HLR')
plt.grid(True)

# Draw a horizontal line at y = 10
plt.axhline(y=no_pm, color='r', linestyle='--', label='y=10')


plt.savefig(r'C:\Users\mraniereneves\OneDrive - Yale University\Yale\TB\Modelling\DR_TB_HM_averagecost.png')

plt.show()
