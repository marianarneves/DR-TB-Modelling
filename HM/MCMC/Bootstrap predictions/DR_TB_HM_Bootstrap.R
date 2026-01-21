# Load necessary libraries
library(dplyr)   # for data manipulation
library(caret)   # for model training
library(glmnet)
library(dplyr)
library(pROC)
library(ROCR)
library(brms)
library(ggplot2)
library(rms)
library(betacal)
source("/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/HM_model_specification.R")
source("/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/ROC_performance.R")
source("/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/crossvalidation_HM.R")

setwd('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/HM Output/Bootstrap')

# Load the new dataset
data_path <-
  "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_HM.csv"
moldova_data <- read.csv(data_path)

# Set seed for reproducibility
set.seed(5)

################
# HM modelling #
################

#### HM model ####

# Start time
start_time <- Sys.time()

hierarchical_model <- brm(
  formula = formula,
  data = moldova_data,
  family = bernoulli(link = "logit"),
  prior = set_prior(R2D2(
    mean_R2 = 0.8,
    prec_R2 = 10,
    cons_D2 = 0.5,
    main = TRUE
  ),
  class = "b"),
  iter = 100000,
  chains = 4,
  control = list(adapt_delta = 0.9999)
)

# End time
end_time <- Sys.time()

# Calculate the time difference
time_taken <- end_time - start_time

############################
# Bootstrap - Predictions #
############################

# Define the number of bootstrap samples
S <- 500

# Initialize a list to store the predictions for each bootstrap sample
all_predictions <- list()
bootstrap_sample <- list()

start_time <- Sys.time()

# Loop over S bootstrap samples
for (i in 1:S) {
  print(i)
  
  # Generate bootstrap sample using dplyr's sample_n
  bootstrap_sample[[i]] <- moldova_data %>% sample_n(size = n(), replace = TRUE)
  
  # Predict on the original dataset (or any test set)
  bootstrap_sample_predictions <-
    posterior_epred(hierarchical_model,
                    newdata = bootstrap_sample[[i]],
                    allow_new_levels = TRUE)
  
  # Average of the simulated 
  bootstrap_sample_y_prob <-
    apply(bootstrap_sample_predictions, 2,  function(x)
      mean(x))
  
  #### Using a beta calibration curve ####
  bc <- beta_calibration(bootstrap_sample_y_prob, bootstrap_sample[[i]]$FLQ_R, parameters = "abm")
  beta = beta_predict(bootstrap_sample_y_prob, bc)
  rms::val.prob(beta, bootstrap_sample[[i]]$FLQ_R)
  
  # Save the predictions
  all_predictions[[i]] <- data.frame(bootstrap_sample = rep(i, dim(moldova_data)[1]), predicted = beta, observed = bootstrap_sample[[i]]$FLQ_R)
  
}

# Combine all predictions into a single data frame using dplyr
combined_dataframe <- do.call(rbind, all_predictions)

# Save the predictions to a CSV file
write.csv(combined_dataframe, "HM_bootstrap_calibrated_predictions.csv", row.names = FALSE)

###########################
# All data  - Predictions #
###########################

# Predict on the original dataset (or any test set)
moldova_data_predictions <-
  posterior_epred(hierarchical_model,
                  newdata = moldova_data,
                  allow_new_levels = TRUE)

# Average of the simulated 
moldova_data_y_prob <-
  apply(moldova_data_predictions, 2,  function(x)
    mean(x))

#### Using a beta calibration curve ####
moldova_data_bc <- beta_calibration(moldova_data_y_prob, moldova_data$FLQ_R, parameters = "abm")
moldova_data_beta = beta_predict(moldova_data_y_prob, bc)
rms::val.prob(moldova_data_beta, moldova_data$FLQ_R)

# Sex in Moldova data
moldovaSex = ifelse(moldova_data$Sex == 1, "Female", "Male" )

# Save the predictions
moldova_data_all_predictions<- data.frame(predicted = moldova_data_beta, observed = moldova_data$FLQ_R, age = moldova_data$Age, sex = moldovaSex)

# Save the predictions to a CSV file
write.csv(moldova_data_all_predictions, "HM_mainPM_calibrated_predictions.csv", row.names = FALSE)
