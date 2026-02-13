import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from Functions import *
import statistics

def plot_roc(fpr, tpr, label):
    plt.plot(fpr, tpr, lw=2, label=label)

seed = 27

# Specify the directory to save the plot
save_dir = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Modelling/'

# Load the dataset
drtb_path = "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_NN.csv"
drtb = pd.read_csv(drtb_path)

# Define target and covariates
y = drtb['FLQ_R']
X = drtb.drop('FLQ_R', axis=1)

# Standardize specific features: 'Age'
features_to_standardize = ['Age']
scaler = StandardScaler()
X[features_to_standardize] = scaler.fit_transform(X[features_to_standardize])

# Define a Random Forest model with 100 trees and minimum samples per leaf set to 5
model = RandomForestClassifier(
    n_estimators=100,
    min_samples_leaf=15,
    random_state=7
)

# Perform 5-fold cross-validation without feature selection
fpr_cv_full, tpr_cv_full, roc_auc_cv_full = cross_validate(model, X, y, 5, seed)
print("CV Average AUC - All Features:", statistics.mean(roc_auc_cv_full))
# All data without feature selection
roc_auc_alldata_allfeatures, fpr_alldata_allfeatures, tpr_alldata_allfeatures = AUC_performance(model, X, y)
print("All Dataset Average AUC - All Features:", roc_auc_alldata_allfeatures)

# Select features using permutation importance
selected_features_pi = select_features(model, X, y, random_state = seed, method = "PI", n_repeats = 10, num_selected_features = 12)
#print(selected_features_pi)
# Evaluate the model with selected features from PI
fpr_cv_pi, tpr_cv_pi, roc_auc_cv_pi = cross_validate(model, X[selected_features_pi], y, 5, seed)
print("CV Average AUC - PI:", statistics.mean(roc_auc_cv_pi))
# All data - PI
roc_auc_test_alldata_pi, fpr_alldata_pi, tpr_alldata_pi = AUC_performance(model, X[selected_features_pi], y)
print("All Dataset Average AUC - RFE:", roc_auc_test_alldata_pi)

# Feature selection using RFE
selected_features_rfe = select_features(model, X, y, random_state = seed, method = "RFE", n_repeats = 10, num_selected_features = 12)

#print(selected_features_rfe)

# Evaluate the model with selected features from RFE
fpr_cv_rfe, tpr_cv_rfe, roc_auc_cv_rfe = cross_validate(model, X[selected_features_rfe], y, 5, seed)
print("CV Average AUC - RFE:", statistics.mean(roc_auc_cv_rfe))
# All data - RFE
roc_auc_test_alldata_rfe, fpr_alldata_rfe, tpr_alldata_rfe = AUC_performance(model, X[selected_features_rfe], y)
print("All Dataset Average AUC - RFE:", roc_auc_test_alldata_rfe)


# Define a list of colors with the same size as the loop range
colors = ['red', 'green', 'blue', 'purple', 'yellow']  # Add more colors as needed

# Loop over the number of folds
for i in range(5):
    # Use the corresponding color for each iteration
    plot_roc(fpr_cv_full[i], tpr_cv_full[i], f'CV ROC curve (AUC = {roc_auc_cv_full[i]:.2f}) - All Features')

# All dataset
plt.plot(fpr_alldata_allfeatures, tpr_alldata_allfeatures, color='darkorange', lw=2, label=f'All data (AUC = {roc_auc_alldata_allfeatures:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Random Forest - All Features - ROC Curve')
plt.legend(loc="lower right")

# Automatically save the plot in the specified directory
plt.savefig(save_dir + '/' +  'DR_TB_RF_ROC_allfeatures.png')

plt.show()

# Loop over the number of folds
for i in range(5):
    # Use the corresponding color for each iteration
    plt.plot(fpr_cv_pi[i], tpr_cv_pi[i], color=colors[i % len(colors)], lw=2, label=f'Fold {[i+1]} (AUC = {roc_auc_cv_pi[i]:.2f})')

# All dataset
plt.plot(fpr_alldata_pi, tpr_alldata_pi, color='darkorange', lw=2, label=f'All data (AUC = {roc_auc_test_alldata_pi:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Random Forest - PI - ROC Curve')
plt.legend(loc="lower right")

# Automatically save the plot in the specified directory
plt.savefig(save_dir + '/' +  'DR_TB_RF_ROC_PIfeatures.png')

plt.show()

# Loop over the number of folds
for i in range(5):

    # Use the corresponding color for each iteration
    plt.plot(fpr_cv_rfe[i], tpr_cv_rfe[i], color=colors[i % len(colors)], lw=2, label=f'Fold {[i+1]} (AUC = {roc_auc_cv_rfe[i]:.2f})')
# All dataset
plt.plot(fpr_alldata_rfe, tpr_alldata_rfe, color='darkorange', lw=2, label=f'All data (AUC = {roc_auc_test_alldata_rfe:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Random Forest - RFE - ROC Curve')
plt.legend(loc="lower right")

# Automatically save the plot in the specified directory
plt.savefig(save_dir + '/' +  'DR_TB_RF_ROC_RFEfeatures.png')

plt.show()

# Calculate the optimism corrected AUC
p_corrected_full, ci_low_full, ci_high_full = optimism_corrected_auc("Final Evaluation", model, X, y, 200, 0.05, seed, selected_features= X.columns)
print("Optimism-Corrected Performance (All Features):", p_corrected_full)
print(f"{(1-0.05)*100}% Bootstrap Confidence Interval (All Features): [{ci_low_full}, {ci_high_full}]")

p_corrected_pi, ci_low_pi, ci_high_pi = optimism_corrected_auc("Final Evaluation", model, X, y, 200, 0.05, seed, selected_features= selected_features_pi)
print("Optimism-Corrected Performance (PI):", p_corrected_pi)
print(f"{(1-0.05)*100}% Bootstrap Confidence Interval (PI): [{ci_low_pi}, {ci_high_pi}]")

p_corrected_rfe, ci_low_rfe, ci_high_rfe = optimism_corrected_auc("Final Evaluation", model, X, y, 200, 0.05, seed, selected_features=selected_features_rfe)
print("Optimism-Corrected Performance (RFE):", p_corrected_rfe)
print(f"{(1-0.05)*100}% Bootstrap Confidence Interval (RFE): [{ci_low_rfe}, {ci_high_rfe}]")
