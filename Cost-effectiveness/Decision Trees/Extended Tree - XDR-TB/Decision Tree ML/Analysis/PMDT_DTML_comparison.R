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

# Read the Excel file (first sheet by default)
df <- read_excel('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Decision Tree ML/PM Boostrap/DTML_wtp2_bootstrapping_samplesize200.xlsx')


# 2. Summary function for avg NMB and CI
compute_avg_nmb <- function(df) {
  df %>%
    group_by(Threshold) %>%
    summarise(
      NMB = mean(NMB_SdTreat_DM),
      uciNMB = NMB + qt(0.975, df = length(NMB_SdTreat_DM) - 1) * sd(NMB_SdTreat_DM) / sqrt(length(NMB_SdTreat_DM)),
      lciNMB = NMB - qt(0.975, df = length(NMB_SdTreat_DM) - 1) * sd(NMB_SdTreat_DM) / sqrt(length(NMB_SdTreat_DM))
    ) 
}

DTML_nmb_avg = compute_avg_nmb(df)%>%
  rename_with(
    ~ paste0(.x, "_DTML"),
    .cols = -Threshold
  )

ggplot(DTML_nmb_avg, aes(x = Threshold, y = NMB_DTML)) +
  geom_line() +
  geom_ribbon(aes(ymin = lciNMB_DTML, ymax = uciNMB_DTML), alpha = 0.3, fill = "grey") +
    labs(x = "Classification threshold", y = "Change in NMB") +
  theme_minimal(base_size = 16) +
  theme(legend.position = "none")


# Read the data
Classification_PMDT <- read_xlsx('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/PMDT_wtp2bootstrapping_samplesize200.xlsx')

PMDT_nmb_avg = compute_avg_nmb(Classification_PMDT)%>%
  rename_with(
    ~ paste0(.x, "_PMDT"),
    .cols = -Threshold
  )

ggplot(PMDT_nmb_avg, aes(x = Threshold, y = NMB_PMDT)) +
  geom_line() +
  geom_ribbon(aes(ymin = lciNMB_PMDT, ymax = uciNMB_PMDT), alpha = 0.3, fill = "grey") +
  labs(x = "Classification threshold", y = "Change in NMB") +
  theme_minimal(base_size = 16) +
  theme(legend.position = "none")


### Compare

PMDT_DTML_nmb <- DTML_nmb_avg %>%
  mutate(Threshold = round(Threshold, 6)) %>%
  left_join(
    PMDT_nmb_avg %>% mutate(Threshold = round(Threshold, 6)),
    by = "Threshold"
  ) %>%
  mutate(NMB_PMDT_DTML = NMB_PMDT - NMB_DTML,
         percNMB_PMDT_DTML = NMB_DTML/NMB_PMDT)


ggplot(PMDT_DTML_nmb, aes(x = Threshold, y = NMB_PMDT_DTML)) +
  geom_line() +
  labs(x = "Classification threshold", y = "Change in NMB") +
  theme_minimal(base_size = 16) +
  theme(legend.position = "none")

ggplot(PMDT_DTML_nmb, aes(x = Threshold, y = percNMB_PMDT_DTML)) +
  geom_line() +
  labs(x = "Classification threshold", y = "Change in NMB") +
  theme_minimal(base_size = 16) +
  theme(legend.position = "none")


