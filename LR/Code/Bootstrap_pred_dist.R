# Load necessary libraries
library(dplyr)    # For data manipulation
library(ggplot2)  # For data visualization
library(readxl)
library(stringr)

setwd('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/Test')

# 1. Load Data
# Reading a CSV file into a dataframe called `LR_bootstrap`. The `header = TRUE` argument ensures
# that the first row of the CSV is treated as column names.
LR_bootstrap = read.csv(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/LR_bootstrap_platt_beta_compare.csv',
  header = TRUE
)

# 2. Average Prevalence Calculation and Histogram Plot
# Here, `LR_bootstrap` is grouped by `bootstrap_sample`, and the mean of `observed_bootstrap` is
# calculated for each group. This aggregated data is saved as `bootstrap_sample_prev`.
bootstrap_sample_prev = LR_bootstrap %>%
  group_by(bootstrap_sample) %>%
  summarise(prevalence = mean(observed_bootstrap))

# Plot a histogram of `prevalence` values to show the distribution of average prevalence
# across bootstrap samples. Setting `binwidth = 0.008` controls the granularity of the histogram.
ggplot(bootstrap_sample_prev, aes(x = prevalence)) +
  geom_histogram(binwidth = 0.008, fill = "skyblue", color = "black", alpha = 0.7) +
  labs(title = "Distribution of Prevalence", x = "Prevalence", y = "Frequency") +
  theme_minimal()

# 3. Mean Predicted Prevalence by Observed Bootstrap
# Here, `LR_bootstrap` is grouped by both `bootstrap_sample` and `observed_bootstrap`, and the
# mean of `predicted_beta_bootstrap` is calculated for each group. The result is stored in
# `bootstrap_sample_meanpred`.
# Create a combined data frame for all predictions
combined_data <- LR_bootstrap %>%
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
ggplot(combined_data, aes(x = mean_pred, fill = data_source)) + 
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
# Calculate the minimum max_pred for each data_source and method
min_values <- combined_data %>%
  group_by(data_source, method) %>%
  summarise(min_value = min(max_pred, na.rm = TRUE))

# Plot the density distributions and add vertical lines at the minimum for each data source and method
max_pre_boots_plot = ggplot(combined_data, aes(x = max_pred, fill = data_source)) + 
  geom_density(alpha = 0.6, position = "identity", bw = 0.02) +  # Adjust the bandwidth (smaller = less smooth)
  labs(title = "Distributions of Maximum Predicted Values in the 200 Bootstrap Steps",
       x = "Maximum Predicted",
       y = "Density") +
  theme_minimal() +
  scale_fill_brewer(palette = "Set1", name = "Data Source") +
  theme(legend.title = element_blank()) +
  facet_wrap(~ method) +  # Separate the plots by method
  xlim(0, 1) +  # Set x-axis limits from 0 to 1
  geom_vline(data = min_values, aes(xintercept = min_value, color = data_source),
             linetype = "dashed", size = 0.5) +  # Add vertical dashed lines at min values
  geom_text(data = min_values, aes(x = min_value, y = 0, label = round(min_value, 2)),
            color = "black", vjust = -0.5)  # Annotate the minimum value near the line

ggsave(
  filename = 'max_pre_boots_plot.png',
  plot = max_pre_boots_plot,
  width = 8,
  height = 6,
  bg = "white"
)

# 6. Probabilities in the DT

DecisionTree_probs  = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/Optimism Correction/PM Sample/Original/DecisionTree_probs_alt.xlsx')

#Comparing the probabilities calculated with traditional and alternative
P_R_R = DecisionTree_probs %>%
  filter(Variable == 'P_R_R') %>%
  select(-Variable)

#Select only the alternative calculated probabilities
# Filter rows where Variable column has the suffix "_alt"
   
#Plot all bootstrap samples
plot_data <- P_R_R %>%
 pivot_longer(cols = -threshold, names_to = "metric", values_to = "value")

# Plot the data without legend
P_R_R_bootstrap_trajectory_plot = ggplot(plot_data, aes(x = threshold, y = value, color = metric)) +
  geom_line() +
  labs(x = "Threshold", y = "P(D+|T+)", title = "Trajectory of 200 Bootstrap Samples of P(D+|T+) by Threshold") +
  theme_minimal() +
  theme(legend.position = "none")  # Exclude the legend

ggsave(
  filename = 'P_R_R_bootstrap_trajectory_plot.png',
  plot = P_R_R_bootstrap_trajectory_plot,
  width = 8,
  height = 6,
  bg = "white"
)

   
#Find the percentage of Bootstrap with no predictions above or below the threshold
# Calculate the proportion of NA values by row
na_proportion <- apply(P_R_R, 1, function(row) mean(is.na(row)))

# Add the result as a new column to the dataset 
P_R_R_NAprop <- P_R_R %>%
 select(-threshold) %>%
 mutate(NA_proportion = na_proportion) %>%
 select(NA_proportion) %>%
 cbind(P_R_R$threshold) %>%
 rename('threshold' = 'P_R_R$threshold')

P_R_R_NAprop_bootstrap_plot = ggplot(P_R_R_NAprop, aes(x = threshold, y = NA_proportion)) +
  geom_line() +  # Or geom_point() if you want points instead of lines
  labs(title = "Proportion of Undefined P(D+|T+) Across 200 Bootstrap Samples by Threshold",
       x = "Threshold",
       y = "Proportion") +
  theme_minimal()

ggsave(
  filename = 'P_R_R_NAprop_bootstrap_plot.png',
  plot = P_R_R_NAprop_bootstrap_plot,
  width = 8,
  height = 6,
  bg = "white"
)


##P_S_S

#Comparing the probabilities calculated with traditional and alternative
P_S_S = DecisionTree_probs %>%
  filter(Variable == 'P_S_S') %>%
  select(-Variable)

#Select only the alternative calculated probabilities
# Filter rows where Variable column has the suffix "_alt"

#Plot all bootstrap samples
plot_data <- P_S_S %>%
  pivot_longer(cols = -threshold, names_to = "metric", values_to = "value")

# Plot the data without legend
P_S_S_bootstrap_trajectory_plot = ggplot(plot_data, aes(x = threshold, y = value, color = metric)) +
  geom_line() +
  labs(x = "Threshold", y = "P(D+|T+)", title = "Trajectory of 200 Bootstrap Samples of P(D-|T-) by Threshold") +
  theme_minimal() +
  theme(legend.position = "none")  # Exclude the legend

ggsave(
  filename = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/Optimism Correction/PM Sample/Original/P_S_S_bootstrap_trajectory_plot.png',
  plot = P_S_S_bootstrap_trajectory_plot,
  width = 8,
  height = 6,
  bg = "white"
)
