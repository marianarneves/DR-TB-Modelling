# =============================================================================
# Inter-Expert PMDT Analysis
# =============================================================================
# Purpose : Compute YLL-weighted optimal treatment thresholds (p*) per patient,
#           identify each patient's most important feature driving the
#           recommended treatment, and plot feature importance for both the
#           ML-Assisted Decision Model framework and the LR Surrogate.
#
# Inputs  : LR predictions, life expectancy table, PIDEM probability outputs,
#           decision-tree NMB outputs, patient-level Moldova data.
# Outputs : Side-by-side bar charts of top-5 feature importance.
# =============================================================================


# -----------------------------------------------------------------------------
# 0. Libraries
# -----------------------------------------------------------------------------

library(readxl)
library(dplyr)
library(ggplot2)
library(scales)
library(tidyverse)
library(pROC)
library(patchwork)   # side-by-side plots
library(irr)


# -----------------------------------------------------------------------------
# 1. Working directory & sourced scripts
# -----------------------------------------------------------------------------
# NOTE: Variables produced by sourced scripts (e.g. feature_weights,
#       predict_originalmodel, formula, moldova_data, get_main_contribution,
#       feature_contributions_patient) retain their original names to stay
#       consistent with those scripts.

setwd('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/R01 TB/Papers/Inter Exp PMDT')

# Fit and calibrate the logistic regression used throughout the analysis
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/All Methods Comparisson/Exploring PIDEM structure/Training_Calibrating_LR.R')

# Compute feature weights from the calibrated model
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/All Methods Comparisson/Exploring PIDEM structure/Feature_Weight_Calculation.R')

# Patient-level feature contribution function
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/All Methods Comparisson/Exploring PIDEM structure/Feature_Contribution_Calculation.R')

# Main-contribution function for the LR surrogate
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/All Methods Comparisson/main_contribution_LR_surrogate.R')


# -----------------------------------------------------------------------------
# 2. Helper: expand WHO age-band string into a vector of individual ages
# -----------------------------------------------------------------------------

expand_ageband <- function(ageband) {
  
  ageband <- str_trim(ageband)
  
  if (ageband == "<1 year") return(0)
  
  if (str_detect(ageband, "\\+")) {
    lower <- as.numeric(str_extract(ageband, "\\d+"))
    return(seq(100, lower, by = -1))
  }
  
  bounds <- as.numeric(str_extract_all(ageband, "\\d+")[[1]])
  seq(bounds[2], bounds[1], by = -1)
}


# -----------------------------------------------------------------------------
# 3. Helper: look up remaining life expectancy (used as YLL) per individual
# -----------------------------------------------------------------------------

  classify_age <- function(age) {
    dplyr::case_when(
      age < 1   ~ "<1 year",
      age <= 4  ~ "1-4 years",
      age <= 9  ~ "5-9 years",
      age <= 14 ~ "10-14 years",
      age <= 19 ~ "15-19 years",
      age <= 24 ~ "20-24 years",
      age <= 29 ~ "25-29 years",
      age <= 34 ~ "30-34 years",
      age <= 39 ~ "35-39 years",
      age <= 44 ~ "40-44 years",
      age <= 49 ~ "45-49 years",
      age <= 54 ~ "50-54 years",
      age <= 59 ~ "55-59 years",
      age <= 64 ~ "60-64 years",
      age <= 69 ~ "65-69 years",
      age <= 74 ~ "70-74 years",
      age <= 79 ~ "75-79 years",
      age <= 84 ~ "80-84 years",
      TRUE       ~ "85+ years"
    )
  }


# -----------------------------------------------------------------------------
# 4. Load data
# -----------------------------------------------------------------------------

lr_predictions <- read.csv(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/LR_MainPM_platt_beta_compare.csv'
)

le_data <- read.csv(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/LE_Moldova.csv'
)

nmb_by_yll <- read_excel(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/DT Only/Input_V10/Test age x NMB/PIDEMp/PIDEMp_YLLcontinuous_test_output_2.xlsx'
)

pidem_probabilities <- read_xlsx(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM input Only/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx'
)

pidem_patient_data <- read.csv(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/No Calibration/PM input Only/Input/ModLE/Moldova_data_opt_treat_prediction_allthresholds_wtp2.csv'
)

shap_long <- read_csv(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/No Calibration/PM input Only/Pre pruning/MaxTreeDepth 10/SHAP_long_wtp2.csv'
)


# -----------------------------------------------------------------------------
# 5. Compute YLL for every patient in the LR predictions data
# -----------------------------------------------------------------------------
LE_2019_Moldova <- 70.94

lr_predictions <- lr_predictions %>%
  mutate(YLL = ifelse(age > LE_2019_Moldova, 0, LE_2019_Moldova - age))

# -----------------------------------------------------------------------------
# 6. Compute NMB and the optimal treatment threshold (p*)
# -----------------------------------------------------------------------------

WTP <- 5714.43

nmb_with_pstar <- nmb_by_yll %>%
  mutate(
    NMB_FLQ_R = WTP * DALY_FLQres + Cost_FLQres,
    NMB_FLQ_S = WTP * DALY_FLQsus + Cost_FLQsus,
    pstar     = (NMB_DLM - NMB_FLQ_S) / (NMB_FLQ_R - NMB_FLQ_S),
    Age = Person
  ) %>%
  select(Age, pstar, Opt_Treat) 

#---6.b
pt_pstar_above1 = lr_predictions %>%
                    left_join(nmb_with_pstar, by = c('age' = 'Age')) %>%
                    filter(pstar > 0.99)

#---6.c
# Ensure data is sorted
nmb_with_pstar <- nmb_with_pstar %>% arrange(Age)

# -------------------------------
# Find crossing point p* ≈ 1
# -------------------------------
cross_x <- nmb_with_pstar %>%
  slice(which.min(abs(pstar - 1))) %>%
  pull(Age)

cross_x <- nmb_with_pstar$Age[which.min(abs(nmb_with_pstar$pstar - 1))]

# -------------------------------
# Build Plot
# -------------------------------

Prob_Age = ggplot(nmb_with_pstar, aes(x = Age, y = pstar)) +
  
  # --- RIBBONS FIRST (background layer) ---
  geom_ribbon(aes(ymin = 0, ymax = pstar, fill = "BPaLM"), alpha = 0.25) +
  geom_ribbon(aes(ymin = pstar, ymax = max(pstar, na.rm = TRUE), fill = "BPaLC"), alpha = 0.20) +
  
  # --- REFERENCE LINE (draw AFTER ribbons so it stays visible) ---
  geom_hline(yintercept = 1, linetype = "dotted", color = "gray40", linewidth = 1) +
  
  # --- MAIN LINE (draw AFTER EVERYTHING so it is always visible) ---
  geom_line(color = "#1f4e79", linewidth = 1.4) +
  # add a white outline to make it visible near 0
  geom_line(color = "white", linewidth = 2, alpha = 0.4) +
  geom_point(color = "#163758", size = 1) +
  
  # Crossing marker
  geom_vline(xintercept = cross_x, linetype = "dashed", color = "#d62728", linewidth = 1.1) +
  
  # Annotation
  annotate(
    "label",
    x = cross_x - 10,
    y = max(nmb_with_pstar$pstar, na.rm = TRUE) * 0.9,
    label = paste0("Age ≈ ", round(cross_x, 1)),
    size = 4.5,
    fill = "white",
    color = "#d62728",
    label.size = 0
  ) +
  
  labs(
    #title = "Probability Threshold p* as a Function of Years of Life Lost",
    x = "Age",
    y = "p*(Z)",
    fill = "Recommendation"
  ) +
  
  scale_x_continuous(
    breaks = seq(0, ceiling(max(nmb_with_pstar$Age, na.rm = TRUE)), by = 5),
    labels = scales::number_format(accuracy = 1),
    expand = expansion(mult = c(0, 0.02))
  ) +
  scale_y_continuous(
    breaks = seq(0, ceiling(max(nmb_with_pstar$pstar, na.rm = TRUE)), by = 0.25),
    labels = scales::number_format(accuracy = 0.01),
    expand = expansion(mult = c(0, 0))
  ) +
  
  scale_fill_manual(values = c("BPaLM" = "#7eb6ff", "BPaLC" = "#ffb866")) +
  
  theme_minimal(base_size = 15) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0, size = 16),
    axis.text.y = element_text(size = 14,  face = "bold"),
    axis.text.x = element_text(size = 14),
    axis.title.x = element_text(size = 16, face = "bold"),
    axis.title.y = element_text(size = 16, face = "bold"),
    panel.grid.major = element_line(color = "grey85", linewidth = 0.4),
    panel.grid.minor = element_blank(),
    axis.title = element_text(face = "bold"),
    legend.position = "bottom",
    legend.title = element_text(size = 14,face = "bold"),
    legend.text = element_text(size = 14),
    legend.key.width = unit(1, "cm")
  )

ggsave('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/R01 TB/Papers/Inter Exp PMDT/figures/Pstar_age_plot.png', Prob_Age, width = 12, height = 6, dpi = 300)

# -----------------------------------------------------------------------------
# 7. Build YLL distribution weights from observed patients
# -----------------------------------------------------------------------------

ageband_weights <- lr_predictions %>%
  mutate(age_band = classify_age(age)) %>%
  count(age_band) %>%
  mutate(weight = n / sum(n)) %>%
  select(age_band, weight)


# -----------------------------------------------------------------------------
# 8. Join p* values with YLL weights and expand to individual ages
# -----------------------------------------------------------------------------

pstar_avg <- nmb_with_pstar %>%
  left_join(tibble(Age = 0:100) %>%
              mutate(age_band = classify_age(Age)) %>%
              left_join(ageband_weights, by = "age_band"), by = "Age") %>%
  group_by(age_band, weight) %>%
  summarise(pstar_byage = mean(pstar, na.rm=TRUE)) %>%
  mutate(pstar_byage_weighted = weight * pstar_byage) %>%
  ungroup()%>%
  summarise(pstar_weightedavg = sum(pstar_byage_weighted, na.rm=TRUE))%>%
  pull(pstar_weightedavg)


# -----------------------------------------------------------------------------
# 9. Fit LR surrogate model on PIDEM optimal-treatment labels
# -----------------------------------------------------------------------------

set.seed(123)

pidem_model_data <- pidem_patient_data %>%
  mutate(Opt_Treat_n = as.integer(Opt_Treat != "FLQ")) %>%
  select(-c(Person, Pt_id, FLQ_R, n, Residence, Opt_Treat))

x_matrix <- model.matrix(Opt_Treat_n ~ ., pidem_model_data)[, -1]
y_vector  <- pidem_model_data$Opt_Treat_n
n_obs     <- nrow(x_matrix)

surrogate_fit <- glm(
  Opt_Treat_n ~ .,
  data   = data.frame(Opt_Treat_n = y_vector, x_matrix),
  family = binomial()
)

summary(surrogate_fit)


# -----------------------------------------------------------------------------
# 10. Apparent performance of the LR surrogate
# -----------------------------------------------------------------------------

pidem_model_data$pred_prob  <- predict(surrogate_fit, type = "response")
pidem_model_data$pred_class <- as.integer(pidem_model_data$pred_prob > 0.5)

roc_apparent <- roc(y_vector, pidem_model_data$pred_prob)
cat("Apparent AUC:", round(auc(roc_apparent), 3), "\n")


# -----------------------------------------------------------------------------
# 11. 5-fold cross-validation for the LR surrogate
# -----------------------------------------------------------------------------

k        <- 5
fold_ids <- sample(rep(1:k, length.out = n_obs))
cv_probs <- rep(NA_real_, n_obs)

fold_metrics <- data.frame(
  fold     = integer(k),
  accuracy = numeric(k),
  mcc      = numeric(k)
)

for (fold in 1:k) {
  
  test_idx  <- which(fold_ids == fold)
  train_idx <- setdiff(seq_len(n_obs), test_idx)
  
  fold_fit <- glm(
    y ~ .,
    data   = data.frame(y = y_vector[train_idx], x_matrix[train_idx, ]),
    family = binomial()
  )
  
  fold_probs <- predict(
    fold_fit,
    newdata = data.frame(y = y_vector[test_idx], x_matrix[test_idx, ]),
    type = "response"
  )
  
  cv_probs[test_idx] <- fold_probs
  
  fold_preds <- as.integer(fold_probs > 0.5)
  fold_truth <- y_vector[test_idx]
  
  TP <- sum(fold_preds == 1 & fold_truth == 1)
  TN <- sum(fold_preds == 0 & fold_truth == 0)
  FP <- sum(fold_preds == 1 & fold_truth == 0)
  FN <- sum(fold_preds == 0 & fold_truth == 1)
  
  accuracy  <- (TP + TN) / length(fold_truth)
  mcc_denom <- sqrt((TP + FP) * (TP + FN) * (TN + FP) * (TN + FN))
  mcc       <- if (mcc_denom == 0) 0 else (TP * TN - FP * FN) / mcc_denom
  
  fold_metrics[fold, ] <- c(fold, accuracy, mcc)
}

cat("\nPer-fold CV metrics (threshold = 0.5):\n")
print(round(fold_metrics, 3))

cat(sprintf(
  "\nMean Accuracy : %.3f  (SD %.3f)\n",
  mean(fold_metrics$accuracy), sd(fold_metrics$accuracy)
))
cat(sprintf(
  "Mean MCC      : %.3f  (SD %.3f)\n",
  mean(fold_metrics$mcc), sd(fold_metrics$mcc)
))

roc_cv <- roc(y_vector, cv_probs)
cat(sprintf("Pooled CV AUC : %.3f\n", round(auc(roc_cv), 3)))

pidem_model_data$pred_prob_cv <- cv_probs


# -----------------------------------------------------------------------------
# 12. Main contribution (LR surrogate) for all patients
# -----------------------------------------------------------------------------

surrogate_main_contributions <- map_dfr(
  seq_len(n_obs),
  ~ get_main_contribution(
    fit        = surrogate_fit,
    x_matrix   = x_matrix,
    y_vector   = y_vector,
    patient_id = .x
  )
)

driver_frequency <- surrogate_main_contributions %>%
  rename(variable = main_variable) %>%
  mutate(
    variable = gsub("_(?=[^_]*$).*", "", variable, perl = TRUE),
    variable = gsub("_", " ", variable),
    variable = ifelse(variable == "prevalence", "Prevalence", variable),
    variable = ifelse(variable == "TB type", "TB Type", variable)
  ) %>%
  count(variable, sort = TRUE)

print(head(driver_frequency, 10))

#--12.b

#Evaluating explanations for patients with pstar > 1
pt_pstar_above1 %>%
  left_join(surrogate_main_contributions, by = c('pt_id' = 'patient_id'))


# -----------------------------------------------------------------------------
# 12b. Load and prepare DT surrogate SHAP explanations
# -----------------------------------------------------------------------------

n_patients <- 540

# Step 1: Select top feature per patient BEFORE cleaning names
# Logic mirrors get_main_contribution: select feature supporting the recommendation
# CLZ (predicted == 1) -> most positive SHAP value
# FLQ (predicted == 0) -> most negative SHAP value
dt_top_feature_per_patient <- shap_long %>%
  group_by(Pt_id) %>%
  summarise(
    top_feature = case_when(
      first(predicted) == 1 ~ feature[which.max(shap_value)],
      first(predicted) == 0 ~ feature[which.min(shap_value)]
    ),
    .groups = "drop"
  ) %>%
  rename(feature = top_feature)

# Ensure all 540 patients present
dt_top_feature_per_patient <- tibble(Pt_id = seq_len(n_patients)) %>%
  left_join(dt_top_feature_per_patient, by = "Pt_id")

cat("Number of patients:", nrow(dt_top_feature_per_patient), "\n")
cat("Patients with NA:", sum(is.na(dt_top_feature_per_patient$feature)), "\n")

# Step 2: Clean feature names AFTER selecting top feature
dt_top_feature_per_patient <- dt_top_feature_per_patient %>%
  mutate(
    feature = trimws(gsub(":.*", "", feature)),
    feature = ifelse(feature == "Living_condition_missing", "Living Condition", feature),
    feature = ifelse(feature == "prevalence_NA", "Prevalence", feature),
    feature = ifelse(feature == "Money_assistance_missing", "Money Assistance", feature)
  )

# Step 3: Top 5 features for DT surrogate (normalized frequency)
dt_top5 <- dt_top_feature_per_patient %>%
  count(feature, name = "n") %>%
  mutate(normalized_importance = n / sum(n)) %>%
  arrange(desc(normalized_importance)) %>%
  slice_head(n = 5) %>%
  rename(variable = feature)

# Step 4: Also clean shap_long names for any downstream use
shap_long <- shap_long %>%
  mutate(
    feature = trimws(gsub(":.*", "", feature)),
    feature = ifelse(feature == "Living_condition_missing", "Living Condition", feature)
  )


# Step 5: Evaluating explanations for patients with pstar > 1
pt_pstar_above1 %>%
  left_join(dt_top_feature_per_patient, by = c('pt_id' = 'Pt_id'))

# -----------------------------------------------------------------------------
# 13. Identify the most important feature per patient (PIDEM framework)
# -----------------------------------------------------------------------------

most_important_feature <- map_chr(seq_len(n_patients), function(i) {
  
  pt_lr    <- lr_predictions %>% filter(pt_id == i)
  pt_pidem <- pidem_probabilities %>% filter(Person == pt_lr$pt_id - 1)
  
  patient_row <- moldova_data %>%
    slice(pt_lr$pt_id) %>%
    select(-Pt_id) %>%
    as.data.frame()
  
  feature_contribs <- feature_contributions_patient(
    patient_row     = patient_row,
    feature_weights = feature_weights,
    predict_fn      = predict_originalmodel,
    formula         = formula
  )
  
  yll_contrib <- nmb_with_pstar %>%
    filter(Age == patient_row$Age) %>%
    mutate(YLLcontrib = as.numeric(pstar_avg) - pstar) %>%
    pull(YLLcontrib)
  
  all_contribs <- bind_rows(
    feature_contribs,
    tibble(Feature = "YLL", Contribution = yll_contrib)
  )
  
  aligned_contribs <- if (pt_pidem$Opt_Treat == "FLQ") {
    filter(all_contribs, Contribution < 0)
  } else {
    filter(all_contribs, Contribution > 0)
  }
  
  if (nrow(aligned_contribs) == 0) return(NA_character_)
  
  aligned_contribs %>%
    mutate(rel_importance = abs(Contribution) / sum(abs(Contribution))) %>%
    slice_max(rel_importance, n = 1, with_ties = FALSE) %>%
    pull(Feature)
})


# -----------------------------------------------------------------------------
# 14. Prepare feature importance tables for plotting
# -----------------------------------------------------------------------------

# ---- PIDEM framework: top-5 features ----
pidem_top5 <- as.data.frame(table(most_important_feature)) %>%
  rename(variable = most_important_feature, n = Freq) %>%
  mutate(
    variable = case_when(
      variable == "Tb Type" ~ "TB Type",
      variable == "YLL"     ~ "Age (Z)",
      TRUE                   ~ variable
    ),
    normalized_importance = n / sum(n)
  ) %>%
  arrange(desc(normalized_importance)) %>%
  slice_head(n = 5)

# ---- LR surrogate: top-5 features ----
surrogate_top5 <- driver_frequency %>%
  mutate(normalized_importance = n / sum(n)) %>%
  arrange(desc(normalized_importance)) %>%
  slice_head(n = 5)


# -----------------------------------------------------------------------------
# 15. Agreement: does the LR surrogate's top feature match the PIDEM top feature?
# -----------------------------------------------------------------------------

# ---- 1. Clean LR surrogate feature names to match PIDEM labels ----
surrogate_top_feature_clean <- surrogate_main_contributions %>%
  mutate(
    feature_clean = gsub("_(?=[^_]*$).*", "", main_variable, perl = TRUE),
    feature_clean = gsub("_", " ", feature_clean),
    feature_clean = ifelse(feature_clean == "prevalence", "Prevalence", feature_clean)
  ) %>%
  pull(feature_clean)

# ---- 2. Apply the same display relabelling to PIDEM features ----
pidem_top_feature_clean <- case_when(
  most_important_feature == "Tb Type" ~ "TB type",
  most_important_feature == "YLL"     ~ "Age",
  TRUE                                 ~ most_important_feature
)

# ---- 3. Build a per-patient comparison table ----
feature_agreement <- tibble(
  patient_id        = seq_len(n_patients),
  pidem_feature     = pidem_top_feature_clean,
  surrogate_feature = surrogate_top_feature_clean,
  match             = pidem_feature == surrogate_feature
)

# ---- 4. Overall agreement (excluding patients where PIDEM returned NA) ----
agreement_summary <- feature_agreement %>%
  filter(!is.na(pidem_feature)) %>%
  summarise(
    n_compared    = n(),
    n_match       = sum(match),
    pct_agreement = mean(match) * 100
  )

cat("\n--- Feature Agreement: LR Surrogate vs PIDEM Framework ---\n")
cat(sprintf(
  "Patients compared (non-NA PIDEM feature): %d\n",
  agreement_summary$n_compared
))
cat(sprintf(
  "Matching top feature                    : %d (%.1f%%)\n",
  agreement_summary$n_match,
  agreement_summary$pct_agreement
))

# ---- 5. Agreement broken down by PIDEM feature ----
agreement_by_feature <- feature_agreement %>%
  filter(!is.na(pidem_feature)) %>%
  group_by(pidem_feature) %>%
  summarise(
    n             = n(),
    n_match       = sum(match),
    pct_agreement = round(mean(match) * 100, 1),
    .groups       = "drop"
  ) %>%
  arrange(desc(n))

cat("\nAgreement by PIDEM top feature:\n")
print(agreement_by_feature)


# -----------------------------------------------------------------------------
# 15b. Agreement: DT surrogate vs PIDEM and LR surrogate
# -----------------------------------------------------------------------------

harmonise_features <- function(x) {
  case_when(
    tolower(x) == "tb type"          ~ "TB Type",
    tolower(x) == "family size"      ~ "Family Size",
    tolower(x) == "family size18"    ~ "Family Size18",
    tolower(x) == "money assistance" ~ "Money Assistance",
    tolower(x) == "living condition" ~ "Living Condition",
    tolower(x) == "outside moldova"  ~ "Outside Moldova",
    tolower(x) == "yll"              ~ "Age",
    TRUE                              ~ x
  )
}

# Clean DT top feature per patient to match PIDEM labels
dt_top_feature_clean <- dt_top_feature_per_patient %>%
  arrange(Pt_id) %>%
  mutate(
    feature_clean = case_when(
      feature == "Tb Type" ~ "TB type",
      feature == "YLL"     ~ "Age",
      TRUE                  ~ feature
    )
  ) %>%
  pull(feature_clean)

# Build three-way comparison table
feature_agreement_3way <- tibble(
  patient_id        = seq_len(n_patients),
  pidem_feature     = pidem_top_feature_clean,
  surrogate_feature = surrogate_top_feature_clean,
  dt_feature        = dt_top_feature_clean,
  match_lr_pidem    = pidem_feature == surrogate_feature,
  match_dt_pidem    = pidem_feature == dt_feature,
  match_dt_lr       = surrogate_feature == dt_feature,
  match_all_three   = pidem_feature == surrogate_feature & pidem_feature == dt_feature
)

feature_agreement_3way <- feature_agreement_3way %>%
  mutate(across(c(pidem_feature, surrogate_feature, dt_feature), harmonise_features))

# Overall agreement summary
agreement_summary_3way <- feature_agreement_3way %>%
  filter(!is.na(pidem_feature)) %>%
  summarise(
    n_compared       = n(),
    n_match_lr_pidem = sum(match_lr_pidem),
    n_match_dt_pidem = sum(match_dt_pidem),
    n_match_dt_lr    = sum(match_dt_lr),
    n_match_all      = sum(match_all_three),
    pct_lr_pidem     = mean(match_lr_pidem) * 100,
    pct_dt_pidem     = mean(match_dt_pidem) * 100,
    pct_dt_lr        = mean(match_dt_lr) * 100,
    pct_all_three    = mean(match_all_three) * 100
  )

cat("\n--- Three-Way Feature Agreement ---\n")
cat(sprintf("Patients compared              : %d\n",   agreement_summary_3way$n_compared))
cat(sprintf("LR Surrogate vs PIDEM          : %d (%.1f%%)\n", agreement_summary_3way$n_match_lr_pidem, agreement_summary_3way$pct_lr_pidem))
cat(sprintf("DT Surrogate vs PIDEM          : %d (%.1f%%)\n", agreement_summary_3way$n_match_dt_pidem, agreement_summary_3way$pct_dt_pidem))
cat(sprintf("DT Surrogate vs LR Surrogate   : %d (%.1f%%)\n", agreement_summary_3way$n_match_dt_lr,    agreement_summary_3way$pct_dt_lr))
cat(sprintf("All three agree                : %d (%.1f%%)\n", agreement_summary_3way$n_match_all,      agreement_summary_3way$pct_all_three))

# Cohen's Kappa - full dataset
kappa_lr_pidem <- kappa2(data.frame(
  rater1 = feature_agreement_3way$pidem_feature,
  rater2 = feature_agreement_3way$surrogate_feature
))

kappa_dt_pidem <- kappa2(data.frame(
  rater1 = feature_agreement_3way$pidem_feature,
  rater2 = feature_agreement_3way$dt_feature
))

kappa_dt_lr <- kappa2(data.frame(
  rater1 = feature_agreement_3way$surrogate_feature,
  rater2 = feature_agreement_3way$dt_feature
))

cat("\n--- Cohen's Kappa (full dataset) ---\n")
cat(sprintf("LR Surrogate vs PIDEM        : kappa = %.3f (p = %.4f)\n", kappa_lr_pidem$value, kappa_lr_pidem$p.value))
cat(sprintf("DT Surrogate vs PIDEM        : kappa = %.3f (p = %.4f)\n", kappa_dt_pidem$value, kappa_dt_pidem$p.value))
cat(sprintf("DT Surrogate vs LR Surrogate : kappa = %.3f (p = %.4f)\n", kappa_dt_lr$value,    kappa_dt_lr$p.value))

# Agreement broken down by PIDEM feature
agreement_by_feature_3way <- feature_agreement_3way %>%
  filter(!is.na(pidem_feature)) %>%
  group_by(pidem_feature) %>%
  summarise(
    n                = n(),
    pct_lr_pidem     = round(mean(match_lr_pidem)  * 100, 1),
    pct_dt_pidem     = round(mean(match_dt_pidem)  * 100, 1),
    pct_all_three    = round(mean(match_all_three) * 100, 1),
    .groups = "drop"
  ) %>%
  arrange(desc(n))

cat("\nThree-way agreement by PIDEM top feature:\n")
print(agreement_by_feature_3way)

# --- Agreement excluding edge cases ---

dt_top_feature_per_patient_edgeexcluded <- dt_top_feature_per_patient %>%
  arrange(Pt_id) %>%
  mutate(
    feature_clean = case_when(
      feature == "Tb Type" ~ "TB type",
      feature == "YLL"     ~ "Age",
      TRUE                  ~ feature
    )
  ) %>%
  filter(!(Pt_id %in% pt_pstar_above1$pt_id))

surrogate_top_feature_clean_edgeexcluded <- surrogate_main_contributions %>%
  filter(!(patient_id %in% pt_pstar_above1$pt_id)) %>%
  mutate(
    feature_clean = gsub("_(?=[^_]*$).*", "", main_variable, perl = TRUE),
    feature_clean = gsub("_", " ", feature_clean),
    feature_clean = ifelse(feature_clean == "prevalence", "Prevalence", feature_clean)
  ) %>%
  pull(feature_clean)

pidem_top_feature_clean_edgeexcluded <- data.frame(most_important_feature= most_important_feature,
  Patient = seq(1:540)) %>%
  filter(!(Patient %in% pt_pstar_above1$pt_id)) %>%
  mutate(
    most_important_feature_vector = case_when(
      most_important_feature == "Tb Type" ~ "TB type",
      most_important_feature == "YLL"     ~ "Age",
      TRUE                      ~ most_important_feature
    )
  ) %>%
  pull(most_important_feature_vector)

# Build three-way comparison table - edge cases excluded
feature_agreement_3way_edgeexcluded <- tibble(
  patient_id        = seq_len(n_patients - 18),
  pidem_feature     = pidem_top_feature_clean_edgeexcluded,
  surrogate_feature = surrogate_top_feature_clean_edgeexcluded,
  dt_feature        = dt_top_feature_per_patient_edgeexcluded$feature_clean,
  match_lr_pidem    = pidem_feature == surrogate_feature,
  match_dt_pidem    = pidem_feature == dt_feature,
  match_dt_lr       = surrogate_feature == dt_feature,
  match_all_three   = pidem_feature == surrogate_feature & pidem_feature == dt_feature
)

# edge-excluded
feature_agreement_3way_edgeexcluded <- feature_agreement_3way_edgeexcluded %>%
  mutate(across(c(pidem_feature, surrogate_feature, dt_feature), harmonise_features))

# Overall agreement summary - edge cases excluded
agreement_summary_3way_edgeexcluded <- feature_agreement_3way_edgeexcluded %>%
  filter(!is.na(pidem_feature)) %>%
  summarise(
    n_compared       = n(),
    n_match_lr_pidem = sum(match_lr_pidem),
    n_match_dt_pidem = sum(match_dt_pidem),
    n_match_dt_lr    = sum(match_dt_lr),
    n_match_all      = sum(match_all_three),
    pct_lr_pidem     = mean(match_lr_pidem) * 100,
    pct_dt_pidem     = mean(match_dt_pidem) * 100,
    pct_dt_lr        = mean(match_dt_lr) * 100,
    pct_all_three    = mean(match_all_three) * 100
  )

cat("\n--- Three-Way Feature Agreement (edge cases excluded) ---\n")
cat(sprintf("Patients compared              : %d\n",   agreement_summary_3way_edgeexcluded$n_compared))
cat(sprintf("LR Surrogate vs PIDEM          : %d (%.1f%%)\n", agreement_summary_3way_edgeexcluded$n_match_lr_pidem, agreement_summary_3way_edgeexcluded$pct_lr_pidem))
cat(sprintf("DT Surrogate vs PIDEM          : %d (%.1f%%)\n", agreement_summary_3way_edgeexcluded$n_match_dt_pidem, agreement_summary_3way_edgeexcluded$pct_dt_pidem))
cat(sprintf("DT Surrogate vs LR Surrogate   : %d (%.1f%%)\n", agreement_summary_3way_edgeexcluded$n_match_dt_lr,    agreement_summary_3way_edgeexcluded$pct_dt_lr))
cat(sprintf("All three agree                : %d (%.1f%%)\n", agreement_summary_3way_edgeexcluded$n_match_all,      agreement_summary_3way_edgeexcluded$pct_all_three))

# Cohen's Kappa - edge cases excluded
kappa_lr_pidem_ee <- kappa2(data.frame(
  rater1 = feature_agreement_3way_edgeexcluded$pidem_feature,
  rater2 = feature_agreement_3way_edgeexcluded$surrogate_feature
))

kappa_dt_pidem_ee <- kappa2(data.frame(
  rater1 = feature_agreement_3way_edgeexcluded$pidem_feature,
  rater2 = feature_agreement_3way_edgeexcluded$dt_feature
))

kappa_dt_lr_ee <- kappa2(data.frame(
  rater1 = feature_agreement_3way_edgeexcluded$surrogate_feature,
  rater2 = feature_agreement_3way_edgeexcluded$dt_feature
))

cat("\n--- Cohen's Kappa (edge cases excluded) ---\n")
cat(sprintf("LR Surrogate vs PIDEM        : kappa = %.3f (p = %.4f)\n", kappa_lr_pidem_ee$value, kappa_lr_pidem_ee$p.value))
cat(sprintf("DT Surrogate vs PIDEM        : kappa = %.3f (p = %.4f)\n", kappa_dt_pidem_ee$value, kappa_dt_pidem_ee$p.value))
cat(sprintf("DT Surrogate vs LR Surrogate : kappa = %.3f (p = %.4f)\n", kappa_dt_lr_ee$value,    kappa_dt_lr_ee$p.value))

# -----------------------------------------------------------------------------
# 16. Plot — three panels side by side
# -----------------------------------------------------------------------------

# Okabe-Ito colorblind-safe palette
color_pidem     <- "#0072B2"  # blue
color_surrogate <- "#E69F00"  # amber
color_dt        <- "#009E73"  # green

# Publication-ready theme
publication_theme <- theme_classic() +
  theme(
    axis.text          = element_text(size = 11, color = "black"),
    axis.title         = element_text(size = 12, color = "black"),
    plot.title         = element_text(size = 12, face = "bold", hjust = 0.5),
    panel.grid.major.x = element_line(color = "grey90"),
    axis.line          = element_line(color = "black")
  )

p_pidem <- ggplot(
  pidem_top5,
  aes(x = reorder(variable, normalized_importance), y = normalized_importance)
) +
  geom_col(fill = color_pidem) +
  coord_flip() +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.2)) +
  labs(
    x     = "Patient Characteristic",
    y     = "Normalized Frequency",
    title = "ML-Assisted Decision Model\nDecomposition"
  ) +
  publication_theme

p_surrogate <- ggplot(
  surrogate_top5,
  aes(x = reorder(variable, normalized_importance), y = normalized_importance)
) +
  geom_col(fill = color_surrogate) +
  coord_flip() +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.2)) +
  labs(
    x     = "Patient Characteristic",
    y     = "Normalized Frequency",
    title = "LR Surrogate"
  ) +
  publication_theme

p_dt <- ggplot(
  dt_top5,
  aes(x = reorder(variable, normalized_importance), y = normalized_importance)
) +
  geom_col(fill = color_dt) +
  coord_flip() +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.2)) +
  labs(
    x     = "Patient Characteristic",
    y     = "Normalized Frequency",
    title = "DT Surrogate"
  ) +
  publication_theme

p_pidem + p_surrogate + p_dt

ggsave(
  filename = "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/R01 TB/Papers/Inter Exp PMDT/figures/feature_importance_top5.png",
  plot     = p_pidem + p_surrogate + p_dt,
  width    = 10,
  height   = 4,
  units    = "in",
  device   = "png"
)