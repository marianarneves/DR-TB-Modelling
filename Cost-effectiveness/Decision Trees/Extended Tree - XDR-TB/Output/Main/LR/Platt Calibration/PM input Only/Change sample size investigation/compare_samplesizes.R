library(readxl)
library(dplyr)
library(tidyr)
library(ggplot2)
library(gridExtra)
library(patchwork)
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Analysis/DR_TB_PMDT_Analysis_Functions.R')


#Prediction
Prediction_PMDT_5 = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/PMDT_wtp2bootstrapping_samplesize5.xlsx')
Prediction_PMDT_5_output_loc = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/')
Prediction_PMDT_5_varwtp = read_output_tolist_varyingwtp(Prediction_PMDT_5_output_loc, "PMDT_","bootstrapping_samplesize5", 6)


#Prediction
Prediction_PMDT_100 = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/PMDT_wtp2bootstrapping_samplesize100.xlsx')
Prediction_PMDT_100_output_loc = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/')
Prediction_PMDT_100_varwtp = read_output_tolist_varyingwtp(Prediction_PMDT_100_output_loc, "PMDT_","bootstrapping_samplesize100", 6)

#Prediction
Prediction_PMDT_200 = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/PMDT_wtp2bootstrapping_samplesize200.xlsx')
Prediction_PMDT_200_output_loc = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/')
Prediction_PMDT_200_varwtp = read_output_tolist_varyingwtp(Prediction_PMDT_200_output_loc, "PMDT_","bootstrapping_samplesize200", 6)

#Prediction
Prediction_PMDT_300 = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/PMDT_wtp2bootstrapping_samplesize300.xlsx')
Prediction_PMDT_300_output_loc = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/')
Prediction_PMDT_300_varwtp = read_output_tolist_varyingwtp(Prediction_PMDT_300_output_loc, "PMDT_","bootstrapping_samplesize300", 6)


#Prediction
Prediction_PMDT_400 = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/PMDT_wtp2bootstrapping_samplesize400.xlsx')
Prediction_PMDT_400_output_loc = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/')
Prediction_PMDT_400_varwtp = read_output_tolist_varyingwtp(Prediction_PMDT_400_output_loc, "PMDT_","bootstrapping_samplesize400", 6)

#Prediction
Prediction_PMDT_500 = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/PMDT_wtp2bootstrapping_samplesize500.xlsx')
Prediction_PMDT_500_output_loc = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/')
Prediction_PMDT_500_varwtp = read_output_tolist_varyingwtp(Prediction_PMDT_400_output_loc, "PMDT_","bootstrapping_samplesize500", 6)

#Prediction
Prediction_PMDT_600 = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/PMDT_wtp2bootstrapping_samplesize600.xlsx')
Prediction_PMDT_600_output_loc = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/')
Prediction_PMDT_600_varwtp = read_output_tolist_varyingwtp(Prediction_PMDT_400_output_loc, "PMDT_","bootstrapping_samplesize600", 6)


#Prediction
Prediction_PMDT_700 = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/PMDT_wtp2bootstrapping_samplesize700.xlsx')
Prediction_PMDT_700_output_loc = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/')
Prediction_PMDT_700_varwtp = read_output_tolist_varyingwtp(Prediction_PMDT_400_output_loc, "PMDT_","bootstrapping_samplesize700", 6)

#Prediction
Prediction_PMDT_800 = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/PMDT_wtp2bootstrapping_samplesize800.xlsx')
Prediction_PMDT_800_output_loc = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/')
Prediction_PMDT_800_varwtp = read_output_tolist_varyingwtp(Prediction_PMDT_400_output_loc, "PMDT_","bootstrapping_samplesize800", 6)


#Prediction
Prediction_PMDT_900 = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/PMDT_wtp2bootstrapping_samplesize900.xlsx')
Prediction_PMDT_900_output_loc = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/')
Prediction_PMDT_900_varwtp = read_output_tolist_varyingwtp(Prediction_PMDT_400_output_loc, "PMDT_","bootstrapping_samplesize900", 6)


#Prediction
Prediction_PMDT_1000 = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/PMDT_wtp2bootstrapping_samplesize1000.xlsx')
Prediction_PMDT_1000_output_loc = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM input Only/1000 samples/')
Prediction_PMDT_1000_varwtp = read_output_tolist_varyingwtp(Prediction_PMDT_400_output_loc, "PMDT_","bootstrapping_samplesize1000", 6)



Prediction_PMDT_5_NMBavg_overall = Prediction_PMDT_5_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

Prediction_PMDT_5_max_Thresholds <- Prediction_PMDT_5_NMBavg_overall %>%
  slice_max(NMB_avg_mean, with_ties = FALSE) %>%  # Get the maximum NMB_avg_mean across all Thresholds
  pull(Threshold) %>%
  as.data.frame()

Prediction_PMDT_5_max_Thresholds$wtp = seq(1:6)
colnames(Prediction_PMDT_5_max_Thresholds) = c("Threshold", "wtp")

Prediction_PMDT_5_NMBavg_FLQstatus = Prediction_PMDT_5_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

Prediction_PMDT_5_NMB_avg = bind_rows(Prediction_PMDT_5_NMBavg_FLQstatus, Prediction_PMDT_5_NMBavg_overall)%>%
  group_by(wtp, FLQ_Status) 

Prediction_PMDT_5_NMB_avg_max = data.frame()
for (i in 1:length(Prediction_PMDT_5_max_Thresholds$wtp)){
  
  ax = Prediction_PMDT_5_NMB_avg %>%
    filter(Threshold == Prediction_PMDT_5_max_Thresholds$Threshold[i] & wtp == Prediction_PMDT_5_max_Thresholds$wtp[i])
  
  Prediction_PMDT_5_NMB_avg_max = bind_rows(Prediction_PMDT_5_NMB_avg_max, ax)
  
}

Prediction_PMDT_5_NMB_avg_max = Prediction_PMDT_5_NMB_avg_max %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQ',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQ',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))





#Prediction

Prediction_PMDT_100_NMBavg_overall = Prediction_PMDT_100_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

Prediction_PMDT_100_max_Thresholds <- Prediction_PMDT_100_NMBavg_overall %>%
  slice_max(NMB_avg_mean, with_ties = FALSE) %>%  # Get the maximum NMB_avg_mean across all Thresholds
  pull(Threshold) %>%
  as.data.frame()

Prediction_PMDT_100_max_Thresholds$wtp = seq(1:6)
colnames(Prediction_PMDT_100_max_Thresholds) = c("Threshold", "wtp")

Prediction_PMDT_100_NMBavg_FLQstatus = Prediction_PMDT_100_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

Prediction_PMDT_100_NMB_avg = bind_rows(Prediction_PMDT_100_NMBavg_FLQstatus, Prediction_PMDT_100_NMBavg_overall)%>%
  group_by(wtp, FLQ_Status) 

Prediction_PMDT_100_NMB_avg_max = data.frame()
for (i in 1:length(Prediction_PMDT_100_max_Thresholds$wtp)){
  
  ax = Prediction_PMDT_100_NMB_avg %>%
    filter(Threshold == Prediction_PMDT_100_max_Thresholds$Threshold[i] & wtp == Prediction_PMDT_100_max_Thresholds$wtp[i])
  
  Prediction_PMDT_100_NMB_avg_max = bind_rows(Prediction_PMDT_100_NMB_avg_max, ax)
  
}

Prediction_PMDT_100_NMB_avg_max = Prediction_PMDT_100_NMB_avg_max %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQ',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQ',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))



Prediction_PMDT_200_NMBavg_overall = Prediction_PMDT_200_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

Prediction_PMDT_200_max_Thresholds <- Prediction_PMDT_200_NMBavg_overall %>%
  slice_max(NMB_avg_mean, with_ties = FALSE) %>%  # Get the maximum NMB_avg_mean across all Thresholds
  pull(Threshold) %>%
  as.data.frame()

Prediction_PMDT_200_max_Thresholds$wtp = seq(1:6)
colnames(Prediction_PMDT_200_max_Thresholds) = c("Threshold", "wtp")

Prediction_PMDT_200_NMBavg_FLQstatus = Prediction_PMDT_200_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

Prediction_PMDT_200_NMB_avg = bind_rows(Prediction_PMDT_200_NMBavg_FLQstatus, Prediction_PMDT_200_NMBavg_overall)%>%
  group_by(wtp, FLQ_Status) 

Prediction_PMDT_200_NMB_avg_max = data.frame()
for (i in 1:length(Prediction_PMDT_200_max_Thresholds$wtp)){
  
  ax = Prediction_PMDT_200_NMB_avg %>%
    filter(Threshold == Prediction_PMDT_200_max_Thresholds$Threshold[i] & wtp == Prediction_PMDT_200_max_Thresholds$wtp[i])
  
  Prediction_PMDT_200_NMB_avg_max = bind_rows(Prediction_PMDT_200_NMB_avg_max, ax)
  
}

Prediction_PMDT_200_NMB_avg_max = Prediction_PMDT_200_NMB_avg_max %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQ',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQ',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))





Prediction_PMDT_300_NMBavg_overall = Prediction_PMDT_300_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

Prediction_PMDT_300_max_Thresholds <- Prediction_PMDT_300_NMBavg_overall %>%
  slice_max(NMB_avg_mean, with_ties = FALSE) %>%  # Get the maximum NMB_avg_mean across all Thresholds
  pull(Threshold) %>%
  as.data.frame()

Prediction_PMDT_300_max_Thresholds$wtp = seq(1:6)
colnames(Prediction_PMDT_300_max_Thresholds) = c("Threshold", "wtp")

Prediction_PMDT_300_NMBavg_FLQstatus = Prediction_PMDT_300_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

Prediction_PMDT_300_NMB_avg = bind_rows(Prediction_PMDT_300_NMBavg_FLQstatus, Prediction_PMDT_300_NMBavg_overall)%>%
  group_by(wtp, FLQ_Status) 

Prediction_PMDT_300_NMB_avg_max = data.frame()
for (i in 1:length(Prediction_PMDT_300_max_Thresholds$wtp)){
  
  ax = Prediction_PMDT_300_NMB_avg %>%
    filter(Threshold == Prediction_PMDT_300_max_Thresholds$Threshold[i] & wtp == Prediction_PMDT_300_max_Thresholds$wtp[i])
  
  Prediction_PMDT_300_NMB_avg_max = bind_rows(Prediction_PMDT_300_NMB_avg_max, ax)
  
}

Prediction_PMDT_300_NMB_avg_max = Prediction_PMDT_300_NMB_avg_max %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQ',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQ',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))












Prediction_PMDT_400_NMBavg_overall = Prediction_PMDT_400_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

Prediction_PMDT_400_max_Thresholds <- Prediction_PMDT_400_NMBavg_overall %>%
  slice_max(NMB_avg_mean, with_ties = FALSE) %>%  # Get the maximum NMB_avg_mean across all Thresholds
  pull(Threshold) %>%
  as.data.frame()

Prediction_PMDT_400_max_Thresholds$wtp = seq(1:6)
colnames(Prediction_PMDT_400_max_Thresholds) = c("Threshold", "wtp")

Prediction_PMDT_400_NMBavg_FLQstatus = Prediction_PMDT_400_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

Prediction_PMDT_400_NMB_avg = bind_rows(Prediction_PMDT_400_NMBavg_FLQstatus, Prediction_PMDT_400_NMBavg_overall)%>%
  group_by(wtp, FLQ_Status) 

Prediction_PMDT_400_NMB_avg_max = data.frame()
for (i in 1:length(Prediction_PMDT_400_max_Thresholds$wtp)){
  
  ax = Prediction_PMDT_400_NMB_avg %>%
    filter(Threshold == Prediction_PMDT_400_max_Thresholds$Threshold[i] & wtp == Prediction_PMDT_400_max_Thresholds$wtp[i])
  
  Prediction_PMDT_400_NMB_avg_max = bind_rows(Prediction_PMDT_400_NMB_avg_max, ax)
  
}

Prediction_PMDT_400_NMB_avg_max = Prediction_PMDT_400_NMB_avg_max %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQ',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQ',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))











Prediction_PMDT_500_NMBavg_overall = Prediction_PMDT_500_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

Prediction_PMDT_500_max_Thresholds <- Prediction_PMDT_500_NMBavg_overall %>%
  slice_max(NMB_avg_mean, with_ties = FALSE) %>%  # Get the maximum NMB_avg_mean across all Thresholds
  pull(Threshold) %>%
  as.data.frame()

Prediction_PMDT_500_max_Thresholds$wtp = seq(1:6)
colnames(Prediction_PMDT_500_max_Thresholds) = c("Threshold", "wtp")

Prediction_PMDT_500_NMBavg_FLQstatus = Prediction_PMDT_500_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

Prediction_PMDT_500_NMB_avg = bind_rows(Prediction_PMDT_500_NMBavg_FLQstatus, Prediction_PMDT_500_NMBavg_overall)%>%
  group_by(wtp, FLQ_Status) 

Prediction_PMDT_500_NMB_avg_max = data.frame()
for (i in 1:length(Prediction_PMDT_500_max_Thresholds$wtp)){
  
  ax = Prediction_PMDT_500_NMB_avg %>%
    filter(Threshold == Prediction_PMDT_500_max_Thresholds$Threshold[i] & wtp == Prediction_PMDT_500_max_Thresholds$wtp[i])
  
  Prediction_PMDT_500_NMB_avg_max = bind_rows(Prediction_PMDT_500_NMB_avg_max, ax)
  
}

Prediction_PMDT_500_NMB_avg_max = Prediction_PMDT_500_NMB_avg_max %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQ',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQ',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))







Prediction_PMDT_600_NMBavg_overall = Prediction_PMDT_600_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

Prediction_PMDT_600_max_Thresholds <- Prediction_PMDT_600_NMBavg_overall %>%
  slice_max(NMB_avg_mean, with_ties = FALSE) %>%  # Get the maximum NMB_avg_mean across all Thresholds
  pull(Threshold) %>%
  as.data.frame()

Prediction_PMDT_600_max_Thresholds$wtp = seq(1:6)
colnames(Prediction_PMDT_600_max_Thresholds) = c("Threshold", "wtp")

Prediction_PMDT_600_NMBavg_FLQstatus = Prediction_PMDT_600_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

Prediction_PMDT_600_NMB_avg = bind_rows(Prediction_PMDT_600_NMBavg_FLQstatus, Prediction_PMDT_600_NMBavg_overall)%>%
  group_by(wtp, FLQ_Status) 

Prediction_PMDT_600_NMB_avg_max = data.frame()
for (i in 1:length(Prediction_PMDT_600_max_Thresholds$wtp)){
  
  ax = Prediction_PMDT_600_NMB_avg %>%
    filter(Threshold == Prediction_PMDT_600_max_Thresholds$Threshold[i] & wtp == Prediction_PMDT_600_max_Thresholds$wtp[i])
  
  Prediction_PMDT_600_NMB_avg_max = bind_rows(Prediction_PMDT_600_NMB_avg_max, ax)
  
}

Prediction_PMDT_600_NMB_avg_max = Prediction_PMDT_600_NMB_avg_max %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQ',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQ',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))







Prediction_PMDT_700_NMBavg_overall = Prediction_PMDT_700_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

Prediction_PMDT_700_max_Thresholds <- Prediction_PMDT_700_NMBavg_overall %>%
  slice_max(NMB_avg_mean, with_ties = FALSE) %>%  # Get the maximum NMB_avg_mean across all Thresholds
  pull(Threshold) %>%
  as.data.frame()

Prediction_PMDT_700_max_Thresholds$wtp = seq(1:6)
colnames(Prediction_PMDT_700_max_Thresholds) = c("Threshold", "wtp")

Prediction_PMDT_700_NMBavg_FLQstatus = Prediction_PMDT_700_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

Prediction_PMDT_700_NMB_avg = bind_rows(Prediction_PMDT_700_NMBavg_FLQstatus, Prediction_PMDT_700_NMBavg_overall)%>%
  group_by(wtp, FLQ_Status) 

Prediction_PMDT_700_NMB_avg_max = data.frame()
for (i in 1:length(Prediction_PMDT_700_max_Thresholds$wtp)){
  
  ax = Prediction_PMDT_700_NMB_avg %>%
    filter(Threshold == Prediction_PMDT_700_max_Thresholds$Threshold[i] & wtp == Prediction_PMDT_700_max_Thresholds$wtp[i])
  
  Prediction_PMDT_700_NMB_avg_max = bind_rows(Prediction_PMDT_700_NMB_avg_max, ax)
  
}

Prediction_PMDT_700_NMB_avg_max = Prediction_PMDT_700_NMB_avg_max %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQ',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQ',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))





Prediction_PMDT_800_NMBavg_overall = Prediction_PMDT_800_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

Prediction_PMDT_800_max_Thresholds <- Prediction_PMDT_800_NMBavg_overall %>%
  slice_max(NMB_avg_mean, with_ties = FALSE) %>%  # Get the maximum NMB_avg_mean across all Thresholds
  pull(Threshold) %>%
  as.data.frame()

Prediction_PMDT_800_max_Thresholds$wtp = seq(1:6)
colnames(Prediction_PMDT_800_max_Thresholds) = c("Threshold", "wtp")

Prediction_PMDT_800_NMBavg_FLQstatus = Prediction_PMDT_800_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

Prediction_PMDT_800_NMB_avg = bind_rows(Prediction_PMDT_800_NMBavg_FLQstatus, Prediction_PMDT_800_NMBavg_overall)%>%
  group_by(wtp, FLQ_Status) 

Prediction_PMDT_800_NMB_avg_max = data.frame()
for (i in 1:length(Prediction_PMDT_800_max_Thresholds$wtp)){
  
  ax = Prediction_PMDT_800_NMB_avg %>%
    filter(Threshold == Prediction_PMDT_800_max_Thresholds$Threshold[i] & wtp == Prediction_PMDT_800_max_Thresholds$wtp[i])
  
  Prediction_PMDT_800_NMB_avg_max = bind_rows(Prediction_PMDT_800_NMB_avg_max, ax)
  
}

Prediction_PMDT_800_NMB_avg_max = Prediction_PMDT_800_NMB_avg_max %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQ',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQ',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))




Prediction_PMDT_900_NMBavg_overall = Prediction_PMDT_900_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

Prediction_PMDT_900_max_Thresholds <- Prediction_PMDT_900_NMBavg_overall %>%
  slice_max(NMB_avg_mean, with_ties = FALSE) %>%  # Get the maximum NMB_avg_mean across all Thresholds
  pull(Threshold) %>%
  as.data.frame()

Prediction_PMDT_900_max_Thresholds$wtp = seq(1:6)
colnames(Prediction_PMDT_900_max_Thresholds) = c("Threshold", "wtp")

Prediction_PMDT_900_NMBavg_FLQstatus = Prediction_PMDT_900_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

Prediction_PMDT_900_NMB_avg = bind_rows(Prediction_PMDT_900_NMBavg_FLQstatus, Prediction_PMDT_900_NMBavg_overall)%>%
  group_by(wtp, FLQ_Status) 

Prediction_PMDT_900_NMB_avg_max = data.frame()
for (i in 1:length(Prediction_PMDT_900_max_Thresholds$wtp)){
  
  ax = Prediction_PMDT_900_NMB_avg %>%
    filter(Threshold == Prediction_PMDT_900_max_Thresholds$Threshold[i] & wtp == Prediction_PMDT_900_max_Thresholds$wtp[i])
  
  Prediction_PMDT_900_NMB_avg_max = bind_rows(Prediction_PMDT_900_NMB_avg_max, ax)
  
}

Prediction_PMDT_900_NMB_avg_max = Prediction_PMDT_900_NMB_avg_max %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQ',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQ',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))






Prediction_PMDT_1000_NMBavg_overall = Prediction_PMDT_1000_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

Prediction_PMDT_1000_max_Thresholds <- Prediction_PMDT_1000_NMBavg_overall %>%
  slice_max(NMB_avg_mean, with_ties = FALSE) %>%  # Get the maximum NMB_avg_mean across all Thresholds
  pull(Threshold) %>%
  as.data.frame()

Prediction_PMDT_1000_max_Thresholds$wtp = seq(1:6)
colnames(Prediction_PMDT_1000_max_Thresholds) = c("Threshold", "wtp")

Prediction_PMDT_1000_NMBavg_FLQstatus = Prediction_PMDT_1000_varwtp$output_df %>%
  calculate_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

Prediction_PMDT_1000_NMB_avg = bind_rows(Prediction_PMDT_1000_NMBavg_FLQstatus, Prediction_PMDT_1000_NMBavg_overall)%>%
  group_by(wtp, FLQ_Status) 

Prediction_PMDT_1000_NMB_avg_max = data.frame()
for (i in 1:length(Prediction_PMDT_1000_max_Thresholds$wtp)){
  
  ax = Prediction_PMDT_1000_NMB_avg %>%
    filter(Threshold == Prediction_PMDT_1000_max_Thresholds$Threshold[i] & wtp == Prediction_PMDT_1000_max_Thresholds$wtp[i])
  
  Prediction_PMDT_1000_NMB_avg_max = bind_rows(Prediction_PMDT_1000_NMB_avg_max, ax)
  
}

Prediction_PMDT_1000_NMB_avg_max = Prediction_PMDT_1000_NMB_avg_max %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQ',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQ',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))







# Combine data
Prediction_PMDT <- bind_rows(
  Prediction_PMDT_1000_NMB_avg_max %>% mutate(sample_size = "SS1000", ss = 1000),
  Prediction_PMDT_900_NMB_avg_max %>% mutate(sample_size = "SS900", ss = 900),
  Prediction_PMDT_800_NMB_avg_max %>% mutate(sample_size = "SS800", ss = 800),
  Prediction_PMDT_700_NMB_avg_max %>% mutate(sample_size = "SS700", ss = 700),
  Prediction_PMDT_600_NMB_avg_max %>% mutate(sample_size = "SS600", ss = 600),
  Prediction_PMDT_500_NMB_avg_max %>% mutate(sample_size = "SS500", ss = 500),
  Prediction_PMDT_400_NMB_avg_max %>% mutate(sample_size = "SS400", ss = 400),
  Prediction_PMDT_300_NMB_avg_max %>% mutate(sample_size = "SS300", ss = 300),
  Prediction_PMDT_200_NMB_avg_max %>% mutate(sample_size = "SS200", ss = 200),
  Prediction_PMDT_100_NMB_avg_max %>% mutate(sample_size = "SS100", ss = 100),
  Prediction_PMDT_5_NMB_avg_max %>% mutate(sample_size = "SS5", ss = 5)
)

# Plot
Prediction_PMDT_plot_NMB_wtp <- ggplot(Prediction_PMDT %>%
                                         filter(wtp == 2),
                                       aes(x = ss, y = NMB_avg_mean)) +
  geom_line(size = 1) +
  geom_ribbon(aes(ymin = t_interval_lower, ymax = t_interval_upper), alpha = 0.3, color = NA) +
  labs(
    x = "Willingness-to-pay value as a portion of Moldova's GDP per capita",
    y = "Change in NMB",
    title = "Incremental NMB with respect to the standard of care and 95% confidence intervals"
  ) +
  theme_minimal(base_size = 18) +
  facet_grid(. ~ FLQ_Status_m, scales = "free_y") +
  theme(legend.position = "right")  # Show legend for sample sizes
