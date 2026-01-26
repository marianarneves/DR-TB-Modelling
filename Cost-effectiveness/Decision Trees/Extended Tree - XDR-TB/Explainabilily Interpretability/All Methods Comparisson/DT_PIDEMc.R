# =============================================================
# 1. Load Libraries
# -------------------------------------------------------------
# These packages handle:
#  - glmnet/brms/caret for ML modeling support
#  - dplyr/tidyr for data wrangling
#  - pROC/ROCR for ROC metrics
#  - ggplot2 for visualizations
#  - readxl for loading Excel files
#  - betacal/rms for calibration and regression utilities
# =============================================================
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
library(readxl)
library(pre)        # RuleFit implementation
library(DT)         # Interactive tables
library(partykit)   # Needed for ctree_control
library(purrr)
library(mltools)      # MCC calculation
library(progressr)
library(data.tree)

# =============================================================
# 2. Set working directory
# -----------------------------
set.seed(5)

setwd('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/R01 TB/Papers/Inter Exp PMDT')
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/Analysis/Rules_to_DT.R')


# -----------------------------
# 3. Load Decision Tree rules and code
# -----------------------------
DT_PIDEMc_tree_data <- '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/PM Boostrap/Pre Pruning/MaxTreeDepth 5/DT_rules_output_WTP2_maxNMB_acc_DTML.txt'

DT_PIDEMc_tree_plot = plot_decision_tree(DT_PIDEMc_tree_data)

export_graph(DT_PIDEMc_tree_plot, file_name = "DT_PIDEMc_tree_plot.png", file_type = "png")

# =============================================================
# 2. Import Data
# -------------------------------------------------------------
# Here we load:
#  (1) DTML: Decision Tree ML results (PIDEMc-based)
#  (2) PMDT: Classification model results trained on PMDT data
#
# Each dataset contains:
#   - patient ID
#   - classification threshold
#   - predicted optimal treatment
#   - NMB under the predicted treatment (relative to standard)
#
# These datasets will later be:
#   • aligned by threshold
#   • compared in terms of NMB
#   • compared in terms of treatment accuracy
# =============================================================
DTML <- read_excel(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/PM Boostrap/Pre Pruning/MaxTreeDepth 5/DTML_wtp2_bootstrapping_PIDEMc.xlsx'
)

Classification_PMDT <- read_xlsx(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx'
)

# =============================================================
# 3. Helper Function: Mean NMB + 95% Confidence Interval
# -------------------------------------------------------------
# This function:
#   • groups results by classification threshold
#   • computes:
#        mean NMB
#        upper/lower 95% CI using t-distribution
#
# This allows us to compare uncertainty in NMB curves across
# models and thresholds.
# =============================================================
compute_avg_nmb <- function(df) {
  df %>%
    group_by(Threshold) %>%
    summarise(
      NMB = mean(NMB_SdTreat_DM),
      uciNMB = NMB + qt(0.975, df = n() - 1) * sd(NMB_SdTreat_DM) / sqrt(n()),
      lciNMB = NMB - qt(0.975, df = n() - 1) * sd(NMB_SdTreat_DM) / sqrt(n())
    )
}

#------------------------------------------------------------
# Manual MCC function
#------------------------------------------------------------
mcc_manual <- function(y_true, y_pred) {
  TP <- sum(y_true == 1 & y_pred == 1)
  TN <- sum(y_true == 0 & y_pred == 0)
  FP <- sum(y_true == 0 & y_pred == 1)
  FN <- sum(y_true == 1 & y_pred == 0)
  
  denom <- sqrt((TP + FP) * (TP + FN) * (TN + FP) * (TN + FN))
  if (denom == 0) return(NA_real_)
  (TP * TN - FP * FN) / denom
}

# =============================================================
# 4. Compute Average NMB for Both Methods
# -------------------------------------------------------------
# We now apply the CI function to:
#   • DTML outputs
#   • PMDT classification outputs
#
# Result: two smooth NMB curves, each with confidence bands.
# =============================================================
DTML_nmb_avg <- compute_avg_nmb(DTML)
PMDT_nmb_avg <- compute_avg_nmb(Classification_PMDT)

# =============================================================
# 5. Merge and Compare NMB (PIDEMc vs DTML)
# -------------------------------------------------------------
# This block:
#   • aligns thresholds across methods
#   • renames columns to avoid collisions
#   • computes:
#        (PIDEMc NMB) − (DTML NMB)
#        a special-case ratio (if zeros appear)
#
# The resulting table will power the “PIDEMc − DT” plot.
# =============================================================
PMDT_DTML_nmb <- DTML_nmb_avg %>%
  rename_with(~ paste0(.x, "_DTML"), .cols = -Threshold) %>%
  mutate(Threshold = round(Threshold, 6)) %>%
  left_join(
    PMDT_nmb_avg %>%
      rename_with(~ paste0(.x, "_PMDT"), .cols = -Threshold) %>%
      mutate(Threshold = round(Threshold, 6)),
    by = "Threshold"
  ) %>%
  mutate(
    NMB_PMDT_DTML = NMB_PMDT - NMB_DTML,
    percNMB_PMDT_DTML = case_when(
      NMB_PMDT == 0 & NMB_DTML == 0 ~ 1,
      NMB_PMDT > 0 & NMB_DTML == 0 ~ -1,
      NMB_PMDT == 0 & NMB_DTML > 0 ~ 10,
      TRUE ~ NMB_DTML / NMB_PMDT
    )
  )

# =============================================================
# 6. Merge NMB Curves for Combined Plotting
# -------------------------------------------------------------
# Creates a long-format dataset:
#    Threshold | Method | NMB | CI
#
# This allows dtML and PIDEMc curves to be plotted together.
# =============================================================
NMB_by_method <- bind_rows(
  DTML_nmb_avg %>% 
    bind_rows(
      data.frame(
        Threshold =1,
        NMB = 0,
        uciNMB = 0,
        lciNMB =0
      )
    ) %>%
    mutate(Method = "DT surrogate"),
  PMDT_nmb_avg %>% 
    bind_rows(
      data.frame(
        Threshold =1,
        NMB = 0,
        uciNMB = 0,
        lciNMB =0
      )
    ) %>%
    mutate(Method = "PIDEMc")
)

# =============================================================
# 7. Compute Accuracy of Treatment Assignment
# -------------------------------------------------------------
# This block evaluates:
#   “How often does PMDT agree with the DTML optimal treatment?”
#
# Steps:
#   1. Align patient identifiers
#   2. Align thresholds
#   3. Compare optimal treatment categories
#   4. Compute:
#        • accuracy at each threshold
#        • average NMB at each threshold
#
# Result: a threshold → accuracy curve.
# =============================================================
PMDT_DTML_acc <- DTML %>%
  mutate(Threshold = round(Threshold, 10)) %>%
  rename_with(~ paste0(., "_DTML"), -c(Person, Threshold)) %>%
  left_join(
    Classification_PMDT %>%
      mutate(Threshold = round(Threshold, 10), Person1 = Person + 1) %>%
      distinct(Person, Threshold, .keep_all = TRUE) %>%
      rename_with(~ paste0(., "_PMDT"), -c(Person, Person1, Threshold)),
    by = c("Threshold", "Person" = "Person1")
  ) %>%
  mutate(
    # TRUE label from PMDT
    y_true = case_when(
      Opt_Treat_PMDT == "FLQ" ~ 1,
      Opt_Treat_PMDT == "DLM" ~ 0
    ),
    # predicted from DTML rule
    y_pred = case_when(
      DT_Opt_Treat_DTML == "BPaLM" ~ 1,
      DT_Opt_Treat_DTML == "BPaLC" ~ 0
    ),
    # Your existing accuracy variable
    NMB_PMDT_correct = as.integer(y_true == y_pred)
  ) %>%
  group_by(Threshold) %>%
  summarise(
    accuracy = mean(NMB_PMDT_correct),
    MCC = mcc_manual(y_true, y_pred),
    NMB = mean(NMB_SdTreat_DM_DTML),
    TP = sum(y_true == 1 & y_pred == 1),
    TN = sum(y_true == 0 & y_pred == 0),
    FP = sum(y_true == 0 & y_pred == 1),
    FN = sum(y_true == 1 & y_pred == 0)
  ) %>%
  bind_rows(
    data.frame(
      Threshold = 1,
      accuracy = 1,
      MCC = 1,
      NMB = 0
    )
  )

# =============================================================
# 8. Identify Highest NMB Threshold with Accuracy > 95%
# -------------------------------------------------------------
# Filters thresholds where:
#   accuracy > 0.95
#
# Then selects the threshold with the highest NMB.
# =============================================================
PMDT_DTML_acc %>%
  filter(accuracy > 0.95) %>%
  slice_max(NMB, n = 1)


#### Identify only the thresholds when there is at least 20 patients per class

threshold_range_FLQ_DLM_20obs  = Classification_PMDT %>%
  count(Threshold, Opt_Treat) %>%
  filter(Opt_Treat %in% c("FLQ", "DLM")) %>%
  tidyr::pivot_wider(
    names_from = Opt_Treat,
    values_from = n,
    values_fill = 0
  ) %>%
  filter(FLQ >= 20, DLM >= 20) %>%
  summarise(
    min_threshold = min(Threshold),
    max_threshold = max(Threshold)
  )

# =============================================================
# 9. Plot Accuracy Curve Across Thresholds
# -------------------------------------------------------------
# Shows how well PMDT matches DTML optimal treatment
# as the classification threshold varies.
# =============================================================
PIDEMc_Acc_by_classthreshold = ggplot(PMDT_DTML_acc, aes(x = Threshold, y = accuracy)) +
  geom_line(color = "red") +
  labs(
    title = "Accuracy of DT by classification threshold",
    x = "Classification threshold",
    y = "Accuracy"
  ) +
  
  # Axis breaks
  scale_x_continuous(breaks = seq(0, 1, by = 0.1), 
                     limits = c(threshold_range_FLQ_DLM_20obs$min_threshold, 
                                threshold_range_FLQ_DLM_20obs$max_threshold),
                     expand = c(0, 0)
                     ) +
  scale_y_continuous(breaks = seq(0, 1, by = 0.1), 
                     limits = c(0, 1),
                     expand = c(0, 0) 
                     ) +
  
  # Clean theme with normal grid
  theme_minimal(base_size = 16) +
  theme(
    axis.title = element_text(face = "bold"),
    legend.position = "none",
    plot.margin = margin(12, 14, 12, 14)
  )

ggsave('DT_PIDEMc_accuracy_by_classthreshold.png', DT_PIDEMc_Acc_by_classthreshold, width = 12, height = 6, dpi = 300)


# Accuracy plot
DT_accuracy_plot_PIDEMc_maxNMB <- ggplot(PMDT_DTML_acc, aes(x = Threshold, y = accuracy)) +
  geom_line(color = 'darkred') +
  labs(title = 'Accuracy across PIDEMc\nclassification thresholds', x = 'Classification threshold', y = 'Accuracy') +
  # X axis: ticks every 0.1, force start=0 end=1
  scale_x_continuous(
    breaks = seq(0, 1, by = 0.1),
    limits = c(threshold_range_FLQ_DLM_20obs$min_threshold, 
               threshold_range_FLQ_DLM_20obs$max_threshold),
    expand = c(0, 0)     
  ) +
  scale_y_continuous(
    breaks = seq(0, 1, by = 0.1),
    limits = c(0, 1),
    expand = c(0, 0)  
  ) +
  
  theme_minimal(base_size = 16) +
  theme(
    legend.position = "top",
    legend.text = element_text(size = 14),
    axis.title = element_text(face = "bold"),
    plot.margin = margin(12, 14, 12, 14)
  )

# MCC plot
DT_mcc_plot_PIDEMc_maxNMB <- ggplot(PMDT_DTML_acc, aes(x = Threshold, y = MCC)) +
  geom_line(color = 'darkblue') +
  labs(title = 'MCC across PIDEMc\nclassification thresholds', x = 'Classification threshold', y = 'MCC') +
  scale_x_continuous(
    breaks = seq(-1, 1, by = 0.1),
    limits = c(threshold_range_FLQ_DLM_20obs$min_threshold, 
               threshold_range_FLQ_DLM_20obs$max_threshold),
    expand = c(0, 0)     
  )+
  scale_y_continuous(
    breaks = seq(0, 1, by = 0.1),
    limits = c(0, 1),
    expand = c(0, 0)  
  ) +
  
  theme_minimal(base_size = 16) +
  theme(
    legend.position = "top",
    legend.text = element_text(size = 14),
    axis.title = element_text(face = "bold"),
    plot.margin = margin(12, 14, 12, 14)
  )

DT_accuracy_mcc_PIDEMc_min20obs_plot <- grid.arrange(DT_accuracy_plot_PIDEMc_maxNMB, DT_mcc_plot_PIDEMc_maxNMB, ncol = 2)

ggsave('DT_accuracy_mcc_PIDEMc_min20obs_plot.png', DT_accuracy_mcc_PIDEMc_min20obs_plot, width = 12, height = 6, dpi = 300)


# =============================================================
# 10. Plot NMB Curves for Both Models
# -------------------------------------------------------------
# Shows:
#   • mean NMB curve for DTML
#   • mean NMB curve for PIDEMc
#   • shaded 95% CI bands
#
# Helps identify thresholds where one method dominates.
# =============================================================
 DT_PIDEMc_NMB_by_classthreshold =  
  ggplot(NMB_by_method,
         aes(x = Threshold, y = NMB, color = Method, fill = Method)) +
  
  geom_line(size = 1.1) +
  geom_ribbon(aes(ymin = lciNMB, ymax = uciNMB),
              alpha = 0.18, color = NA) +
  
  labs(
    x = "Classification threshold",
    y = "Average change in NMB \n compared to standard treatment",
    color = "",
    fill = ""
  ) +
  
  scale_color_manual(values = c("DT surrogate" = "#377eb8", "PIDEMc" = "#e41a1c")) +
  scale_fill_manual(values = c("DT surrogate" = "#377eb8", "PIDEMc" = "#e41a1c")) +
  
  # X axis: ticks every 0.1, force start=0 end=1
  scale_x_continuous(
    breaks = seq(0, 1, by = 0.1),
    limits = c(threshold_range_FLQ_DLM_20obs$min_threshold, 
               threshold_range_FLQ_DLM_20obs$max_threshold),
    expand = c(0, 0)     
  ) +
  
  scale_y_continuous(
    breaks = seq(-1000, 1000, by = 100)
  ) +
  
  theme_minimal(base_size = 16) +
  theme(
    legend.position = "top",
    legend.text = element_text(size = 14),
    axis.title = element_text(face = "bold"),
    plot.margin = margin(12, 14, 12, 14)
  )

ggsave('DT_PIDEMc_NMB_by_classthreshold.png', DT_PIDEMc_NMB_by_classthreshold, width = 12, height = 6, dpi = 300)

# =============================================================
# 11. Plot Difference in NMB (PIDEMc − DTML)
# -------------------------------------------------------------
# Positive values = PIDEMc has higher NMB
# Negative values = DTML has higher NMB
#
# Useful for threshold selection and model comparison.
# =============================================================
ggplot(PMDT_DTML_nmb, aes(x = Threshold, y = NMB_PMDT_DTML)) +
  geom_line(size = 1.2, color = "#1f78b4") +
  geom_hline(yintercept = 0, linetype = "dotted") +
  labs(x = "Classification threshold", y = "Change in NMB (PIDEMc − DT)") +
  theme_minimal(base_size = 16)


# =============================================================
# 12. RuleFit
# -------------------------------------------------------------
# Positive values = PIDEMc has higher NMB
# Negative values = DTML has higher NMB
#
# Useful for threshold selection and model comparison.
# =============================================================

############################################################
# Load the patient-level dataset containing predicted thresholds,
# optimal treatment assignment, and patient characteristics.
############################################################
Pt_characteristics_PIDEMc_opt_treat <- read.csv(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/PM Boostrap/Input/moldova_data_opt_treat_classification_allthresholds_wtp2.csv'
)

############################################################
# Identify the minimum threshold at which the Net Monetary Benefit (NMB)
# becomes positive. This indicates the earliest point where treating
# patients is cost-effective.
############################################################
PIDEMc_NMB_minthreshold <- PMDT_nmb_avg$Threshold[
  min(which(PMDT_nmb_avg$NMB > 0))
]

############################################################
# Identify the maximum threshold at which the Net Monetary Benefit (NMB)
# remains positive. This defines the upper limit of the cost-effective
# treatment region.
############################################################
PIDEMc_NMB_maxthreshold <- PMDT_nmb_avg$Threshold[
  max(which(PMDT_nmb_avg$NMB > 0))
]

############################################################
# Filter the patient-level dataset to include only those rows where
# the threshold lies within the cost-effective range (NMB > 0).
# Then convert the optimal treatment decision into a numerical
# indicator: 0 for FLQ and 1 for alternative treatment.
############################################################
Pt_characteristics_PIDEMc_opt_treat_positiveNMB <- Pt_characteristics_PIDEMc_opt_treat %>%
  filter(
    Threshold >= PIDEMc_NMB_minthreshold &
      Threshold <= PIDEMc_NMB_maxthreshold
  ) %>%
  mutate(
    Opt_Treat_n = ifelse(Opt_Treat == 'FLQ', 0, 1)
  )

############################################################
# Prepare the dataset for modelling by removing non-predictor variables:
# - Threshold values
# - Personal identifiers
# - Variables not used as predictors
# Convert Opt_Treat_n to a factor for classification models.
############################################################
Pt_characteristics_PIDEMc_opt_treat_positiveNMB_subset <- Pt_characteristics_PIDEMc_opt_treat_positiveNMB %>%
  select(
    -c(Threshold, Person, Pt_id, FLQ_R, n, Residence, Opt_Treat)
  )

Pt_characteristics_PIDEMc_opt_treat_positiveNMB_subset$Opt_Treat_n <- 
  factor(Pt_characteristics_PIDEMc_opt_treat_positiveNMB_subset$Opt_Treat_n)

#------------------------------------------------------------
# RuleFit control
#------------------------------------------------------------
ctrl <- ctree_control(maxdepth = 3, minsplit = 1, minbucket = 1)

#------------------------------------------------------------
# Unique thresholds
#------------------------------------------------------------
thresholds <- unique(Pt_characteristics_PIDEMc_opt_treat_positiveNMB$Threshold)

#------------------------------------------------------------
# Function to compute metrics for one threshold 
#------------------------------------------------------------
compute_metrics_safe <- function(threshold, progress = NULL) {
  if(!is.null(progress)) progress()  # advance progress bar
  
  df <- Pt_characteristics_PIDEMc_opt_treat_positiveNMB %>%
    filter(Threshold == threshold) %>%
    select(-c(Threshold, Person, Pt_id, FLQ_R, n, Residence, Opt_Treat)) %>%
    mutate(Opt_Treat_n = factor(Opt_Treat_n, levels = c(0, 1)))
  
  y <- as.numeric(as.character(df$Opt_Treat_n))
  
  # Ensure both classes exist AND have ≥2 samples
  counts <- table(y)
  if(length(counts) < 2 || any(counts < 5)) {
    return(tibble(
      Threshold = threshold,
      AUC       = NA_real_,
      Accuracy  = NA_real_,
      MCC       = NA_real_
    ))
  }
  
  # Try fitting; if it fails, return NA
  fit <- tryCatch({
    pre(Opt_Treat_n ~ ., data = df, family = "binomial", tree.control = ctrl)
  }, error = function(e) return(NULL))
  
  if(is.null(fit)) {
    return(tibble(
      Threshold = threshold,
      AUC       = NA_real_,
      Accuracy  = NA_real_,
      MCC       = NA_real_
    ))
  }
  
  pred_prob  <- predict(fit, type = "response")
  pred_class <- ifelse(pred_prob > 0.5, 1, 0)
  
  tibble(
    Threshold = threshold,
    AUC       = as.numeric(pROC::roc(y, pred_prob)$auc),
    Accuracy  = mean(pred_class == y),
    MCC       = mcc_manual(y, pred_class)
  )
}

#------------------------------------------------------------
# Run all thresholds with progress bar
#------------------------------------------------------------
handlers("txtprogressbar")

metrics_by_threshold <- with_progress({
  p <- progressor(along = thresholds)
  map_dfr(thresholds, ~ compute_metrics_safe(.x, progress = p))
}) %>% 
  tibble(
    data.frame(
      Threshold =1,
      accuracy = 1,
      NMB = 0)
  )




#---------------------------------------------------------
# Base clean theme
#---------------------------------------------------------
theme_clean <- theme_minimal(base_size = 14) +
  theme(
    plot.title       = element_text(size = 18, face = "bold"),
    axis.title       = element_text(size = 14),
    axis.text        = element_text(size = 12),
    panel.grid.minor = element_blank(),
    panel.grid.major = element_line(color = "grey85", linewidth = 0.3),
    plot.margin      = margin(10, 15, 10, 15)
  )

#=========================================================
# ACCURACY PLOT (0–1 y-axis, x step = 0.01)
#=========================================================
p_acc <- ggplot(metrics_by_threshold, aes(x = Threshold, y = Accuracy)) +
  geom_line(color = "darkred", linewidth = 1.2) +
  labs(
    title = "Accuracy by Threshold",
    x = "Threshold",
    y = "Accuracy"
  ) +
  scale_y_continuous(limits = c(0, 1)) +
  scale_x_continuous(breaks = seq(0, 1, by = 0.1), limits = c(0, 1)) +
  theme_clean

#=========================================================
# MCC PLOT (–1 to 1 y-axis, x step = 0.01)
#=========================================================
p_mcc <- ggplot(metrics_by_threshold, aes(x = Threshold, y = MCC)) +
  geom_line(color = "navy", linewidth = 1.2) +
  labs(
    title = "MCC by Threshold",
    x = "Threshold",
    y = "MCC"
  ) +
  scale_y_continuous(limits = c(-1, 1)) +
  scale_x_continuous(breaks = seq(0, 1, by = 0.1), limits = c(0, 1)) +
  theme_clean

##- evaluate only threshold with PIDEMc for max NMB
############################################################
# Identify the threshold at which the Net Monetary Benefit (NMB)
# is max. 
############################################################
PIDEMc_NMB_maxNMB_threshold <- PMDT_nmb_avg$Threshold[
  max(which(PMDT_nmb_avg$NMB == max(PMDT_nmb_avg$NMB)))
]

############################################################
# Filter the patient-level dataset to include only those rows where
# the threshold lies within the cost-effective range (NMB > 0).
# Then convert the optimal treatment decision into a numerical
# indicator: 0 for FLQ and 1 for alternative treatment.
############################################################
Pt_characteristics_PIDEMc_opt_treat_maxNMB <- Pt_characteristics_PIDEMc_opt_treat %>%
  filter(
    Threshold == PIDEMc_NMB_maxNMB_threshold
  ) %>%
  mutate(
    Opt_Treat_n = ifelse(Opt_Treat == 'FLQ', 0, 1)
  )

############################################################
# Prepare the dataset for modelling by removing non-predictor variables:
# - Threshold values
# - Personal identifiers
# - Variables not used as predictors
# Convert Opt_Treat_n to a factor for classification models.
############################################################
Pt_characteristics_PIDEMc_opt_treat_maxNMB_subset <- Pt_characteristics_PIDEMc_opt_treat_maxNMB %>%
  select(
    -c(Threshold, Person, Pt_id, FLQ_R, n, Residence, Opt_Treat)
  )

Pt_characteristics_PIDEMc_opt_treat_maxNMB_subset$Opt_Treat_n <- 
  factor(Pt_characteristics_PIDEMc_opt_treat_maxNMB_subset$Opt_Treat_n)

# -----------------------------
# 6. Fit RuleFit model
# -----------------------------
ctrl <- ctree_control(maxdepth = 3, minsplit = 1, minbucket = 1)

fit_rulefit_PIDEMc_maxNMB <- pre(
  Opt_Treat_n ~ .,
  data = Pt_characteristics_PIDEMc_opt_treat_maxNMB_subset,
  family = "binomial",
  tree.control = ctrl
)


# -----------------------------
# 7. Variable Importance (RuleFit)
# -----------------------------
imp_raw_PIDEMc_maxNMB <- importance(fit_rulefit_PIDEMc_maxNMB)

varimp_PIDEMc_maxNMB <- data.frame(
  var = imp_raw_PIDEMc_maxNMB$varimps$varname,
  rel.importance = round(imp_raw_PIDEMc_maxNMB$varimps$imp, 4),
  stringsAsFactors = FALSE
) %>% arrange(desc(rel.importance))%>%
  mutate(var_name = case_when(
    var == "Sex_2" ~ "Female",
    var == "TB_type_2"  ~ "Relapse",
    var == "TB_type_3"  ~ "TB Return from Default",
    var == "TB_type_4"  ~ "Treatment Failure",
    var == "TB_type_5"  ~ "Chronic TB",
    var == "TB_type_6"  ~ "Initiated Treatment Abroad",
    var == "TB_type_21" ~ "SSM Negative Relapse",
    var == "TB_type_22" ~ "Extrapulmonary Relapse",
    var == "Occupation_1" ~ "Employed",
    var == "Occupation_2" ~ "Disabled",
    var == "Occupation_3" ~ "Retired",
    var == "Occupation_4" ~ "Student",
    var == "Occupation_5" ~ "Unemployed",
    var == "Education_1" ~ "Primary Education",
    var == "Education_2" ~ "Secondary Education",
    var == "Education_3" ~ "Specialized Secondary Education",
    var == "Education_4" ~ "Higher Education",
    var == "Education_5" ~ "No Education",
    var == "Living_condition_0" ~ "Unsatisfactory Living Conditions",
    var == "Living_condition_1" ~ "Satisfactory Living Conditions",
    var == "Living_condition_missing" ~ "Living condition missing",
    var == "Outside_moldova_1" ~ "Resided outside of Moldova",
    var == "Urban_0" ~ "Rural Area",
    var == "Urban_1" ~ "Urban Area",
    var == "Homeless_1" ~ "Homeless",
    var == "Homeless_missing" ~ "Homeless missing",
    var == "Money_assistance_missing" ~ "Money assistance missing",
    var == "Money_assistance_1" ~ "Receives Monetary Assistance",
    var == "Incarceration_1" ~ "Previously Incarcerated",
    var == "Microscopy_1" ~ "Positive Microscopy",
    var == "prevalence_0" ~ "Reside in District with Prevalence < 10%",
    var == "prevalence_1" ~ "Reside in District with Prevalence < 20% and > 10%",
    var == "prevalence_2" ~ "Reside in District with Prevalence >20%",
    TRUE ~ NA_character_
  )
  )

# Plot top 10 variables
top10_PIDEMc_maxNMB_plot <-  ggplot(
  top10,
  aes(x = rel.importance,
      y = reorder(var_name, rel.importance),
      fill = rel.importance)
) +
  # bars
  geom_col(width = 0.8) +
  
  # value labels at end of bars
  # geom_text(aes(label = rel.importance),
  #          hjust = -0.1, size = 4) +
  
  # gradient color
  scale_fill_gradient(
    low = "#bdd7e7",
    high = "#6baed6",
    name = "Variable\nImportance"
  ) +
  
  # labels
  labs(
    title = "Top 10 Variables",
    x = "Relative Importance",
    y = "Variable"
  ) +
  
  # clean theme
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(
      face = "bold",
      size = 20,
      hjust = 0.5
    ),
    legend.position = "right"
  )  +
  scale_x_continuous(breaks = seq(0, 1.2, by = 0.1), limits = c(0, 1.2)) 


ggsave('rulesfit_top10_variables_PIDEMc_maxNMB_plot.png', top10_PIDEMc_maxNMB_plot, width = 8, height = 6, dpi = 300)

# -----------------------------
# 8. Rule Importance
# -----------------------------
ruleimp_PIDEMc_maxNMB <- data.frame(
  rule = imp_raw_PIDEMc_maxNMB$baseimps$description,
  rel.importance = round(imp_raw_PIDEMc_maxNMB$baseimps$imp, 4),
  stringsAsFactors = FALSE
) %>% arrange(desc(rel.importance))

rule_PIDEMc_maxNMB_plot <- ggplot(head(ruleimp_PIDEMc_maxNMB, 10), aes(x = reorder(rule, rel.importance), y = rel.importance)) +
  geom_col(fill = 'darkorange') + coord_flip() +
  labs(title = 'Top 10 Rules (RuleFit)', x = 'Rule', y = 'Importance') +
  theme_minimal()

# -----------------------------
# 9. ROC and AUC
# -----------------------------
pred_prob_PIDEMc_maxNMB <- predict(fit_rulefit_PIDEMc_maxNMB, type = 'response')
Pt_characteristics_PIDEMc_opt_treat_maxNMB_truth <- as.numeric(as.character(Pt_characteristics_PIDEMc_opt_treat_maxNMB$Opt_Treat_n))

roc_obj_PIDEMc_maxNMB <- roc(Pt_characteristics_PIDEMc_opt_treat_maxNMB_truth, pred_prob_PIDEMc_maxNMB)
auc_value_PIDEMc_maxNMB <- auc(roc_obj_PIDEMc_maxNMB)
auc_value_PIDEMc_maxNMB

# -----------------------------
# 10. Threshold sweep: Accuracy & MCC
# -----------------------------
thresholds <- seq(0, 1, by = 0.01)

accuracy_PIDEMc_maxNMB <- data.frame(
  threshold = thresholds,
  accuracy = sapply(thresholds, function(t) mean(ifelse(pred_prob_PIDEMc_maxNMB >= t, 1, 0) == Pt_characteristics_PIDEMc_opt_treat_maxNMB_truth)),
  mcc = sapply(thresholds, function(t) mcc(ifelse(pred_prob_PIDEMc_maxNMB >= t, 1, 0), Pt_characteristics_PIDEMc_opt_treat_maxNMB_truth))
)

# Accuracy plot
accuracy_plot_PIDEMc_maxNMB <- ggplot(accuracy_PIDEMc_maxNMB, aes(x = threshold, y = accuracy)) +
  geom_line(color = 'darkred') +
  labs(title = 'Accuracy across\nclassification thresholds', x = 'Classification threshold', y = 'Accuracy') +
  # X axis: ticks every 0.1, force start=0 end=1
  scale_x_continuous(
    breaks = seq(0, 1, by = 0.1),
    limits = c(0, 1),
    expand = c(0, 0)     
  ) +
  scale_y_continuous(
    breaks = seq(0, 1, by = 0.1),
    limits = c(0, 1),
    expand = c(0, 0)  
  ) +
    
    theme_minimal(base_size = 16) +
    theme(
      legend.position = "top",
      legend.text = element_text(size = 14),
      axis.title = element_text(face = "bold"),
      plot.margin = margin(12, 14, 12, 14)
    )

# MCC plot
mcc_plot_PIDEMc_maxNMB <- ggplot(accuracy_PIDEMc_maxNMB, aes(x = threshold, y = mcc)) +
  geom_line(color = 'darkblue') +
  labs(title = 'MCC across\nclassification thresholds', x = 'Classification threshold', y = 'MCC') +
  scale_x_continuous(
    breaks = seq(-1, 1, by = 0.1),
    limits = c(0, 1),
    expand = c(0, 0)     
  )+
scale_y_continuous(
  breaks = seq(0, 1, by = 0.1),
  limits = c(0, 1),
  expand = c(0, 0)  
) +
  
  theme_minimal(base_size = 16) +
  theme(
    legend.position = "top",
    legend.text = element_text(size = 14),
    axis.title = element_text(face = "bold"),
    plot.margin = margin(12, 14, 12, 14)
  )

accuracy_mcc_PIDEMc_maxNMB <- grid.arrange(accuracy_plot_PIDEMc_maxNMB, mcc_plot_PIDEMc_maxNMB, ncol = 2)

ggsave('accuracy_mcc_PIDEMc_maxNMB_plot.png', accuracy_mcc_PIDEMc_maxNMB, width = 12, height = 6, dpi = 300)
