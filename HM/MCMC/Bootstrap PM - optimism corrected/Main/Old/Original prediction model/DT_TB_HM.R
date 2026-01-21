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

source("HM_model_specification.R")
source("ROC_performance.R")
source("crossvalidation_HM.R")


set.seed(3)

# Load the new dataset
data_path <-
  "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_HM.csv"
moldova_data <- read.csv(data_path)


################
# HM modelling #
################

#### HM model ####
start_time <- Sys.time()
  hierarchical_model <- brm(
    formula = formula,
    data = moldova_data,
    family = bernoulli(link = "logit"),
    prior = set_prior(R2D2(
      mean_R2 = 0.8,
      prec_R2 = 10,
      cons_D2 = 0.1,
      main = TRUE
    ),
    class = "b"),
    iter = 1000,
    chains = 4,
    control = list(adapt_delta = 0.999)
  )
  
end_time <- Sys.time()

print(end_time - start_time)

# HM predictions
# Predict on test data
predictions <-
  posterior_epred(hierarchical_model,
                  newdata = moldova_data,
                  allow_new_levels = TRUE)
# Average of the simulated 
y_prob <-
  apply(predictions, 2,  function(x)
    mean(x))

#### Performance of the HM ####
HM_performance = roc_performance(y_prob, moldova_data, moldova_data$FLQ_R)

# Write Predictions in CSV
moldovaSex = ifelse(moldova_data$Sex == 1, "Female", "Male" )
write.csv(data.frame(pred = y_prob, obs = moldova_data$FLQ_R, age = moldova_data$Age, sex = moldovaSex), file.path("HM Output", "pred_obs.csv"), row.names = FALSE)
# Write Rates in CSV
write.csv(HM_performance$sens_spec, file.path("HM Output","sens_spec_adjusted.csv"), row.names = FALSE)

# ROC plot
plot(
  HM_performance$roc_curve,
  main = "ROC Curve for Hierarchical Logistic Regression",
  col.main = "darkblue",
  lwd = 2
)
# Add legend with labels based on cv_results$roc_auc_fulldata
legend(
  "bottomright",
  legend = round(HM_performance$roc_curve$auc, 2),
  lwd = 2,
  title = "AUROC",
  cex = 0.8
)

#### Plot sensitivity and specificity ####
plot(HM_performance$sens_spec$threshold, HM_performance$sens_spec$sensitivity, type = "l", col = "blue",
     xlab = "Threshold", ylab = "Sensitivity", ylim = c(0, 1), lwd = 2)
lines(HM_performance$sens_spec$threshold, HM_performance$sens_spec$specificity, col = "red", lty = 2, lwd = 2)
legend("bottomright", legend = c("Sensitivity", "Specificity"), col = c("blue", "red"), lty = c(1, 2), lwd = 2)

# Plot probabilities calculated with Bayes Theorem
ggplot(HM_performance$sens_spec, aes(x = threshold)) +
  geom_line(aes(y = P_S_R, color = "P_S_R")) +
  geom_line(aes(y = P_R_R, color = "P_R_R")) +
  scale_color_manual(values = c( "blue", "red"), name = "Variable") +
  labs(x = "Threshold", y = "Value") +
  theme_minimal() +
  theme(legend.position = "top")

ggplot(HM_performance$sens_spec, aes(x = threshold)) +
  geom_line(aes(y = P_S_S, color = "P_S_S")) +
  geom_line(aes(y = P_R_S, color = "P_R_S")) +
  scale_color_manual(values = c( "blue", "red"), name = "Variable") +
  labs(x = "Threshold", y = "Value") +
  theme_minimal() +
  theme(legend.position = "top")


#####################
# Model Calibration #
#####################

#Calibration evaluation
source("Calibration_analysis.R")

# Plot calibration curve
rms::val.prob(y_prob, moldova_data$FLQ_R)
# From this calibration curve  we can see that the model looks poorly calibrated

#### Using a beta calibration curve ####
bc <- beta_calibration(y_prob, moldova_data$FLQ_R, parameters = "abm")
beta = beta_predict(y_prob, bc)
rms::val.prob(beta, moldova_data$FLQ_R)

# Write Adjusted Predictions in CSV
write.csv(data.frame(pred = beta, obs = moldova_data$FLQ_R, age = moldova_data$Age, sex = moldovaSex), file.path("HM Output", "pred_obs_calibrated_model.csv"), row.names = FALSE)

#### Performance of the calibrated HM predictions ####
HM_cal_performance = roc_performance(beta, moldova_data, moldova_data$FLQ_R)

#Write Rates in CSV
write.csv(HM_cal_performance$sens_spec, file.path("HM Output", "sens_spec_calibrated_model.csv"), row.names = FALSE)

# Create a data frame for the sensitivity and specificity data
sens_spec_data <- data.frame(
  Threshold = HM_cal_performance$sens_spec$threshold,
  Sensitivity = HM_cal_performance$sens_spec$sensitivity,
  Specificity = HM_cal_performance$sens_spec$specificity
)

# Fitering minimun values for sens and spec
sens_spec_selectvalues = sens_spec_data %>%
  filter(Sensitivity >0.65 & Specificity >0.5)

min_thre = min(sens_spec_selectvalues$Threshold)
max_thre = max(sens_spec_selectvalues$Threshold)

# Convert data to long format for ggplot2
sens_spec_data_long <- sens_spec_data %>%
  gather(key = "Metric", value = "Value", -Threshold)

# Create the ggplot2 plot with transparent shaded area between 0.1 and 0.15
sen_spec_cal_model_plot <- ggplot(sens_spec_data_long, aes(x = Threshold, y = Value)) +
  geom_line(aes(color = Metric, linetype = Metric), size = 0.8) +  # Set color and linetype within geom_line
  labs(title = "Sensitivity and Specificity Across Thresholds",
       x = "Threshold",
       y = "Value") +
  scale_color_manual(values = c("Sensitivity" = "#2171b5", "Specificity" = "#fdae6b")) +  # Blue for Sensitivity, Orange for Specificity
  guides(color = guide_legend(title = NULL), linetype = guide_legend(title = NULL)) +  # Remove legend titles
  theme_minimal() +
  xlim(0, 1) +  # Set x-axis from 0 to 1
  ylim(0, 1) +  # Set y-axis from 0 to 1
  # Add transparent shaded area between x = 0.1 and 0.15
  geom_ribbon(data = subset(sens_spec_data_long, Threshold >= min_thre & Threshold <= max_thre), 
              aes(ymin = 0, ymax = 1), fill = "red", alpha = 0.2) +  # Shading with transparency
  theme(legend.position = "bottom",
        plot.background = element_rect(fill = "white", color = NA),  # White plot background
        panel.background = element_rect(fill = "white", color = NA), # White panel background
        panel.grid = element_line(color = "gray90"),                 # Light gray grid
        plot.title = element_text(size = 16, face = "bold"),         # Increase title text size
        axis.title = element_text(size = 16),                        # Increase axis title text size
        axis.text = element_text(size = 16),                         # Increase axis labels text size
        legend.text = element_text(size = 16),                       # Increase legend text size
        legend.title = element_text(size = 16))                      # Increase legend title text size



# Save the plot with similar style
ggsave(file.path("HM Output", "sens_spec_calibration_plot.png"), plot = sen_spec_cal_model_plot, width = 8, height = 6, dpi = 300)


#### Plot threshold and probabilities - Positive classified ####
plot(HM_cal_performance$sens_spec$threshold, HM_cal_performance$sens_spec$P_S_R, type = "l", col = "blue",
     xlab = "Threshold", ylab = "P_S_R", ylim = c(0, 1), lwd = 2)
lines(HM_cal_performance$sens_spec$threshold, HM_cal_performance$sens_spec$P_R_R, col = "red", lty = 2, lwd = 2)
legend("bottomright", legend = c("P_S_R", "P_R_R"), col = c("blue", "red"), lty = c(1, 2), lwd = 2)

# Plot threshold and probabilities - Negative classified
plot(HM_cal_performance$sens_spec$threshold, HM_cal_performance$sens_spec$P_S_S, type = "l", col = "blue",
     xlab = "Threshold", ylab = "P_S_R", ylim = c(0, 1), lwd = 2)
lines(HM_cal_performance$sens_spec$threshold, HM_cal_performance$sens_spec$P_R_S, col = "red", lty = 2, lwd = 2)
legend("bottomright", legend = c("P_S_R", "P_R_R"), col = c("blue", "red"), lty = c(1, 2), lwd = 2)


####################
# Cross Validation #
####################

#source("CrossValidation.R")

############################
# Optimism corrected AUROC #
############################

#source("OptimismCorrected_AUC.R")