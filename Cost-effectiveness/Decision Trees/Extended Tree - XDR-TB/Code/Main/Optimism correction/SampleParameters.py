import pandas as pd
import numpy as np
import time

class ParameterSampler:
    def __init__(self, disease_prevalence, prob_data, cost_data, dalyweight_data, dalylength_data, sideeffectdaly_data, sideeffectfreq_data, sideeffectlength_data,  nsamples):
        """
        Initialize the ParameterSampler with the provided data and number of samples.

        :param cost_data: DataFrame with 'Cost Variable' and 'Cost Value' columns.
        :param dalyweight_data: DataFrame with 'DALY Weight Variable' and 'DALY Weight Value' columns.
        :param dalylength_data: DataFrame with 'DALY Length Variable' and 'DALY Length Value' columns.
        :param nsamples: Number of samples to generate for each parameter.
        """

        self.disease_prevalence = disease_prevalence
        self.prob_data = prob_data
        self.cost_data = cost_data
        self.dalyweight_data = dalyweight_data
        self.dalylength_data = dalylength_data
        self.sideeffectdaly_data = sideeffectdaly_data
        self.sideeffectfreq_data = sideeffectfreq_data
        self.sideeffectlength_data = sideeffectlength_data
        self.nsamples = nsamples

    def find_beta_alpha_beta(self, mu, sigma2):
        alpha = ((1 - mu) / sigma2 - 1 / mu) * mu ** 2
        beta = alpha * (1 / mu - 1)

        return pd.DataFrame({
            'par': ['alpha', 'beta'],
            'val': [alpha, beta]
        })

    def find_gamma_alpha_beta(self, mu, sigma2):
        alpha = mu ** 2 / sigma2  # shape parameter
        beta = sigma2 / mu  # scale parameter

        return pd.DataFrame({
            'par': ['alpha', 'beta'],
            'val': [alpha, beta]
        })


    def sample_disease_prevalence(self):

        beta_pars = self.find_beta_alpha_beta(self.disease_prevalence, self.disease_prevalence * 0.1)
        alpha = beta_pars.set_index('par').at['alpha', 'val']
        beta = beta_pars.set_index('par').at['beta', 'val']
        samples = np.random.beta(alpha, beta, self.nsamples)

        columns = [f'Sample_{i + 1}' for i in range(self.nsamples)]

        return pd.DataFrame(samples.reshape(1, -1), columns=columns)

    def sample_prob_parameters(self):
        data = []
        # Extract unique contexts based on the suffix of the variable names
        self.prob_data['Category'] = self.prob_data['Probability Variable'].str.extract(r'_(\w+)$')[0]
        categories = self.prob_data['Category'].unique()

        # Generate samples for each category
        for category in categories:
            # Filter rows for the current category
            category_data = self.prob_data[self.prob_data['Category'] == category]
            alpha = category_data[
                        'Probability Value'].values * category_data['Sample Size'].values  # the factor multiplying the values specify how disperse is the distribution (c=100 => more concentrated distribution))
            variables = category_data['Probability Variable'].values

            # Generate Dirichlet samples
            samples = np.random.dirichlet(alpha, size=self.nsamples)

            # Store the samples in the required format
            for i, var in enumerate(variables):
                data.append([var] + list(samples[:, i]))


        # Convert the results into a DataFrame (if needed)
        columns = ['Probability Variable'] + [f'Sample_{i + 1}' for i in range(self.nsamples)]
        sampled_data = pd.DataFrame(data, columns=columns)

        # Return or save the results as needed
        return sampled_data

    def sample_cost_parameters(self):
        data = []
        for _, row in self.cost_data.iterrows():
            cost_variable = row['Cost Variable']
            cost_value = row['Cost Value']

            if cost_value != 0:
                gamma_pars = self.find_gamma_alpha_beta(cost_value, cost_value * 0.1)
                alpha = gamma_pars.set_index('par').at['alpha', 'val']
                beta = gamma_pars.set_index('par').at['beta', 'val']
                samples = np.random.gamma(alpha, beta, self.nsamples)
            else:
                samples = np.zeros(self.nsamples)

            data.append([cost_variable] + list(samples))

        columns = ['Cost Variable'] + [f'Sample_{i + 1}' for i in range(self.nsamples)]
        return pd.DataFrame(data, columns=columns)

    def sample_dalyweight_parameters(self):
        data = []
        for _, row in self.dalyweight_data.iterrows():
            dalyweight_variable = row['DALY Weight Variable']
            dalyweight_value = row['DALY Weight Value']

            if dalyweight_value != 1 and dalyweight_value != 0:
                beta_pars = self.find_beta_alpha_beta(dalyweight_value, dalyweight_value * 0.1)
                alpha = beta_pars.set_index('par').at['alpha', 'val']
                beta = beta_pars.set_index('par').at['beta', 'val']
                samples = np.random.beta(alpha, beta, self.nsamples)
            elif dalyweight_value == 1:
                samples = [1] * self.nsamples
            else:
                samples = np.zeros(self.nsamples)

            data.append([dalyweight_variable] + list(samples))

        columns = ['DALY Weight Variable'] + [f'Sample_{i + 1}' for i in range(self.nsamples)]
        return pd.DataFrame(data, columns=columns)

    def sample_dalylength_parameters(self):
        data = []
        for _, row in self.dalylength_data.iterrows():
            dalylength_variable = row['DALY Length Variable']
            dalylength_value = row['DALY Length Value']

            if dalylength_value != 0:
                gamma_pars = self.find_gamma_alpha_beta(dalylength_value, dalylength_value * 0.1)
                alpha = gamma_pars.set_index('par').at['alpha', 'val']
                beta = gamma_pars.set_index('par').at['beta', 'val']
                samples = np.random.gamma(alpha, beta, self.nsamples)
            else:
                samples = np.zeros(self.nsamples)

            data.append([dalylength_variable] + list(samples))

        columns = ['DALY Length Variable'] + [f'Sample_{i + 1}' for i in range(self.nsamples)]
        return pd.DataFrame(data, columns=columns)

    def sample_sideeffectdaly_parameters(self):
        data = []
        for _, row in self.sideeffectdaly_data.iterrows():
            sideeffectdaly_variable = row['Side Effect DALY Variable']
            sideeffectdaly_value = row['Side Effect DALY Value']
            category = row['Category']

            if sideeffectdaly_value != 1 and sideeffectdaly_value != 0:
                beta_pars = self.find_beta_alpha_beta(sideeffectdaly_value, sideeffectdaly_value * 0.1)
                alpha = beta_pars.set_index('par').at['alpha', 'val']
                beta = beta_pars.set_index('par').at['beta', 'val']
                samples = np.random.beta(alpha, beta, self.nsamples)
            elif sideeffectdaly_value == 1:
                samples = [1] * self.nsamples
            else:
                samples = np.zeros(self.nsamples)

            data.append([category] + [sideeffectdaly_variable] + list(samples))

        columns = ['Category'] + ['Side Effect DALY Variable'] + [f'Sample_{i + 1}' for i in range(self.nsamples)]
        return pd.DataFrame(data, columns=columns)

    def sample_sideeffectfreq_parameters(self):
        data = []
        for _, row in self.sideeffectfreq_data.iterrows():
            sideeffectfreq_variable = row['Side Effect Frequency Variable']
            sideeffectfreq_value = row['Side Effect Frequency Value']
            category = row['Category']

            if sideeffectfreq_value != 1 and sideeffectfreq_value != 0:
                beta_pars = self.find_beta_alpha_beta(sideeffectfreq_value, sideeffectfreq_value * 0.1)
                alpha = beta_pars.set_index('par').at['alpha', 'val']
                beta = beta_pars.set_index('par').at['beta', 'val']
                samples = np.random.beta(alpha, beta, self.nsamples)
            elif sideeffectfreq_value == 1:
                samples = [1] * self.nsamples
            else:
                samples = np.zeros(self.nsamples)

            data.append([category] + [sideeffectfreq_variable] + list(samples))

        columns = ['Category'] + ['Side Effect Frequency Variable'] + [f'Sample_{i + 1}' for i in range(self.nsamples)]
        return pd.DataFrame(data, columns=columns)

    def sample_sideeffectlength_parameters(self):
        data = []
        for _, row in self.sideeffectlength_data.iterrows():
            sideeffectlength_variable = row['Side Effect Length Variable']
            sideeffectlength_value = row['Side Effect Length Value']
            category = row['Category']

            if sideeffectlength_value != 0:
                gamma_pars = self.find_gamma_alpha_beta(sideeffectlength_value, sideeffectlength_value * 0.1)
                alpha = gamma_pars.set_index('par').at['alpha', 'val']
                beta = gamma_pars.set_index('par').at['beta', 'val']
                samples = np.random.gamma(alpha, beta, self.nsamples)
            else:
                samples = np.zeros(self.nsamples)

            data.append([category] + [sideeffectlength_variable] + list(samples))

        columns = ['Category'] + ['Side Effect Length Variable'] + [f'Sample_{i + 1}' for i in range(self.nsamples)]
        return pd.DataFrame(data, columns=columns)


    def diseaseprev_input(self, diseaseprev_sampled_par, j):

        column_name = f'Sample_{j}'
        if column_name in diseaseprev_sampled_par.columns:
            return float(diseaseprev_sampled_par[column_name].values[0])
        else:
            raise ValueError(f"Column {j} is out of range. Valid range is 1 to {self.nsamples}.")


    def prob_cost_daly_input_table(
            self, prob_sampled_par, cost_sampled_par, dalyweight_sampled_par, dalylength_sampled_par,
            sideeffectdaly_sampled_par, sideeffectfreq_sampled_par, sideeffectlength_sampled_par, j
    ):
        # Precompute the column name
        sample_col = f'Sample_{j}'

        # Preload the column data as NumPy arrays for fast operations
        prob_values = prob_sampled_par[sample_col].to_numpy()
        cost_values = cost_sampled_par[sample_col].to_numpy()
        dalyweight_values = dalyweight_sampled_par[sample_col].to_numpy()
        dalylength_values = dalylength_sampled_par[sample_col].to_numpy()
        sideeffectdaly_values = sideeffectdaly_sampled_par[sample_col].to_numpy()
        sideeffectfreq_values = sideeffectfreq_sampled_par[sample_col].to_numpy()
        sideeffectlength_values = sideeffectlength_sampled_par[sample_col].to_numpy()

        # Vectorized dictionary creation
        prob_data_sampled = dict(zip(prob_sampled_par['Probability Variable'], prob_values))

        # COSTS
        cost_data_sampled_ax = dict(zip(cost_sampled_par['Cost Variable'], cost_values))

        Cost_FLQ = cost_data_sampled_ax['Cost_Bedaquiline_firstmonth'] + 5 * cost_data_sampled_ax['Cost_Bedaquiline_afterfirstmonth'] +\
                   6 * (cost_data_sampled_ax['Cost_Pretomanid'] + cost_data_sampled_ax['Cost_Linezolid'] + cost_data_sampled_ax['Cost_Moxifloxacin'] +
                   cost_data_sampled_ax['Cost_Culture_test'] + cost_data_sampled_ax['Cost_monitor_sideeffects'])

        Cost_DLM = cost_data_sampled_ax['Cost_Bedaquiline_firstmonth'] + 5 * cost_data_sampled_ax['Cost_Bedaquiline_afterfirstmonth'] +\
                   6 * (cost_data_sampled_ax['Cost_Pretomanid'] + cost_data_sampled_ax['Cost_Linezolid'] + cost_data_sampled_ax['Cost_Clofazimine'] +
                   cost_data_sampled_ax['Cost_Culture_test'] + cost_data_sampled_ax['Cost_monitor_sideeffects'])

        Cost_Cure_FLQsus = 0

        Cost_Recurrence_FLQsus = cost_data_sampled_ax['Cost_DST'] + 1.1 * (18 * (cost_data_sampled_ax['Cost_Bedaquiline_afterfirstmonth'] +\
                   cost_data_sampled_ax['Cost_Pretomanid'] + cost_data_sampled_ax['Cost_Linezolid'] + cost_data_sampled_ax['Cost_Clofazimine'] +
                   cost_data_sampled_ax['Cost_Culture_test'] + cost_data_sampled_ax['Cost_monitor_sideeffects']))


        Cost_TF_FLQsus = Cost_Recurrence_FLQsus

        Cost_D_FLQsus = 0

        Cost_Cure_FLQres = 0

        Cost_Recurrence_FLQres = Cost_Recurrence_FLQsus

        Cost_TF_FLQres = Cost_Recurrence_FLQsus

        Cost_D_FLQres = 0

        Cost_Cure_DLM = 0

        Cost_Recurrence_DLM = Cost_Recurrence_FLQsus

        Cost_TF_DLM = Cost_Recurrence_FLQsus

        Cost_D_DLM = 0

        cost_data_sampled = {'Cost_FLQ': Cost_FLQ,
                            'Cost_DLM': Cost_DLM,
                            'Cost_Cure_FLQsus': Cost_Cure_FLQsus,
                            'Cost_Recurrence_FLQsus': Cost_Recurrence_FLQsus,
                            'Cost_TF_FLQsus': Cost_TF_FLQsus,
                            'Cost_D_FLQsus': Cost_D_FLQsus,
                            'Cost_Cure_FLQres': Cost_Cure_FLQres,
                            'Cost_Recurrence_FLQres': Cost_Recurrence_FLQres,
                            'Cost_TF_FLQres': Cost_TF_FLQres,
                            'Cost_D_FLQres': Cost_D_FLQres,
                            'Cost_Cure_DLM': Cost_Cure_DLM,
                            'Cost_Recurrence_DLM': Cost_Recurrence_DLM,
                            'Cost_TF_DLM': Cost_TF_DLM,
                            'Cost_D_DLM': Cost_D_DLM
                            }

        # Vectorized DALY computation using NumPy
        daly_values = dalyweight_values * dalylength_values
        daly_data_sampled = dict(zip(dalyweight_sampled_par['DALY Weight Variable'], daly_values))

        # Compute side effect contributions in a vectorized way
        sideeffect_values = sideeffectdaly_values * sideeffectfreq_values * sideeffectlength_values
        # Grouping side effects by category
        categories = sideeffectdaly_sampled_par['Category'].to_numpy()
        unique_categories, indices = np.unique(categories, return_inverse=True)
        grouped_sideeffect_values = np.bincount(indices, weights=sideeffect_values)

        # Convert grouped results into a dictionary
        sideeffect_data_dict = {f'DALY_{category}': value for category, value in
                                zip(unique_categories, grouped_sideeffect_values)}

        # Combine all data
        combined_data_sampled = {**prob_data_sampled, **cost_data_sampled, **daly_data_sampled, **sideeffect_data_dict}

        return combined_data_sampled


if __name__ == '__main__':
    # Common directory paths
    base_path = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/'
    hm_output_path = base_path + 'LR/Output/Optimism Corrected/'
    # hm_output_path_method632 = hm_output_path + 'Method 632/'
    cost_effectiveness_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'
    Input_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'
    Output_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/'

    # Read data
    booststrap_pred_data = pd.read_csv(hm_output_path + 'LR_bootstrap_PlattCalibration.csv')
    # booststrap_pred_data = pd.read_csv(hm_output_path_method632 + 'LR_bootstrap_PlattCalibration_Method632.csv')
    mainpm_pred_data = pd.read_csv(hm_output_path + 'LR_MainPM_PlattCalibration.csv')
    prob_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V9.xlsx', 'Probabilities')
    cost_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V9.xlsx', 'Costs')
    dalyweight_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V9.xlsx', 'DALY Weight')
    dalylength_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V9.xlsx', 'DALY Length')
    sideeffectdaly_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V9.xlsx',
                                              'Side Effects DALY')
    sideeffectfreq_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V9.xlsx',
                                              'Side Effects Frequency')
    sideeffectlength_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V9.xlsx',
                                                'Side Effects Length')

    LE_data = pd.read_csv(cost_effectiveness_path + 'LE_Moldova.csv')

    # Constants
    GDP_moldova = 5714.43
    LE_2019_Moldova = 70.94
    FLQ_Res_prev = 1 - 0.812963

    nsamples = 1000

    parsampler = ParameterSampler(FLQ_Res_prev, prob_data_prior, cost_data_prior, dalyweight_data_prior, dalylength_data_prior, sideeffectdaly_data_prior, sideeffectfreq_data_prior, sideeffectlength_data_prior, nsamples)

    # Sampling from the prior probabilities
    prob_sampled_par = parsampler.sample_prob_parameters()
    # Sampling from the prior costs
    cost_sampled_par = parsampler.sample_cost_parameters()
    # Sampling from the prior daly weights
    dalyweight_sampled_par = parsampler.sample_dalyweight_parameters()
    # Sampling from the prior daly length
    dalylength_sampled_par = parsampler.sample_dalylength_parameters()
    # Sampling from the prior disease prevalence
    diseaseprev_sampled_par = parsampler.sample_disease_prevalence()

    # Sampling from the prior daly weights
    sideeffectdaly_sampled_par = parsampler.sample_sideeffectdaly_parameters()
    # Sampling from the prior daly length
    sideeffectfreq_sampled_par = parsampler.sample_sideeffectfreq_parameters()
    # Sampling from the prior disease prevalence
    sideeffectlength_sampled_par = parsampler.sample_sideeffectlength_parameters()

    # print(sideeffectdaly_sampled_par)
    # print(sideeffectfreq_sampled_par)
    # print(sideeffectlength_sampled_par)

    results = []

    # Start the timer
    # start_time = time.time()
    #
    # for j in range(1, nsamples + 1):  # Replace start_value and end_value with the desired range
    #     result = parsampler.prob_cost_daly_input_table(
    #         prob_sampled_par,
    #         cost_sampled_par,
    #         dalyweight_sampled_par,
    #         dalylength_sampled_par,
    #         sideeffectdaly_sampled_par,
    #         sideeffectfreq_sampled_par,
    #         sideeffectlength_sampled_par,
    #         j
    #     )
    #     results.append(result)
    #
    # # End the timer
    # end_time = time.time()
    #
    # # Calculate the elapsed time
    # elapsed_time = end_time - start_time
    #
    # # Print the results and the elapsed time
    # print(f"Results: {result}")
    # print(f"Elapsed time: {elapsed_time:.2f} seconds")

    results = []

    for j in range(1, nsamples + 1):
        result = parsampler.prob_cost_daly_input_table(
            prob_sampled_par,
            cost_sampled_par,
            dalyweight_sampled_par,
            dalylength_sampled_par,
            sideeffectdaly_sampled_par,
            sideeffectfreq_sampled_par,
            sideeffectlength_sampled_par,
            j
        )
        results.append(result)

    # Compute mean for each key
    keys = results[0].keys()
    averages = {key: np.mean([r[key] for r in results]) for key in keys}

    # Print the results
    for key, value in averages.items():
        print(f"{key}: {value:.4f}")

    # Step 1: Extract all keys
    keys = results[0].keys()

    # Step 2: Compute mean and variance
    summary_data = []
    for key in keys:
        values = [r[key] for r in results]
        mean_val = np.mean(values)
        var_val = np.var(values, ddof=1)  # Sample variance
        summary_data.append({'Parameter': key, 'Mean': mean_val, 'Variance': var_val})

    # Step 3: Create DataFrame
    summary_df = pd.DataFrame(summary_data)

    # Step 4: Save to Excel
    summary_df.to_excel('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/Sampled Parameters/parameter_averages_1000_revision17_07.xlsx', index=False)
    #
    # df = pd.DataFrame(list(averages.items()), columns=["Parameter", "Average"])
    # df.to_excel('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/Sampled Parameters/parameter_averages_1000.xlsx", index=False)