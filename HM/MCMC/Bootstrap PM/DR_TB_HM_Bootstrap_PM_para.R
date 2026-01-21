# Load required packages
library(foreach)
library(doParallel)
library(dplyr)
library(brms)
library(rms)
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
#set.seed(5)

# Define the number of bootstrap samples
S <- 10

# Number of cores to use
n_cores <- parallel::detectCores() - 1  # Use all but one core

# Initialize the parallel backend
cl <- makeCluster(n_cores)
registerDoParallel(cl)

start_time <- Sys.time()

# Initialize list to store predictions
all_predictions <- list()

# Parallelized bootstrap sampling and model fitting
all_predictions <- foreach(i = 1:S, .packages = c('dplyr', 'brms', 'rms'), .combine = 'rbind') %dopar% {
  
  print(i)
  
  # Generate bootstrap sample
  bootstrap_sample <- moldova_data %>% sample_n(size = n(), replace = TRUE)
  
  # Fit the hierarchical model
  hierarchical_model <- brm(
    formula = formula,
    data = bootstrap_sample,
    family = bernoulli(link = "logit"),
    prior = set_prior(R2D2(
      mean_R2 = 0.8,
      prec_R2 = 10,
      cons_D2 = 0.5,
      main = TRUE
    ), class = "b"),
    iter = 100000,
    chains = 4,
    control = list(adapt_delta = 0.9999)
  )
  
  # Predict on the original dataset (or test set)
  bootstrap_sample_predictions <- posterior_epred(hierarchical_model,
                                                  newdata = bootstrap_sample,
                                                  allow_new_levels = TRUE)
  
  # Average of the simulated predictions
  bootstrap_sample_y_prob <- apply(bootstrap_sample_predictions, 2, mean)
  
  # Beta calibration
  bc <- beta_calibration(bootstrap_sample_y_prob, bootstrap_sample$FLQ_R, parameters = "abm")
  beta <- beta_predict(bootstrap_sample_y_prob, bc)
  rms::val.prob(beta, bootstrap_sample$FLQ_R)
  
  # Save the predictions
  data.frame(bootstrap_sample = rep(i, dim(moldova_data)[1]), predicted = beta, observed = bootstrap_sample$FLQ_R)
}

stopCluster(cl)  # Stop the cluster

end_time <- Sys.time()

execution_time <- end_time - start_time
print(paste("Execution Time:", execution_time))
