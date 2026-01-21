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
source('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Analysis/DR_TB_PMDT_Analysis_Functions.R')

set.seed(1)

# Function that merges Personal Characteristics into the results of PIDEMs
add_opt_treat <- function(df, threshold = 'N') {
  if(threshold == 'N'){
    moldova_data %>%
      left_join(
        df %>%
          select(Person, Opt_Treat) %>%
          mutate(Person_m = Person + 1),
        by = c("Pt_id" = "Person_m")
      ) %>%
      mutate(
        Opt_Treat = ifelse(Opt_Treat == "DLM", "CLZ", "FLQ")
      )
  }
  else{
    moldova_data %>%
      left_join(
        df %>%
          select(Person, Opt_Treat, Threshold) %>%
          mutate(Person_m = Person + 1),
        by = c("Pt_id" = "Person_m")
      ) %>%
      mutate(
        Opt_Treat = ifelse(Opt_Treat == "DLM", "CLZ", "FLQ")
      )
  }
}

# Load the new dataset
data_path <-
  "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_LR_Augumented.csv"
moldova_data <- read.csv(data_path)
moldova_data$Pt_id = seq(1:dim(moldova_data)[1])


########################################
#       Probability Based Method       #
########################################

output_loc = '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM input Only/'
Prediction_PMDT_varwtp <- read_output_tolist_varyingwtp(output_loc, "PMDT_", "bootstrapping_samplesize200", 6)

# Apply and save each to a CSV file
for (i in 1:6) {
  df_i <- add_opt_treat(Prediction_PMDT_varwtp$output_list[[i]], threshold = 'N')
  
  write.csv(
    df_i,
    file = paste0(
      "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Decision Tree ML/PM input Only/moldova_data_opt_treat_prediction_allthresholds_wtp",
      i, ".csv"
    ),
    row.names = FALSE
  )
}

###########################################
#       Classification Based Method       #
###########################################

output_loc = '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/Input_V10/'
Classification_PMDT_varwtp <- read_output_tolist_varyingwtp(output_loc, "PMDT_", "bootstrapping_samplesize200", 6)

# Maximum NMB threshold, WTP = 1

Classification_PMDT_meanNMB = calculate_ci(Classification_PMDT_varwtp$output_list$wtp_2,  NMB_SdTreat_DM, Threshold)

Classication_threshold_max = Classification_PMDT_meanNMB %>%
                              slice_max(NMB_avg_mean, n = 1) %>%
                              pull(Threshold)

Classification_PMDT_threshold_max = Classification_PMDT_varwtp$output_list$wtp_2 %>%
                                      filter(Threshold == Classication_threshold_max)

moldova_data_opt_treat_classification = add_opt_treat(Classification_PMDT_threshold_max, threshold = 'N')

write.csv(moldova_data_opt_treat_classification, '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Decision Tree ML/PM Boostrap/moldova_data_opt_treat_classification_optthreshold_wtp1.csv', row.names = FALSE)

# All thresholds

# Apply and save each to a CSV file
for (i in 1:6) {
  df_i <- add_opt_treat(Classification_PMDT_varwtp$output_list[[i]], threshold = 'Y')
  
  print(length(unique(df_i$Threshold)))
  
  write.csv(
    df_i,
    file = paste0(
      '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Decision Tree ML/PM Boostrap/Input/test/moldova_data_opt_treat_classification_allthresholds_wtp',
      i, ".csv"
    ),
    row.names = FALSE
  )
}




