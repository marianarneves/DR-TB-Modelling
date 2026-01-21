import pandas as pd
from SampleParameters import *

class PMPerformance:
    def __init__(self, pred_data, par_sampler):
        self.pred_data_bootstrap = pred_data
        self.n_bootstrap_sample = self.pred_data_bootstrap['bootstrap_sample'].nunique()
        self.par_sampler = par_sampler

    def get_bootstrap_sample(self, j):

        pred_data_filtered = self.pred_data_bootstrap.query('bootstrap_sample == @j').drop(columns=['bootstrap_sample'])

        return pred_data_filtered

    def evaluate_pm(self, threshold):
        # Check if the required columns are in the dataframe
        if 'predicted' not in self.pred_data_bootstrap.columns or 'observed' not in self.pred_data_bootstrap.columns:
            raise ValueError("DataFrame must contain 'predicted' and 'observed' columns")

        # Initialize a dictionary to store results for each metric across all bootstrap samples
        results = {
            'Variable': ['TPR', 'TNR', 'FPR', 'FNR', 'positiveclass_proportion', 'negativeclass_proportion']
        }

        for i in range(1, self.n_bootstrap_sample + 1):
            pred_data_bootstrapsample = self.get_bootstrap_sample(i)  # Ensure a copy is made

            # Add classification column based on the threshold
            pred_data_bootstrapsample['classification'] = (pred_data_bootstrapsample['predicted'] >= threshold).astype(int)

            # Calculate True Positives (TP), True Negatives (TN), False Positives (FP), and False Negatives (FN)
            TP = ((pred_data_bootstrapsample['classification'] == 1) & (pred_data_bootstrapsample['observed'] == 1)).sum()
            TN = ((pred_data_bootstrapsample['classification'] == 0) & (pred_data_bootstrapsample['observed'] == 0)).sum()
            FP = ((pred_data_bootstrapsample['classification'] == 1) & (pred_data_bootstrapsample['observed'] == 0)).sum()
            FN = ((pred_data_bootstrapsample['classification'] == 0) & (pred_data_bootstrapsample['observed'] == 1)).sum()

            # Calculate TPR, TNR, FPR, and FNR
            TPR = TP / (TP + FN) if (TP + FN) > 0 else 0  # Sensitivity or Recall
            TNR = TN / (TN + FP) if (TN + FP) > 0 else 0  # Specificity
            FPR = FP / (FP + TN) if (FP + TN) > 0 else 0  # Fall-out
            FNR = FN / (TP + FN) if (TP + FN) > 0 else 0  # Miss rate

            # Calculate the proportion of patients classified as positive and negative
            total_patients = len(pred_data_bootstrapsample)
            positiveclass_proportion = (pred_data_bootstrapsample['classification'] == 1).sum() / total_patients
            negativeclass_proportion = (pred_data_bootstrapsample['classification'] == 0).sum() / total_patients

            # Append the results for this bootstrap sample
            results[f'Bootstrap_sample_{i}'] = [
                TPR, TNR, FPR, FNR, positiveclass_proportion, negativeclass_proportion
            ]

        return pd.DataFrame(results)

    def evaluate_pm_sample_dic(self, evaluate_pm_df, j):

        evaluate_pm_dic = dict(zip(evaluate_pm_df['Variable'], evaluate_pm_df[f'Bootstrap_sample_{j}']))

        return evaluate_pm_dic

    def calculate_decisiontree_prob(self, diseaseprev_sampled_par, evaluate_pm_df):

        # Initialize a dictionary to store results for each metric across all bootstrap samples
        results = {
            'Variable': ['P_R_R', 'P_S_S', 'P_R_S', 'P_S_R']
        }


        for j in range(1, self.n_bootstrap_sample + 1):

            sampled_disease_prevalence = self.par_sampler.diseaseprev_input(diseaseprev_sampled_par, j)
            evaluate_pm_dic = self.evaluate_pm_sample_dic(evaluate_pm_df, j)

            # Calculate True Positives (TP), True Negatives (TN), False Positives (FP), and False Negatives (FN)
            P_R_R = evaluate_pm_dic['TPR']/evaluate_pm_dic['positiveclass_proportion'] * sampled_disease_prevalence if evaluate_pm_dic['positiveclass_proportion'] > 0 else 0
            P_S_S = evaluate_pm_dic['TNR']/evaluate_pm_dic['negativeclass_proportion'] * (1-sampled_disease_prevalence) if evaluate_pm_dic['negativeclass_proportion'] > 0 else 0
            P_R_S = 1 - P_S_S
            P_S_R = 1 - P_R_R

            # Append the results for this bootstrap sample
            results[f'Bootstrap_sample_{j}'] = [
                P_R_R, P_S_S, P_R_S, P_S_R
            ]

        return pd.DataFrame(results)


if __name__ == '__main__':
    # Common directory paths
    base_path = '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/'
    hm_output_path = base_path + 'HM/HM Output/'
    cost_effectiveness_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'
    Input_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'
    Ouput_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/'

    # Read data
    booststrap_pred_data = pd.read_csv(
        '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/HM Output/Bootstrap/HM_bootstrap_predictions.csv')
    mainpm_pred_data = pd.read_csv(
        '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/HM Output/Bootstrap/HM_mainPM_predictions.csv')
    prob_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'Probabilities')
    cost_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'Costs')
    dalyweight_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'DALY Weight')
    dalylength_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'DALY Lenght')
    FLQ_Res_prev = 1 - 0.812963
    par_samplesize = 500
    par_sampler = ParameterSampler(FLQ_Res_prev, cost_data_prior, dalyweight_data, dalylength_data,
                                   nsamples=par_samplesize)

    # Sampling from the prior costs
    cost_sampled_par = par_sampler.sample_cost_parameters()
    # Sampling from the prior daly weights
    dalyweight_sampled_par = par_sampler.sample_dalyweight_parameters()
    # Sampling from the prior daly length
    dalylength_sampled_par = par_sampler.sample_dalylength_parameters()
    # Sampling from the prior disease prevalence
    diseaseprev_sampled_par = par_sampler.sample_disease_prevalence()


    # Instantiate PMPerformance with the dataframe
    pm_perf = PMPerformance(booststrap_pred_data, par_sampler)

    bootstrap_sample_id = 2

    # Test get_bootstrap_sample with a specific bootstrap sample ID
    sample_df = pm_perf.get_bootstrap_sample(bootstrap_sample_id)

    # print(f"Data for Bootstrap Sample {bootstrap_sample_id}:")
    # print(sample_df)

    # Evaluate the model with a specific threshold on the full dataset
    # Generate the sequence from 0 to 1 with a step of 0.0025
    threshold_values = np.arange(0, 1.0025, 0.0025)

    # Initialize an empty list to store DataFrames
    evaluate_pm_df_list = []

    # Iterate over threshold values
    for threshold in threshold_values:
        # Evaluate performance for the current threshold
        evaluate_pm_df = pm_perf.evaluate_pm(threshold)

        # Insert a new column with the current threshold value
        evaluate_pm_df['threshold'] = threshold

        # Append the DataFrame to the list
        evaluate_pm_df_list.append(evaluate_pm_df)

    # Concatenate all DataFrames in the list into a single DataFrame
    final_evaluate_pm_df = pd.concat(evaluate_pm_df_list, ignore_index=True)

    # Create a dynamic file path
    file_path_final_evaluate_pm_df = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Tests/Test PM bootstraping/' + f'Booststrap_Sens_Spec.xlsx'
    # Save the DataFrame to an Excel file
    final_evaluate_pm_df.to_excel(
        file_path_final_evaluate_pm_df,
        index=False)

    # print(evaluate_pm_df)
    # test = pm_perf.evaluate_pm_sample_dic(evaluate_pm_df,2)
    # test2 = pm_perf.calculate_decisiontree_prob(diseaseprev_sampled_par, evaluate_pm_df)
    #
    # # # # Output the results
    # print(test)