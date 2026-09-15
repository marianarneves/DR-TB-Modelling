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
DT_PIDEMp_tree_data <- '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/No Calibration/PM input Only/Pre pruning/MaxTreeDepth 10/DT_rules_output_wtp2.txt'

# Generate plot from rules
DT_PIDEMp_tree_plot <- plot_decision_tree(DT_PIDEMp_tree_data)

# Export tree visualization
export_graph(DT_PIDEMp_tree_plot, file_name = "DT_PIDEMp_tree_plot.png", file_type = "png")
