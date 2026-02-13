import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
from Functions import *
import statistics

# Set seed for reproducibility
seed = 27

# Specify the directory to save the plot
save_dir = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Modelling/'

# Load the dataset
drtb_path = "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_NN.csv"
drtb = pd.read_csv(drtb_path)

# Split target and covariates
y = drtb['FLQ_R']
X = drtb.drop('FLQ_R', axis=1)

# Standardize specific features: 'Age'
features_to_standardize = ['Age']
scaler = StandardScaler()
X[features_to_standardize] = scaler.fit_transform(X[features_to_standardize])

# Define a logistic regression model with L1 regularization
logreg_model_l1 = LogisticRegression(penalty='l1', solver='liblinear', random_state=seed,  max_iter=10000, C=0.2)

# Perform 5-fold cross-validation - L1 regularization
fpr_cv_logreg_l1, tpr_cv_logreg_l1, roc_auc_cv_logreg_l1 =  cross_validate(logreg_model_l1, X, y, 5, seed)
print("CV Average AUC - L1:", statistics.mean(roc_auc_cv_logreg_l1))
# All data -  L1 regularization
roc_auc_test_alldata_l1, fpr_alldata_l1, tpr_alldata_l1 = AUC_performance(logreg_model_l1, X, y)
print("All Dataset Average AUC - L1:", roc_auc_test_alldata_l1)


# Specify the model without regularization
logreg_model = LogisticRegression(max_iter=10000)

# Pre-fit the model on the entire dataset
logreg_model.fit(X, y)

# Perform 5-fold cross-validation - All features
fpr_cv_logreg_allfeatures, tpr_cv_logreg_allfeatures, roc_auc_cv_logreg_allfeatures =  cross_validate(logreg_model, X, y, 5, seed)
print("CV Average AUC - All Features:", statistics.mean(roc_auc_cv_logreg_allfeatures))
# All data without feature selection
roc_auc_test_alldata_allfeatures, fpr_alldata_allfeatures, tpr_alldata_allfeatures = AUC_performance(logreg_model, X, y)
print("All Dataset Average AUC - All Features:", roc_auc_test_alldata_allfeatures)

# Compute permutation importance
perm_importance = permutation_importance(logreg_model, X, y, n_repeats=10, random_state=seed)
sorted_feature_indices = np.argsort(perm_importance.importances_mean)[::-1]
num_selected_features = 27  # Adjust this based on your preference
selected_features_pi = X.columns[sorted_feature_indices[:num_selected_features]]

# Perform 5-fold cross-validation - PI
fpr_cv_logreg_pi, tpr_cv_logreg_pi, roc_auc_cv_logreg_pi =  cross_validate(logreg_model, X[selected_features_pi], y, 5, seed)
print("CV Average AUC - PI:", statistics.mean(roc_auc_cv_logreg_pi))
# All data - PI
roc_auc_test_alldata_pi, fpr_alldata_pi, tpr_alldata_pi = AUC_performance(logreg_model, X[selected_features_pi], y)
print("All Dataset Average AUC - PI:", roc_auc_test_alldata_pi)

# Initialize RFE with the logistic regression model
rfe = RFE(logreg_model, n_features_to_select=num_selected_features)

# Fit RFE on the entire training data
rfe.fit(X, y)

# Get selected features
selected_features_rfe = X.columns[rfe.support_]

# Perform 5-fold cross-validation - RFE
fpr_cv_logreg_rfe, tpr_cv_logreg_rfe, roc_auc_cv_logreg_rfe = cross_validate(logreg_model, X[selected_features_rfe], y, 5, seed)
print("CV Average AUC - RFE:", statistics.mean(roc_auc_cv_logreg_rfe))
# All data - RFE
roc_auc_test_alldata_rfe, fpr_alldata_rfe, tpr_alldata_rfe = AUC_performance(logreg_model, X[selected_features_rfe], y)
print("All Dataset Average AUC - RFE:", roc_auc_test_alldata_rfe)


# Define a list of colors with the same size as the loop range
colors = ['red', 'green', 'blue', 'purple', 'yellow']  # Add more colors as needed

# Loop over the number of folds
for i in range(5):
    # Use the corresponding color for each iteration
    plt.plot(fpr_cv_logreg_allfeatures[i], tpr_cv_logreg_allfeatures[i], color=colors[i % len(colors)], lw=2, label=f'Fold {[i+1]} (AUC = {roc_auc_cv_logreg_allfeatures[i]:.2f})')
    # All dataset
plt.plot(fpr_alldata_allfeatures, tpr_alldata_allfeatures, color='darkorange', lw=2, label=f'All data (AUC = {roc_auc_test_alldata_pi:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Logistic Regression - All features - ROC Curve')
plt.legend(loc="lower right")

# Automatically save the plot in the specified directory
plt.savefig(save_dir + '/' +  'DR_TB_LR_ROC_allfeatures.png')

plt.show()

# Loop over the number of folds
for i in range(5):
    # Use the corresponding color for each iteration
    plt.plot(fpr_cv_logreg_l1[i], tpr_cv_logreg_l1[i], color=colors[i % len(colors)], lw=2, label=f'Fold {[i+1]} (AUC = {roc_auc_cv_logreg_l1[i]:.2f})')
# All dataset
plt.plot(fpr_alldata_l1, tpr_alldata_l1, color='darkorange', lw=2, label=f'All data (AUC = {roc_auc_test_alldata_l1:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Logistic Regression - L1 - ROC Curve')
plt.legend(loc="lower right")

# Automatically save the plot in the specified directory
plt.savefig(save_dir + '/' +  'DR_TB_LR_ROC_L1.png')

plt.show()

# Loop over the number of folds
for i in range(5):
    # Use the corresponding color for each iteration
    plt.plot(fpr_cv_logreg_pi[i], tpr_cv_logreg_pi[i], color=colors[i % len(colors)], lw=2, label=f'Fold {[i+1]} (AUC = {roc_auc_cv_logreg_rfe[i]:.2f})')
# All dataset
plt.plot(fpr_alldata_pi, tpr_alldata_pi, color='darkorange', lw=2, label=f'All data (AUC = {roc_auc_test_alldata_l1:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Logistic Regression - PI - ROC Curve')
plt.legend(loc="lower right")

# Automatically save the plot in the specified directory
plt.savefig(save_dir + '/' +  'DR_TB_LR_ROC_PI.png')

plt.show()

# Loop over the number of folds
for i in range(5):
    # Use the corresponding color for each iteration
    plt.plot(fpr_cv_logreg_rfe[i], tpr_cv_logreg_rfe[i], color=colors[i % len(colors)], lw=2, label=f'Fold {[i+1]} (AUC = {roc_auc_cv_logreg_pi[i]:.2f})')
# All dataset
plt.plot(fpr_alldata_rfe, tpr_alldata_rfe, color='darkorange', lw=2, label=f'All data (AUC = {roc_auc_test_alldata_rfe:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Logistic Regression - RFE - ROC Curve')
plt.legend(loc="lower right")

# Automatically save the plot in the specified directory
plt.savefig(save_dir + '/' +  'DR_TB_LR_ROC_RFE.png')

plt.show()

######################################
# Calculate the optmism corrected AUC #
#######################################

# Step 1: Compute AUC on the full dataset with the selected features
# All Features
logreg_model.fit(X, y)
y_pred_full_allfeatures = logreg_model.predict(X)
roc_auc_fulldata_allfeatures = roc_auc_score(y, y_pred_full_allfeatures)

# With permutation importance
logreg_model.fit(X[selected_features_pi], y)
y_pred_full_pi = logreg_model.predict(X[selected_features_pi])
roc_auc_fulldata_pi = roc_auc_score(y, y_pred_full_pi)

# With RFE
logreg_model.fit(X[selected_features_rfe], y)
y_pred_full_rfe = logreg_model.predict(X[selected_features_rfe])
roc_auc_fulldata_rfe = roc_auc_score(y, y_pred_full_rfe)

#L1 Regularization
logreg_model_l1.fit(X, y)
y_pred_full_l1 = logreg_model_l1.predict(X)
roc_auc_fulldata_l1 = roc_auc_score(y, y_pred_full_l1)


# Step 2: Bootstrap resampling
num_bootstrap_samples = 200
bootstrap_performances_allfeatures = []
bootstrap_performances_pi = []
bootstrap_performances_rfe = []
bootstrap_performances_l1 = []

for i in range(num_bootstrap_samples):
    # Create a bootstrap sample
    bootstrap_indices = np.random.choice(len(X), len(X), replace=True)
    y_bootstrap = y.iloc[bootstrap_indices]

    X_bootstrap_allfeatures = X.iloc[bootstrap_indices]
    X_bootstrap_pi = X.iloc[bootstrap_indices][selected_features_pi]
    X_bootstrap_rfe = X.iloc[bootstrap_indices][selected_features_rfe]
    X_bootstrap_l1 = X.iloc[bootstrap_indices]

    ### All features

    # Develop bootstrap predictive model - all features
    logreg_model.fit(X_bootstrap_allfeatures, y_bootstrap)
    # Calculate bootstrap performance on bootstrap sample
    y_pred_bootstrap_allfeatures = logreg_model.predict(X_bootstrap_allfeatures)
    bootstrap_performance_allfeatures = roc_auc_score(y_bootstrap, y_pred_bootstrap_allfeatures)
    # Calculate bootstrap performance on the original sample
    y_pred_orig_allfeatures = logreg_model.predict(X)
    orig_performance_allfeatures = roc_auc_score(y, y_pred_orig_allfeatures)
    # Calculate optimism
    optimism_allfeatures = bootstrap_performance_allfeatures - orig_performance_allfeatures
    bootstrap_performances_allfeatures.append(optimism_allfeatures)

    ### PI

    # Develop bootstrap predictive model - PI
    logreg_model.fit(X_bootstrap_pi, y_bootstrap)
    # Calculate bootstrap performance on bootstrap sample
    y_pred_bootstrap_pi = logreg_model.predict(X_bootstrap_pi)
    bootstrap_performance_pi = roc_auc_score(y_bootstrap, y_pred_bootstrap_pi)
    # Calculate bootstrap performance on the original sample
    y_pred_orig_pi = logreg_model.predict(X[selected_features_pi])
    orig_performance_pi = roc_auc_score(y, y_pred_orig_pi)
    # Calculate optimism
    optimism_pi = bootstrap_performance_pi - orig_performance_pi
    bootstrap_performances_pi.append(optimism_pi)

    ### RFE

    # Develop bootstrap predictive model - RFE
    logreg_model.fit(X_bootstrap_rfe, y_bootstrap)
    # Calculate bootstrap performance on bootstrap sample
    y_pred_bootstrap_rfe = logreg_model.predict(X_bootstrap_rfe)
    bootstrap_performance_rfe = roc_auc_score(y_bootstrap, y_pred_bootstrap_rfe)
    # Calculate bootstrap performance on the original sample
    y_pred_orig_rfe = logreg_model.predict(X[selected_features_rfe])
    orig_performance_rfe = roc_auc_score(y, y_pred_orig_rfe)
    # Calculate optimism
    optimism_rfe = bootstrap_performance_rfe - orig_performance_rfe
    bootstrap_performances_rfe.append(optimism_rfe)

    ### l1

    # Develop bootstrap predictive model - L1
    logreg_model_l1.fit(X_bootstrap_l1, y_bootstrap)
    # Calculate bootstrap performance on bootstrap sample
    y_pred_bootstrap_l1 = logreg_model_l1.predict(X_bootstrap_l1)
    bootstrap_performance_l1 = roc_auc_score(y_bootstrap, y_pred_bootstrap_l1)
    # Calculate bootstrap performance on the original sample
    y_pred_orig_l1 = logreg_model_l1.predict(X)
    orig_performance_l1 = roc_auc_score(y, y_pred_orig_l1)
    # Calculate optimism
    optimism_l1 = bootstrap_performance_l1 - orig_performance_l1
    bootstrap_performances_l1.append(optimism_l1)

# Step 3: Calculate the average optimism
average_optimism_allfeatures = np.mean(bootstrap_performances_allfeatures)
average_optimism_pi = np.mean(bootstrap_performances_pi)
average_optimism_rfe = np.mean(bootstrap_performances_rfe)
average_optimism_l1 = np.mean(bootstrap_performances_l1)

# Step 4: Calculate optimism-corrected performance and confidence interval
alpha = 0.05

# All features
p_corrected_allfeatures = roc_auc_fulldata_allfeatures - average_optimism_allfeatures
percentiles_allfeatures = np.percentile(bootstrap_performances_allfeatures, [alpha/2*100, (1-alpha/2)*100])
ci_low_allfeatures = roc_auc_fulldata_allfeatures - percentiles_allfeatures[1]
ci_high_allfeatures = roc_auc_fulldata_allfeatures - percentiles_allfeatures[0]


# PI
p_corrected_pi = roc_auc_fulldata_pi - average_optimism_pi
percentiles_pi = np.percentile(bootstrap_performances_pi, [alpha/2*100, (1-alpha/2)*100])
ci_low_pi = roc_auc_fulldata_pi - percentiles_pi[1]
ci_high_pi = roc_auc_fulldata_pi - percentiles_pi[0]

#RFE
p_corrected_rfe = roc_auc_fulldata_rfe - average_optimism_rfe
percentiles_rfe = np.percentile(bootstrap_performances_rfe, [alpha/2*100, (1-alpha/2)*100])
ci_low_rfe = roc_auc_fulldata_rfe - percentiles_rfe[1]
ci_high_rfe = roc_auc_fulldata_rfe - percentiles_rfe[0]

#RFE
p_corrected_l1 = roc_auc_fulldata_l1 - average_optimism_l1
percentiles_l1 = np.percentile(bootstrap_performances_l1, [alpha/2*100, (1-alpha/2)*100])
ci_low_l1 = roc_auc_fulldata_l1 - percentiles_l1[1]
ci_high_l1 = roc_auc_fulldata_l1 - percentiles_l1[0]

print("Optimism-Corrected Performance - All Features:", p_corrected_allfeatures)
print(f"{(1-alpha)*100}% Bootstrap Confidence Interval: [{ci_low_allfeatures}, {ci_high_allfeatures}]")

print("Optimism-Corrected Performance - PI:", p_corrected_pi)
print(f"{(1-alpha)*100}% Bootstrap Confidence Interval: [{ci_low_pi}, {ci_high_pi}]")

print("Optimism-Corrected Performance - RFE:", p_corrected_rfe)
print(f"{(1-alpha)*100}% Bootstrap Confidence Interval: [{ci_low_rfe}, {ci_high_rfe}]")

print("Optimism-Corrected Performance - L1:", p_corrected_l1)
print(f"{(1-alpha)*100}% Bootstrap Confidence Interval: [{ci_low_l1}, {ci_high_l1}]")
