import pandas as pd
import numpy as np

class ParameterSampler:
    def __init__(self, disease_prevalence, cost_data, dalyweight_data, dalylength_data, nsamples):
        """
        Initialize the ParameterSampler with the provided data and number of samples.

        :param cost_data: DataFrame with 'Cost Variable' and 'Cost Value' columns.
        :param dalyweight_data: DataFrame with 'DALY Weight Variable' and 'DALY Weight Value' columns.
        :param dalylength_data: DataFrame with 'DALY Length Variable' and 'DALY Length Value' columns.
        :param nsamples: Number of samples to generate for each parameter.
        """

        self.disease_prevalence = disease_prevalence
        self.cost_data = cost_data
        self.dalyweight_data = dalyweight_data
        self.dalylength_data = dalylength_data
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

    def diseaseprev_input(self, diseaseprev_sampled_par, j):

        column_name = f'Sample_{j}'
        if column_name in diseaseprev_sampled_par.columns:
            return float(diseaseprev_sampled_par[column_name].values[0])
        else:
            raise ValueError(f"Column {j} is out of range. Valid range is 1 to {self.nsamples}.")


    def cost_daly_input_table(self, cost_sampled_par, dalyweight_sampled_par, dalylength_sampled_par, j):
        cost_data_sampled = dict(zip(cost_sampled_par['Cost Variable'], cost_sampled_par[f'Sample_{j}']))

        sample_j_dalyweight = dalyweight_sampled_par[f'Sample_{j}']
        sample_j_dalylength = dalylength_sampled_par[f'Sample_{j}']
        daly_data_sampled = dict(
            zip(dalyweight_sampled_par['DALY Weight Variable'], sample_j_dalyweight * sample_j_dalylength))

        combined_data_sampled = {**cost_data_sampled, **daly_data_sampled}

        return combined_data_sampled


if __name__ == '__main__':
    # # Initialize data
    # base_path = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/'
    # cost_effectiveness_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'
    #
    # cost_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'Costs')
    # dalyweight_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'DALY Weight')
    # dalylength_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'DALY Lenght')
    #
    # # Create ParameterSampler instance
    # sampler = ParameterSampler(cost_data, dalyweight_data, dalylength_data, nsamples=10)
    #
    # # Generate and display cost samples
    # cost_sampled_par = sampler.sample_cost_parameters()
    # sample_columns_costs = cost_sampled_par.loc[:, 'Sample_1':'Sample_10']
    # average_values_costs = sample_columns_costs.mean(axis=1)
    # new_cost_sampled_par = pd.DataFrame({
    #     'Cost Variable': cost_sampled_par['Cost Variable'],
    #     'Average_Sample_Values': average_values_costs
    # })
    # # print(new_cost_sampled_par)
    #
    # # Generate and display DALY weight samples
    # dalyweight_sampled_par = sampler.sample_dalyweight_parameters()
    # sample_columns_dalyweight = dalyweight_sampled_par.loc[:, 'Sample_1':'Sample_10']
    # average_values_dalyweight = sample_columns_dalyweight.mean(axis=1)
    # new_dalyweight_sampled_par = pd.DataFrame({
    #     'DALY Weight Variable': dalyweight_sampled_par['DALY Weight Variable'],
    #     'Average_Sample_Values': average_values_dalyweight
    # })
    # # print(new_dalyweight_sampled_par)
    #
    # # Generate and display DALY length samples
    # dalylength_sampled_par = sampler.sample_dalylength_parameters()
    # sample_columns_dalylength = dalylength_sampled_par.loc[:, 'Sample_1':'Sample_10']
    # average_values_dalylength = sample_columns_dalylength.mean(axis=1)
    # new_dalylength_sampled_par = pd.DataFrame({
    #     'DALY Length Variable': dalylength_sampled_par['DALY Length Variable'],
    #     'Average_Sample_Values': average_values_dalylength
    # })
    # # print(new_dalylength_sampled_par)
    #
    # test = sampler.cost_daly_input_table(cost_sampled_par, dalyweight_sampled_par, dalylength_sampled_par, 3)
    #
    # df = pd.DataFrame(list(test.items()), columns=['Parameter', 'Value'])
    #
    # print(df)

    import pandas as pd

    # Initialize parameters for testing
    disease_prevalence = 0.2  # Example prevalence rate
    cost_data = pd.DataFrame({'Cost Variable': [], 'Cost Value': []})  # Empty for this test
    dalyweight_data = pd.DataFrame({'DALY Weight Variable': [], 'DALY Weight Value': []})  # Empty for this test
    dalylength_data = pd.DataFrame({'DALY Length Variable': [], 'DALY Length Value': []})  # Empty for this test
    nsamples = 5  # Number of samples

    # Create an instance of the ParameterSampler
    sampler = ParameterSampler(disease_prevalence, cost_data, dalyweight_data, dalylength_data, nsamples)

    # Test the sample_disease_prevalence method
    disease_prevalence_samples = sampler.sample_disease_prevalence()
    # print("Disease Prevalence Samples:")
    # print(disease_prevalence_samples)

    # Test the diseaseprev_input method for each sample
    # for j in range(1, nsamples + 1):
    #     diseaseprev_sampled_input = sampler.diseaseprev_input(disease_prevalence_samples, j)
    #     print(f"\nDisease Prevalence Input for Sample {j}:")
    #     print(diseaseprev_sampled_input)
