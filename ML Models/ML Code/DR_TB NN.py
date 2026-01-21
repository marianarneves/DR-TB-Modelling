from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
import matplotlib.pyplot as plt
from Functions import *
import ast
import statistics

# Set seed for reproducibility
seed = 27

# Specify the directory to save the plot
save_dir = '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/ML Models/ML Output/NN'/xcc

# Load the dataset
drtb_path = "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_NN.csv"
drtb = pd.read_csv(drtb_path)

# Split target and covariates
y = drtb['FLQ_R']
X = drtb.drop('FLQ_R', axis=1)

# Standardize specific features: 'Age', 'Family_size', and 'Family_size18'
features_to_standardize = ['Age']
scaler = StandardScaler()
X[features_to_standardize] = scaler.fit_transform(X[features_to_standardize])

# Define a neural network model with lbfgs solver, tanh activation, and one hidden layer
model = MLPClassifier(
    hidden_layer_sizes=(X.shape[1] + 2,),
    activation='tanh',
    solver='lbfgs',
    random_state=seed,
    max_iter=10000
)

# Fit the model on the entire dataset
model.fit(X, y)

# Evaluate the model on full dataset
roc_auc_fulldata, fpr_fulldata, tpr_fulldata = AUC_performance(model, X, y)
print("All Dataset Average AUC - All Features:", roc_auc_fulldata)
fpr_cv_full, tpr_cv_full, roc_auc_cv_full = cross_validate(model, X, y, 5, seed)
print("CV Average AUC - All Features:", statistics.mean(roc_auc_cv_full))

# Compute permutation importance
perm_importance = permutation_importance(model, X, y, n_repeats=10, random_state=seed)
sorted_feature_indices = np.argsort(perm_importance.importances_mean)[::-1]
num_selected_features = 30
selected_features = X.columns[sorted_feature_indices[:num_selected_features]]
print(selected_features)

selected_features = ['Age', 'Family_size', 'Family_size18', 'prevalence_0',
                     'prevalence_1', 'prevalence_2', 'TB_type_1', 'TB_type_2',
                    'Education_1', 'Education_2', 'Occupation_5', 'Microscopy_0',
                     'Urban_0', 'Urban_1', 'Microscopy_1', 'Living_condition_0']

# Define a neural network model with lbfgs solver, tanh activation, and one hidden layer with selected features only
model = MLPClassifier(
    hidden_layer_sizes = (num_selected_features + 2,),
    activation = 'tanh',
    solver = 'lbfgs',
    random_state = seed,
    max_iter=10000
)

# Perform 5-fold cross-validation and get true labels and predicted probabilities
fpr_cv, tpr_cv, roc_auc_cv = cross_validate(model, X, y, 5, seed)

# Plot ROC curves side by side
plt.figure(figsize=(8, 8))

# ROC curve for the full dataset
# plt.subplot(1, 2, 1)
plt.plot(fpr_fulldata, tpr_fulldata, color='darkorange', lw=2, label=f'Full Dataset (AUC = {roc_auc_fulldata:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
#plt.title('Neural Networks - Full dataset - ROC Curve')
plt.legend(loc="lower right")

# Define a list of colors with the same size as the loop range
colors = ['red', 'green', 'blue', 'purple', 'yellow']  # Add more colors as needed

# Loop over the number of folds
for i in range(5):
    # Use the corresponding color for each iteration
    plt.plot(fpr_cv[i], tpr_cv[i], color=colors[i % len(colors)], lw=2, label=f'Fold {[i+1]} (AUC = {roc_auc_cv[i]:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Neural Networks - ROC Curve')
    plt.legend(loc="lower right")

# Automatically save the plot in the specified directory
plt.savefig(save_dir + '/' +  'DR_TB_NN_ROC.png')

plt.show()

########################################
# Calculate the optimism corrected AUC #
########################################
alpha = 0.05

p_corrected, ci_low, ci_high = optimism_corrected_auc("Final Evaluation", model, X, y, 200, alpha, seed,
                                                      selected_features = selected_features)

print("Optimism-Corrected Performance:", p_corrected)
print(f"{(1-alpha)*100}% Bootstrap Confidence Interval: [{ci_low}, {ci_high}]")

bootstrap_performances, bootstrap_selectedfeatures = (
    optimism_corrected_auc("Feature Selection", model, X, y,
                                                     200, alpha, seed, 15 ))


# Flatten the list of lists
all_features = [feature for sublist in bootstrap_selectedfeatures for feature in sublist]

# Count the occurrences of each feature
feature_counts = {feature: all_features.count(feature) for feature in set(all_features)}

# Calculate the percentage of occurrence for each feature
total_samples = len(bootstrap_selectedfeatures)
percentages = {feature: (count / total_samples) * 100 for feature, count in feature_counts.items()}

# Sort the features by their frequency
sorted_features = sorted(percentages.items(), key=lambda x: x[1], reverse=True)

# Extract features and their corresponding percentages
features = [f[0] for f in sorted_features]
percentages = [f[1] for f in sorted_features]

print(features)

# Plot horizontal bar chart
plt.figure(figsize=(10, 8))
plt.barh(features, percentages, color='skyblue')
plt.xlabel('Percentage of Occurrence (%)')
plt.ylabel('Features')
plt.title('Percentage of Occurrence of Features in Bootstrap Samples')
plt.gca().invert_yaxis()  # Invert y-axis to have the most common feature at the top
# Automatically save the plot in the specified directory
plt.savefig(save_dir + '/' +  'DR_TB_NN_FeatureImportance.png')
plt.show()

print(features)
print(len(features))


model = MLPClassifier(
    hidden_layer_sizes=(X.shape[1] + 2,),
    activation='tanh',
    solver='lbfgs',
    random_state=seed,
    max_iter=100000
)

# Fit the model on the entire dataset
model.fit(X, y)

bootstrap_features_p_corrected = {}
bootstrap_p_corrected = []

# Start with the first 5 elements of the features list
features_subset = features[:5]

# Perform computations for subsets starting from 5 elements and increasing by 1 in each iteration
for i in range(5, len(features)):
    print(features_subset)
    p_corrected, _, _ = optimism_corrected_auc("Final Evaluation", model, X, y, 200, alpha, seed,
                                               selected_features=features_subset)
    bootstrap_p_corrected.append(p_corrected)
    bootstrap_features_p_corrected[str(features_subset)] = p_corrected

    # Append the next element to the subset
    features_subset.append(features[i])

# Plotting
plt.plot(range(5, len(features)), bootstrap_p_corrected, marker='o', linestyle='-')
plt.xlabel('Number of features')
plt.ylabel('AUROC')
plt.title('AUROC (Optimism corrected) vs Number of Features')
plt.grid(True)

# Automatically save the plot in the specified directory
plt.savefig(save_dir + '/' +  'DR_TB_NN_optcorrected_PI.png')

plt.show()

selected_features = max(bootstrap_features_p_corrected, key=lambda k: bootstrap_features_p_corrected[k])
print(selected_features)

# Define a neural network model with lbfgs solver, tanh activation, and one hidden layer with selected features only
model = MLPClassifier(
    hidden_layer_sizes = (len(selected_features) + 2,),
    activation = 'tanh',
    solver = 'lbfgs',
    random_state = seed,
    max_iter=10000
)

# Convert to list
selected_features_l = ast.literal_eval(selected_features)

# Convert the list of feature names into a list of column indices
X_selected_columns = X.loc[:, X.columns.isin(selected_features_l)]

# Now, X_selected contains only the columns corresponding to the selected features
model.fit(X_selected_columns, y)

# Evaluate the model on full dataset
roc_auc_fulldata, fpr_fulldata, tpr_fulldata = AUC_performance(model, X_selected_columns, y)

# Perform 5-fold cross-validation and get true labels and predicted probabilities
fpr_cv, tpr_cv, roc_auc_cv = cross_validate(model, X_selected_columns, y, 5, seed)

# Plot ROC curves side by side
plt.figure(figsize=(8, 8))

# ROC curve for the full dataset
# plt.subplot(1, 2, 1)
plt.plot(fpr_fulldata, tpr_fulldata, color='darkorange', lw=2, label=f'Full Data (AUC = {roc_auc_fulldata:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
#plt.title('Neural Networks - Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc="lower right")


# Define a list of colors with the same size as the loop range
colors = ['red', 'green', 'blue', 'purple', 'yellow']  # Add more colors as needed

# Loop over the number of folds
for i in range(5):
    # Use the corresponding color for each iteration
    plt.plot(fpr_cv[i], tpr_cv[i], color=colors[i % len(colors)], lw=2, label=f'Fold {[i+1]} (AUC = {roc_auc_cv[i]:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Neural Networks - PI - ROC Curve')
    plt.legend(loc="lower right")

# Automatically save the plot in the specified directory
plt.savefig(save_dir + '/' +  'DR_TB_NN_ROC_PIfeatures.png')

plt.show()

########################################
# Calculate the optimism corrected AUC #
########################################
alpha = 0.05

p_corrected, ci_low, ci_high = optimism_corrected_auc("Final Evaluation", model, X, y, 200, alpha, seed,
                                                      selected_features = selected_features_l)

print("Optimism-Corrected Performance:", p_corrected)
print(f"{(1-alpha)*100}% Bootstrap Confidence Interval: [{ci_low}, {ci_high}]")

print(selected_features_l)

print("CV Average AUC:", statistics.mean(roc_auc_cv))