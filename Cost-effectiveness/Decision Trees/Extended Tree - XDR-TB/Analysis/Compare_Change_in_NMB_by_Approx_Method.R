library(readxl)
library(dplyr)
library(tidyr)
library(ggplot2)
library(gridExtra)
library(patchwork)

#1000 samples

PMDT_sampled_1000_orig = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/Optimism Correction/PM Sample/Original/PMDT_wtp2bootstrapping_samplesize200.xlsx')
PMDT_sampled_1000_adj = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/Optimism Correction/PM Sample/Adjusted/Test - Prob sampled/PMDT_wtp2bootstrapping_samplesize200.xlsx')
PMDT_sampled_1000_beta = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/Optimism Correction/PM Sample/Beta/Test - Truncated Probs/PMDT_wtp2bootstrapping_samplesize200.xlsx')
PMDT_sampled_1000_predonly = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/Optimism Correction/Prediction Only/PMDT_wtp2bootstrapping_samplesize200.xlsx')

PMDT_sampled_1000_orig_avg = PMDT_sampled_1000_orig%>%
  group_by(Threshold)%>%
  summarise(NMB = mean(NMB_SdTreat_DM)) %>%
  mutate(method = "Original")


PMDT_sampled_1000_adj_avg = PMDT_sampled_1000_adj%>%
  group_by(Threshold)%>%
  summarise(NMB = mean(NMB_SdTreat_DM)) %>%
  mutate(method = "Average")

PMDT_sampled_1000_beta_avg = PMDT_sampled_1000_beta%>%
  group_by(Threshold)%>%
  summarise(NMB = mean(NMB_SdTreat_DM)) %>%
  mutate(method = "Beta")

PMDT_sampled_1000_predonly_avg = PMDT_sampled_1000_predonly%>%
  group_by(Threshold)%>%
  summarise(NMB = mean(NMB_SdTreat_DM)) %>%
  mutate(method = "Prediction Only")


PMDT_sampled_1000 = rbind(PMDT_sampled_1000_orig_avg, PMDT_sampled_1000_adj_avg, PMDT_sampled_1000_beta_avg)

PMDT_sampled_1000_avg_graph <- ggplot(PMDT_sampled_1000, aes(x = Threshold, y = NMB, color = method)) +
  # Add lines
  geom_line(size = 0.7) +
  # Horizontal line
  geom_hline(yintercept = PMDT_sampled_1000_predonly_avg$NMB, color = "red", linetype = "dashed") +
  # Add annotation for the horizontal line
  annotate(
    "text",
    x = 0.6,  # Adjust x position as needed
    y = PMDT_sampled_1000_predonly_avg$NMB +50,  # Align y position with the line
    label = "Prediction Only",
    color = "red",
    size = 5,
    hjust = 0
  ) +
  # Customize axes
  scale_y_continuous(breaks = seq(-850, 450, by = 50), limits = c(-850, 450)) +
  scale_x_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.1)) +
  # Add labels
  ylab("Change in NMB") +
  xlab("Classification threshold") +
  # Customize theme
  theme_minimal() +
  theme(
    legend.position = "bottom",
    text = element_text(size = 18)
  )
