import pandas as pd
import numpy as np
from scipy.stats import dirichlet

# Common directory paths
cost_effectiveness_path = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'

prob_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V4_test.xlsx', 'Probabilities')


def sample_prob_parameters(prob_data_prior, n_samples=5):
    data = []
    # Extract unique contexts based on the suffix of the variable names
    prob_data_prior['Category'] = prob_data_prior['Probability Variable'].str.extract(r'_(\w+)$')[0]
    categories = prob_data_prior['Category'].unique()

    # Generate samples for each category
    for category in categories:
        # Filter rows for the current category
        category_data = prob_data_prior[prob_data_prior['Category'] == category]
        alpha = category_data['Probability Value'].values * 100 # the factor multiplying the values specify how disperse is the distribution (c=100 => more concentrated distribution))
        variables = category_data['Probability Variable'].values

        # Generate Dirichlet samples
        samples = np.random.dirichlet(alpha, size=n_samples)
        print(samples)

        # Store the samples in the required format
        for i, var in enumerate(variables):
            data.append([var] + list(samples[:, i]))


    print(data)


    # Convert the results into a DataFrame (if needed)
    columns = ['Probability Variable'] + [f'Sample_{i + 1}' for i in range(n_samples)]
    sampled_data = pd.DataFrame(data, columns=columns)

    # Return or save the results as needed
    return sampled_data

sampled_data = sample_prob_parameters(prob_data_prior, n_samples=10)

print(sampled_data)

