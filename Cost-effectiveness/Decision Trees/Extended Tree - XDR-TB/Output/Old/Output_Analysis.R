library(readxl)
library(dplyr)
library(tidyr)
library(ggplot2)

pmdt_data = readxl::read_xlsx("/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/PMDT_sampled.xlsx")

# Change in NMB PMDT compared to Standard Treatment
cnmb_pmdt_sdtreat = pmdt_data%>%
  group_by(threshold)%>%
  summarise(m = mean(NMB_SdTreat_PMDT)) %>%
  ggplot(aes(x = threshold, y = m)) +
  geom_line()
  