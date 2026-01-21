library(dplyr)
library(ggplot2)

setwd('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/Optimism Corrected/')

# Load the new dataset
data_path <-
  "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_LR_Augumented.csv"
moldova_data <- read.csv(data_path)
moldova_data$Pt_id = seq(1:dim(moldova_data)[1])

# Read predictions for logistic regression
pred_LR <- read.csv('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/Optimism Corrected/LR_MainPM_platt_beta_compare.csv')

library(dplyr)

# Step 1: Prepare calibration data
calibration_data <- data.frame(
  platt_pred = pred_LR$predicted_platt_mainpred,
  beta_pred = pred_LR$predicted_beta_mainpred,
  original_pred = pred_LR$predicted_original_mainpred,
  outcome = moldova_data$FLQ_R
)

bins <- cut(seq(0.01, 1, by = 0.1), breaks = seq(0, 1, by = 0.1), include.lowest = TRUE)

# Initialize vectors
mean_actual_plat <- mean_actual_beta <- mean_actual_original <- rep(NA, length(bins))
mean_platt_pred <- mean_beta_pred <- mean_original_pred <- rep(NA, length(bins))
bin_count <- rep(0, length(bins))

# Step 2: Bin data and compute means
for(i in 1:length(bins)) {
  bin_data <- calibration_data %>%
    mutate(bin = cut(platt_pred, breaks = seq(0, 1, by = 0.1), include.lowest = TRUE))
  
  # Select each bin
  bin_data_plat <- bin_data %>% filter(bin == bins[i]) %>% select(platt_pred, outcome)
  bin_data_beta <- calibration_data %>%
    mutate(bin = cut(beta_pred, breaks = seq(0, 1, by = 0.1), include.lowest = TRUE)) %>%
    filter(bin == bins[i]) %>% select(beta_pred, outcome)
  bin_data_original <- calibration_data %>%
    mutate(bin = cut(original_pred, breaks = seq(0, 1, by = 0.1), include.lowest = TRUE)) %>%
    filter(bin == bins[i]) %>% select(original_pred, outcome)
  
  # Means per bin
  mean_actual_plat[i] <- mean(bin_data_plat$outcome, na.rm = TRUE)
  mean_platt_pred[i] <- mean(bin_data_plat$platt_pred, na.rm = TRUE)
  mean_actual_beta[i] <- mean(bin_data_beta$outcome, na.rm = TRUE)
  mean_beta_pred[i] <- mean(bin_data_beta$beta_pred, na.rm = TRUE)
  mean_actual_original[i] <- mean(bin_data_original$outcome, na.rm = TRUE)
  mean_original_pred[i] <- mean(bin_data_original$original_pred, na.rm = TRUE)
  
  # Bin count for ECE
  bin_count[i] <- nrow(bin_data_plat)
}

cal = data.frame(bins = bins, mean_actual_plat = mean_actual_plat, mean_platt_pred = mean_platt_pred, mean_actual_beta = mean_actual_beta, mean_beta_pred = mean_beta_pred, mean_actual_original = mean_actual_original, mean_original_pred = mean_original_pred)

# Total for weighting ECE
total_count <- sum(bin_count)

# Step 3: Calibration metrics

# Brier score
brier_platt <- mean((calibration_data$platt_pred - calibration_data$outcome)^2)
brier_beta <- mean((calibration_data$beta_pred - calibration_data$outcome)^2)
brier_original <- mean((calibration_data$original_pred - calibration_data$outcome)^2)

# ECE function
ece <- function(mean_pred, mean_actual, bin_counts, total_count) {
  weights <- bin_counts / total_count
  sum(weights * abs(mean_pred - mean_actual), na.rm = TRUE)
}

ece_platt <- ece(mean_platt_pred, mean_actual_plat, bin_count, total_count)
ece_beta <- ece(mean_beta_pred, mean_actual_beta, bin_count, total_count)
ece_original <- ece(mean_original_pred, mean_actual_original, bin_count, total_count)

# MCE
mce_platt <- max(abs(mean_platt_pred - mean_actual_plat), na.rm = TRUE)
mce_beta <- max(abs(mean_beta_pred - mean_actual_beta), na.rm = TRUE)
mce_original <- max(abs(mean_original_pred - mean_actual_original), na.rm = TRUE)

# Calibration-in-the-large
cal_in_large_platt <- mean(calibration_data$platt_pred) - mean(calibration_data$outcome)
cal_in_large_beta <- mean(calibration_data$beta_pred) - mean(calibration_data$outcome)
cal_in_large_original <- mean(calibration_data$original_pred) - mean(calibration_data$outcome)

# Step 4: Bootstrap CI for Brier and Calibration-in-the-large
bootstrap_calibration_metrics <- function(pred, actual, n_boot = 1000) {
  set.seed(123)
  n <- length(pred)
  brier_vec <- cal_large_vec <- numeric(n_boot)
  
  for (i in 1:n_boot) {
    idx <- sample(1:n, replace = TRUE)
    pred_boot <- pred[idx]
    actual_boot <- actual[idx]
    
    brier_vec[i] <- mean((pred_boot - actual_boot)^2)
    cal_large_vec[i] <- mean(pred_boot) - mean(actual_boot)
  }
  
  list(
    brier_ci = quantile(brier_vec, c(0.025, 0.975)),
    cal_large_ci = quantile(cal_large_vec, c(0.025, 0.975))
  )
}

boot_platt <- bootstrap_calibration_metrics(calibration_data$platt_pred, calibration_data$outcome)
boot_beta <- bootstrap_calibration_metrics(calibration_data$beta_pred, calibration_data$outcome)
boot_original <- bootstrap_calibration_metrics(calibration_data$original_pred, calibration_data$outcome)

# Step 5: Output summary table
results <- data.frame(
  Method = c("Platt", "Beta", "Original"),
  Brier = c(brier_platt, brier_beta, brier_original),
  Brier_Lower_CI = c(boot_platt$brier_ci[1], boot_beta$brier_ci[1], boot_original$brier_ci[1]),
  Brier_Upper_CI = c(boot_platt$brier_ci[2], boot_beta$brier_ci[2], boot_original$brier_ci[2]),
  ECE = c(ece_platt, ece_beta, ece_original),
  MCE = c(mce_platt, mce_beta, mce_original),
  CalInLarge = c(cal_in_large_platt, cal_in_large_beta, cal_in_large_original),
  CalInLarge_Lower_CI = c(boot_platt$cal_large_ci[1], boot_beta$cal_large_ci[1], boot_original$cal_large_ci[1]),
  CalInLarge_Upper_CI = c(boot_platt$cal_large_ci[2], boot_beta$cal_large_ci[2], boot_original$cal_large_ci[2])
)

print(results)

#---------- Calibration plot

calibration_plot = ggplot() +
  geom_abline(intercept = 0, slope = 1, linetype = "dashed", color = "#e41a1c", linewidth = 0.8) +
  geom_smooth(data = cal, aes(y = mean_actual_original, x = mean_original_pred,
                              color = factor("Original", levels = c("Original", "Platt", "Beta"))),
              method = "loess", span = 1, se = FALSE, linewidth = 0.8) +
  geom_smooth(data = cal, aes(y = mean_actual_plat, x = mean_platt_pred,
                              color = factor("Platt", levels = c("Original", "Platt", "Beta"))),
              method = "loess", span = 1, se = FALSE, linewidth = 0.8) +
  geom_smooth(data = cal, aes(y = mean_actual_beta, x = mean_beta_pred,
                              color = factor("Beta", levels = c("Original", "Platt", "Beta"))),
              method = "loess", span = 1, se = FALSE, linewidth = 0.8) +labs(
    y = "Observed Proportion",
    x = "Predicted Risk",
    color = "Model Calibration"
  ) +
  scale_color_manual(
    values = c(
      "Platt" = "#1b9e77",  
      "Beta" = "#fdae61",   
      "Original" = "#7570b3"
    ),
    labels = c(
      "Platt" = paste0("Platt Calibration (Brier Score = ", round(brier_platt, 3), ", ECE = ", round(ece_platt, 3), ")"),
      "Beta" = paste0("Beta Calibration (Brier Score = ", round(brier_beta, 3), ", ECE = ", round(ece_beta, 3), ")"),
      "Original" = paste0("Original (Brier Score = ", round(brier_original, 3), ", ECE = ", round(ece_original, 3), ")")
    )
  ) +
  guides(color = guide_legend(title = NULL, nrow = 3)) +
  theme_minimal() +
  xlim(0, 1) +
  ylim(0, 1) +
  theme(
    legend.position = "bottom",
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA),
    panel.grid = element_line(color = "gray90"),
    plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 16),
    axis.text = element_text(size = 16),
    legend.text = element_text(size = 14),
    legend.title = element_text(size = 16)
  )


ggsave("Calibration_Plot_DR_TB.png", plot = calibration_plot, width = 8, height = 6)
