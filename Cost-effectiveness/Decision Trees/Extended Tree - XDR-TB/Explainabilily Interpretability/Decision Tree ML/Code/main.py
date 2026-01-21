# === main.py ===
import os
from load_and_preprocess import load_and_preprocess_data
from features import custom_feature_names
from train_tree import tune_tree_depth, train_final_tree, tune_tree_pruning, prune_redundant_nodes
from plot_tree_utils import save_sklearn_tree, plot_custom_tree
from evaluate_nmb import _prepare_treatment_result
from sklearn.preprocessing import LabelEncoder
from InputData import *
from sklearn.tree import export_text
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt

# Add each folder to the system path
sys.path.append('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Code/Main/Optimism correction')

from Preliminary_DALY_Class import *

random_state = np.random.seed(42)

preliminary_DALY = Preliminary_DALY(mainpm_pred_data, LE_data)
DALY_individual_Moldova = preliminary_DALY.compute_daly_individual()

# === Settings from original code ===
preliminary_daly_costs = preliminary_DALY.calculate_pre_daly_cost_s(
    par_sampler, mainpm_pred_data, DALY_individual_Moldova,
    diseaseprev_sampled_par, prob_sampled_par, cost_sampled_par,
    dalyweight_sampled_par, dalylength_sampled_par,
    sideeffectdaly_sampled_par, sideeffectfreq_sampled_par,
    sideeffectlength_sampled_par,
    wtp_value, par_samplesize
)

method = 'pred'
pruning = 'pre'

if method == 'pred':

    for i in range(1, 7):
        # Alternative PIDEMp path
        if pruning == "pre":
            dir_path = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/PM input Only/Pre pruning/MaxTreeDepth 5'
        elif pruning == "post":
            dir_path = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/PM input Only/Post pruning/MaxTreeDepth 5'
        else:
            raise ValueError(f"Invalid pruning method: {pruning}. Choose 'pre' or 'post'.")

        input_file_path = f'/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/PM input Only/Input/moldova_data_opt_treat_prediction_allthresholds_wtp{i}.csv'
        input_file = pd.read_csv(input_file_path)
        DT_plot_file_original = os.path.join(dir_path, f'DT_Opt_Treat_wtp{i}.png')
        DT_plot_file_truelabels = os.path.join(dir_path, f'DT_Opt_Treat_Truelabes_wtp{i}.png')

        drop_cols = ['Pt_id', 'n', 'Person', 'FLQ_R', 'Residence']

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
        if pruning == "pre":
            tree_params = tune_tree_depth(X_renamed, y, random_state, max_treedepth = 5)
            print(f"Best max_depth: {tree_params}")
        elif pruning == "post":
            tree_params = tune_tree_pruning(X_renamed, y, random_state)
            print(f"Best ccp_alpha: {tree_params}")
        else:
            raise ValueError(f"Invalid pruning method: {pruning}. Choose 'pre' or 'post'.")

        # === Step 4: Train final tree ===
        clf = train_final_tree(X_renamed, y, random_state, **tree_params)

        prune_redundant_nodes(clf)

        # Save feature importances
        importances = clf.feature_importances_
        importance_df = pd.DataFrame({
            "feature": X_renamed.columns,
            "importance": importances
        })
        importance_df = importance_df.sort_values("importance", ascending=False)

        importance_output_path = os.path.join(dir_path, f"DT_feature_importance_wtp{i}.csv")
        importance_df.to_csv(importance_output_path, index=False)
        print(f"Feature importance saved to {importance_output_path}")

        # === Step 4.5: Extract and save decision rules ===
        rules = export_text(clf, feature_names=list(X_renamed.columns))
        rules_output_path = os.path.join(dir_path, f'DT_rules_output_wtp{i}.txt')
        with open(rules_output_path, 'w') as f:
            f.write(rules)
        print(f"Decision rules saved to {rules_output_path}")

        # === Step 5: Evaluate performance ===
        y_pred = clf.predict(X_renamed)
        pred_df = pd.DataFrame({
            'Pt_id': input_file['Pt_id'].reset_index(drop=True),
            'observed': input_file['Opt_Treat'].reset_index(drop=True),
            'predicted': y_pred,
            'flq_status': input_file['FLQ_R'].reset_index(drop=True)
        })

        # === Step 6: Save sklearn tree plot ===
        feature_names_list = list(X_renamed.columns)
        save_sklearn_tree(clf, feature_names_list, DT_plot_file_original)
        print(f"Sklearn tree saved to {DT_plot_file_original}")

        # === Step 7: Save custom tree plot ===
        plot_custom_tree(clf, feature_names_list, ["FLQ", "CLZ"], DT_plot_file_truelabels)
        print(f"Custom tree saved to {DT_plot_file_truelabels}")

        # === Step 8: Calculate NMB and save results ===
        excel_output_path = os.path.join(dir_path, f'DTML_wtp{i}_bootstrapping_PIDEMp.xlsx')
        test_results = _prepare_treatment_result(pred_df, preliminary_daly_costs, DALY_individual_Moldova, wtp_value, threshold="none")
        results_df = pd.DataFrame(test_results)
        results_df.to_excel(excel_output_path, index=False)
        print(f"NMB results saved to {excel_output_path}")


if method == 'class':

    for i in range(1, 7):
        # Alternative PIDEMc path
        if pruning == "pre":
            dir_path = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/PM Boostrap/Pre pruning/MaxTreeDepth 5'
        elif pruning == "post":
            dir_path = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/PM Boostrap/Post pruning/MaxTreeDepth 5'
        else:
            raise ValueError(f"Invalid pruning method: {pruning}. Choose 'pre' or 'post'.")

        input_file_path = f'/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/PM Boostrap/Input/moldova_data_opt_treat_classification_allthresholds_wtp{i}.csv'
        input_file = pd.read_csv(input_file_path).drop_duplicates(subset=["Threshold", "Person"])
        DT_plot_file_original_path = os.path.join(dir_path, 'DT_Opt_Treat.png')
        DT_plot_file_truelabels_path = os.path.join(dir_path, 'DT_Opt_Treat_Truelabes.png')

        NMB_threshold = []

        for thresh in input_file['Threshold'].unique():
            subset = input_file[input_file['Threshold'] == thresh]
            # do something with subset
            print(f"Subset for threshold = {thresh}:")

            drop_cols = ['Pt_id', 'n', 'Person', 'FLQ_R', 'Residence']

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
            if pruning == "pre":
                tree_params = tune_tree_depth(X_renamed, y, random_state, max_treedepth = 5)
                print(f"Best max_depth: {tree_params}")
            elif pruning == "post":
                tree_params = tune_tree_pruning(X_renamed, y, random_state)
                print(f"Best ccp_alpha: {tree_params}")
            else:
                raise ValueError(f"Invalid pruning method: {pruning}. Choose 'pre' or 'post'.")

            # === Step 4: Train final tree ===
            clf = train_final_tree(X_renamed, y, random_state, **tree_params)

            # === Step 5: Evaluate performance ===
            y_pred = clf.predict(X_renamed)
            # Combine Pt_id, observed FLQ_R, and predicted
            pred_df = pd.DataFrame({
                'Pt_id': subset['Pt_id'].reset_index(drop=True),
                'observed': subset['Opt_Treat'].reset_index(drop=True),
                'predicted': y_pred,
                'flq_status': subset['FLQ_R'].reset_index(drop=True)
            })

            # === Step 6: Calculate NMB and save results ===
            NMB_threshold.extend(_prepare_treatment_result(pred_df, preliminary_daly_costs, DALY_individual_Moldova, wtp_value,
                                                     thresh))

            if thresh > 0.328 and thresh < 0.330:
                # === Step 4.5: Extract and save decision rules ===
                rules = export_text(clf, feature_names=list(X_renamed.columns))
                rules_output_path = os.path.join(dir_path, f"DT_rules_output_WTP{i}_maxNMB_acc_DTML.txt")
                with open(rules_output_path, "w") as f:
                    f.write(rules)

                # === Step 4.6: Save decision tree plot ===
                plt.figure(figsize=(20, 10))
                plot_tree(
                    clf,
                    feature_names=list(X_renamed.columns),
                    class_names=[str(c) for c in clf.classes_],
                    filled=True,
                    rounded=True,
                    fontsize=10
                )
                plot_output_path = os.path.join(dir_path, f"DT_plot_output_WTP{i}_maxNMB_acc_DTML.png")
                plt.savefig(plot_output_path, dpi=300, bbox_inches="tight")
                plt.close()

                print(f"Decision rules saved to {rules_output_path}")
                print(f"Decision tree plot saved to {plot_output_path}")


            if thresh > 0.307 and thresh < 0.308:
                # === Step 4.5: Extract and save decision rules ===
                rules = export_text(clf, feature_names=list(X_renamed.columns))
                rules_output_path = os.path.join(dir_path, f"DT_rules_output_WTP{i}_maxNMB_PIDEMc.txt")
                with open(rules_output_path, "w") as f:
                    f.write(rules)

                # === Step 4.6: Save decision tree plot ===
                plt.figure(figsize=(20, 10))
                plot_tree(
                    clf,
                    feature_names=list(X_renamed.columns),
                    class_names=[str(c) for c in clf.classes_],
                    filled=True,
                    rounded=True,
                    fontsize=10
                )
                plot_output_path = os.path.join(dir_path, f"DT_plot_output_WTP{i}_maxNMB_PIDEMc.png")
                plt.savefig(plot_output_path, dpi=300, bbox_inches="tight")
                plt.close()

                print(f"Decision rules saved to {rules_output_path}")
                print(f"Decision tree plot saved to {plot_output_path}")

            # Output paths
        excel_output_path = os.path.join(dir_path, f'DTML_wtp{i}_bootstrapping_PIDEMc.xlsx')

        results_df = pd.DataFrame(NMB_threshold)
        results_df.to_excel(excel_output_path, index=False)
        print(f"NMB results saved to {excel_output_path}")


if method == 'none':
    dir_path = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/Perfect Classifier'
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

