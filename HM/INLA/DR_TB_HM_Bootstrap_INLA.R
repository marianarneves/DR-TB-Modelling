# -----------------------------------
# Load libraries
# -----------------------------------
library(INLA)
library(dplyr)
library(pROC)
library(ggplot2)
library(rms)
library(betacal)

# Source helper scripts
source('HM_model_specification.R')
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/Bootstrap PM - optimism corrected/Main/Code/ROC_performance.R')
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/Bootstrap PM - optimism corrected/Main/Code/crossvalidation_HM.R')

setwd('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/INLA')

# -----------------------------------
# Load dataset
# -----------------------------------
data_path <- "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_HM.csv"
moldova_data <- read.csv(data_path)

set.seed(5)

# Ensure outcome is binary numeric
moldova_data$FLQ_R <- as.numeric(moldova_data$FLQ_R)

# -----------------------------------
# Fit HM model with INLA
# -----------------------------------
start_time <- Sys.time()

hierarchical_model <- inla(
  formula = formula_inla,
  data = moldova_data,
  family = "binomial",
  control.predictor = list(link = 1, compute = TRUE),  # compute = TRUE is required
  control.compute = list(dic = TRUE, waic = TRUE, cpo = TRUE),
  control.fixed = list(
    mean = 0,
    prec.intercept = 0.001,  # weak prior on intercept
    prec = 0.001            # apply modest shrinkage across all fixed effects
  )
)


end_time <- Sys.time()
time_taken <- end_time - start_time
print(time_taken)


############################
# Main Model - Predictions #
############################

# Extract predicted probabilities from the fitted INLA model
bootstrap_sample_y_prob <- hierarchical_model$summary.fitted.values$mean

# Get the true binary labels
true_labels <- moldova_data$FLQ_R

# Load AUC function
library(pROC)

# Calculate AUC
auc_result <- auc(response = true_labels, predictor = bootstrap_sample_y_prob)

# Print AUC
print(auc_result)


# -----------------------------------
# Bootstrap Predictions with Calibration
# -----------------------------------
S <- 500
all_predictions <- list()
bootstrap_sample <- list()

start_time <- Sys.time()

for (i in 1:S) {
  print(i)
  
  bootstrap_sample[[i]] <- moldova_data %>% sample_n(size = n(), replace = TRUE)
  
  # Refit model on bootstrap sample
  model_boot <- inla(
    formula = formula_inla,
    data = bootstrap_sample[[i]],
    family = "binomial",
    control.predictor = list(link = 1, compute = TRUE),
    control.compute = list(dic = FALSE),
    control.fixed = list(mean = 0, prec = 0.001)
  )
  
  # Predict on original data
  pred_probs <- model_boot$summary.fitted.values$mean
  
  # Beta calibration
  bc <- beta_calibration(pred_probs, bootstrap_sample[[i]]$FLQ_R, parameters = "abm")
  beta <- beta_predict(pred_probs, bc)
  
  rms::val.prob(beta, bootstrap_sample[[i]]$FLQ_R)
  
  all_predictions[[i]] <- data.frame(
    bootstrap_sample = rep(i, nrow(moldova_data)),
    predicted = beta,
    observed = bootstrap_sample[[i]]$FLQ_R
  )
}

combined_dataframe <- do.call(rbind, all_predictions)
write.csv(combined_dataframe, "HM_bootstrap_calibrated_predictions.csv", row.names = FALSE)

# -----------------------------------
# Predict on Full Dataset with Calibration
# -----------------------------------
pred_probs_full <- hierarchical_model$summary.fitted.values$mean

moldova_data_bc <- beta_calibration(pred_probs_full, moldova_data$FLQ_R, parameters = "abm")
moldova_data_beta <- beta_predict(pred_probs_full, moldova_data_bc)

rms::val.prob(moldova_data_beta, moldova_data$FLQ_R)

# Format sex
moldovaSex <- ifelse(moldova_data$Sex == 1, "Female", "Male")

moldova_data_all_predictions <- data.frame(
  predicted = moldova_data_beta,
  observed = moldova_data$FLQ_R,
  age = moldova_data$Age,
  sex = moldovaSex
)

write.csv(moldova_data_all_predictions, "HM_mainPM_calibrated_predictions.csv", row.names = FALSE)

