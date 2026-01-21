# ========================
#     SHAP EXPLANATION
# ========================

# 📦 Load packages
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
library(iml)
library(DALEX)

# Set working directory to script location
if (rstudioapi::isAvailable()) {
  setwd(dirname(rstudioapi::getSourceEditorContext()$path))
}

# Load helper functions
source("LR_model_specification.R")
source("ROC_performance.R")
source("crossvalidation_HM.R")

set.seed(1)

# ========================
#     Load Data
# ========================

data_path <- "/Users/mariananeves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_LR_Augumented.csv"
moldova_data <- read.csv(data_path)
moldova_data$Pt_id <- seq_len(nrow(moldova_data))

# ========================
#   Prepare Data
# ========================

# Define the logistic regression formula (make sure 'formula' is defined correctly in your sourced R script)
# Example fallback if not defined:
# formula <- FLQ_R ~ age + sex + HIV + urban + smear + previous_TB

# Build design matrix (exclude intercept)
x <- model.matrix(formula, moldova_data)[, -1]

# Outcome: FLQ resistance (should be binary 0/1)
y <- as.numeric(moldova_data$FLQ_R)

# ========================
#   Train Ridge Logistic
# ========================

ridge_model <- cv.glmnet(
  x, y,
  family = "binomial",
  alpha = 0  # alpha = 0 => ridge
)

# Best lambda
best_lambda <- ridge_model$lambda.min
cat("Best lambda:", best_lambda, "\n")

# Predicted probabilities
y_prob <- predict(ridge_model, newx = x, s = best_lambda, type = "response")

# Evaluate AUC
roc_mainPM <- roc(moldova_data$FLQ_R, as.vector(y_prob))
auc_mainPM <- roc_mainPM$auc
cat("AUC:", auc_mainPM, "\n")

# ========================
#     SHAP Values
# ========================

# Prepare data frame version of x
x_df <- as.data.frame(x)
y_vec <- y

# Define custom predict function for glmnet
predict_glmnet <- function(model, newdata) {
  new_matrix <- as.matrix(newdata)
  predict(model, newx = new_matrix, s = best_lambda, type = "response")[, 1]
}

# Create iml Predictor
predictor <- Predictor$new(
  model = ridge_model,
  data = x_df,
  y = y_vec,
  predict.fun = predict_glmnet,
  type = "prob"
)

# Explain one patient — patient index 10
shap_10 <- Shapley$new(predictor, x.interest = x_df[10, ])

# Plot SHAP explanation for that instance
plot(shap_10)

# ========================
#  Global SHAP Importance
# ========================

# Compute SHAP for multiple patients
n_explain <- 540  # number of rows to explain
shap_list <- lapply(1:n_explain, function(i) {
  s <- Shapley$new(predictor, x.interest = x_df[i, ])
  df <- data.frame(s$results)
  df$Pt_id <- moldova_data$Pt_id[i]
  df
})

shap_df <- bind_rows(shap_list)

# Average absolute SHAP values per feature
shap_summary <- shap_df %>%
  group_by(feature) %>%
  summarise(mean_abs_phi = mean(abs(phi), na.rm = TRUE)) %>%
  arrange(desc(mean_abs_phi))

print(shap_summary, n = Inf)

# ========================
#  Save Results
# ========================

# Save global SHAP values to Excel or CSV
write.csv(shap_summary,
          file = "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/SHAP_summary_FLQ_R.csv",
          row.names = FALSE)

# Optional: Save individual SHAP values (for n = 50 patients)
write.csv(shap_df,
          file = "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/SHAP_individual_values_FLQ_R.csv",
          row.names = FALSE)

cat("✅ SHAP analysis complete. Results saved.\n")
