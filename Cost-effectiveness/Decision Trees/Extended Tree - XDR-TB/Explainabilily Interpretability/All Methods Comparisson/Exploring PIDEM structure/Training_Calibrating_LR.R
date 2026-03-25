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

# Identify binary (dummy) vs continuous columns
is_dummy <- apply(x, 2, function(col) all(col %in% c(0, 1)))

# Standardize only continuous variables, leave dummies as-is
x_scaled <- x
x_mean <- rep(0, ncol(x))
x_sd   <- rep(1, ncol(x))
names(x_mean) <- names(x_sd) <- colnames(x)

x_mean[!is_dummy] <- colMeans(x[, !is_dummy])
x_sd[!is_dummy]   <- apply(x[, !is_dummy], 2, sd)

x_scaled[, !is_dummy] <- scale(x[, !is_dummy])

# Convert outcome variable to numeric
y <- as.numeric(moldova_data$FLQ_R)

# Ridge Logistic Regression (standardize=FALSE since we did it manually)
ridge_model <- cv.glmnet(
  x_scaled, y,
  family = "binomial",
  alpha = 0,
  standardize = FALSE
)

# Best lambda (minimizes cross-validation error)
best_lambda <- ridge_model$lambda.min
print(best_lambda)

# Coefficients at the best lambda (now comparable across predictors)
coef(ridge_model, s = best_lambda)

# Predicted probabilities (raw)
y_prob <- predict(ridge_model, newx = x_scaled, s = best_lambda, type = "response")

# -------------------------------
# 1) Calibrated prediction function
# -------------------------------
predict_originalmodel <- function(newx_mat) {
  # Ensure input is always a matrix
  if (!is.matrix(newx_mat)) {
    newx_mat <- matrix(newx_mat, nrow = 1, dimnames = list(NULL, names(newx_mat)))
  }
  
  # Apply the same scaling as training data (continuous variables only)
  newx_scaled <- newx_mat
  newx_scaled[, !is_dummy] <- scale(
    newx_mat[, !is_dummy, drop = FALSE],
    center = x_mean[!is_dummy],
    scale  = x_sd[!is_dummy]
  )
  predict(
    ridge_model,
    newx = newx_scaled,
    s = best_lambda,
    type = "response"
  )
}