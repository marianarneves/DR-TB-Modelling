############################################################
# 1. Load libraries
############################################################
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

############################################################
# 2. Import data
############################################################
# Decision Tree ML results (PIDEMc outputs)
DTML <- read_excel(
  '/Users/mariananeves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/PM Boostrap/Pre Pruning/DTML_wtp2_bootstrapping_PIDEMc.xlsx'
)

# Classification model results (PMDT outputs)
Classification_PMDT <- read_xlsx(
  '/Users/mariananeves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx'
)

############################################################
# 3. Helper function: compute average NMB and 95% CI
############################################################
compute_avg_nmb <- function(df) {
  df %>%
    group_by(Threshold) %>%
    summarise(
      NMB = mean(NMB_SdTreat_DM),
      uciNMB = NMB + qt(0.975, df = length(NMB_SdTreat_DM) - 1) *
        sd(NMB_SdTreat_DM) / sqrt(length(NMB_SdTreat_DM)),
      lciNMB = NMB - qt(0.975, df = length(NMB_SdTreat_DM) - 1) *
        sd(NMB_SdTreat_DM) / sqrt(length(NMB_SdTreat_DM))
    )
}

############################################################
# 4. Compute average NMB for DTML and PMDT
############################################################
DTML_nmb_avg <- compute_avg_nmb(DTML)

PMDT_nmb_avg <- compute_avg_nmb(Classification_PMDT) 

############################################################
# 5. Compare NMB between DTML and PMDT
############################################################
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

############################################################
# 6. NMB for DTML and PMDT
############################################################

NMB_by_method = bind_rows(DTML_nmb_avg %>%
  mutate(Method = "DTML"), 
PMDT_nmb_avg%>%
  mutate(Method = "PIDEMc"))

############################################################
# 7. Compare accuracy of treatment assignment by threshold
############################################################
PMDT_DTML_acc <- DTML %>%
  mutate(Threshold = round(Threshold, 10)) %>%
  rename_with(~ paste0(., "_DTML"), -c(Person, Threshold)) %>%   # keep keys clean
  left_join(
    Classification_PMDT %>%
      mutate(Threshold = round(Threshold, 10), Person1 = Person + 1) %>%
      distinct(Person, Threshold, .keep_all = TRUE) %>%
      rename_with(~ paste0(., "_PMDT"), -c(Person, Person1, Threshold)),
    by = c("Threshold", "Person" = "Person1")
  ) %>%
  mutate(
    NMB_PMDT_correct = case_when(
      Opt_Treat_DTML == "BPaLM" & Opt_Treat_PMDT == "FLQ" ~ 1,
      Opt_Treat_DTML == "BPaLC" & Opt_Treat_PMDT == "DLM" ~ 1,
      TRUE ~ 0
    )
  ) %>%
  group_by(Threshold) %>%
  summarise(accuracy = mean(NMB_PMDT_correct),
            NMB = mean(NMB_SdTreat_DM_DTML)
            )

############################################################
# 7. Decision Tree highest NMB with accuracy > 95% 
############################################################
PMDT_DTML_acc %>%
  filter(accuracy > 0.95) %>%
  slice_max(NMB, n = 1)
  
