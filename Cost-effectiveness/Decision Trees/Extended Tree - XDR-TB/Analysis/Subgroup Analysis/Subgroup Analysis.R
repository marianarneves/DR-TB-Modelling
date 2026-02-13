library(readxl)
library(dplyr)
library(tidyr)
library(ggplot2)
library(gridExtra)
library(patchwork)
library(purrr)
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Analysis/DR_TB_PMDT_Analysis_Functions.R')

setwd("/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Results Comparison/")



# === Function to process NMB results ===
process_input_data <- function(file_path, output_loc, calibrated_label) {
  data <- read_xlsx(file_path)
  varwtp <- read_output_tolist_varyingwtp(output_loc, "PMDT_", "bootstrapping_samplesize200", 6)
  
  # Overall average NMB
  NMB_avg_overall <- varwtp$output_df %>%
    calculate_ci(NMB_SdTreat_DM, c(wtp, Threshold)) %>%
    mutate(FLQ_Status = "All patients")
  
  # Max threshold by WTP
  max_thresholds <- NMB_avg_overall %>%
    slice_max(NMB_avg_mean, with_ties = FALSE) %>%
    pull(Threshold) %>%
    as.data.frame() %>%
    mutate(wtp = 1:6)
  colnames(max_thresholds) <- c("Threshold", "wtp")
  
  # NMB by FLQ status
  NMB_avg_FLQ <- varwtp$output_df %>%
    calculate_ci(NMB_SdTreat_DM, c(wtp, FLQ_Status, Threshold))
  
  # Combine overall and stratified results
  NMB_combined <- bind_rows(NMB_avg_FLQ, NMB_avg_overall) %>%
    group_by(wtp, FLQ_Status)
  
  # Filter to only rows with max threshold
  NMB_max <- data.frame()
  for (i in seq_len(nrow(max_thresholds))) {
    row_data <- NMB_combined %>%
      filter(
        Threshold == max_thresholds$Threshold[i],
        wtp == max_thresholds$wtp[i]
      )
    NMB_max <- bind_rows(NMB_max, row_data)
  }
  
  # Add readable WTP and FLQ labels
  NMB_max %>%
    mutate(
      wtp_real = case_when(
        wtp == 1 ~ 0.5,
        wtp == 2 ~ 1,
        wtp == 3 ~ 1.5,
        wtp == 4 ~ 2,
        wtp == 5 ~ 2.5,
        wtp == 6 ~ 3
      ),
      FLQ_Status_m = case_when(
        FLQ_Status == "FLQ Resistant" ~ "B. Among patients with TB resistant \n to rifampicin and FLQ",
        FLQ_Status == "FLQ Susceptible" ~ "C. Among patients with TB resistant \n to rifampicin but susceptible to FLQ",
        FLQ_Status == "All patients" ~ "A. Among all patients with TB \n resistant to rifampicin"
      ),
      Model = calibrated_label
    )
}


# 2. Summary function for avg NMB and CI
compute_avg_nmb <- function(df, wtp_val) {
  df %>%
    group_by(Threshold) %>%
    summarise(
      NMB = mean(NMB_SdTreat_DM),
      uciNMB = NMB + qt(0.975, df = length(NMB_SdTreat_DM) - 1) * sd(NMB_SdTreat_DM) / sqrt(length(NMB_SdTreat_DM)),
      lciNMB = NMB - qt(0.975, df = length(NMB_SdTreat_DM) - 1) * sd(NMB_SdTreat_DM) / sqrt(length(NMB_SdTreat_DM))
    ) %>%
    mutate(WTP = wtp_val)
}

#  Function that merges Personal Characteristics into the results of PIDEMs

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
  "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_LR_Augumented.csv"
moldova_data <- read.csv(data_path)
moldova_data$Pt_id = seq(1:dim(moldova_data)[1])

# Read bootstrapped data
Classification_PMDT_varwtp <- read_output_tolist_varyingwtp('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/', "PMDT_", "bootstrapping_samplesize200", 6)

Classification_PMDT_wtp2_ptchar = Classification_PMDT_varwtp$output_list$wtp_2 %>%
  mutate(Person_m = Person + 1) %>%
  left_join(moldova_data,
            by = c("Person_m" = "Pt_id"))

Classification_PMDT_wtp2_female = Classification_PMDT_wtp2_ptchar %>%
  filter(Sex_2 == 1)

Classification_PMDT_wtp2_female_avgNMB = compute_avg_nmb(Classification_PMDT_wtp2_female, 1)

ggplot(Classification_PMDT_wtp2_female_avgNMB, aes(x = Threshold, y = NMB)) +
  geom_line() +
  geom_ribbon(aes(ymin = lciNMB, ymax = uciNMB), alpha = 0.3, fill = "grey") +
  labs(x = "Classification threshold", y = "Change in NMB") +
  theme_minimal(base_size = 16) +
  theme(legend.position = "none")


Classification_PMDT_wtp2_male = Classification_PMDT_wtp2_ptchar %>%
  filter(Sex_2 == 0)

Classification_PMDT_wtp2_male_avgNMB = compute_avg_nmb(Classification_PMDT_wtp2_male, 1)

ggplot(Classification_PMDT_wtp2_male_avgNMB, aes(x = Threshold, y = NMB)) +
  geom_line() +
  geom_ribbon(aes(ymin = lciNMB, ymax = uciNMB), alpha = 0.3, fill = "grey") +
  labs(x = "Classification threshold", y = "Change in NMB") +
  theme_minimal(base_size = 16) +
  theme(legend.position = "none")

