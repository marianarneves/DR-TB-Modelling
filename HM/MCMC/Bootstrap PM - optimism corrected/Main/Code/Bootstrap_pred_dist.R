# Load necessary libraries
library(dplyr)    # For data manipulation
library(ggplot2)  # For data visualization

# 1. Load Data
# Reading a CSV file into a dataframe called `HM_bootstrap`. The `header = TRUE` argument ensures
# that the first row of the CSV is treated as column names.
HM_bootstrap = read.csv(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/Bootstrap PM - optimism corrected/Main/Output/cons_D201/HM_bootstrap_d2_01_platt_beta_compare_1000000runs.csv',
  header = TRUE
) %>%
  rename(predicted_beta_origdata = predicted_beta_origidata)


# 2. Average Prevalence Calculation and Histogram Plot
# Here, `HM_bootstrap` is grouped by `bootstrap_sample`, and the mean of `observed_bootstrap` is
# calculated for each group. This aggregated data is saved as `bootstrap_sample_prev`.
bootstrap_sample_prev = HM_bootstrap %>%
  group_by(bootstrap_sample) %>%
  summarise(prevalence = mean(observed_bootstrap))

# Plot a histogram of `prevalence` values to show the distribution of average prevalence
# across bootstrap samples. Setting `binwidth = 0.008` controls the granularity of the histogram.
ggplot(bootstrap_sample_prev, aes(x = prevalence)) +
  geom_histogram(binwidth = 0.008, fill = "skyblue", color = "black", alpha = 0.7) +
  labs(title = "Distribution of Prevalence", x = "Prevalence", y = "Frequency") +
  theme_minimal()

# 3. Mean Predicted Prevalence by Observed Bootstrap
# Here, `HM_bootstrap` is grouped by both `bootstrap_sample` and `observed_bootstrap`, and the
# mean of `predicted_beta_bootstrap` is calculated for each group. The result is stored in
# `bootstrap_sample_meanpred`.
# Create a combined data frame for all predictions
combined_data <- HM_bootstrap %>%
  select(bootstrap_sample, observed_bootstrap,
         predicted_platt_bootstrap, predicted_beta_bootstrap,
         predicted_platt_origdata, predicted_beta_origdata) %>%
  pivot_longer(
    cols = starts_with("predicted"),
    names_to = c("method", "data_source"),
    names_pattern = "predicted_(.*)_(.*)",  # Use names_pattern for more control
    values_to = "prediction"
  ) %>%
  mutate(method = recode(method,
                         platt = "Platt",
                         beta = "Beta"),
         data_source = recode(data_source,
                              bootstrap = "Bootstrap",
                              origdata = "Original Data")) %>%
  group_by(bootstrap_sample, method, data_source) %>%
  summarise(mean_pred = mean(prediction),
            max_pred = max(prediction),
            min_pred = min(prediction))
  

# Create a combined factor for the fill aesthetic
combined_data$fill_group <- interaction(combined_data$method, combined_data$data_source)

# Plotting the density distributions for Beta and Platt in separate panels
ggplot(combined_data, aes(x = prediction, fill = data_source)) + 
  geom_density(alpha = 0.6, position = "identity") +  # Overlay density plots
  labs(title = "Density Distributions of Predicted Prevalence",
       x = "Predicted Prevalence",
       y = "Density") +
  theme_minimal() +
  scale_fill_brewer(palette = "Set1", name = "Data Source") +
  theme(legend.title = element_blank()) +
  facet_wrap(~ method)  # Separate the plots by method


# 4. Minimum Predicted Prevalence by Observed Bootstrap
# Plotting the density distributions for Beta and Platt in separate panels
ggplot(combined_data, aes(x = min_pred, fill = data_source)) + 
  geom_density(alpha = 0.6, position = "identity") +  # Overlay density plots
  labs(title = "Density Distributions of Minimum Predicted Values",
       x = "Minimum Predicted",
       y = "Density") +
  theme_minimal() +
  scale_fill_brewer(palette = "Set1", name = "Data Source") +
  theme(legend.title = element_blank()) +
  facet_wrap(~ method) +  # Separate the plots by method
  xlim(0, 1)  # Set x-axis limits from 0 to 1


# 5. Maximum Predicted Prevalence by Observed Bootstrap
ggplot(combined_data, aes(x = max_pred, fill = data_source)) + 
  geom_density(alpha = 0.6, position = "identity") +  # Overlay density plots
  labs(title = "Density Distributions of Maximum Predicted Values",
       x = "Maximum Predicted",
       y = "Density") +
  theme_minimal() +
  scale_fill_brewer(palette = "Set1", name = "Data Source") +
  theme(legend.title = element_blank()) +
  facet_wrap(~ method) +  # Separate the plots by method
  xlim(0, 1)  # Set x-axis limits from 0 to 1