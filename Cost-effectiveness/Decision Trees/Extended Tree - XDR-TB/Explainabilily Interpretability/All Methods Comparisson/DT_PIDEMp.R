# =============================================================
# Full Pipeline: Decision Tree (DT) Evaluation + RuleFit Model
# =============================================================

# =============================================================
# 1. Load Required Libraries
# =============================================================
library(openxlsx)     # Reading Excel outputs
library(mltools)      # MCC calculation
library(pre)          # RuleFit implementation
library(dplyr)        # Data wrangling
library(ggplot2)      # Plots
library(DT)           # Interactive tables
library(partykit)     # Conditional inference trees (used in RuleFit)
library(pROC)         # ROC and AUC calculations
library(readxl)       # Reading Excel/CSV
library(tidyr)        # Data cleaning and manipulation
library(gridExtra)    # Arranging multiple plots
library(patchwork)    # For combining ggplot objects
library(forcats)     # For working with factor levels
library(DT)         # Interactive tables
library(stringr)   # String manipulation functions (replace, detect, capitalize, etc.)

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


# =============================================================
# 2. Set Working Directory and Seed
# =============================================================
set.seed(5)  # Ensure reproducibility

setwd('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/R01 TB/Papers/Inter Exp PMDT')

# Load custom DT plotting functions
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/Analysis/Rules_to_DT.R')

# =============================================================
# 3. Decision Tree: Load and Visualize
# =============================================================
DT_PIDEMp_tree_data <- '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/Beta Calibration/PM input Only/Pre pruning/MaxTreeDepth 5/DT_rules_output_wtp2.txt'

# Generate plot from rules
DT_PIDEMp_tree_plot <- plot_decision_tree(DT_PIDEMp_tree_data)

# Export tree visualization
export_graph(DT_PIDEMp_tree_plot, file_name = "DT_PIDEMp_tree_plot.png", file_type = "png")

# =============================================================
# 4. Decision Tree: Accuracy & MCC
# =============================================================
DT_output_path <- '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/Beta Calibration/PM input Only/Pre pruning/MaxTreeDepth 5/DTML_wtp2_bootstrapping_PIDEMp.xlsx'

# Read bootstrapped DT predictions
PIDEMp_DT_output <- read.xlsx(DT_output_path)

# Calculate accuracy
DT_accuracy <- mean(PIDEMp_DT_output$DT_Opt_Treat == PIDEMp_DT_output$PIDEM_opt_treat)
print(DT_accuracy)

# Convert factors to numeric for MCC calculation
pred <- as.numeric(as.factor(PIDEMp_DT_output$DT_Opt_Treat))
truth <- as.numeric(as.factor(PIDEMp_DT_output$PIDEM_opt_treat))

# Calculate Matthews Correlation Coefficient
DT_mcc_value <- mcc(preds = pred, actuals = truth)
print(DT_mcc_value)

# =============================================================
# 5. RuleFit: Load Data and Prepare
# =============================================================
PIDEMp_input_path <- '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/Beta Calibration/PM input Only/Input/LE by Age and Sex/moldova_data_opt_treat_prediction_allthresholds_wtp2.csv'

PIDEMp_PMDT <- read.csv(PIDEMp_input_path)

# Convert target variable to binary
PIDEMp_PMDT_maxNMB <- PIDEMp_PMDT %>%
  mutate(Opt_Treat_n = ifelse(Opt_Treat == 'FLQ', 0, 1))

# Select predictors only and convert target to factor
df <- PIDEMp_PMDT_maxNMB %>%
  select(-c(Person, Pt_id, FLQ_R, n, Residence, Opt_Treat)) %>%
  mutate(Opt_Treat_n = factor(Opt_Treat_n))

# =============================================================
# 6. Fit RuleFit Model
# =============================================================
# Define tree control parameters (shallow trees for RuleFit)
ctrl <- ctree_control(maxdepth = 3, minsplit = 1, minbucket = 1)

# Fit RuleFit
fit_rulefit <- pre(
  Opt_Treat_n ~ .,
  data = df,
  family = "binomial",
  tree.control = ctrl
)

# =============================================================
# 7. RuleFit: Variable Importance
# =============================================================
imp_raw <- importance(fit_rulefit)

# Map variable names to human-readable labels
varimp_df <- data.frame(
  var = imp_raw$varimps$varname,
  rel.importance = round(imp_raw$varimps$imp, 4),
  stringsAsFactors = FALSE
) %>%
  arrange(desc(rel.importance)) %>%
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
    var == "Living_condition_missing" ~ "Living Condition Missing",
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
    var == "prevalence_1" ~ "Reside in District with Prevalence 10-20%",
    var == "prevalence_2" ~ "Reside in District with Prevalence >20%",
    TRUE ~ NA_character_
  ))

# Plot top 10 variables
top10_plot <- ggplot(head(varimp_df, 10), aes(x = reorder(var, rel.importance), y = rel.importance)) +
  geom_col(fill = 'steelblue') +
  coord_flip() +
  labs(title = 'Top 10 Variables (RuleFit)', x = 'Variable', y = 'Importance') +
  theme_minimal()

ggsave('rulesfit_top10_variables_plot.png', top10_plot, width = 8, height = 6, dpi = 300)

# =============================================================
# 8. RuleFit: Rule Importance
# =============================================================
ruleimp_df <- data.frame(
  rule = imp_raw$baseimps$description,
  rel.importance = round(imp_raw$baseimps$imp, 4),
  stringsAsFactors = FALSE
) %>%
  arrange(desc(rel.importance))

rule_plot <- ggplot(head(ruleimp_df, 10), aes(x = reorder(rule, rel.importance), y = rel.importance)) +
  geom_col(fill = 'darkorange') +
  coord_flip() +
  labs(title = 'Top 10 Rules (RuleFit)', x = 'Rule', y = 'Importance') +
  theme_minimal()

# =============================================================
# 9. RuleFit: ROC and AUC
# =============================================================
pred_prob <- predict(fit_rulefit, type = 'response')
truth <- as.numeric(as.character(df$Opt_Treat_n))

roc_obj <- roc(truth, pred_prob)
auc_value <- auc(roc_obj)
print(auc_value)

# =============================================================
# 10. Threshold Sweep: Accuracy & MCC
# =============================================================
thresholds <- seq(0, 1, by = 0.01)

accuracy_df <- data.frame(
  threshold = thresholds,
  accuracy = sapply(thresholds, function(t) mean(ifelse(pred_prob >= t, 1, 0) == truth)),
  mcc = sapply(thresholds, function(t) mcc(ifelse(pred_prob >= t, 1, 0), truth))
)

# Custom theme for plots
custom_theme <- theme_minimal(base_size = 13) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0, size = 16),      # title size
    axis.title.x = element_text(size = 14, face = "bold"),               # x-axis label size
    axis.title.y = element_text(size = 14, face = "bold"),               # y-axis label size
    axis.text.x = element_text(size = 12),                               # x-axis tick labels
    axis.text.y = element_text(size = 12),                               # y-axis tick labels
    legend.title = element_text(size = 14, face = "bold"),               # legend title
    legend.text = element_text(size = 12),                               # legend labels
    panel.grid.major.y = element_line(color = "grey80"),
    panel.grid.major.x = element_line(color = "grey80"),
    plot.margin = margin(10, 20, 10, 10),
    legend.position = "bottom"
  )

# Accuracy plot
accuracy_plot <- ggplot() +
  geom_line(data = accuracy_df, aes(x = threshold, y = accuracy, color = "RuleFit"), linewidth = 1.5) +
  geom_hline(aes(yintercept = DT_accuracy, color = "Decision Tree"), linewidth = 1.5) +
  scale_color_manual(values = c("RuleFit" = "#6baed6", "Decision Tree" = "#E67E22"), name = "Model") +
  scale_x_continuous(breaks = seq(0, 1, by = 0.1),
                     expand = c(0.002,0.002)) +
  scale_y_continuous(breaks = seq(0, 1, by = 0.1), limits = c(0,1)) +
  labs(title = "Accuracy Across Thresholds", x = "Threshold", y = "Accuracy") +
  custom_theme

# MCC plot
mcc_plot <- ggplot() +
  geom_line(data = accuracy_df, aes(x = threshold, y = mcc, color = "RuleFit"), linewidth = 1.5) +
  geom_hline(aes(yintercept = DT_mcc_value, color = "Decision Tree"), linewidth = 1.5) +
  scale_color_manual(values = c("RuleFit" = "#6baed6", "Decision Tree" = "#E67E22"), name = "Model") +
  scale_x_continuous(breaks = seq(0, 1, by = 0.1),
                     expand = c(0.002,0.002)) +
  scale_y_continuous(breaks = seq(0, 1, by = 0.1)) +
  labs(title = "MCC Across Thresholds", x = "Threshold", y = "MCC") +
  custom_theme

# Combine accuracy and MCC plots with shared legend
accuracy_mcc_plots <- accuracy_plot + mcc_plot +
  plot_layout(ncol = 2, guides = "collect") &
  theme(legend.position = "bottom")

ggsave('accuracy_mcc_plots.png', accuracy_mcc_plots, width = 12, height = 6, dpi = 300)

# =============================================================
# 11. Variable Importance Comparison: DT vs RuleFit
# =============================================================
# Load Decision Tree variable importance
DT_var_importance_path <- '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/Beta Calibration/PM input Only/Pre pruning/MaxTreeDepth 5/DT_feature_importance_wtp2.csv'

DT_var_importance <- read.csv(DT_var_importance_path)

DT_var_importance_positive <- DT_var_importance %>%
  filter(importance > 0) %>%
  mutate(
    variable = feature %>%
      gsub("^.*?:", "", .) %>%      # Remove everything before the colon
      gsub("_missing$", "", .) %>%  # Remove _missing suffix
      trimws()                       # Remove extra spaces
  )


# Decision Tree variable importance plot
DT_var_importance_plot <- ggplot(DT_var_importance_positive, aes(x = importance, y = reorder(variable, importance), fill = importance)) +
  geom_col(width = 0.7) +
  scale_x_continuous(
    breaks = seq(0, 0.3, by = 0.05),
    limits = c(0, 0.3)
  ) +
  scale_fill_gradient(low = "#FDEBD0", high = "#E67E22", guide = "none") +
  labs(title = "Decision Tree – Factor-level importance ", x = "Importance (normalized)", y = NULL) +
  theme_minimal(base_size = 13) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0, size = 14),
    axis.text.y = element_text(size = 13),
    axis.text.x = element_text(size = 12),
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank(),
    legend.position = "right",
    plot.margin = margin(10, 20, 10, 10)
  )

# Normalize top 8 RuleFit variables for comparison
rulefit_top8 <- varimp_df %>%
  arrange(desc(rel.importance)) %>%
  slice(1:8) %>%
  mutate(rel.importance = rel.importance / sum(rel.importance))

rulefit_var_importance_plot <- ggplot(rulefit_top8, aes(x = rel.importance, y = reorder(var_name, rel.importance), fill = rel.importance)) +
  geom_col(width = 0.7) +
  scale_x_continuous(
    breaks = seq(0, 0.3, by = 0.05),
    limits = c(0, 0.3)
  ) +
  scale_fill_gradient(low = "#bdd7e7", high = "#6baed6", guide = "none") +
  labs(title = "RuleFit – Factor-level importance", x = "Importance (normalized)", y = NULL) +
  theme_minimal(base_size = 13) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0, size = 14),
    axis.text.y = element_text(size = 13),
    axis.text.x = element_text(size = 12),
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank(),
    legend.position = "right",
    plot.margin = margin(10, 20, 10, 10)
  )

# Combine DT and RuleFit variable importance plots
var_imp_combined_plot <- DT_var_importance_plot + rulefit_var_importance_plot +
  plot_layout(ncol = 2)

ggsave('var_imp_combined_plot.png', var_imp_combined_plot, width = 14, height = 6, dpi = 300)

# =============================================================
# 12. Count Non-zero RuleFit Coefficients
# =============================================================
# coef_all must be defined from your RuleFit object; assuming coef_all <- coef(fit_rulefit)
# sum(coef_all$coefficient > 0)

# =============================================================
# 13. Combine all plots: Accuracy/MCC + Variable Importance
# =============================================================
final_2x2_plot <- accuracy_mcc_plots / var_imp_combined_plot

final_2x2_plot


###### NMB

# =============================================================
# 4. Compute Average NMB for Both Methods
# -------------------------------------------------------------
# We now apply the CI function to:
#   • DTML outputs
#   • PMDT classification outputs
#
# Result: two smooth NMB curves, each with confidence bands.
# =============================================================

#Original PIDEM output
Probability_PMDT <- read_xlsx(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM input Only/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx'
)

DTML_nmb_avg <- compute_avg_nmb(PIDEMp_DT_output)
PMDT_nmb_avg <- compute_avg_nmb(Probability_PMDT)


#calculating NMB for RuleFit
RuleFit_nmb <- expand_grid(
  Person = 0:539,
  Threshold = thresholds
) %>%
  mutate(
    Opt_Treat = ifelse(pred_prob[Person + 1] > Threshold, "DLM", "FLQ"),
    NMB_SdTreat_DM = ifelse(
      Opt_Treat == "DLM",
      Probability_PMDT$NMB_SdTreat[Person + 1] - Probability_PMDT$NMB_DLM[Person + 1],
      Probability_PMDT$NMB_SdTreat[Person + 1] - Probability_PMDT$NMB_FLQ[Person + 1]
    )
  )

RuleFit_nmb_avg <- compute_avg_nmb(RuleFit_nmb)

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

# Prepare DTML and PMDT data as flat lines across thresholds
thresholds_df <- data.frame(Threshold = thresholds)

DTML_nmb_line <- thresholds_df %>%
  mutate(
    NMB = DTML_nmb_avg$NMB,
    lciNMB = DTML_nmb_avg$lciNMB,
    uciNMB = DTML_nmb_avg$uciNMB,
    Method = "DT surrogate"
  )

PMDT_nmb_line <- thresholds_df %>%
  mutate(
    NMB = PMDT_nmb_avg$NMB,
    lciNMB = PMDT_nmb_avg$lciNMB,
    uciNMB = PMDT_nmb_avg$uciNMB,
    Method = "PIDEMc"
  )

# RuleFit is already by threshold, just add Method column
RuleFit_nmb_avg <- RuleFit_nmb_avg %>%
  mutate(Method = "RuleFit")

# Combine all
plot_data <- bind_rows(DTML_nmb_line, PMDT_nmb_line, RuleFit_nmb_avg)

# Plot
DT_RuleFit_PIDEMc_NMB_by_classthreshold <- ggplot(plot_data,
                                          aes(x = Threshold, y = NMB, color = Method, fill = Method)) +
  geom_line(size = 1.1) +
  geom_ribbon(aes(ymin = lciNMB, ymax = uciNMB), alpha = 0.18, color = NA) +
  labs(
    x = "Classification threshold",
    y = "Average change in NMB \n compared to standard treatment",
    color = "",
    fill = ""
  ) +
  scale_color_manual(values = c("DT surrogate" = "#E67E22", "PIDEMc" = "#e41a1c", "RuleFit" = "#6baed6")) +
  scale_fill_manual(values = c("DT surrogate" = "#E67E22", "PIDEMc" = "#e41a1c", "RuleFit" = "#6baed6")) +
  scale_x_continuous(
    breaks = seq(0, 1, by = 0.1),
    expand = c(0, 0)
  ) +
  scale_y_continuous(
    breaks = seq(-400, 700, by = 100),
    limits = c(-400, 700)
  ) +
  theme_minimal(base_size = 16) +
  theme(
    legend.position = "top",
    legend.text = element_text(size = 14),
    axis.title = element_text(face = "bold"),
    plot.margin = margin(12, 14, 12, 14)
  )

ggsave('DT_RuleFit_PIDEMc_NMB_by_classthreshold.png', DT_RuleFit_PIDEMc_NMB_by_classthreshold, width = 12, height = 6, dpi = 300)


# =============================================================
# 2. Load the DT feature importance file
# =============================================================
DT_var_importance_path <- '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/Beta Calibration/PM input Only/Pre pruning/MaxTreeDepth 5/DT_feature_importance_wtp2.csv'

DT_var_importance <- read.csv(DT_var_importance_path, stringsAsFactors = FALSE)

# Keep only positive importance values
DT_var_importance_positive <- DT_var_importance %>%
  filter(importance > 0)

# =============================================================
# 3. Extract base variable names
# -------------------------------------------------------------
# Rules:
#   • If feature contains ":", take text before colon
#   • If feature ends with "_missing", remove that suffix
#   • Otherwise, keep as is
# =============================================================
DT_var_importance_positive <- DT_var_importance_positive %>%
  mutate(
    variable = feature %>%
      gsub(":.*$", "", .) %>%      # Remove category after colon
      gsub("_missing$", "", .) %>% # Remove _missing suffix
      trimws()                      # Remove extra spaces
  )

# =============================================================
# 4. Aggregate importance by variable using MAX
# -------------------------------------------------------------
DT_factor_table <- dplyr::summarize(
  dplyr::group_by(DT_var_importance_positive, variable),
  max_importance = max(importance, na.rm = TRUE),
  .groups = "drop"
) %>%
  dplyr::arrange(desc(max_importance))

# =============================================================
# 5. Plot top N variables
# =============================================================
top_n <- 10
DT_factor_table_top <- head(DT_factor_table, top_n)
DT_factor_table_top <- DT_factor_table_top %>%
  mutate(rel_importance = max_importance / sum(max_importance))

DT_global_var_importance_plot = ggplot(DT_factor_table_top,
       aes(x = rel_importance,
           y = fct_reorder(variable, rel_importance),
           fill = rel_importance)) +
  geom_col(width = 0.7) +
  scale_fill_gradient(low = "#FDEBD0", high = "#E67E22", guide = "none") +
  labs(
    title = "Decision Tree – Variable-level importance (MAX per variable)",
    x = "Importance (normalized)",
    y = NULL
  ) +
  theme_minimal(base_size = 13) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0, size = 14),
    axis.text.y = element_text(size = 13),
    axis.text.x = element_text(size = 12),
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank()
  )

# =============================================================
# 6. Optional: View factor_table_top in interactive table
# =============================================================
DT::datatable(DT_factor_table_top, options = list(pageLength = 10))



# =============================================================
# 11. Prepare RuleFit Feature Importance Data
# -------------------------------------------------------------
# Copy original varimp_df and rename columns for consistency
# -------------------------------------------------------------
varimp_df2 <- varimp_df
names(varimp_df2)[names(varimp_df2) == "var"] <- "feature"
names(varimp_df2)[names(varimp_df2) == "rel.importance"] <- "importance"

# =============================================================
# 12. Aggregate Importance Across Factor Levels
# -------------------------------------------------------------
# Rationale:
#   • RuleFit outputs importance for each category/dummy
#   • We want overall factor-level importance
#   • MAX aggregation used to avoid inflating importance due to correlated categories
# -------------------------------------------------------------

# Extract factor names by removing numeric suffix
varimp_df2$factor <- gsub("(_[0-9]+|_missing)$", "", varimp_df2$feature)

# Split data by factor
factor_list <- split(varimp_df2, varimp_df2$factor)

# Compute max importance per factor
RuleFit_factor_table <- do.call(rbind, lapply(factor_list, function(df) {
  data.frame(
    factor = df$factor[1],                     # Factor code
    factor_importance = max(df$importance),    # MAX category importance
    stringsAsFactors = FALSE
  )
}))

# Sort factors by descending importance
RuleFit_factor_table <- RuleFit_factor_table[order(-RuleFit_factor_table$factor_importance), ]

# =============================================================
# 13. Plot Top N Factors
# -------------------------------------------------------------
top_n <- dim(DT_factor_table_top)[1]
RuleFit_factor_table_top <- RuleFit_factor_table %>%
  head(top_n) %>%
  mutate(
    rel_importance = factor_importance / sum(factor_importance),
    factor = str_to_title(str_replace_all(factor, "_", " ")),
    factor = str_replace_all(factor, "\\bTb\\b", "TB") 
  )

rulefit_global_var_importance_plot = ggplot(RuleFit_factor_table_top,
       aes(x = rel_importance,
           y = forcats::fct_reorder(factor, rel_importance),
           fill = rel_importance)) +
  geom_col(width = 0.7) +
  scale_fill_gradient(low = "#bdd7e7", high = "#6baed6", guide = "none") +
  labs(
    title = "RuleFit – Variable-level importance (MAX per variable)",
    x = "Importance (normalized)",
    y = NULL
  ) +
  theme_minimal(base_size = 13) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0, size = 14),
    axis.text.y = element_text(size = 13),
    axis.text.x = element_text(size = 12),
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank()
  )

# Combine DT and RuleFit GLOBAL variable importance plots
global_var_imp_combined_plot <- DT_global_var_importance_plot + rulefit_global_var_importance_plot +
  plot_layout(ncol = 2)

ggsave('global_var_imp_combined_plot.png', global_var_imp_combined_plot, width = 14, height = 6, dpi = 300)

# =============================================================
# 14. Compute Feature Contributions for a Single Patient
# -------------------------------------------------------------
# Source user-defined function for computing contributions
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/RuleFit/Calculate_Feature_Contribution.R')

# Extract non-zero coefficients at selected lambda
coefs <- coef(fit_rulefit$glmnet.fit, s = "lambda.min")

coef_df <- data.frame(
  Feature = rownames(coefs),
  Coefficient = round(as.numeric(coefs), 4),
  row.names = NULL
) %>%
  dplyr::filter(!is.na(Coefficient) & Coefficient != 0)

# View top 10 coefficients interactively
DT::datatable(coef_df, options = list(pageLength = 10))

# =============================================================
# 15. Extract Patient Data from RuleFit Design Matrix
# -------------------------------------------------------------
X_all <- fit_rulefit$modmat   # n x p matrix of rules + linear terms

# Select a single patient (e.g., row 150)
x_patient <- X_all[38, , drop = FALSE]

# Compute contributions using sourced function
patient_fit <- compute_contributions(x_patient, coef_df)
feature_contribution <- patient_fit$contrib_df %>%
  left_join(coef(fit_rulefit), by = c('Feature'='rule'))

# =============================================================
# 16. Plot Patient Feature Contributions
# -------------------------------------------------------------
feature_contribution_by_pt_plot = ggplot(feature_contribution,
       aes(x = reorder(Feature, Contribution),
           y = Contribution,
           fill = Contribution > 0)) +
  geom_col() +
  coord_flip() +
  labs(
    title = "Feature Contributions for Patient 150",
    x = "Feature / Rule",
    y = "Contribution (logit)"
  ) +
  scale_fill_manual(values = c("TRUE" = "steelblue", "FALSE" = "tomato"), guide = "none") +
  theme_minimal(base_size = 13) +
  theme(
    plot.title = element_text(face = "bold", size = 14),
    axis.text.y = element_text(size = 12),
    axis.text.x = element_text(size = 11)
  )

ggsave('feature_contribution_by_pt_plot.png', feature_contribution_by_pt_plot, width = 14, height = 6, dpi = 300)


# =============================================================
# 17. SMDM Figure
# -------------------------------------------------------------

# Accuracy plot
accuracy_plot_SMDM <- ggplot() +
  geom_line(data = accuracy_df, aes(x = threshold, y = accuracy, color = "RuleFit surrogate"), linewidth = 1.5) +
  geom_hline(aes(yintercept = DT_accuracy, color = "Decision Tree surrogate"), linewidth = 1.5) +
  scale_color_manual(values = c("RuleFit surrogate" = "#6baed6", "Decision Tree surrogate" = "#E67E22"),
                     name = "Surrogate model") +  # <-- rename legend here
  scale_x_continuous(breaks = seq(0, 1, by = 0.1),
                     expand = c(0.002,0.002)) +
  scale_y_continuous(breaks = seq(0, 1, by = 0.1), limits = c(0,1), expand = c(0.002,0.002)) +
  labs(x = "Classification threshold", y = "Accuracy") +
  custom_theme

# MCC plot
mcc_plot_SMDM <- ggplot() +
  geom_line(data = accuracy_df, aes(x = threshold, y = mcc, color = "RuleFit surrogate"), linewidth = 1.5) +
  geom_hline(aes(yintercept = DT_mcc_value, color = "Decision Tree surrogate"), linewidth = 1.5) +
  scale_color_manual(values = c("RuleFit surrogate" = "#6baed6", "Decision Tree surrogate" = "#E67E22"),
                     name = "Surrogate model") +  # <-- and here
  scale_x_continuous(breaks = seq(0, 1, by = 0.1),
                     expand = c(0.002,0.002)) +
  scale_y_continuous(breaks = seq(0, 1, by = 0.1), limits = c(0, 1), expand = c(0.002,0.002)) +
  labs(x = "Classification threshold", y = "MCC") +
  custom_theme


# Combine accuracy and MCC plots with shared legend
accuracy_mcc_plots_SMDM <-
  (
    accuracy_plot_SMDM + mcc_plot_SMDM +
      plot_layout(ncol = 2, guides = "collect") +
      plot_annotation(
        title = "A. Surrogate fidelity across classification thresholds",
        theme = theme(
          plot.title = element_text(
            face = "bold",
            size = 16,
            color = "black"
          )
        )
      )
  ) &
  theme(
    legend.position = "right",
    legend.title = element_text(face = "bold", size = 12, color = "black"),  # bold + size
    legend.text = element_text(size = 11)  # optional: slightly bigger legend labels
  )


ggsave('accuracy_mcc_plots_SMDM.png', accuracy_mcc_plots_SMDM, width = 14, height = 4, dpi = 300)


#--------------------

DT_global_var_importance_plot_SMDM = ggplot(DT_factor_table_top,
                                       aes(x = rel_importance,
                                           y = fct_reorder(variable, rel_importance),
                                           fill = rel_importance)) +
  geom_col(width = 0.7) +
  scale_fill_gradient(low = "#FDEBD0", high = "#E67E22", guide = "none") +
  labs(
    title = "Decision tree surrogate",
    x = "Variable importance",
    y = NULL
  ) +
  scale_x_continuous(
    limits = c(0, 0.4),
    breaks = seq(0, 0.4, by = 0.05),
    expand = c(0, 0)
  )+
  theme_minimal(base_size = 13) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0, size = 14),
    axis.text.y = element_text(size = 12,  face = "bold"),
    axis.text.x = element_text(size = 12),
    axis.title.x = element_text(size = 14, face = "bold"),               # x-axis label size
    axis.title.y = element_text(size = 14, face = "bold"),  
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank(),
    panel.grid.major.x = element_line(color = "grey80", linetype = "dashed")
  )

rulefit_global_var_importance_plot_SMDM = ggplot(RuleFit_factor_table_top,
                                            aes(x = rel_importance,
                                                y = forcats::fct_reorder(factor, rel_importance),
                                                fill = rel_importance)) +
  geom_col(width = 0.7) +
  scale_fill_gradient(low = "#bdd7e7", high = "#6baed6", guide = "none") +
  labs(
    title = "RuleFit surrogate",
    x = "Variable importance",
    y = NULL
  ) +
  scale_x_continuous(
    limits = c(0, 0.4),
    breaks = seq(0, 0.4, by = 0.05),
    expand = c(0, 0)
  )+
  theme_minimal(base_size = 13) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0, size = 14),
    axis.text.y = element_text(size = 12,  face = "bold"),
    axis.text.x = element_text(size = 12),
    axis.title.x = element_text(size = 14, face = "bold"),               # x-axis label size
    axis.title.y = element_text(size = 14, face = "bold"),  
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank(),
    panel.grid.major.x = element_line(color = "grey80", linetype = "dashed")
  )

# Combine DT and RuleFit GLOBAL variable importance plots
global_var_imp_combined_plot_SMDM <- DT_global_var_importance_plot_SMDM + 
  rulefit_global_var_importance_plot_SMDM +
  plot_layout(ncol = 2) +
  plot_annotation(
    title = "B. Drivers of treatment recommendation",
    theme = theme(
      plot.title = element_text(
        face = "bold",      # bold text
        size = 16,          # larger font size
        #hjust = 0.5,        # center the title
        color = "black"     # can choose another color if you want
      )
    )
  )

ggsave('global_var_imp_combined_plot_SMDM.png', global_var_imp_combined_plot_SMDM, width = 14, height = 4, dpi = 300)


all_comparison =  (accuracy_plot_SMDM  + 
  rulefit_global_var_importance_plot_SMDM +
  mcc_plot_SMDM + DT_global_var_importance_plot_SMDM +
  plot_layout(nrow =2, ncol = 2, guides = "collect") +
  plot_annotation(
    title = "A. Surrogate fidelity across classification thresholds",
    theme = theme(
      plot.title = element_text(
        face = "bold",
        size = 16,
        color = "black"
      )
    )
  )
 )&
  theme(
    legend.position = "right",
    legend.title = element_text(face = "bold", size = 12, color = "black"),  # bold + size
    legend.text = element_text(size = 11)  # optional: slightly bigger legend labels
  )


# Modified version for SMDM poster


DT_global_var_importance_plot_SMDM_mod = ggplot(DT_factor_table_top,
                                            aes(x = rel_importance,
                                                y = fct_reorder(variable, rel_importance),
                                                fill = rel_importance)) +
  geom_col(width = 0.7) +
  scale_fill_gradient(low = "#FDEBD0", high = "#E67E22", guide = "none") +
  labs(
    title = "Decision Tree Surrogate",
    x = "Explanations identifying variable as top-ranked (%)",
    y = NULL
  ) +
  scale_x_continuous(
    limits = c(0, 0.4),
    breaks = seq(0, 0.4, by = 0.05),
    labels = scales::percent_format(accuracy = 1),
    expand = c(0, 0)
  )+
  theme_minimal(base_size = 13) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0, size = 14),
    axis.text.y = element_text(size = 12,  face = "bold"),
    axis.text.x = element_text(size = 12),
    axis.title.x = element_text(size = 14, face = "bold"),               # x-axis label size
    axis.title.y = element_text(size = 14, face = "bold"),  
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank(),
    panel.grid.major.x = element_line(color = "grey80", linetype = "dashed")
  )


rulefit_global_var_importance_plot_SMDM_mod = ggplot(RuleFit_factor_table_top,
                                                 aes(x = rel_importance,
                                                     y = forcats::fct_reorder(factor, rel_importance),
                                                     fill = rel_importance)) +
  geom_col(width = 0.7) +
  scale_fill_gradient(low = "#bdd7e7", high = "#6baed6", guide = "none") +
  labs(
    title = "Logistic Regression Surrogate",
    x = "Explanations identifying variable as top-ranked (%)",
    y = NULL
  ) +
  scale_x_continuous(
    limits = c(0, 0.4),
    breaks = seq(0, 0.4, by = 0.05),
    labels = scales::percent_format(accuracy = 1),
    expand = c(0, 0)
  )+
  theme_minimal(base_size = 13) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0, size = 14),
    axis.text.y = element_text(size = 12,  face = "bold"),
    axis.text.x = element_text(size = 12),
    axis.title.x = element_text(size = 14, face = "bold"),               # x-axis label size
    axis.title.y = element_text(size = 14, face = "bold"),  
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank(),
    panel.grid.major.x = element_line(color = "grey80", linetype = "dashed")
  )

var_importance_only =  (  rulefit_global_var_importance_plot_SMDM_mod +
                          DT_global_var_importance_plot_SMDM_mod +
                          plot_layout(nrow = 1, ncol = 2, guides = "collect") 
                         
)&
  theme(
    legend.position = "right",
    legend.title = element_text(face = "bold", size = 12, color = "black"),  # bold + size
    legend.text = element_text(size = 11)  # optional: slightly bigger legend labels
  )
