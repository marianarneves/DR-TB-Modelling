library(glmnet)
library(dplyr)
library(pROC)
library(ROCR)
library(brms)
library(caret)
library(ggplot2)
library(rms)
library(betacal)
library(tidyr)

# Set working directory to the script's location
if (rstudioapi::isAvailable()) {
  setwd(dirname(rstudioapi::getSourceEditorContext()$path))
}

source("Calculate_sens_spec.R")

predictions_bootstrap = read.csv('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/Optimism Corrected/LR_bootstrap_BetaCalibration.csv')
predictions_mainpm = read.csv('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/Optimism Corrected/LR_MainPM_BetaCalibration.csv')

########################################################
#   Sensitivity and specificity - Optimism Correction  #
########################################################

nbootstrap = length(unique(predictions_bootstrap$bootstrap_sample))

# Pre-calculate tvalues outside the loop to avoid redundant computations
tvalues = seq(0, 1, by = 0.001)

# Initialize the list to store results
sens_spec_optcorr <- vector(mode = 'list', length = nbootstrap)

# Pre-compute bootstrap samples and store them outside the loop to avoid repeating work
predicted_observed_bootstrap_list <- split(predictions_bootstrap, predictions_bootstrap$bootstrap_sample)

for(i in 1:nbootstrap){
  
  # Select necessary columns for the bootstrap sample and original data
  predicted_observed_bootstrap = predicted_observed_bootstrap_list[[i]][, c("predicted_bootstrap", "observed_bootstrap")]
  predicted_observed_origidata = predicted_observed_bootstrap_list[[i]][, c("predicted_origdata", "observed_origdata")]
  
  # Pre-allocate vectors for sensitivity and specificity
  sensitivity_bootstrap = numeric(length(tvalues))
  specificity_bootstrap = numeric(length(tvalues))
  sensitivity_origdata = numeric(length(tvalues))
  specificity_origdata = numeric(length(tvalues))
  sensitivity_bootstrap_origdata = numeric(length(tvalues))
  specificity_bootstrap_origdata = numeric(length(tvalues))
  
  # Vectorized calculation for each threshold value
  for(t in 1:length(tvalues)){
    # Apply the threshold and calculate the sensitivity and specificity
    predicted_bootstrap_class = as.integer(predicted_observed_bootstrap$predicted_bootstrap > tvalues[t])
    predicted_origdata_class = as.integer(predicted_observed_origidata$predicted_origdata > tvalues[t])
    
    sens_spec_bootstrap = calculate_sens_spec(predicted_observed_bootstrap$observed_bootstrap, predicted_bootstrap_class)
    sens_spec_origdata = calculate_sens_spec(predicted_observed_origidata$observed_origdata, predicted_origdata_class)
    
    # Store the results
    sensitivity_bootstrap[t] = sens_spec_bootstrap$Sensitivity
    specificity_bootstrap[t] = sens_spec_bootstrap$Specificity
    sensitivity_origdata[t] = sens_spec_origdata$Sensitivity
    specificity_origdata[t] = sens_spec_origdata$Specificity
    sensitivity_bootstrap_origdata[t] = sens_spec_bootstrap$Sensitivity - sens_spec_origdata$Sensitivity
    specificity_bootstrap_origdata[t] = sens_spec_bootstrap$Specificity - sens_spec_origdata$Specificity
  }
  
  # Create the data frame with results for this bootstrap sample
  sens_spec_optcorr_dataframe = data.frame(
    bootstrap_sample = rep(i, length(tvalues)),
    threshold_values = tvalues,
    sensitivity_bootstrap = sensitivity_bootstrap,
    specificity_bootstrap = specificity_bootstrap,
    sensitivity_origdata = sensitivity_origdata,
    specificity_origdata = specificity_origdata,
    sensitivity_bootstrap_origdata = sensitivity_bootstrap_origdata,
    specificity_bootstrap_origdata = specificity_bootstrap_origdata
  )
  
  # Store the results for this bootstrap sample
  sens_spec_optcorr[[i]] = sens_spec_optcorr_dataframe
  
  cat("Bootstrap", i, "- Completed\n")
}

alpha = 0.05

# Assuming sens_spec_optcorr is a list of data frames
average_optimism <- bind_rows(sens_spec_optcorr) %>%
  group_by(threshold_values) %>%
  summarise(
    avg_optmism_sensitivity = mean(sensitivity_bootstrap_origdata, na.rm = TRUE),
    uci_optmism_sensitivity = quantile(sensitivity_bootstrap_origdata, alpha / 2),
    lci_optmism_sensitivity = quantile(sensitivity_bootstrap_origdata, 1- alpha / 2),
    avg_optmism_specificity = mean(specificity_bootstrap_origdata, na.rm = TRUE),
    uci_optmism_specificity = quantile(specificity_bootstrap_origdata, alpha / 2),
    lci_optmism_specificity = quantile(specificity_bootstrap_origdata, 1- alpha / 2)
  )

# Assuming 'average_optimism' is the dataframe with the necessary data
ggplot(average_optimism, aes(x = threshold_values)) +
  # Plot avg_optmism_sensitivity with shaded confidence interval
  geom_line(aes(y = avg_optmism_sensitivity, color = "Avg Sensitivity"), size = 1) +
  geom_ribbon(aes(ymin = lci_optmism_sensitivity, ymax = uci_optmism_sensitivity), alpha = 0.2, fill = "blue") +
  # Plot avg_optmism_specificity
  geom_line(aes(y = avg_optmism_specificity, color = "Avg Specificity"), size = 1, linetype = "dashed") +
  geom_ribbon(aes(ymin = lci_optmism_specificity, ymax = uci_optmism_specificity), alpha = 0.2, fill = "blue") +
  # Customize the plot
  labs(x = "Threshold Values", 
       y = "Optimized Sensitivity and Specificity", 
       title = "Optimized Sensitivity and Specificity with Confidence Intervals",
       color = "Metric") +
  # Add a minimal theme and customize legend position
  theme_minimal() +
  theme(legend.position = "top")


# Initialize the dataframe with the correct number of rows
sens_spec_mainpred_dataframe <- data.frame(
  threshold_values = numeric(length(tvalues)),
  sensitivity_mainpred = numeric(length(tvalues)),
  specificity_mainpred = numeric(length(tvalues))
)

# Loop through tvalues and assign values
for(t in 1:length(tvalues)){
  
  predicted_mainpred_class = ifelse(predictions_mainpm$predicted > tvalues[t], 1, 0)
  sens_spec_mainpred = calculate_sens_spec(predictions_mainpm$observed, predicted_mainpred_class)
  
  sens_spec_mainpred_dataframe$threshold_values[t] = tvalues[t]
  sens_spec_mainpred_dataframe$sensitivity_mainpred[t] = sens_spec_mainpred$Sensitivity
  sens_spec_mainpred_dataframe$specificity_mainpred[t] = sens_spec_mainpred$Specificity
  
}


# Assuming 'sens_spec_mainpred_averagedoptimism' is the data frame you want to plot
ggplot(sens_spec_mainpred_dataframe, aes(x = threshold_values)) +
  geom_line(aes(y = sensitivity_mainpred, color = "Sensitivity"), size = 1) +
  geom_line(aes(y = specificity_mainpred, color = "Specificity"), size = 1) +
  labs(x = "Threshold Values", 
       y = "Optimized Sensitivity and Specificity",
       title = "Optimized Sensitivity and Specificity by Threshold",
       color = "Metric") +
  theme_minimal() +
  theme(legend.position = "top")

sens_spec_mainpred_averagedoptimism <- sens_spec_mainpred_dataframe %>%
  inner_join(average_optimism, by = "threshold_values") %>%
  mutate(sensitivity_optcorr = sensitivity_mainpred - avg_optmism_sensitivity,
         lci_sensitivity_optcorr = sensitivity_mainpred - lci_optmism_sensitivity,
         uci_sensitivity_optcorr = sensitivity_mainpred - uci_optmism_sensitivity,
         specificity_optcorr = specificity_mainpred - avg_optmism_specificity,
         lci_specificity_optcorr = specificity_mainpred - lci_optmism_specificity,
         uci_specificity_optcorr = specificity_mainpred - uci_optmism_specificity,
         sensitivity_optcorr_censored = case_when(
           sensitivity_mainpred - avg_optmism_sensitivity < 0 ~ 0,
           sensitivity_mainpred - avg_optmism_sensitivity > 1 ~ 1 ,
           TRUE ~ sensitivity_mainpred - avg_optmism_sensitivity),
         lci_sensitivity_optcorr_censored = case_when(
           sensitivity_mainpred - lci_optmism_sensitivity < 0 ~ 0,
           sensitivity_mainpred - lci_optmism_sensitivity > 1 ~ 1 ,
           TRUE ~ sensitivity_mainpred - lci_optmism_sensitivity),
         uci_sensitivity_optcorr_censored = case_when(
           sensitivity_mainpred - uci_optmism_sensitivity < 0 ~ 0,
           sensitivity_mainpred - uci_optmism_sensitivity > 1 ~ 1 ,
           TRUE ~ sensitivity_mainpred - uci_optmism_sensitivity),
         specificity_optcorr_censored = case_when(
           specificity_mainpred - avg_optmism_specificity < 0 ~ 0,
           specificity_mainpred - avg_optmism_specificity > 1 ~ 1 ,
           TRUE ~ specificity_mainpred - avg_optmism_specificity),
         lci_specificity_optcorr_censored = case_when(
           specificity_mainpred - lci_optmism_specificity < 0 ~ 0,
           specificity_mainpred - lci_optmism_specificity > 1 ~ 1 ,
           TRUE ~ specificity_mainpred - lci_optmism_specificity),
         uci_specificity_optcorr_censored = case_when(
           specificity_mainpred - uci_optmism_specificity < 0 ~ 0,
           specificity_mainpred - uci_optmism_specificity > 1 ~ 1 ,
           TRUE ~ specificity_mainpred - uci_optmism_specificity)
         )


# Step 1: Identify the optimal threshold
optimal_row <- sens_spec_mainpred_averagedoptimism %>%
  mutate(sum_sens_spec_optcorr = sensitivity_optcorr + specificity_optcorr) %>%
  slice_max(sum_sens_spec_optcorr, with_ties = FALSE)

optimal_threshold <- optimal_row$threshold_values

# Step 2: Build the plot
sensitivity_specificity_censored_plot <- ggplot(sens_spec_mainpred_averagedoptimism, aes(x = threshold_values)) +
  
  # Optimism-corrected sensitivity
  geom_line(aes(y = sensitivity_optcorr_censored, color = "Optimism-Corrected Sensitivity"), size = 1, linetype = "twodash") +
  geom_ribbon(aes(ymin = lci_sensitivity_optcorr_censored, ymax = uci_sensitivity_optcorr_censored), alpha = 0.3, fill = "darkblue") +
  
  # Optimism-corrected specificity
  geom_line(aes(y = specificity_optcorr_censored, color = "Optimism-Corrected Specificity"), size = 1, linetype = "twodash") +
  geom_ribbon(aes(ymin = lci_specificity_optcorr_censored, ymax = uci_specificity_optcorr_censored), alpha = 0.3, fill = "darkred") +
  
  # Apparent values
  geom_line(aes(y = sensitivity_mainpred, color = "Apparent Sensitivity"), size = 1, linetype = "solid") +
  geom_line(aes(y = specificity_mainpred, color = "Apparent Specificity"), size = 1, linetype = "solid") +
  
  # Vertical dashed red line for max sum sens + spec
  geom_vline(aes(xintercept = optimal_threshold, color = "Max Optimism-Corrected Sensitivity + Specificity"), linetype = "twodash", size = 1) +
  
  # Text annotation of the threshold value
  annotate("text", x = optimal_threshold, y = 0.58, label = round(optimal_threshold, 2),
           angle = 90, vjust = -0.5, hjust = 0, size = 5, color = "red") +
  
  # Axis labels and legend
  labs(
    x = "Classification Threshold", 
    y = "Sensitivity and Specificity", 
    color = NULL
  ) +
  
  # Set colors and control order of legend
  scale_color_manual(
    values = c(
      "Optimism-Corrected Sensitivity" = "darkblue", 
      "Optimism-Corrected Specificity" = "darkred",
      "Apparent Sensitivity" = "darkblue",
      "Apparent Specificity" = "darkred",
      "Max Optimism-Corrected Sensitivity + Specificity" = "red"
    ),
    breaks = c(
      "Optimism-Corrected Sensitivity",
      "Optimism-Corrected Specificity",
      "Apparent Sensitivity",
      "Apparent Specificity",
      "Max Optimism-Corrected Sensitivity + Specificity"
    )
  ) +
  
  # Legend layout: horizontal with 3 rows
  guides(color = guide_legend(nrow = 3, byrow = TRUE)) +
  
  # Theme
  theme_minimal() +
  theme(
    legend.position = "bottom",
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA),
    panel.grid = element_line(color = "gray90"),
    plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 16),
    axis.text = element_text(size = 16),
    legend.text = element_text(size = 16)
  )

ggsave("/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/Optimism Corrected/Sens_Spec_mainpm_optimismcorrected_censored.png", plot = sensitivity_specificity_censored_plot, width = 10, height = 6)

