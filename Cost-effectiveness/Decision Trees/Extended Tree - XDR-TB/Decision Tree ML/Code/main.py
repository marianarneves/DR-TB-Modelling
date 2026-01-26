# === main.py ===
import os
from load_and_preprocess import load_and_preprocess_data
from features import custom_feature_names
from train_tree import tune_tree_depth, train_final_tree
from plot_tree_utils import save_sklearn_tree, plot_custom_tree
from evaluate_nmb import _prepare_treatment_result
from sklearn.preprocessing import LabelEncoder
from InputData import *
from sklearn.tree import export_text

# Add each folder to the system path
sys.path.append('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Code/Main/Optimism correction')

from PreliminaryDALYs import *

np.random.seed(5)

# === Settings from original code ===
preliminary_daly_costs = calculate_pre_daly_cost_s(
    par_sampler, mainpm_pred_data, DALY_individual_Moldova,
    diseaseprev_sampled_par, prob_sampled_par, cost_sampled_par,
    dalyweight_sampled_par, dalylength_sampled_par,
    sideeffectdaly_sampled_par, sideeffectfreq_sampled_par,
    sideeffectlength_sampled_par,
    wtp_value, par_samplesize
)

method = 'class'

if method == 'pred':

    # Alternative PIDEMp path
    dir_path = '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Decision Tree ML/PM input Only'
    input_file_path = os.path.join(dir_path, 'moldova_data_opt_treat_prediction_allthresholds_wtp1.csv')
    input_file = pd.read_csv(input_file_path)
    DT_plot_file_original = os.path.join(dir_path, 'DT_Opt_Treat.png')
    DT_plot_file_truelabels = os.path.join(dir_path, 'DT_Opt_Treat_Truelabes.png')

    drop_cols = ['Pt_id', 'n', 'Person', 'FLQ_R']

    # === Step 1: Preprocess ===
    _, encoders = load_and_preprocess_data(input_file, drop_cols)
    df_filtered = input_file.drop(columns=drop_cols).fillna(0)

    # Set custom label encoding
    df_filtered['Opt_Treat'] = df_filtered['Opt_Treat'].astype(str).map({'FLQ': 0, 'CLZ': 1})

    label_encoders = {}
    for col in df_filtered.columns:
        if df_filtered[col].dtype == 'object' or df_filtered[col].apply(type).nunique() > 1:
            df_filtered[col] = df_filtered[col].astype(str)
            le = LabelEncoder()
            df_filtered[col] = le.fit_transform(df_filtered[col])
            label_encoders[col] = le

    # === Step 2: Define features and target ===
    X = df_filtered.drop(columns='Opt_Treat')
    y = df_filtered['Opt_Treat']

    # Rename features
    X_renamed = X.rename(columns=custom_feature_names)

    # === Step 3: Tune tree depth ===
    best_depth = tune_tree_depth(X_renamed, y)
    print(f"Best max_depth: {best_depth}")

    # === Step 4: Train final tree ===
    clf = train_final_tree(X_renamed, y, max_depth=best_depth)

    # === Step 4.5: Extract and save decision rules ===
    rules = export_text(clf, feature_names=list(X_renamed.columns))
    rules_output_path = os.path.join(dir_path, 'DT_rules_output.txt')
    with open(rules_output_path, 'w') as f:
        f.write(rules)
    print(f"Decision rules saved to {rules_output_path}")

    # === Step 5: Evaluate performance ===
    y_pred = clf.predict(X_renamed)
    pred_df = pd.DataFrame({
        'Pt_id': input_file['Pt_id'].reset_index(drop=True),
        'observed': input_file['FLQ_R'].reset_index(drop=True),
        'predicted': y_pred
    })

    # === Step 6: Save sklearn tree plot ===
    feature_names_list = list(X_renamed.columns)
    save_sklearn_tree(clf, feature_names_list, DT_plot_file_original)
    print(f"Sklearn tree saved to {DT_plot_file_original}")

    # === Step 7: Save custom tree plot ===
    plot_custom_tree(clf, feature_names_list, ["FLQ", "CLZ"], DT_plot_file_truelabels)
    print(f"Custom tree saved to {DT_plot_file_truelabels}")

    # === Step 8: Calculate NMB and save results ===
    excel_output_path = os.path.join(dir_path, 'DTML_wtpbootstrapping_samplesize200.xlsx')
    test_results = _prepare_treatment_result(pred_df, preliminary_daly_costs, DALY_individual_Moldova, wtp_value, threshold="none")
    results_df = pd.DataFrame(test_results)
    results_df.to_excel(excel_output_path, index=False)
    print(f"NMB results saved to {excel_output_path}")


if method == 'class':

    for i in range(1, 7):
        # Alternative PIDEMc path
        dir_path = '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Decision Tree ML/PM Boostrap'
        input_file_path = os.path.join(dir_path, f'moldova_data_opt_treat_classification_allthresholds_wtp{i}.csv')
        input_file = pd.read_csv(input_file_path)
        DT_plot_file_original_path = os.path.join(dir_path, 'DT_Opt_Treat.png')
        DT_plot_file_truelabels_path = os.path.join(dir_path, 'DT_Opt_Treat_Truelabes.png')

        NMB_threshold = []

        for thresh in input_file['Threshold'].unique():
            subset = input_file[input_file['Threshold'] == thresh]
            # do something with subset
            print(f"Subset for threshold = {thresh}:")

            drop_cols = ['Pt_id', 'n', 'Person', 'FLQ_R']

            # === Step 1: Preprocess ===
            # For preprocessing, drop ID and irrelevant columns and fill missing values
            _, encoders = load_and_preprocess_data(subset, drop_cols)
            # But load_and_preprocess_data returns only filtered data; to match original, do:
            df_filtered = subset.drop(columns=drop_cols)
            df_filtered = df_filtered.fillna(0)

            # Set custom label encoding
            df_filtered['Opt_Treat'] = df_filtered['Opt_Treat'].astype(str).map({'FLQ': 0, 'CLZ': 1})

            label_encoders = {}
            for col in df_filtered.columns:
                if df_filtered[col].dtype == 'object' or df_filtered[col].apply(type).nunique() > 1:
                    df_filtered[col] = df_filtered[col].astype(str)
                    le = LabelEncoder()        # <— This line works now because of the added import
                    df_filtered[col] = le.fit_transform(df_filtered[col])
                    label_encoders[col] = le


            # === Step 2: Define features and target ===
            X = df_filtered.drop(columns='Opt_Treat')
            y = df_filtered['Opt_Treat']

            # Rename features
            X_renamed = X.rename(columns=custom_feature_names)

            # === Step 3: Tune tree depth ===
            best_depth = tune_tree_depth(X_renamed, y)
            print(f"Best max_depth: {best_depth}")

            # === Step 4: Train final tree ===
            clf = train_final_tree(X_renamed, y, max_depth=best_depth)

            # === Step 5: Evaluate performance ===
            y_pred = clf.predict(X_renamed)
            # Combine Pt_id, observed FLQ_R, and predicted
            pred_df = pd.DataFrame({
                'Pt_id': subset['Pt_id'].reset_index(drop=True),
                'observed': subset['FLQ_R'].reset_index(drop=True),
                'predicted': y_pred
            })

            # === Step 6: Calculate NMB and save results ===
            NMB_threshold.extend(_prepare_treatment_result(pred_df, preliminary_daly_costs, DALY_individual_Moldova, wtp_value,
                                                     thresh))

            if thresh > 0.408 and thresh < 0.409:
                # === Step 4.5: Extract and save decision rules ===
                rules = export_text(clf, feature_names=list(X_renamed.columns))
                rules_output_path = os.path.join(dir_path, f'DT_rules_output_WTP{i}.txt')
                with open(rules_output_path, 'w') as f:
                    f.write(rules)
                print(f"Decision rules saved to {rules_output_path}")

            # Output paths
        excel_output_path = os.path.join(dir_path, f'DTML_wtp{i}_bootstrapping_samplesize200.xlsx')

        results_df = pd.DataFrame(NMB_threshold)
        results_df.to_excel(excel_output_path, index=False)
        print(f"NMB results saved to {excel_output_path}")


if method == 'none':
    dir_path = '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Decision Tree ML/Perfect Classifier'
    input_file_path = os.path.join(dir_path, f'moldova_data_opt_treat_classification_allthresholds_wtp2.csv')
    input_file = pd.read_csv(input_file_path)


    pred_df = pd.DataFrame({
        'Pt_id': input_file['Pt_id'].reset_index(drop=True),
        'observed': input_file['FLQ_R'].reset_index(drop=True),
        'predicted': input_file['FLQ_R'].reset_index(drop=True)
    })

    NMB_threshold = _prepare_treatment_result(pred_df, preliminary_daly_costs, DALY_individual_Moldova, wtp_value,
                                                   threshold="none")

    # Output paths
    excel_output_path = os.path.join(dir_path, 'Perfect_Classifier.xlsx')

    results_df = pd.DataFrame(NMB_threshold)
    results_df.to_excel(excel_output_path, index=False)
    print(f"NMB results saved to {excel_output_path}")

