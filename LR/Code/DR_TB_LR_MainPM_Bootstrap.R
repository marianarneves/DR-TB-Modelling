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

source("LR_model_specification.R")
source("ROC_performance.R")
source("crossvalidation_HM.R")

set.seed(1)

# Load the new dataset
data_path <-
  "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_LR_Augumented.csv"
moldova_data <- read.csv(data_path)
moldova_data$Pt_id = seq(1:dim(moldova_data)[1])

#################
#   Main Pred   #
#################

# Convert predictor variables to a matrix
x <- model.matrix(formula, moldova_data)[,-1]  # Remove the intercept column

# Convert outcome variable to numeric
y <- as.numeric(moldova_data$FLQ_R)  # Replace <outcome_variable> with the actual outcome column name

# Lasso Logistic Regression
ridge_model <- cv.glmnet(
  x, y,
  family = "binomial",
  alpha = 0,             # Lasso regularization
)

# Best lambda (minimizes cross-validation error)
best_lambda <- ridge_model$lambda.min
print(best_lambda)

# Coefficients at the best lambda
coef(ridge_model, s = best_lambda)

# Predicted probabilities
y_prob <- predict(ridge_model, newx = x, s = best_lambda, type = "response")

roc_mainPM = roc(moldova_data$FLQ_R, as.vector(y_prob))
auc_mainPM = roc_mainPM$auc

# Beta calibration
bc_mainpred <- beta_calibration(y_prob, moldova_data$FLQ_R, parameters = "abm")
beta_mainpredp <- beta_predict(y_prob, bc_mainpred)


# Fit logistic regression to recalibrate
platt_model_mainpred <- glm(moldova_data$FLQ_R ~ y_prob, family = binomial(link = "logit"))
# Get recalibrated probabilities
platt_pred_mainpred <- predict(platt_model_mainpred, newdata = data.frame( y_prob), type = "response")

# Write Predictions in CSV
moldovaSex = ifelse(moldova_data$Sex == 1, "Female", "Male" )

predictions_mainpred_calcompare <- data.frame(pt_id = moldova_data$Pt_id, observed_mainpred = moldova_data$FLQ_R, predicted_original_mainpred = as.vector(y_prob), predicted_beta_mainpred = beta_mainpredp, predicted_platt_mainpred = platt_pred_mainpred, age = moldova_data$Age, sex = moldovaSex)

#Using no calibration
predictions_mainpred <- data.frame(pt_id = moldova_data$Pt_id, observed = moldova_data$FLQ_R, predicted = as.vector(y_prob), age = moldova_data$Age, sex = moldovaSex)

#Using platt calibration
predictions_calplatt_mainpred <- data.frame(pt_id = moldova_data$Pt_id, observed = moldova_data$FLQ_R, predicted = platt_pred_mainpred, age = moldova_data$Age, sex = moldovaSex)

#Using Beta calibration
predictions_calbeta_mainpred <- data.frame(pt_id = moldova_data$Pt_id, observed = moldova_data$FLQ_R, predicted = beta_mainpredp, age = moldova_data$Age, sex = moldovaSex)


write.csv(predictions_mainpred_calcompare, "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/Optimism Corrected/LR_MainPM_platt_beta_compare.csv", row.names = FALSE)
write.csv(predictions_mainpred, "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/Optimism Corrected/LR_MainPM_nocalibration.csv", row.names = FALSE)
write.csv(predictions_calplatt_mainpred, "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/Optimism Corrected/LR_MainPM_PlattCalibration.csv", row.names = FALSE)
write.csv(predictions_calbeta_mainpred, "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/Optimism Corrected/LR_MainPM_BetaCalibration.csv", row.names = FALSE)


#### Crossvalidation ####

# Cross-validation settings
n_folds <- 5

# Initialize a vector to store AUC scores for each fold
auc_scores <- numeric(n_folds)

# Split data into folds
folds <- sample(1:n_folds, size = nrow(moldova_data), replace = TRUE)

# Perform k-fold cross-validation
for (i in 1:n_folds) {
  # Split the data into training and testing sets
  train_indices <- which(folds != i)
  test_indices <- which(folds == i)
  
  x_train <- model.matrix(formula, moldova_data[train_indices, ])[, -1]
  y_train <- as.numeric(moldova_data$FLQ_R[train_indices])
  x_test <- model.matrix(formula, moldova_data[test_indices, ])[, -1]
  y_test <- as.numeric(moldova_data$FLQ_R[test_indices])
  
  # Train the model using the training set
  ridge_model <- cv.glmnet(
    x_train, y_train,
    family = "binomial",
    alpha = 0  # Lasso regularization
  )
  
  # Get the best lambda for this fold
  best_lambda <- ridge_model$lambda.min
  
  # Make predictions on the test set
  y_prob <- predict(ridge_model, newx = x_test, s = best_lambda, type = "response")
  
  # Calculate AUC for this fold
  roc_obj <- roc(y_test, as.vector(y_prob))
  auc_scores[i] <- roc_obj$auc
}

# Calculate and print the mean AUC across all folds
mean_auc <- mean(auc_scores)
print(paste("Mean AUC across all folds:", mean_auc))
sd(auc_scores)


######################################
#   Bootstrap - Optimism Correction  #
######################################

all_predictions_platt <- data.frame()
all_predictions_beta <- data.frame()
all_predictions_platt_beta_compare <- data.frame()
all_predictions_nocalibration <- data.frame()
auc_adjusted = c()

nbootstrap = 200
  
# Parallelized bootstrap sampling and model fitting
for(i in 1:nbootstrap){
  
  print(i)
  
  set.seed(i)
  bootstrap_sample <- moldova_data %>% sample_n(size = n(), replace = TRUE)
  
  # Convert predictor variables to a matrix
  x <- model.matrix(formula, bootstrap_sample)[,-1]  # Remove the intercept column
  
  # Convert outcome variable to numeric
  y <- as.numeric(bootstrap_sample$FLQ_R)  # Replace <outcome_variable> with the actual outcome column name
  
  # Lasso Logistic Regression
  ridge_model <- cv.glmnet(
    x, y,
    family = "binomial",
    alpha = 0,             # ridge regularization
  )
  
  # Best lambda (minimizes cross-validation error)
  best_lambda <- ridge_model$lambda.min
  
  # Coefficients at the best lambda
  coef(ridge_model, s = best_lambda)
  
  # Predicted probabilities
  bootstrap_sample_y_prob <- predict(ridge_model, newx = x, s = best_lambda, type = "response")
  
  #ROC
  roc_bootstrap = roc(bootstrap_sample$FLQ_R, as.vector(bootstrap_sample_y_prob), quiet = TRUE)
  auc_bootstrap = roc_bootstrap$auc
  
  print(paste("AUC Bootstrap", auc_bootstrap))

  # Beta calibration
  bc_bootstrap <- beta_calibration(bootstrap_sample_y_prob, bootstrap_sample$FLQ_R, parameters = "abm")
  beta_bootstrap <- beta_predict(bootstrap_sample_y_prob, bc_bootstrap)

  # Fit logistic regression to recalibrate
  platt_model_bootstrap <- glm(bootstrap_sample$FLQ_R ~ bootstrap_sample_y_prob, family = binomial(link = "logit"))
  # Get recalibrated probabilities
  recalibrated_pred_bootstrap <- predict(platt_model_bootstrap, newdata = data.frame( bootstrap_sample_y_prob), type = "response")

  # X in the original data
  x_orig <- model.matrix(formula, moldova_data)[,-1]  # Remove the intercept column

  # Predict on the original dataset
  origdata_y_prob <- predict(ridge_model, newx = x_orig, s = best_lambda, type = "response")
  
  #ROC
  roc_origidata = roc(moldova_data$FLQ_R, as.vector(origdata_y_prob), , quiet = TRUE)
  auc_origidata = roc_origidata$auc
  
  print(paste("AUC Original", auc_origidata))
  
  # Beta calibration
  bc_origdata <- beta_calibration(origdata_y_prob, moldova_data$FLQ_R, parameters = "ab")
  beta_origdata <- beta_predict(origdata_y_prob, bc_origdata)

  # Fit logistic regression to recalibrate
  platt_model_origdata <- glm(moldova_data$FLQ_R ~ origdata_y_prob, family = binomial(link = "logit"))
  # Get recalibrated probabilities
  recalibrated_pred_origdata <- predict(platt_model_origdata, newdata = data.frame(origdata_y_prob), type = "response")

  # Save the original predictions without calibration
  predictions_nocalibration <- data.frame(bootstrap_sample = rep(i, dim(moldova_data)[1]), predicted_bootstrap = as.vector(bootstrap_sample_y_prob), observed_bootstrap = bootstrap_sample$FLQ_R, bootstrap_pt_id = bootstrap_sample$Pt_id, predicted_origdata = as.vector(origdata_y_prob), observed_origdata = moldova_data$FLQ_R)
  all_predictions_nocalibration = rbind(all_predictions_nocalibration, predictions_nocalibration)
  
  # Save the predictions compare
  predictions_platt_beta_compare <- data.frame(bootstrap_sample = rep(i, dim(moldova_data)[1]), predicted_beta_bootstrap = beta_bootstrap, predicted_platt_bootstrap = recalibrated_pred_bootstrap, observed_bootstrap = bootstrap_sample$FLQ_R, bootstrap_pt_id = bootstrap_sample$Pt_id, predicted_beta_origdata = beta_origdata, predicted_platt_origdata = recalibrated_pred_origdata, observed_origdata = moldova_data$FLQ_R)
  all_predictions_platt_beta_compare = rbind(all_predictions_platt_beta_compare, predictions_platt_beta_compare)
  
  #Using Platt calibration - this had to match method applied to main model
  predictions_platt = data.frame(bootstrap_sample = rep(i, dim(moldova_data)[1]), predicted_bootstrap = recalibrated_pred_bootstrap, observed_bootstrap = bootstrap_sample$FLQ_R,bootstrap_pt_id = bootstrap_sample$Pt_id, predicted_origdata = recalibrated_pred_origdata, observed_origdata = moldova_data$FLQ_R)
  all_predictions_platt = rbind(all_predictions_platt, predictions_platt)
  auc_adjusted[i] = auc_bootstrap - auc_origidata
  
  # Save the predictions Beta calibration
  predictions_beta <- data.frame(bootstrap_sample = rep(i, dim(moldova_data)[1]), predicted_bootstrap = beta_bootstrap, observed_bootstrap = bootstrap_sample$FLQ_R, bootstrap_pt_id = bootstrap_sample$Pt_id, predicted_origdata = beta_origdata, observed_origdata = moldova_data$FLQ_R)
  all_predictions_beta = rbind(all_predictions_beta, predictions_beta)
  
}

write.csv(all_predictions_platt, '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/Optimism Corrected/LR_bootstrap_PlattCalibration.csv', row.names = FALSE)
write.csv(all_predictions_beta, '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/Optimism Corrected/LR_bootstrap_BetaCalibration.csv', row.names = FALSE)
write.csv(all_predictions_platt_beta_compare, "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/Optimism Corrected/LR_bootstrap_platt_beta_compare.csv", row.names = FALSE)
write.csv(all_predictions_nocalibration, "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/Optimism Corrected/LR_bootstrap_nocalibration.csv", row.names = FALSE)


# Calculate optimism-corrected performance and confidence interval
alpha <- 0.05
p_corrected <- auc_mainPM- mean(auc_adjusted)
percentiles <-
  quantile(auc_adjusted, c(alpha / 2, 1 - alpha / 2))
ci_low <- auc_mainPM - percentiles[2]
ci_high <- auc_mainPM - percentiles[1]


#############################
#   Bootstrap - Method 632  #
#############################

all_predictions_platt <- data.frame()

# Parallelized bootstrap sampling and model fitting
for(i in 1:200){
  
  print(i)
  
  set.seed(i)
  bootstrap_sample <- moldova_data %>% sample_n(size = n(), replace = TRUE)
  
  # Convert predictor variables to a matrix
  x <- model.matrix(formula, bootstrap_sample)[,-1]  # Remove the intercept column
  
  # Convert outcome variable to numeric
  y <- as.numeric(bootstrap_sample$FLQ_R)  # Replace <outcome_variable> with the actual outcome column name
  
  # Lasso Logistic Regression
  ridge_model <- cv.glmnet(
    x, y,
    family = "binomial",
    alpha = 0,             # ridge regularization
  )
  
  # Best lambda (minimizes cross-validation error)
  best_lambda <- ridge_model$lambda.min
  
  # # Coefficients at the best lambda
  # coef(ridge_model, s = best_lambda)
  # 
  # # Predicted probabilities
  # bootstrap_sample_y_prob <- predict(ridge_model, newx = x, s = best_lambda, type = "response")
  # 
  # #ROC
  # roc_bootstrap = roc(bootstrap_sample$FLQ_R, as.vector(bootstrap_sample_y_prob), quiet = TRUE)
  # auc_bootstrap = roc_bootstrap$auc
  # 
  # print(paste("AUC Bootstrap", auc_bootstrap))
  # 
  # # Beta calibration
  # bc_bootstrap <- beta_calibration(bootstrap_sample_y_prob, bootstrap_sample$FLQ_R, parameters = "ab")
  # beta_bootstrap <- beta_predict(bootstrap_sample_y_prob, bc_bootstrap)
  # 
  # # Fit logistic regression to recalibrate
  # platt_model_bootstrap <- glm(bootstrap_sample$FLQ_R ~ bootstrap_sample_y_prob, family = binomial(link = "logit"))
  # # Get recalibrated probabilities
  # recalibrated_pred_bootstrap <- predict(platt_model_bootstrap, newdata = data.frame( bootstrap_sample_y_prob), type = "response")
  # 
  # Find the rows where 'pt_id' is not in the bootstrap sample (out-of-bag sample)
  oob_sample <- anti_join(moldova_data, bootstrap_sample, by = "Pt_id")
  
  # Convert predictor variables to a matrix
  x_oob_sample <- model.matrix(formula, oob_sample)[,-1]  # Remove the intercept column
  
  # Predict on the original dataset 
  # Predicted probabilities
  oob_sample_predictions <- predict(ridge_model, newx = x_oob_sample, s = best_lambda, type = "response")
  
  #ROC
  roc_oob = roc(oob_sample$FLQ_R, as.vector(oob_sample_predictions), quiet = TRUE)
  auc_oob = roc_oob$auc
  
  print(paste("AUC Original", auc_oob))
  
  # Fit logistic regression to recalibrate
  platt_model_oob <- glm(oob_sample$FLQ_R ~ oob_sample_predictions, family = binomial(link = "logit"))
  # Get recalibrated probabilities
  recalibrated_pred_oob <- predict(platt_model_oob, newdata = data.frame(oob_sample_predictions), type = "response")
  
  

  # Save the predictions
  predictions_platt <- data.frame(bootstrap_sample = rep(i, dim(oob_sample)[1]), predicted_oob_sample = recalibrated_pred_oob, observed_oob_sample = oob_sample$FLQ_R) 
  all_predictions_platt = rbind(all_predictions_platt, predictions_platt)
  
}

write.csv(all_predictions_platt, '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/Method 632/LR_bootstrap_PlattCalibration_Method632.csv', row.names = FALSE)
