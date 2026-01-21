library(readxl)
library(dplyr)
library(tidyr)
library(ggplot2)
library(gridExtra)
library(patchwork)
library(purrr)
source('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/R01 TB/Papers/PMDT  RR_TB/Drafts/Figures/generateFiguresUtils.R')


DTProb_nocal = read_xlsx('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM Bootstrap/Input_V10/DecisionTree_probs_alt.xlsx')
DTProb_cal = read_xlsx('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/Input_V10/DecisionTree_probs_alt.xlsx')

# =====================================================================
# 3. Identify classification threshold(s) with maximum NMB - Beta Calibration
# =====================================================================

PIDEMc_cal_inputV10 = read_xlsx('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx')

Classification_wtp_avgs_cal <- compute_avg_nmb_ci(PIDEMc_cal_inputV10, NMB_SdTreat_DM, Threshold, wtp_val = "1")

# Extract the point with highest NMB for annotation
Classification_max_point_cal <- slice_max(Classification_wtp_avgs_cal, NMB_avg, n = 1)

sprintf("%.20f", Classification_max_point_cal$Threshold)

PIDEMc_cal_maxthreshold = PIDEMc_cal_inputV10 %>%
  slice_min(abs(Threshold - Classification_max_point_cal$Threshold))


# =====================================================================
# 3. Identify classification threshold(s) with maximum NMB - No Calibration
# =====================================================================

PIDEMc_nocal_inputV10 = read_xlsx('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM Bootstrap/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx')

Classification_wtp_avgs_nocal <- compute_avg_nmb_ci(PIDEMc_nocal_inputV10, NMB_SdTreat_DM, Threshold, wtp_val = "1")

# Extract the point with highest NMB for annotation
Classification_max_point_nocal <- slice_max(Classification_wtp_avgs_nocal, NMB_avg, n = 1)

PIDEMc_nocal_maxthreshold = PIDEMc_nocal_inputV10 %>%
  slice_min(abs(Threshold - Classification_max_point_nocal$Threshold))


# =====================================================================
# 3. Combine data
# =====================================================================

#Combine data
alldata = cbind(PIDEMc_cal_inputV10 %>% rename_with(~ paste0(., "_cal")),PIDEMc_nocal_inputV10 %>% rename_with(~ paste0(., "_nocal")))

#Filtering to the threshold that results in max NMB for the calibrated predictions

alldata_filtered_maxcal =  alldata%>%slice_min(abs(Threshold_cal - Classification_max_point_cal$Threshold))

alldata_filtered_selected_maxcal  = alldata_filtered_maxcal %>%
  select(Person_cal,Person_nocal,  Threshold_cal, PM_classification_cal, FLQ_Status_cal, Opt_Treat_cal, Threshold_nocal, PM_classification_nocal, FLQ_Status_nocal, Opt_Treat_nocal)

#Filtering to the threshold that results in max NMB for the non calibrated predictions

alldata_filtered_maxnocal =  alldata%>%slice_min(abs(Threshold_nocal - Classification_max_point_nocal$Threshold))

alldata_filtered_selected_maxnocal  = alldata_filtered_maxnocal %>%
  select(Person_cal,Person_nocal, Threshold_cal, PM_classification_cal, FLQ_Status_cal, Opt_Treat_cal, Threshold_nocal, PM_classification_nocal, FLQ_Status_nocal, Opt_Treat_nocal)

which(alldata_filtered_selected_maxnocal$Opt_Treat_cal != alldata_filtered_selected_maxnocal$Opt_Treat_nocal)

# =====================================================================
# 3. Analising why the max does not match
# =====================================================================

# Threshold in the averaged calibrated data which corresponds to the maximum in the non calibrated data
Classification_wtp_avgs_cal %>%
  slice_min(abs(Threshold - unique(alldata_filtered_selected_maxnocal$Threshold_cal)))

# Threshold in the averaged non calibrated data which corresponds to the maximum in the calibrated data
Classification_wtp_avgs_nocal %>%
  slice_min(abs(Threshold - unique(alldata_filtered_selected_maxcal$Threshold_nocal)))


# =====================================================================
# 3. Find the people in the combined data that have Opt treat not matching
# =====================================================================

Person_notmatch = alldata_filtered_selected_maxnocal %>%
  filter(Opt_Treat_cal != Opt_Treat_nocal) %>%
  select(Person_cal)

alldata_notmatch = alldata %>%
  slice_min(abs(Threshold_cal - unique(alldata_filtered_selected_maxnocal$Threshold_cal))) %>%
  filter(Person_cal %in% Person_notmatch$Person_cal)

#Looking at the NMB

alldata_notmatch_NMB = alldata_notmatch %>%
  select(Opt_Treat_cal, NMB_DLM_cal, NMB_FLQ_cal, Opt_Treat_nocal, NMB_DLM_nocal, NMB_FLQ_nocal)
  




