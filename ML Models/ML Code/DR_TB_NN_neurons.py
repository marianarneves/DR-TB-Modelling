from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
import matplotlib.pyplot as plt
from Functions import *
import ast

# Set seed for reproducibility
seed = 27

# Load the dataset
drtb_path = "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_NN.csv"
drtb = pd.read_csv(drtb_path)

# Split target and covariates
y = drtb['FLQ_R']
X = drtb.drop('FLQ_R', axis=1)

# Standardize specific features: 'Age', 'Family_size', and 'Family_size18'
features_to_standardize = ['Age']
scaler = StandardScaler()
X[features_to_standardize] = scaler.fit_transform(X[features_to_standardize])

# Use same features from paper
selected_features = ['Age', 'Family_size', 'Family_size18', 'prevalence_0',
                     'prevalence_1', 'prevalence_2', 'TB_type_1', 'TB_type_2',
                    'Education_1', 'Education_2', 'Occupation_5', 'Microscopy_0',
                     'Urban_0', 'Urban_1', 'Microscopy_1', 'Living_condition_0']

print(len(selected_features))

# New covariates matrix
X_new = X[selected_features]


roc_auc_tahn = []
fpr_tahn = []
tpr_tahn = []
roc_auc_sig = []
fpr_sig = []
tpr_sig = []

print(range(1, X_new.shape[1] + 3))

for i in range(1, X_new.shape[1] + 3):
    # Define a neural network model with lbfgs solver, tanh activation, and one hidden layer
    model_tanh = MLPClassifier(
        hidden_layer_sizes=(i,),
        activation='tanh',
        solver='lbfgs',
        random_state=seed,
        max_iter=10000
    )

    # Fit the model on the entire dataset
    model_tanh.fit(X_new, y)

    # Evaluate the model on full dataset
    roc_auc_tahn_n, fpr_tahn_n, tpr_tahn_n = AUC_performance(model_tanh, X_new, y)

    roc_auc_tahn.append(roc_auc_tahn_n)
    fpr_tahn.append(fpr_tahn_n)
    tpr_tahn.append(tpr_tahn_n)

    ####### Using Sigmoid Function

    # Define a neural network model with lbfgs solver, tanh activation, and one hidden layer
    model_sig = MLPClassifier(
        hidden_layer_sizes=(i,),
        activation='logistic',
        solver='lbfgs',
        random_state=seed,
        max_iter=10000
    )

    # Fit the model on the entire dataset
    model_sig.fit(X_new, y)

    # Evaluate the model on full dataset
    roc_auc_sig_n, fpr_sig_n, tpr_sig_n = AUC_performance(model_sig, X_new, y)

    roc_auc_sig.append(roc_auc_sig_n)
    fpr_sig.append(fpr_sig_n)
    tpr_sig.append(tpr_sig_n)

# Specify the directory to save the plot
save_dir = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Modelling/'

# Define a list of colors with the same size as the loop range
colors = ['darkorange', 'green', 'blue', 'red', 'purple', 'yellow']  # Add more colors as needed

# Loop over the range of X.shape[1] + 1
for i in range(X_new.shape[1] + 1):
    # Use the corresponding color for each iteration
    plt.plot(fpr_tahn[i], tpr_tahn[i], color=colors[i % len(colors)], lw=2, label=f'#Neurons = {[i+1]} (AUC = {roc_auc_tahn[i]:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Neural Networks - Tahn - ROC Curve')
    plt.legend(loc="lower right")

# Automatically save the plot in the specified directory
plt.savefig(save_dir + '/' +  'DR_TB_NN_ROC_tahn_neurons.png')
plt.show()

# Loop over the range of X.shape[1] + 1
for i in range(X_new.shape[1] + 1):
    # Use the corresponding color for each iteration
    plt.plot(fpr_sig[i], tpr_sig[i], color=colors[i % len(colors)], lw=2, label=f'#Neurons = {[i+1]} (AUC = {roc_auc_sig[i]:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Neural Networks - Sigmoid - ROC Curve')
    plt.legend(loc="lower right")

# Automatically save the plot in the specified directory
plt.savefig(save_dir + '/' +  'DR_TB_NN_ROC_sigmoid_neurons.png')
plt.show()