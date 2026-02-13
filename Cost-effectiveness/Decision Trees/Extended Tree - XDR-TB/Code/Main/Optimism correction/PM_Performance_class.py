import pandas as pd
from SampleParameters import *


class PMPerformance:
    def __init__(self, mainpm_pred_data, booststrap_pred_data, par_sampler):
        self.pred_data_main = mainpm_pred_data.copy()
        self.pred_data_bootstrap = booststrap_pred_data.copy()
        self.bootstrap_samples = self.pred_data_bootstrap['bootstrap_sample']
        self.n_bootstrap_sample = self.bootstrap_samples.nunique()
        self.par_sampler = par_sampler

    def get_bootstrap_sample(self, j, pred_data):
        return pred_data.loc[pred_data['bootstrap_sample'] == j].drop(columns=['bootstrap_sample'])

    def get_pred_sample(self, column_name):
        cols = self.pred_data_bootstrap.columns
        if 'predicted' in cols and 'observed' in cols:
            return self.pred_data_bootstrap

        selected_columns = self.pred_data_bootstrap.filter(like=column_name).copy()
        selected_columns['bootstrap_sample'] = self.bootstrap_samples

        # Use vectorized str.replace for renaming
        selected_columns.columns = selected_columns.columns.str.replace('predicted.*', 'predicted', regex=True)\
                                                           .str.replace('observed.*', 'observed', regex=True)
        return selected_columns

    def _calculate_metrics(self, pred_data, threshold):
        classification = (pred_data['predicted'] >= threshold).astype(int)
        observed = pred_data['observed']

        TP = ((classification == 1) & (observed == 1)).sum()
        TN = ((classification == 0) & (observed == 0)).sum()
        FP = ((classification == 1) & (observed == 0)).sum()
        FN = ((classification == 0) & (observed == 1)).sum()

        TP_FN = TP + FN
        TN_FP = TN + FP
        total_patients = len(pred_data)
        positiveclass = classification.sum()
        negativeclass = total_patients - positiveclass

        TPR = TP / TP_FN if TP_FN else 0
        TNR = TN / TN_FP if TN_FP else 0
        FPR = FP / TN_FP if TN_FP else 0
        FNR = FN / TP_FN if TP_FN else 0

        return [
            TP, TN, FP, FN,
            TPR, TNR, FPR, FNR,
            positiveclass, negativeclass,
            positiveclass / total_patients,
            negativeclass / total_patients,
            observed.sum() / total_patients
        ]


    def evaluate_pm(self, threshold, data):
        data_source_map = {
            'main': self.pred_data_main,
            'bootstrap': self.get_pred_sample('bootstrap'),
            'oob_sample': self.get_pred_sample('oob_sample'),
            'origdata': self.get_pred_sample('origdata')
        }

        pred_data = data_source_map.get(data)
        if pred_data is None:
            raise ValueError("Invalid data source specified")

        if 'predicted' not in pred_data.columns or 'observed' not in pred_data.columns:
            raise ValueError("DataFrame must contain 'predicted' and 'observed' columns")

        results = {
            'Variable': ['TP', 'TN', 'FP', 'FN', 'TPR', 'TNR', 'FPR', 'FNR',
                         'positiveclass', 'negativeclass', 'positiveclass_proportion',
                         'negativeclass_proportion', 'disease_prev_dataset']
        }

        if data == 'main':
            results['Value'] = self._calculate_metrics(pred_data, threshold)
        else:
            for i in range(1, self.n_bootstrap_sample + 1):
                sample_data = self.get_bootstrap_sample(i, pred_data)
                results[f'Bootstrap_sample_{i}'] = self._calculate_metrics(sample_data, threshold)

        return pd.DataFrame(results)

    def evaluate_pm_sample_dic(self, evaluate_pm_df, data='None', j='None'):
        if data == 'main':
            return dict(zip(evaluate_pm_df['Variable'], evaluate_pm_df['Value']))

        if j == 'None':
            raise ValueError('Please specify j.')

        return dict(zip(evaluate_pm_df['Variable'], evaluate_pm_df[f'Bootstrap_sample_{j}']))

    def evaluate_pm_thresholds(self, allthresholds, data, bootstrapsample):
        data_source_map = {
            'main': self.pred_data_main,
            'bootstrap': self.get_pred_sample('bootstrap'),
            'oob_sample': self.get_pred_sample('oob_sample'),
            'origdata': self.get_pred_sample('origdata')
        }

        pred_data = data_source_map.get(data)
        if pred_data is None:
            raise ValueError("Invalid data source specified")

        if 'predicted' not in pred_data.columns or 'observed' not in pred_data.columns:
            raise ValueError("DataFrame must contain 'predicted' and 'observed' columns")

        columns = [
            'Threshold', 'TP', 'TN', 'FP', 'FN', 'TPR', 'TNR', 'FPR', 'FNR',
            'PositiveClass', 'NegativeClass', 'PositiveClassProportion',
            'NegativeClassProportion', 'DiseasePrevalence'
        ]
        results = []

        if data == 'main':
            for threshold in allthresholds['threshold']:
                metrics = self._calculate_metrics(pred_data, threshold)
                results.append([threshold] + metrics)
        else:
            sample_data = self.get_bootstrap_sample(bootstrapsample, pred_data)
            for threshold in allthresholds['threshold']:
                metrics = self._calculate_metrics(sample_data, threshold)
                results.append([threshold] + metrics)

        return pd.DataFrame(results, columns=columns)

    def replace_rows_with_min_classes(self, df, minclass_perc):
        required_cols = {'PositiveClass', 'NegativeClass', 'Threshold'}
        if df.empty or not required_cols.issubset(df.columns):
            raise ValueError("Invalid DataFrame: Ensure it has 'PositiveClass', 'NegativeClass', and 'Threshold' columns.")

        df = df.dropna(subset=['PositiveClass', 'NegativeClass'])
        if df.empty:
            raise ValueError("DataFrame is empty after dropping NaN values.")

        total_class_sum = df.loc[0, 'PositiveClass'] + df.loc[0, 'NegativeClass']
        threshold_x = total_class_sum * minclass_perc

        pos_mask = df['PositiveClass'] > threshold_x
        neg_mask = df['NegativeClass'] > threshold_x

        if not pos_mask.any() or not neg_mask.any():
            raise ValueError("No valid rows found with classes above the threshold.")

        min_positiveclass_row = df.loc[pos_mask, 'PositiveClass'].idxmin()
        min_negativeclass_row = df.loc[neg_mask, 'NegativeClass'].idxmin()

        replace_pos_mask = df['PositiveClass'] < threshold_x
        replace_neg_mask = df['NegativeClass'] < threshold_x

        cols_to_replace = [col for col in df.columns if col != 'Threshold']
        df.loc[replace_pos_mask, cols_to_replace] = df.loc[min_positiveclass_row, cols_to_replace].values
        df.loc[replace_neg_mask, cols_to_replace] = df.loc[min_negativeclass_row, cols_to_replace].values

        return df

    def process_row_for_threshold(self, df, threshold):
        row = df[df['Threshold'] == threshold]
        if row.empty:
            raise ValueError(f"No data found for the specified threshold: {threshold}")

        row = row.iloc[0]
        return {
            'Variable': ['TP', 'TN', 'FP', 'FN', 'TPR', 'TNR', 'FPR', 'FNR',
                         'positiveclass', 'negativeclass', 'positiveclass_proportion',
                         'negativeclass_proportion', 'disease_prev_dataset'],
            'Value': [
                row['TP'], row['TN'], row['FP'], row['FN'],
                row['TPR'], row['TNR'], row['FPR'], row['FNR'],
                row['PositiveClass'], row['NegativeClass'],
                row['PositiveClassProportion'], row['NegativeClassProportion'],
                row['DiseasePrevalence']
            ]
        }

    def extract_results_by_threshold(self, bootstrap_results, all_thresholds):
        results_allthresholds = {}
        variables = ['TP', 'TN', 'FP', 'FN', 'TPR', 'TNR', 'FPR', 'FNR',
                     'positiveclass', 'negativeclass', 'positiveclass_proportion',
                     'negativeclass_proportion', 'disease_prev_dataset']

        for threshold in all_thresholds['threshold']:
            results = {'Variable': variables}

            for i in range(1, len(bootstrap_results) + 1):
                bootstrap_key = f'Bootstrap_{i}'
                if bootstrap_key in bootstrap_results:
                    df_results = bootstrap_results[bootstrap_key]
                    row = df_results[df_results['Threshold'] == threshold]

                    if not row.empty:
                        row = row.iloc[0]
                        results[f'Bootstrap_sample_{i}'] = [
                            row['TP'], row['TN'], row['FP'], row['FN'],
                            row['TPR'], row['TNR'], row['FPR'], row['FNR'],
                            row['PositiveClass'], row['NegativeClass'],
                            row['PositiveClassProportion'], row['NegativeClassProportion'],
                            row['DiseasePrevalence']
                        ]

            results_allthresholds[f'Threshold_{threshold}'] = results

        return results_allthresholds

    def extract_row_and_format(self, df_results, threshold):
        row = df_results[df_results['Threshold'] == threshold]
        if row.empty:
            return None

        row = row.iloc[0]
        return {
            'Variable': ['TP', 'TN', 'FP', 'FN', 'TPR', 'TNR', 'FPR', 'FNR',
                         'positiveclass', 'negativeclass', 'positiveclass_proportion',
                         'negativeclass_proportion', 'disease_prev_dataset'],
            'Value': [
                row['TP'], row['TN'], row['FP'], row['FN'],
                row['TPR'], row['TNR'], row['FPR'], row['FNR'],
                row['PositiveClass'], row['NegativeClass'],
                row['PositiveClassProportion'], row['NegativeClassProportion'],
                row['DiseasePrevalence']
            ]
        }

    def _calculate_probabilities(self, evaluate_pm_dic, disease_prevalence):
        tpos_prob = (evaluate_pm_dic['TPR'] * disease_prevalence +
                     evaluate_pm_dic['FPR'] * (1 - disease_prevalence))
        tneg_prob = (evaluate_pm_dic['FNR'] * disease_prevalence +
                     evaluate_pm_dic['TNR'] * (1 - disease_prevalence))

        P_R_R = (evaluate_pm_dic['TPR'] / tpos_prob * disease_prevalence
                 if tpos_prob > 0 else None)
        P_S_S = (evaluate_pm_dic['TNR'] / tneg_prob * (1 - disease_prevalence)
                 if tneg_prob > 0 else None)

        return P_R_R, P_S_S

    def calculate_decisiontree_prob(self, diseaseprev_sampled_par, evaluate_pm_df, sample_disease_prev="N"):
        results = {'Variable': ['P_R_R', 'P_S_S', 'P_R_S', 'P_S_R']}

        for j in range(1, self.n_bootstrap_sample + 1):
            evaluate_pm_dic = self.evaluate_pm_sample_dic(evaluate_pm_df, j=j)

            if sample_disease_prev == "Y":
                disease_prevalence = self.par_sampler.diseaseprev_input(diseaseprev_sampled_par, j)
            else:
                disease_prevalence = evaluate_pm_dic['disease_prev_dataset']

            P_R_R, P_S_S = self._calculate_probabilities(evaluate_pm_dic, disease_prevalence)

            results[f'Bootstrap_sample_{j}'] = [
                P_R_R, P_S_S,
                1 - P_S_S if P_S_S is not None else None,
                1 - P_R_R if P_R_R is not None else None
            ]

        return pd.DataFrame(results)

    def calculate_decisiontree_prob_optcorr(self, evaluate_pm_df_main, evaluate_pm_df_boot, evaluate_pm_df_origdata):
        results = {
            'Variable': [
                'P_R_R', 'P_S_S', 'P_R_S', 'P_S_R',
                'P_R_R_main', 'P_S_S_main', 'positiveclass_main', 'negativeclass_main',
                'P_R_R_boot', 'P_S_S_boot', 'positiveclass_boot', 'negativeclass_boot',
                'P_R_R_orig', 'P_S_S_orig', 'positiveclass_orig', 'negativeclass_orig'
            ]
        }

        evaluate_pm_dic_main = self.evaluate_pm_sample_dic(evaluate_pm_df_main, 'main')

        for j in range(1, self.n_bootstrap_sample + 1):
            evaluate_pm_dic_boot = self.evaluate_pm_sample_dic(evaluate_pm_df_boot, j=j)
            evaluate_pm_dic_orig = self.evaluate_pm_sample_dic(evaluate_pm_df_origdata, j=j)

            P_R_R_main = (evaluate_pm_dic_main['TP'] / evaluate_pm_dic_main['positiveclass']
                          if evaluate_pm_dic_main['positiveclass'] > 0 else None)
            P_S_S_main = (evaluate_pm_dic_main['TN'] / evaluate_pm_dic_main['negativeclass']
                          if evaluate_pm_dic_main['negativeclass'] > 0 else None)

            P_R_R_boot = (evaluate_pm_dic_boot['TP'] / evaluate_pm_dic_boot['positiveclass']
                          if evaluate_pm_dic_boot['positiveclass'] > 0 else None)
            P_S_S_boot = (evaluate_pm_dic_boot['TN'] / evaluate_pm_dic_boot['negativeclass']
                          if evaluate_pm_dic_boot['negativeclass'] > 0 else None)

            P_R_R_orig = (evaluate_pm_dic_orig['TP'] / evaluate_pm_dic_orig['positiveclass']
                          if evaluate_pm_dic_orig['positiveclass'] > 0 else None)
            P_S_S_orig = (evaluate_pm_dic_orig['TN'] / evaluate_pm_dic_orig['negativeclass']
                          if evaluate_pm_dic_orig['negativeclass'] > 0 else None)

            P_R_R = min(max(P_R_R_main - (P_R_R_boot - P_R_R_orig), 0), 1) \
                if None not in (P_R_R_main, P_R_R_boot, P_R_R_orig) else None
            P_S_S = min(max(P_S_S_main - (P_S_S_boot - P_S_S_orig), 0), 1) \
                if None not in (P_S_S_main, P_S_S_boot, P_S_S_orig) else None

            results[f'Bootstrap_sample_{j}'] = [
                P_R_R, P_S_S,
                1 - P_S_S if P_S_S is not None else None,
                1 - P_R_R if P_R_R is not None else None,
                P_R_R_main, P_S_S_main,
                evaluate_pm_dic_main['positiveclass'], evaluate_pm_dic_main['negativeclass'],
                P_R_R_boot, P_S_S_boot,
                evaluate_pm_dic_boot['positiveclass'], evaluate_pm_dic_boot['negativeclass'],
                P_R_R_orig, P_S_S_orig,
                evaluate_pm_dic_orig['positiveclass'], evaluate_pm_dic_orig['negativeclass']
            ]

        return pd.DataFrame(results)

    def calculate_decisiontree_prob_optcorr_beta(self, evaluate_pm_df_main, evaluate_pm_df_boot,
                                                 evaluate_pm_df_origdata):
        results = {'Variable': ['P_R_R', 'P_S_S', 'P_R_S', 'P_S_R']}

        evaluate_pm_dic_main = self.evaluate_pm_sample_dic(evaluate_pm_df_main, 'main')

        for j in range(1, self.n_bootstrap_sample + 1):
            evaluate_pm_dic_boot = self.evaluate_pm_sample_dic(evaluate_pm_df_boot, j=j)
            evaluate_pm_dic_orig = self.evaluate_pm_sample_dic(evaluate_pm_df_origdata, j=j)

            P_R_R_main = (evaluate_pm_dic_main['TP'] + 1) / (evaluate_pm_dic_main['positiveclass'] + 2)
            P_S_S_main = (evaluate_pm_dic_main['TN'] + 1) / (evaluate_pm_dic_main['negativeclass'] + 2)

            P_R_R_boot = (evaluate_pm_dic_boot['TP'] + 1) / (evaluate_pm_dic_boot['positiveclass'] + 2)
            P_S_S_boot = (evaluate_pm_dic_boot['TN'] + 1) / (evaluate_pm_dic_boot['negativeclass'] + 2)

            P_R_R_orig = (evaluate_pm_dic_orig['TP'] + 1) / (evaluate_pm_dic_orig['positiveclass'] + 2)
            P_S_S_orig = (evaluate_pm_dic_orig['TN'] + 1) / (evaluate_pm_dic_orig['negativeclass'] + 2)

            P_R_R = min(max(P_R_R_main - (P_R_R_boot - P_R_R_orig), 0), 1)
            P_S_S = min(max(P_S_S_main - (P_S_S_boot - P_S_S_orig), 0), 1)

            results[f'Bootstrap_sample_{j}'] = [
                P_R_R, P_S_S,
                1 - P_S_S,
                1 - P_R_R
            ]

        return pd.DataFrame(results)

    def calculate_decisiontree_prob_632(self, diseaseprev_sampled_par, evaluate_pm_df_main, evaluate_pm_df_oob,
                                        sample_disease_prev="N"):
        results = {'Variable': ['P_R_R', 'P_S_S', 'P_R_S', 'P_S_R']}

        evaluate_pm_dic_main = self.evaluate_pm_sample_dic(evaluate_pm_df_main, 'main')
        if sample_disease_prev == "N":
            disease_prevalence_main = evaluate_pm_dic_main['disease_prev_dataset']

        for j in range(1, self.n_bootstrap_sample + 1):
            evaluate_pm_dic_oob = self.evaluate_pm_sample_dic(evaluate_pm_df_oob, j=j)

            if sample_disease_prev == "Y":
                disease_prevalence_main = self.par_sampler.diseaseprev_input(diseaseprev_sampled_par, j)
                disease_prevalence_oob = disease_prevalence_main
            else:
                disease_prevalence_oob = evaluate_pm_dic_oob['disease_prev_dataset']

            P_R_R_main, P_S_S_main = self._calculate_probabilities(evaluate_pm_dic_main, disease_prevalence_main)
            P_R_R_oob, P_S_S_oob = self._calculate_probabilities(evaluate_pm_dic_oob, disease_prevalence_oob)

            P_R_R = (0.368 * P_R_R_main + 0.632 * P_R_R_oob if None not in (P_R_R_main, P_R_R_oob) else None)
            P_S_S = (0.368 * P_S_S_main + 0.632 * P_S_S_oob if None not in (P_S_S_main, P_S_S_oob) else None)

            results[f'Bootstrap_sample_{j}'] = [
                P_R_R, P_S_S,
                1 - P_S_S if P_S_S is not None else None,
                1 - P_R_R if P_R_R is not None else None
            ]

        return pd.DataFrame(results)


if __name__ == '__main__':

    from InputData import *

    par_samplesize = 200
    par_sampler = ParameterSampler(FLQ_Res_prev, prob_data_prior, cost_data_prior, dalyweight_data_prior, dalylength_data_prior, sideeffectdaly_data_prior, sideeffectfreq_data_prior, sideeffectlength_data_prior, nsamples=par_samplesize)

    # Sampling from the prior costs
    cost_sampled_par = par_sampler.sample_cost_parameters()
    # Sampling from the prior daly weights
    dalyweight_sampled_par = par_sampler.sample_dalyweight_parameters()
    # Sampling from the prior daly length
    dalylength_sampled_par = par_sampler.sample_dalylength_parameters()
    # Sampling from the prior disease prevalence
    diseaseprev_sampled_par = par_sampler.sample_disease_prevalence()

    # Instantiate PMPerformance with the dataframe
    pm_perf = PMPerformance(mainpm_pred_data, booststrap_pred_data, par_sampler)

    mainpm_pred_data_sorted = mainpm_pred_data.sort_values(by='predicted').reset_index(drop=True)

    # Calculate the average of two consecutive values in the sorted 'prediction' column
    threshold_values = (mainpm_pred_data_sorted['predicted'].shift(-1) + mainpm_pred_data_sorted['predicted']) / 2
    # Drop the last NaN value caused by the shift
    threshold_values = threshold_values.dropna().reset_index(drop=True)

    # # Generate the sequence from 0 to 1 with a step of 0.0025
    # threshold_values = np.arange(0, 1.0025, 0.0025)

    mainpm_pred_data_sorted = mainpm_pred_data.sort_values(by='predicted').reset_index(drop=True)

    # Calculate the average of two consecutive values in the sorted 'prediction' column
    threshold_values = (mainpm_pred_data_sorted['predicted'].shift(-1) + mainpm_pred_data_sorted['predicted']) / 2
    # Drop the last NaN value caused by the shift
    threshold_values = threshold_values.dropna().reset_index(drop=True)

    # Create the DataFrame
    allthresholds = pd.DataFrame({'threshold': threshold_values})

    import pandas as pd

    final_evaluate_pm_df_main = pd.DataFrame()
    final_evaluate_pm_df_boot = pd.DataFrame()  # Initialize an empty DataFrame before the loop
    final_evaluate_pm_df_origdata = pd.DataFrame()
    final_decisiontree_prob_optcorr_df = pd.DataFrame()  # Initialize an empty DataFrame before the loop

    # # Adjusted
    # # Call the function
    # df_results_main = pm_perf.evaluate_pm_thresholds(allthresholds, "main",
    #                                                  bootstrapsample="None")
    #
    # # Set the percentage for replacement (e.g., 10%)
    # minclass_perc = 0.05
    #
    # # Dictionary to store results for each bootstrap sample
    # bootstrap_results = {}
    # origidata_results = {}
    #
    # for i in range(1, par_samplesize + 1):
    #     # Evaluate thresholds for the current bootstrap sample
    #     df_results_bootstrap = pm_perf.evaluate_pm_thresholds(allthresholds, "bootstrap",
    #                                                           bootstrapsample=i)
    #     df_results_origidata = pm_perf.evaluate_pm_thresholds(allthresholds, "origdata",
    #                                                           bootstrapsample=i)
    #     # Update the DataFrame using the replacement function
    #     df_results_bootstrap_updated = pm_perf.replace_rows_with_min_classes(df_results_bootstrap,
    #                                                                          minclass_perc)
    #     df_results_origidata_updated = pm_perf.replace_rows_with_min_classes(df_results_origidata,
    #                                                                          minclass_perc)
    #
    #     # Store the updated DataFrame in the dictionary
    #     bootstrap_results[f'Bootstrap_{i}'] = df_results_bootstrap_updated
    #     origidata_results[f'Bootstrap_{i}'] = df_results_origidata_updated
    #
    # bootstrap_results_bythreshold = pm_perf.extract_results_by_threshold(bootstrap_results,
    #                                                                      allthresholds)
    # origidata_results_bythreshold = pm_perf.extract_results_by_threshold(origidata_results,
    #                                                                      allthresholds)

    for threshold in allthresholds['threshold']:

        start_time = time.time()
        #Original
        evaluate_pm_df_main = pm_perf.evaluate_pm(threshold, 'main')
        evaluate_pm_df_boot = pm_perf.evaluate_pm(threshold, 'bootstrap')
        evaluate_pm_df_origdata = pm_perf.evaluate_pm(threshold, 'origdata')

        decisiontree_prob_optcorr_df = pm_perf.calculate_decisiontree_prob_optcorr(
                                                                           evaluate_pm_df_main,
                                                                           evaluate_pm_df_boot,
                                                                           evaluate_pm_df_origdata)
        elapsed_time_t = time.time() - start_time
        print(f"Threshold {threshold} done in {elapsed_time_t * 1000:.2f} milliseconds.")

        # # Beta
        # evaluate_pm_df_main = pm_perf.evaluate_pm(threshold, 'main')
        # evaluate_pm_df_boot = pm_perf.evaluate_pm(threshold, 'bootstrap')
        # evaluate_pm_df_origdata = pm_perf.evaluate_pm(threshold, 'origdata')
        #
        # decisiontree_prob_optcorr_df = pm_perf.calculate_decisiontree_prob_optcorr_beta(evaluate_pm_df_main,
        #                                                                                     evaluate_pm_df_boot,
        #                                                                                     evaluate_pm_df_origdata)

        # #Adjusted
        # evaluate_pm_df_main = pm_perf.extract_row_and_format(df_results_main, threshold)
        # evaluate_pm_df_boot = bootstrap_results_bythreshold[f'Threshold_{threshold}']
        # evaluate_pm_df_origdata = origidata_results_bythreshold[f'Threshold_{threshold}']
        #
        #
        # decisiontree_prob_optcorr_df = pm_perf.calculate_decisiontree_prob_optcorr(evaluate_pm_df_main,
        #                                                                                evaluate_pm_df_boot,
        #                                                                                evaluate_pm_df_origdata)

        # Add the threshold value as a column
        decisiontree_prob_optcorr_df['threshold'] = threshold
        evaluate_pm_df_boot['threshold'] = threshold
        evaluate_pm_df_main['threshold'] = threshold
        evaluate_pm_df_origdata['threshold'] = threshold

        # Append the current DataFrame to final_df using pd.concat
        final_decisiontree_prob_optcorr_df = pd.concat(
            [final_decisiontree_prob_optcorr_df, decisiontree_prob_optcorr_df], ignore_index=True)
        final_evaluate_pm_df_boot = pd.concat([final_evaluate_pm_df_boot, pd.DataFrame(evaluate_pm_df_boot)], ignore_index=True)
        final_evaluate_pm_df_main = pd.concat([final_evaluate_pm_df_main, pd.DataFrame(evaluate_pm_df_main)], ignore_index=True)
        final_evaluate_pm_df_origdata = pd.concat([final_evaluate_pm_df_origdata, pd.DataFrame(evaluate_pm_df_origdata)], ignore_index=True)


    # Create a dynamic file path

    base_path = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM Bootstrap/Input_V10/'
    file_path_final_evaluate_pm_df_main = base_path + f'MainData_Sens_Spec_alt.xlsx'
    file_path_final_evaluate_pm_df_boot = base_path + f'Booststrap_Sens_Spec_alt.xlsx'
    file_path_final_evaluate_pm_df_origdata = base_path + f'OrigData_Sens_Spec_alt.xlsx'
    file_path_final_evaluate_pm_df = base_path + f'DecisionTree_probs_alt.xlsx'

    # Save the DataFrame to an Excel file
    final_evaluate_pm_df_main.to_excel(
        file_path_final_evaluate_pm_df_main,
        index=False)

    # Save the DataFrame to an Excel file
    final_evaluate_pm_df_boot.to_excel(
        file_path_final_evaluate_pm_df_boot,
        index=False)

    # Save the DataFrame to an Excel file
    final_evaluate_pm_df_origdata.to_excel(
        file_path_final_evaluate_pm_df_origdata,
        index=False)

    # Save the DataFrame to an Excel file
    final_decisiontree_prob_optcorr_df.to_excel(
        file_path_final_evaluate_pm_df,
        index=False)
