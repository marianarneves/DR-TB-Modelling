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


set.seed(1)

# Load the Moldova dataset
data_path <-
  "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_LR_Augumented.csv"
moldova_data <- read.csv(data_path)
moldova_data$Person = seq(1:dim(moldova_data)[1])


DalyResults = readxl::read_xlsx('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/Daly Cost Analysis/DalyResults_200samples.xlsx')

DalyResults_Moldova = DalyResults %>%
  left_join(moldova_data %>%
              select(FLQ_R, Person), by = 'Person') %>%
  mutate(best_treat = case_when(
    FLQ_R == 1 & DLM_NMB < SdTreat_NMB ~ 1,
    FLQ_R == 0 & DLM_NMB > SdTreat_NMB ~ 1,
    FLQ_R == 1 & DLM_NMB > SdTreat_NMB ~ 0,
    FLQ_R == 0 & DLM_NMB < SdTreat_NMB ~ 0,
    TRUE ~ 0
  ) )


#---------- Max average NMB if all pts receive correct treatment


DalyResults_Moldova_perfectmodel = DalyResults_Moldova %>%
  mutate(perfectmodel_NMB = case_when(
    FLQ_R == 1 ~ DLM_NMB,
    FLQ_R == 0 ~ SdTreat_NMB
  ))

mean(DalyResults_Moldova_perfectmodel$SdTreat_NMB) - mean(DalyResults_Moldova_perfectmodel$perfectmodel_NMB)  
