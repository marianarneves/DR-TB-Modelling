library(readxl)
library(dplyr)
library(tidyr)
library(ggplot2)
library(gridExtra)
library(patchwork)
library(purrr)
library(gganimate)

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


# Read bootstrapped data
Classification_PMDT_varwtp <- read_output_tolist_varyingwtp('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/', "PMDT_", "bootstrapping_samplesize200", 6)

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
Classification_max_thresholds <- Classification_wtp_avgs$PMDT_sampled_1000_1wtp_avg %>% filter(NMB == max(NMB, na.rm = TRUE)) %>% pull(Threshold)

# 5. Plot for WTP = 1
Classification_avg_df <- Classification_wtp_avgs$PMDT_sampled_1000_1wtp_avg
Classification_min_threshold <- min(Classification_avg_df$Threshold[!is.na(Classification_avg_df$NMB)])
Classification_max_threshold <- max(Classification_avg_df$Threshold[!is.na(Classification_avg_df$NMB)])

Classification_avg_df_adj <- Classification_avg_df %>%
  bind_rows(
    Classification_wtp_avgs$PMDT_sampled_1000_1wtp_avg %>%  slice_max(Threshold) %>% mutate(Threshold = 1),
    Classification_wtp_avgs$PMDT_sampled_1000_1wtp_avg %>%  slice_min(Threshold) %>% mutate(Threshold = 0)
  )

# Select every 10th element from the Threshold vector
selected_thresholds <- c(Classification_avg_df_adj$Threshold[seq(1, 439, by = 20)],
                         Classification_avg_df_adj$Threshold[seq(440, length(Classification_avg_df_adj$Threshold), by = 2)])

# Filter the data to include only the selected thresholds
Classification_max_points <- Classification_avg_df_adj %>%
  filter(Threshold %in% selected_thresholds)

base_plot <- ggplot(Classification_avg_df_adj, aes(x = Threshold, y = NMB)) +
  geom_line() +
  geom_ribbon(aes(ymin = lciNMB, ymax = uciNMB), alpha = 0.3, fill = "grey") +
  labs(x = "Classification threshold", y = "Change in NMB per patient") +
  scale_y_continuous(limits = c(-500, 1000), breaks = seq(-500, 1000, by = 100)) +
  theme_minimal(base_size = 16) + 
  theme(
  text = element_text(size = 18),
  legend.text = element_text(size = 18))+
  theme(legend.position = "none")

# Assuming Classification_max_points contains the maximum NMB and corresponding threshold
max_points <- Classification_max_points %>%
  mutate(frame = row_number()) %>%
  select(Threshold, NMB, frame)

# Create a data frame for the blue and red lines
blue_red_lines <- max_points %>%
  pivot_longer(cols = c(Threshold, NMB), names_to = "line_type", values_to = "value") %>%
  mutate(line_color = case_when(
    line_type == "Threshold" ~ "blue",
    line_type == "NMB" ~ "red"
  ))

animated_plot <- base_plot +
  geom_hline(data = blue_red_lines %>% filter(line_type == "NMB"), aes(yintercept = value, color = line_color), linetype = "dashed") +
  geom_text(data = blue_red_lines %>% filter(line_type == "NMB"), aes(x = max(Classification_avg_df_adj$Threshold, na.rm = TRUE) , y = value , label = paste0("NMB = ", round(value, 0))), hjust = +1.5, size = 5, color = "blue") +
  geom_vline(data = blue_red_lines %>% filter(line_type == "Threshold"), aes(xintercept = value, color = line_color), linetype = "dashed") +
  geom_text(data = blue_red_lines %>% filter(line_type == "Threshold"), aes(x = value, y = max(Classification_avg_df_adj$NMB, na.rm = TRUE) , label = paste0("t = ", round(value, 3))), hjust = -0.2, size = 5, color = "red") +
  transition_manual(frames = frame)

animate(animated_plot, fps = 10, duration = 5, width = 800, height = 600)

anim_save("Change_NMB_Dynamic_plot.gif", animation = animated_plot)