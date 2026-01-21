# -----------------------------
# Load required libraries
# -----------------------------
library(dplyr)
library(ggplot2)

# -----------------------------
# 1️⃣ Function to compute contributions for a single patient
# -----------------------------
compute_contributions <- function(x_patient, coef_df) {
  # x_patient: 1-row matrix/data.frame for a single patient from fit_rulefit$modmat
  # coef_df: data.frame of model coefficients with columns: Feature, coefficient
  
  # Remove intercept for individual contributions
  coef_no_intercept <- coef_df %>% filter(Feature != "(Intercept)")
  
  # Keep only the features present in both patient's data and coefficients
  common_terms <- intersect(colnames(x_patient), coef_no_intercept$Feature)
  
  # Compute contributions: contribution = feature_value * coefficient
  contribs <- x_patient[, common_terms, drop = TRUE] *
    coef_no_intercept$Coefficient[match(common_terms, coef_no_intercept$Feature)]
  
  # Extract intercept coefficient
  intercept <- coef_df$Coefficient[coef_df$Feature == "(Intercept)"]
  
  # Total logit (linear predictor) and probability (sigmoid)
  total_logit <- intercept + sum(contribs)
  predicted_prob <- 1 / (1 + exp(-total_logit))
  
  # Tidy contributions into a data frame
  contrib_df <- data.frame(
    Feature = names(contribs),
    Contribution = contribs
  ) %>%
    filter(Contribution != 0) %>%   # remove features with zero contribution
    arrange(desc(abs(Contribution)))  # sort by absolute contribution
  
  # Return all relevant information
  list(
    intercept = intercept,
    contributions = contribs,
    total_logit = total_logit,
    predicted_prob = predicted_prob,
    contrib_df = contrib_df
  )
}
