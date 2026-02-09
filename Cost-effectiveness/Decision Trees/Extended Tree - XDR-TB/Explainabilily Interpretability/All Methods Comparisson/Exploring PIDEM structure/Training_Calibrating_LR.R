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
library(dplyr)
library(tidyr)
library(stringr)

source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Code/LR_model_specification.R')
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Code/ROC_performance.R')
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Code/crossvalidation_HM.R')

set.seed(1)

# Load the Moldova dataset
data_path <-
  "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_LR_Augumented.csv"
moldova_data <- read.csv(data_path)
moldova_data$Pt_id = seq(1:dim(moldova_data)[1])

#################
#   Main Pred   #
#################

# Convert predictor variables to a matrix
x <- model.matrix(formula, moldova_data)[,-1]  # Remove the intercept column

# Convert outcome variable to numeric
y <- as.numeric(moldova_data$FLQ_R)

# Ridge Logistic Regression
ridge_model <- cv.glmnet(
  x, y,
  family = "binomial",
  alpha = 0
)

# Best lambda (minimizes cross-validation error)
best_lambda <- ridge_model$lambda.min
print(best_lambda)

# Coefficients at the best lambda
coef(ridge_model, s = best_lambda)

# Predicted probabilities (raw)
y_prob <- predict(ridge_model, newx = x, s = best_lambda, type = "response")

# Beta calibration
bc_mainpred <- beta_calibration(y_prob, moldova_data$FLQ_R, parameters = "abm")
beta_mainpredp <- beta_predict(y_prob, bc_mainpred)

# -------------------------------
# 1) Calibrated prediction function
# -------------------------------
predict_calibrated <- function(newx_mat) {
  # newx_mat must be a matrix with the same columns as x
  p_raw <- predict(
    ridge_model,
    newx = newx_mat,
    s = best_lambda,
    type = "response"
  )
  beta_predict(p_raw, bc_mainpred)
}

