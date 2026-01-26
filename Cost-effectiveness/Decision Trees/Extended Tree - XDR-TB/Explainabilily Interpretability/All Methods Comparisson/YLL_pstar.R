# -------------------------------
# Load Libraries
# -------------------------------
library(readxl)
library(dplyr)
library(ggplot2)
library(scales)

setwd('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/R01 TB/Papers/Inter Exp PMDT')

# -------------------------------
# Load Data
# -------------------------------
file_path <- "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/DT Only/Input_V10/Test age x NMB/test_output.xlsx"

data <- read_excel(file_path)

# -------------------------------
# Calculate NMB & p*
# -------------------------------

wtp = 5714.43

data_m = data %>%
  mutate(NMB_FLQ_R = wtp * DALY_FLQres + Cost_FLQres,
         NMB_FLQ_S = wtp * DALY_FLQsus + Cost_FLQsus,
         pstar =  (NMB_DLM - NMB_FLQ_S)/ (NMB_FLQ_R - NMB_FLQ_S))

# Ensure data is sorted
data_m <- data_m %>% arrange(Person)

# -------------------------------
# Find crossing point p* ≈ 1
# -------------------------------
cross_x <- data_m %>%
  slice(which.min(abs(pstar - 1))) %>%
  pull(Person)

cross_x <- data_m$Person[which.min(abs(data_m$pstar - 1))]

# -------------------------------
# Build Plot
# -------------------------------

Prob_YLL = ggplot(data_m, aes(x = Person, y = pstar)) +
  
  # --- RIBBONS FIRST (background layer) ---
  geom_ribbon(aes(ymin = 0, ymax = pstar, fill = "FQ"), alpha = 0.25) +
  geom_ribbon(aes(ymin = pstar, ymax = max(pstar, na.rm = TRUE), fill = "CFZ"), alpha = 0.20) +
  
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
    x = cross_x + 10,
    y = max(data_m$pstar, na.rm = TRUE) * 0.9,
    label = paste0("YLL ≈ ", round(cross_x, 1)),
    size = 4.5,
    fill = "white",
    color = "#d62728",
    label.size = 0
  ) +
  
  labs(
    #title = "Probability Threshold p* as a Function of Years of Life Lost",
    x = "Years of Life Lost",
    y = "Probability Threshold p*",
    fill = "Optimal Treatment"
  ) +
  
  scale_x_continuous(
    breaks = seq(0, ceiling(max(data_m$Person, na.rm = TRUE)), by = 5),
    labels = scales::number_format(accuracy = 1),
    expand = expansion(mult = c(0.02, 0.02))
  ) +
  scale_y_continuous(
    breaks = seq(0, ceiling(max(data_m$pstar, na.rm = TRUE)), by = 0.25),
    labels = scales::number_format(accuracy = 0.01),
    expand = expansion(mult = c(0, 0.002))
  ) +
  
  scale_fill_manual(values = c("FQ" = "#7eb6ff", "CFZ" = "#ffb866")) +
  
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

ggsave('Prob_YLL.png', Prob_YLL, width = 12, height = 6, dpi = 300)




##########-----------


 
# ------------------------------------------------------------
# 1. Load data
# ------------------------------------------------------------
# Input data should contain at least:
#   - Threshold   : willingness-to-pay threshold
#   - Opt_Treat   : optimal treatment at each (Threshold, YLL)
#   - Rows ordered by Threshold, then YLL
# ------------------------------------------------------------

file_path <- '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/DT Only/Input_V10/Test age x NMB/PIDEMc/PIDEMc_YLL_test_output.xlsx'
data <- read_excel(file_path)


# ------------------------------------------------------------
# 2. Prepare analysis-ready dataset
# ------------------------------------------------------------
# YLL is reconstructed assuming 101 severity levels per threshold.
# Opt_Treat is coerced to a factor to ensure correct counting.
# ------------------------------------------------------------

data_ax <- data %>%
  filter(Threshold == Threshold[which.min(abs(Threshold - 0.308))]) %>%
  mutate(
    YLL = (row_number() - 1) %% 101,
    Opt_Treat = factor(Opt_Treat, levels = c("FLQ", "DLM")),
    Opt_Treat_m = ifelse(Opt_Treat == "FLQ", "FQ", "CFZ"),
    Opt_Treat_m = factor(Opt_Treat_m, levels = c("FQ", "CFZ")),
    Class = ifelse(PM_prediction == 0.0001, 'FQ Susceptible', 'FQ Resistant'),
    y_pos = as.numeric(Opt_Treat_m) +
      ifelse(Class == "FQ Susceptible", -0.05, 0.05)
  )

opt_treat_PIDEMc_opt_thre = ggplot(data_ax, aes(
  x = YLL,
  y = y_pos,
  colour = Class,
  shape = Class
)) +
  geom_point(size = 2.5) +
  scale_y_continuous(
    breaks = seq_along(levels(data_ax$Opt_Treat_m)),
    labels = levels(data_ax$Opt_Treat_m)
  ) +
  scale_x_continuous(
    breaks = seq(0, max(data_ax$YLL, na.rm = TRUE), by = 5),
    expand = expansion(mult = c(0.02, 0.02))
  ) +
  scale_colour_manual(
    values = c(
      "FQ Susceptible" = "#7eb6ff",  # blue
      "FQ Resistant" = "#ffb866"   # orange
    )
  ) +
  scale_shape_manual(
    values = c(
      "FQ Susceptible" = 15,  # square
      "FQ Resistant" = 16   # circle
    )
  ) +
  labs(
    x = "Years of Life Lost (YLL)",
    y = "Optimal Treatment",
    colour = "Classification",
    shape = "Classification"
  ) +
  theme_minimal(base_size = 15) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0, size = 16),
    axis.text.y = element_text(size = 14,  face = "bold"),
    axis.text.x = element_text(size = 14),
    axis.title.x = element_text(size = 16, face = "bold"),
    axis.title.y = element_text(size = 16, face = "bold"),
    panel.grid.major.x = element_line(color = "grey85", linewidth = 0.4),
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title = element_text(face = "bold"),
    legend.position = "bottom",
    legend.title = element_text(size = 14,face = "bold"),
    legend.text = element_text(size = 14),
    legend.key.width = unit(1, "cm")
  )


ggsave('opt_treat_PIDEMc_opt_thre.png', opt_treat_PIDEMc_opt_thre, width = 12, height = 6, dpi = 300)


############################################################
## Individual predictions and DALY (YLL) lookup
## ---------------------------------------------------------
## This script:
##  1. Loads individual-level prediction outputs
##  2. Maps each individual to an age group and sex
##  3. Extracts remaining life expectancy (used here as YLL)
##  4. Selects representative patients based on YLL and risk
##  5. Extracts corresponding PIDEM probability and
##     classification outputs for those patients
############################################################

############################################################
## 1. Input data
############################################################

# Logistic regression individual predictions
LR_pred <- read.csv(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/LR_MainPM_platt_beta_compare.csv'
)

# Life expectancy table (used to derive YLL)
LE_data <- read.csv(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/LE_Moldova.csv'
)

############################################################
## 2. Helper function: individual YLL lookup
############################################################

# For each individual, this function:
#  - Classifies age into WHO-style age bands
#  - Matches age band, sex, and year in the LE table
#  - Returns the corresponding life expectancy value
#    (interpreted here as YLL)

compute_daly_individual <- function(data, le_data, year = 2019) {
  
  daly_list <- numeric(nrow(data))
  
  for (idx in seq_len(nrow(data))) {
    
    ## ---- Age classification ----
    age <- data$age[idx]
    
    age_s <- if (age < 1) {
      '<1 year'
    } else if (age <= 4) {
      '1-4 years'
    } else if (age <= 9) {
      '5-9 years'
    } else if (age <= 14) {
      '10-14 years'
    } else if (age <= 19) {
      '15-19 years'
    } else if (age <= 24) {
      '20-24 years'
    } else if (age <= 29) {
      '25-29 years'
    } else if (age <= 34) {
      '30-34 years'
    } else if (age <= 39) {
      '35-39 years'
    } else if (age <= 44) {
      '40-44 years'
    } else if (age <= 49) {
      '45-49 years'
    } else if (age <= 54) {
      '50-54 years'
    } else if (age <= 59) {
      '55-59 years'
    } else if (age <= 64) {
      '60-64 years'
    } else if (age <= 69) {
      '65-69 years'
    } else if (age <= 74) {
      '70-74 years'
    } else if (age <= 79) {
      '75-79 years'
    } else if (age <= 84) {
      '80-84 years'
    } else {
      '85+ years'
    }
    
    ## ---- Match LE table ----
    sex_s <- data$sex[idx]
    
    matched <- le_data[
      le_data$Dim2   == age_s &
        le_data$Dim1 == sex_s &
        le_data$Period == year,
    ]
    
    ## ---- Extract YLL ----
    daly_list[idx] <- if (nrow(matched) > 0) {
      matched$Value[1]
    } else {
      NA_real_
    }
  }
  
  return(daly_list)
}

############################################################
## 3. Compute YLL for all individuals
############################################################

LR_pred$YLL <- compute_daly_individual(
  data   = LR_pred,
  le_data = LE_data
)

# Empirical note:
# No patients have YLL < 4 in this dataset

############################################################
## 4. Select representative patients
############################################################

# Low YLL (< 13) and lowest predicted risk
Pt_demo1 <- LR_pred %>%
  filter(YLL < 13) %>%
  slice_min(predicted_beta_mainpred, n = 1)

# Low YLL (< 13) and highest predicted risk
Pt_demo2 <- LR_pred %>%
  filter(YLL < 13) %>%
  slice_max(predicted_beta_mainpred, n = 1)

# High YLL (> 13) and lowest predicted risk
Pt_demo3 <- LR_pred %>%
  filter(YLL > 13) %>%
  slice_min(predicted_beta_mainpred, n = 1)

# High YLL (> 13) and highest predicted risk
# (restricted to be below the max risk observed in low-YLL)
Pt_demo4 <- LR_pred %>%
  filter(YLL > 13 &
           predicted_beta_mainpred < Pt_demo2$predicted_beta_mainpred) %>%
  slice_max(predicted_beta_mainpred, n = 1)

############################################################
## 5. Original PIDEM probability outputs (PIDEMp)
############################################################

Probability_PIDEM <- read_xlsx(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM input Only/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx'
)

# Note: PIDEM Person index is zero-based, hence pt_id - 1
PIDEMp_Pt_demo1 <- Probability_PIDEM %>% filter(Person == Pt_demo1$pt_id - 1)
PIDEMp_Pt_demo2 <- Probability_PIDEM %>% filter(Person == Pt_demo2$pt_id - 1)
PIDEMp_Pt_demo3 <- Probability_PIDEM %>% filter(Person == Pt_demo3$pt_id - 1)
PIDEMp_Pt_demo4 <- Probability_PIDEM %>% filter(Person == Pt_demo4$pt_id - 1)

############################################################
## 6. Original PIDEM classification outputs (PIDEMc)
############################################################

Classification_PIDEM <- read_xlsx(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx'
) %>%
  # Select threshold closest to the optimal value (0.308)
  filter(Threshold == Threshold[which.min(abs(Threshold - 0.308))])

PIDEMc_Pt_demo1 <- Classification_PIDEM %>% filter(Person == Pt_demo1$pt_id - 1)
PIDEMc_Pt_demo2 <- Classification_PIDEM %>% filter(Person == Pt_demo2$pt_id - 1)
PIDEMc_Pt_demo3 <- Classification_PIDEM %>% filter(Person == Pt_demo3$pt_id - 1)
PIDEMc_Pt_demo4 <- Classification_PIDEM %>% filter(Person == Pt_demo4$pt_id - 1)

############################################################
## 7. Next steps
############################################################
# These selected patients can now be used for:
#  - Individual-level decision tree walkthroughs
#  - Comparison of calibrated vs uncalibrated decisions
#  - Illustrative examples in figures or appendices
############################################################