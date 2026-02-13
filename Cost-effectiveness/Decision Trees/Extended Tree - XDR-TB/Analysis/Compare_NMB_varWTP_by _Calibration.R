library(readxl)
library(dplyr)
library(tidyr)
library(ggplot2)
library(gridExtra)
library(patchwork)
library(purrr)
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Analysis/DR_TB_PMDT_Analysis_Functions.R')

setwd("/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Results Comparison/")

# only save if a variable 'should_save' is TRUE
should_save <- FALSE  # change to TRUE to allow saving

if (should_save) {
  ggsave("myplot.png", plot = p, width = 6, height = 4)
} else {
  message("ggsave skipped because condition not met.")
}


# === Function to process NMB results ===
process_input_data <- function(file_path, output_loc, calibrated_label) {
  data <- read_xlsx(file_path)
  varwtp <- read_output_tolist_varyingwtp(output_loc, "PMDT_", "bootstrapping_samplesize200", 6)
  
  # Overall average NMB
  NMB_avg_overall <- varwtp$output_df %>%
    compute_avg_nmb_ci(NMB_SdTreat_DM, c(wtp, Threshold)) %>%
    mutate(FLQ_Status = "All patients")
  
  # Max threshold by WTP
  max_thresholds <- NMB_avg_overall %>%
    slice_max(NMB_avg, with_ties = FALSE) %>%
    pull(Threshold) %>%
    as.data.frame() %>%
    mutate(wtp = 1:6)
  colnames(max_thresholds) <- c("Threshold", "wtp")
  
  # NMB by FLQ status
  NMB_avg_FLQ <- varwtp$output_df %>%
    compute_avg_nmb_ci(NMB_SdTreat_DM, c(wtp, FLQ_Status, Threshold))
  
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


                                                                    #########################
                                                                    # Varying WTP - Max NMB #
                                                                    #########################

##########
# PIDEMc #
##########

# === Calibrated Prediction ===
Classification_PMDT_NMB_avg_max <- process_input_data(
  file_path = "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx",
  output_loc = "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/Input_V10/",
  calibrated_label = "Classification method - Calibrated"
)

# === Uncalibrated Prediction ===
Classification_PMDT_nocal_NMB_avg_max <- process_input_data(
  file_path = "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM Bootstrap/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx",
  output_loc = "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM Bootstrap/Input_V10/",
  calibrated_label = "Classification method - Not Calibrated"
)


# === Combine Results and Plot ===
Classification_NMB_combined <- bind_rows(Classification_PMDT_NMB_avg_max, Classification_PMDT_nocal_NMB_avg_max)

plot_NMB_wtp_classificationmethod <- ggplot(Classification_NMB_combined, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line(size = 1.1) +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Model), alpha = 0.4) +
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's GDP per capita", 
    y = "Change in NMB", 
    color = "DT Input",
    fill = "DT Input"
  ) +
  facet_grid(. ~ FLQ_Status_m, scales = "free_y") +
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    legend.text = element_text(size = 18),
    strip.text = element_text(face = "bold")
  ) +
  ggtitle("Incremental NMB vs standard of care with 95% CI using classification-based method")

# === Save Plot ===
ggsave(
  filename = "plot_NMB_wtp_classificationmethod.png",
  plot = plot_NMB_wtp_classificationmethod,
  width = 16, height = 5
)

########### Plot Average NMB only - with CI ########### 
NMB_panel_A <- Classification_NMB_combined %>%
  filter(FLQ_Status_m == "A. Among all patients with TB \n resistant to rifampicin")

NMB_panel_A$Model <- factor(NMB_panel_A$Model, levels = c(
  "Probability-based method", "Classification-based method"
))

plot_NMB_wtp_panel_A <- ggplot(NMB_panel_A, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line() +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Model), alpha = 0.2, color = NA) +
  geom_hline(yintercept = 0, color = "black") +
  geom_vline(xintercept = 0.5, color = "black") +
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's gross domestic product per capita", 
    y = "Average change in NMB\nper patient with RR-TB", 
    color = "Method", 
    fill = "Method"
  ) +
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    legend.text = element_text(size = 18),
    panel.background = element_blank(),
    plot.background = element_blank(),
    panel.grid.major = element_line(color = "grey80"),
    panel.grid.minor = element_line(color = "grey90"),
    axis.line = element_blank()
  ) +
  ggtitle("Figure. Gain in NMB for varying willingness-to-pay thresholds when proposed methods are used to inform\ntreatment regimens compared to using the standard FLQ-containing regimen for all patients with RR-TB.\nThe shaded regions show the 95% confidence intervals.")

ggsave(filename = "plot_aveeageNMB_wtp_PIDEMc.png", plot = plot_NMB_wtp_panel_A, width = 16, height = 5)

########### Plot Average NMB only - no CI ########### 
plot_NMB_wtp_panel_A_noCI <- ggplot(NMB_panel_A, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line(size = 1.1) +
  geom_hline(yintercept = 0, color = "black") +
  geom_vline(xintercept = 0.5, color = "black") +
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's gross domestic product per capita", 
    y = "Average change in NMB\nper patient with RR-TB", 
    color = "Method", 
    fill = "Method"
  ) +
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    legend.text = element_text(size = 18),
    panel.background = element_blank(),
    plot.background = element_blank(),
    panel.grid.major = element_line(color = "grey80"),
    panel.grid.minor = element_line(color = "grey90"),
    axis.line = element_blank()
  ) +
  ggtitle("Figure. Gain in NMB for varying willingness-to-pay thresholds when proposed methods are used to inform\ntreatment regimens compared to using the standard FLQ-containing regimen for all patients with RR-TB.\nThe shaded regions show the 95% confidence intervals.")

ggsave(filename = "plot_aveeageNMB_wtp_PIDEMc_noCI.png", plot = plot_NMB_wtp_panel_A_noCI, width = 16, height = 5)


##########
# PIDEMp #
##########

# === Calibrated Prediction ===
Prediction_PMDT_cal <- process_input_data(
  file_path = "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM input Only/PMDT_wtp2bootstrapping_samplesize200.xlsx",
  output_loc = "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM input Only/",
  calibrated_label = "Prediction method - Calibrated"
)

# === Uncalibrated Prediction ===
Prediction_PMDT_nocal <- process_input_data(
  file_path = "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM input Only/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx",
  output_loc = "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM input Only/Input_V10/",
  calibrated_label = "Prediction method - Not Calibrated"
)

# === Combine Results and Plot ===
Prediction_NMB_combined <- bind_rows(Prediction_PMDT_cal, Prediction_PMDT_nocal)

plot_NMB_wtp_predictionmethod <- ggplot(Prediction_NMB_combined, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line(size = 1.1) +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Model), alpha = 0.4) +
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's GDP per capita", 
    y = "Change in NMB", 
    color = "DT Input",
    fill = "DT Input"
  ) +
  facet_grid(. ~ FLQ_Status_m, scales = "free_y") +
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    legend.text = element_text(size = 18),
    strip.text = element_text(face = "bold")
  ) +
  ggtitle("Incremental NMB vs standard of care with 95% CI using prediction-based method")

# === Save Plot ===
ggsave(
  filename = "plot_NMB_wtp_predictionmethod.png",
  plot = plot_NMB_wtp_predictionmethod,
  width = 16, height = 5
)

########### Plot Average NMB only - with CI ########### 
Prediction_NMB_panel_A <- Prediction_NMB_combined %>%
  filter(FLQ_Status_m == "A. Among all patients with TB \n resistant to rifampicin", wtp_real <=1 )

plot_Prediction_NMB_wtp_panel_A <- ggplot(Prediction_NMB_panel_A, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line() +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Model), alpha = 0.2, color = NA) +
  geom_hline(yintercept = 0, color = "black") +
  geom_vline(xintercept = 0.5, color = "black") +
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's gross domestic product per capita", 
    y = "Average change in NMB\nper patient with RR-TB", 
    color = "Method", 
    fill = "Method"
  ) +
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    legend.text = element_text(size = 18),
    panel.background = element_blank(),
    plot.background = element_blank(),
    panel.grid.major = element_line(color = "grey80"),
    panel.grid.minor = element_line(color = "grey90"),
    axis.line = element_blank()
  ) +
  ggtitle("Figure. Gain in NMB for varying willingness-to-pay thresholds when proposed methods are used to inform\ntreatment regimens compared to using the standard FLQ-containing regimen for all patients with RR-TB.\nThe shaded regions show the 95% confidence intervals.")


                                                                      ######################################
                                                                      # Classification - NMB by threshold  #
                                                                      ######################################


###########
# PIDEMc  #
###########

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


# Read the data
Classification_PMDT <- read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx')

# Read bootstrapped data
Classification_PMDT_varwtp <- read_output_tolist_varyingwtp('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/Input_V10/', "PMDT_", "bootstrapping_samplesize200", 6)

# Split data by WTP and assign to global environment
walk2(names(split(Classification_PMDT_varwtp$output_df, Classification_PMDT_varwtp$output_df$wtp)), split(Classification_PMDT_varwtp$output_df, Classification_PMDT_varwtp$output_df$wtp), ~ assign(paste0("PMDT_sampled_1000_", .x, "wtp"), .y, envir = .GlobalEnv))

# 3. Process a list of WTP datasets and compute summaries
Classification_wtp_datasets <- list(
  "1" = PMDT_sampled_1000_2wtp,
  "2" = PMDT_sampled_1000_4wtp,
  "3" = PMDT_sampled_1000_6wtp
)

Classification_wtp_avgs <- imap(Classification_wtp_datasets, compute_avg_nmb)
names(Classification_wtp_avgs) <- paste0("PMDT_sampled_1000_", names(Classification_wtp_avgs), "wtp_avg")
list2env(Classification_wtp_avgs, envir = .GlobalEnv)

# 4. Find max thresholds for each WTP
Classification_max_thresholds <- map_dbl(Classification_wtp_avgs, ~ .x %>% filter(NMB == max(NMB, na.rm = TRUE)) %>% pull(Threshold))

# 5. Plot for WTP = 1
Classification_avg_df <- Classification_wtp_avgs$PMDT_sampled_1000_1wtp_avg
Classification_min_threshold <- min(Classification_avg_df$Threshold[!is.na(Classification_avg_df$NMB)])
Classification_max_threshold <- max(Classification_avg_df$Threshold[!is.na(Classification_avg_df$NMB)])

# 6. Combined WTP comparison
Classification_PMDT_sampled_1000_wtpcompare <- bind_rows(Classification_wtp_avgs) %>%
  mutate(WTP_m = recode_factor(as.character(WTP),
                               "1" = "WTP = 1 GDP",
                               "2" = "WTP = 2 GDP",
                               "3" = "WTP = 3 GDP"))

Classification_PMDT_sampled_1000_wtpcompare_adj <- Classification_PMDT_sampled_1000_wtpcompare %>%
  bind_rows(
    Classification_PMDT_sampled_1000_wtpcompare %>% group_by(WTP) %>% slice_max(Threshold) %>% mutate(Threshold = 1),
    Classification_PMDT_sampled_1000_wtpcompare %>% group_by(WTP) %>% slice_min(Threshold) %>% mutate(Threshold = 0)
  )

Classification_max_points <- Classification_PMDT_sampled_1000_wtpcompare_adj %>%
  group_by(WTP_m) %>%
  slice_max(NMB, n = 1)

Classification_plot_NMB_wtp_calibrated <- ggplot(Classification_PMDT_sampled_1000_wtpcompare_adj, aes(x = Threshold, y = NMB, fill = WTP)) +
  geom_line() +
  geom_ribbon(aes(ymin = lciNMB, ymax = uciNMB), alpha = 0.3, fill = "grey") +
  geom_hline(data = Classification_max_points, aes(yintercept = NMB), color = "blue", linetype = "dashed") +
  geom_text(data = Classification_max_points, aes(x = Threshold + 0.025, y = NMB + 100, label = paste0("NMB = ", round(NMB, 0))), hjust = 0, size = 5, color = "blue") +
  geom_vline(data = Classification_max_points, aes(xintercept = Threshold), color = "red", linetype = "dashed") +
  geom_text(data = Classification_max_points, aes(x = Threshold - 0.35, y = NMB - 100, label = paste0("t = ", round(Threshold, 3))), hjust = 0, size = 5, color = "red") +
  facet_grid(. ~ WTP_m, scales = "free_y") +
  labs(x = "Classification threshold", y = "Change in NMB") +
  theme_minimal(base_size = 16) +
  theme(legend.position = "none")

ggsave("Classification_plot_NMB_wtp_calibrated.png", plot = Classification_plot_NMB_wtp_calibrated, width = 14, height = 6)

###################
# No Calibration  #
###################

# Read the data
Classification_nocal_PMDT <- read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM Bootstrap/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx')

# Read bootstrapped data
Classification_nocal_PMDT_varwtp <- read_output_tolist_varyingwtp('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM Bootstrap/Input_V10/', "PMDT_", "bootstrapping_samplesize200", 6)

# Split data by WTP and assign to global environment
walk2(names(split(Classification_nocal_PMDT_varwtp$output_df, Classification_nocal_PMDT_varwtp$output_df$wtp)), split(Classification_nocal_PMDT_varwtp$output_df, Classification_nocal_PMDT_varwtp$output_df$wtp), ~ assign(paste0("PMDT_sampled_1000_", .x, "wtp_nocal"), .y, envir = .GlobalEnv))

# 3. Process a list of WTP datasets and compute summaries
Classification_nocal_wtp_datasets <- list(
  "1" = PMDT_sampled_1000_2wtp_nocal,
  "2" = PMDT_sampled_1000_4wtp_nocal,
  "3" = PMDT_sampled_1000_6wtp_nocal
)

Classification_nocal_wtp_avgs <- imap(Classification_nocal_wtp_datasets, compute_avg_nmb)
names(Classification_nocal_wtp_avgs) <- paste0("PMDT_sampled_1000_", names(Classification_nocal_wtp_avgs), "wtp_avg")
list2env(Classification_nocal_wtp_avgs, envir = .GlobalEnv)

# 4. Find max thresholds for each WTP
Classification_nocal_max_thresholds <- map_dbl(Classification_nocal_wtp_avgs, ~ .x %>% filter(NMB == max(NMB, na.rm = TRUE)) %>% pull(Threshold))

# 5. Plot for WTP = 1
Classification_nocal_avg_df <- Classification_nocal_wtp_avgs$PMDT_sampled_1000_1wtp_avg
Classification_nocal_min_threshold <- min(Classification_nocal_avg_df$Threshold[!is.na(Classification_nocal_avg_df$NMB)])
Classification_nocal_max_threshold <- max(Classification_nocal_avg_df$Threshold[!is.na(Classification_nocal_avg_df$NMB)])

# 6. Combined WTP comparison
Classification_nocal_PMDT_sampled_1000_wtpcompare <- bind_rows(Classification_nocal_wtp_avgs) %>%
  mutate(WTP_m = recode_factor(as.character(WTP),
                               "1" = "WTP = 1 GDP",
                               "2" = "WTP = 2 GDP",
                               "3" = "WTP = 3 GDP"))

Classification_nocal_PMDT_sampled_1000_wtpcompare_adj <- Classification_nocal_PMDT_sampled_1000_wtpcompare %>%
  bind_rows(
    Classification_nocal_PMDT_sampled_1000_wtpcompare %>% group_by(WTP) %>% slice_max(Threshold) %>% mutate(Threshold = 1),
    Classification_nocal_PMDT_sampled_1000_wtpcompare %>% group_by(WTP) %>% slice_min(Threshold) %>% mutate(Threshold = 0)
  )

Classification_nocal_max_points <- Classification_nocal_PMDT_sampled_1000_wtpcompare_adj %>%
  group_by(WTP_m) %>%
  slice_max(NMB, n = 1)

Classification_nocal_plot_NMB_wtp <- ggplot(Classification_nocal_PMDT_sampled_1000_wtpcompare_adj, aes(x = Threshold, y = NMB, fill = WTP)) +
  geom_line() +
  geom_ribbon(aes(ymin = lciNMB, ymax = uciNMB), alpha = 0.3, fill = "grey") +
  geom_hline(data = Classification_nocal_max_points, aes(yintercept = NMB), color = "blue", linetype = "dashed") +
  geom_text(data = Classification_nocal_max_points, aes(x = Threshold + 0.025, y = NMB + 100, label = paste0("NMB = ", round(NMB, 0))), hjust = 0, size = 5, color = "blue") +
  geom_vline(data = Classification_nocal_max_points, aes(xintercept = Threshold), color = "red", linetype = "dashed") +
  geom_text(data = Classification_nocal_max_points, aes(x = Threshold - 0.35, y = NMB - 100, label = paste0("t = ", round(Threshold, 3))), hjust = 0, size = 5, color = "red") +
  facet_grid(. ~ WTP_m, scales = "free_y") +
  labs(x = "Classification threshold", y = "Change in NMB") +
  theme_minimal(base_size = 16) +
  theme(legend.position = "none")

ggsave("Classification_plot_NMB_wtp_notcalibrated.png", plot = Classification_nocal_plot_NMB_wtp, width = 14, height = 6)

                                                  
                                        #############################################################################
                                        # Classification - NMB by threshold and Proportion of alternative treatment #
                                        #############################################################################


###############################
# NMB by threshold - WTP = 1  #
###############################

Classification_PMDT_sampled_1000_wtp1 <- Classification_PMDT_sampled_1000_wtpcompare %>%
  filter(WTP == 1)

Classification_PMDT_sampled_1000_wtp1_adj <- Classification_PMDT_sampled_1000_wtp1 %>%
  bind_rows(
    Classification_PMDT_sampled_1000_wtp1 %>% slice_max(Threshold) %>% mutate(Threshold = 1),
    Classification_PMDT_sampled_1000_wtp1 %>% slice_min(Threshold) %>% mutate(Threshold = 0)
  )


Classification_max_points_wtp1 <- Classification_PMDT_sampled_1000_wtp1_adj %>%
  slice_max(NMB, n = 1)

Classification_plot_NMB_wtp_1calibrated <- ggplot(Classification_PMDT_sampled_1000_wtp1_adj, aes(x = Threshold, y = NMB)) +
  geom_line() +
  geom_ribbon(aes(ymin = lciNMB, ymax = uciNMB), alpha = 0.3, fill = "grey") +
  geom_hline(data = Classification_max_points_wtp1, aes(yintercept = NMB), color = "blue", linetype = "dashed") +
  geom_text(data = Classification_max_points_wtp1, aes(x = Threshold - 0.38, y = NMB - 50, label = paste0("NMB = ", round(NMB, 0))), hjust = 0, size = 5, color = "blue") +
  geom_vline(data = Classification_max_points_wtp1, aes(xintercept = Threshold), color = "red", linetype = "dashed") +
  geom_text(data = Classification_max_points_wtp1, aes(x = Threshold + 0.025, y = NMB + 50, label = paste0("t = ", round(Threshold, 3))), hjust = 0, size = 5, color = "red") +
  labs(x = "Classification Threshold", y = "Gain in NMB per patient with RR-TB") +
  scale_y_continuous(limits = c(-300, 1050), breaks = seq(-300, 1050, by = 150)) +
  scale_x_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.1)) +
  theme_minimal(base_size = 16) +
  theme(
    legend.position = "none", 
    text = element_text(size = 18),
    legend.text = element_text(size = 18),
    panel.background = element_blank(),  # Remove panel background color
    plot.background = element_blank(),   # Remove plot background color
    panel.grid.major = element_line(color = "grey80"),  # Lighter major grid lines
    panel.grid.minor = element_line(color = "grey90"),  # Even lighter minor grid lines
    axis.line = element_blank()  # Remove default axis lines (handled by hline/vline)
  ) +
  geom_hline(yintercept = 0, color = "grey40")  # Add a dashed line at y=0



##############################
# Porportion prescribed Clz  #
##############################


Alt_Treat_prop <- PMDT_sampled_1000_2wtp %>%
  group_by(Threshold) %>%
  summarise(
    Clz_prop = mean(Opt_Treat == "DLM"),
    FLQ_Status = "All Patients",
    .groups = "drop"
  ) %>%
  bind_rows(
    PMDT_sampled_1000_2wtp %>%
      group_by(Threshold, FLQ_Status) %>%
      summarise(
        Clz_prop = mean(Opt_Treat == "DLM"),
        .groups = "drop"
      )
  )


# Define a custom blue-toned color palette
custom_blue_colors <- c(
  "All Patients" = "#004c6d",   # Medium blue
  "FLQ Resistant" = "#6baed6",  # Light blue
  "FLQ Susceptible" = "#3182bd"   # Darker blue
)

# Plot the results with custom blue colors and y-axis ticks by 0.05
Cfz_presc_prop_byFLQstatus_plot <- ggplot(Alt_Treat_prop, aes(x = Threshold, y = Clz_prop, color = FLQ_Status, group = FLQ_Status)) +
  geom_line(size = 0.7) +
  geom_point(size = 0.7) +
  scale_color_manual(values = custom_blue_colors) +  # Use custom blue colors
  labs(
    x = "Classification Threshold",
    y = "Proportion of patients\nprescribed Cfz",
    color = "FLQ Status"
  ) +
  scale_y_continuous(breaks = seq(0, 0.40, by = 0.05), limits = c(0, 0.40)) +  # Set y-axis ticks by 0.05
  scale_x_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.1)) + # Set x-axis limits and breaks
  theme_minimal() +
  guides(color = guide_legend(nrow = 2, title = NULL))+
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    legend.text = element_text(size = 18),
    panel.background = element_blank(),  # Remove panel background color
    plot.background = element_blank(),   # Remove plot background color
    panel.grid.major = element_line(color = "grey80"),  # Lighter major grid lines
    panel.grid.minor = element_line(color = "grey90"),  # Even lighter minor grid lines
    axis.line = element_blank()  # Remove default axis lines (handled by hline/vline)
  )

##################
# Combined Plot  #
##################

# Add pseudo-facet-style titles with plot_annotation
Classification_plot_NMB_wtp_1calibrated <- Classification_plot_NMB_wtp_1calibrated + 
  labs(title = "A. Gain in NMB per Patient\nwith RR-TB") +
  theme(
    plot.title = element_text(size = 18, hjust = 0.5),
    plot.margin = margin(10, 10, 10, 10)
  )+
  ylab(NULL) 

Cfz_presc_prop_byFLQstatus_plot <- Cfz_presc_prop_byFLQstatus_plot + 
  labs(title = "B. Proportion of patients prescribed\nthe BPaLC regimen") +
  theme(
    plot.title = element_text(size = 18, hjust = 0.5),
    plot.margin = margin(10, 10, 10, 10)
  )+
  ylab(NULL) 

# Combine side by side
Classification_plot_NMB_Prop_Clz <- Classification_plot_NMB_wtp_1calibrated + Cfz_presc_prop_byFLQstatus_plot + 
  plot_layout(ncol = 2)

ggsave("Classification_plot_NMB_Prop_Clz.png", plot = Classification_plot_NMB_Prop_Clz, width = 10, height = 6)



