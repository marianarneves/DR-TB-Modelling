# Load required libraries
library(pROC)
library(ggplot2)

# Load the new dataset
data_path <- "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_HM.csv"
moldova_data <- read.csv(data_path)

# Read predictions for consD201, consD205, and logistic regression
pred_consd201 <- read.csv('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/Bootstrap PM - optimism corrected/Main/Output/cons_D201/HM_MainPM_d2_01_platt_beta_compare_1000000runs.csv', header = TRUE)
pred_consd205 <- read.csv('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/Bootstrap PM - optimism corrected/Main/Output/cons_D205/HM_MainPM_d2_05_platt_beta_compare_1000000runs.csv', header = TRUE)
logreg <- read.csv('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/Bootstrap PM - optimism corrected/Tests/Logistic Regression/main_pred.csv', header = TRUE)

# Compute ROC curves for all models
roc_consd201 <- roc(pred_consd201$observed, pred_consd201$predicted_beta)
roc_consd205 <- roc(pred_consd205$observed, pred_consd205$predicted_beta)
roc_logreg <- roc(logreg$observed, logreg$predicted)

# Define custom colors
color_201 <- "#1f77b4"  # Blue for consD201
color_205 <- "#ff7f0e"  # Orange for consD205
color_logreg <- "#2ca02c"  # Green for logistic regression

# Plot ROC curves with custom colors
ggroc(list("D2 0.1" = roc_consd201, "D2 0.5" = roc_consd205, "Logistic Regression" = roc_logreg), aes = c("color")) +
  ggtitle("ROC Curves for D2 0.1, D2 0.5, and Logistic Regression") +
  geom_abline(linetype = "dashed") +  # Add diagonal line for reference
  scale_color_manual(values = c("D2 0.1" = color_201, "D2 0.5" = color_205, "Logistic Regression" = color_logreg)) +
  annotate("text", x = 0.3, y = 0.3, label = paste("AUC (D2_01):", round(auc(roc_consd201), 3)), color = color_201) +
  annotate("text", x = 0.3, y = 0.25, label = paste("AUC (D2_05):", round(auc(roc_consd205), 3)), color = color_205) +
  annotate("text", x = 0.3, y = 0.2, label = paste("AUC (LogReg):", round(auc(roc_logreg), 3)), color = color_logreg) +
  theme_minimal()

#Calibration


calibration_data= data.frame(platt_pred = pred_consd201$predicted_platt, beta_pred = pred_consd201$predicted_beta , moldova_data$FLQ_R) 

mean_actual_plat = NA
mean_actual_beta = NA
mean_platt_pred = NA
mean_beta_pred = NA

bin_breaks <- cut(seq(0.1, 1, by = 0.1), breaks = seq(0, 1, by = 0.1), include.lowest = TRUE)


for(i in 1:length(bin_breaks)){
  
  bin_data_plat = calibration_data %>%
    mutate(bin = cut(platt_pred, breaks = seq(0, 1, by = 0.1), include.lowest = TRUE)) %>%
    filter(bin ==bin_breaks[i]) %>%
    select(platt_pred, moldova_data.FLQ_R ) 
  
  bin_data_beta = calibration_data %>%
    mutate(bin = cut(beta_pred, breaks = seq(0, 1, by = 0.1), include.lowest = TRUE)) %>%
    filter(bin ==bin_breaks[i]) %>%
    select(beta_pred, moldova_data.FLQ_R )
  
  mean_actual_plat[i] = mean(bin_data_plat$moldova_data.FLQ_R)
  mean_actual_beta[i] = mean(bin_data_beta$moldova_data.FLQ_R)
  mean_platt_pred[i] = mean(bin_data_plat$platt_pred)
  mean_beta_pred[i]  = mean(bin_data_beta$beta_pred)
  
}

cal = data.frame(bin_breaks = bin_breaks, mean_actual_plat = mean_actual_plat, mean_platt_pred = mean_platt_pred, mean_actual_beta = mean_actual_beta, mean_beta_pred = mean_beta_pred)
calibration_plot = ggplot() +
  geom_abline(intercept = 0, slope = 1, linetype = "dashed", color = "#de2d26", linewidth = 0.8, aes(label = "Diagonal (y=x)")) +  # Neutral gray dashed diagonal line
  geom_line(data = cal, aes(y = mean_actual_plat, x = mean_platt_pred, color = "Platt Calibration", group = 1), linewidth = 0.8) +  # Medium blue
  geom_line(data = cal, aes(y = mean_actual_beta, x = mean_beta_pred, color = "Beta Calibration", group = 1), linewidth = 0.8) +  # Dark purple
  labs(title = "Calibration Plot: Original Prediction, Platt and Beta Calibration",
       x = "Observed",
       y = "Predicted",
       color = "Type") +
  scale_color_manual(values = c("Platt Calibration" = "#2171b5",  # Medium blue
                                "Beta Calibration" = "#fdae6b",   # Dark purple
                                "Original Prediction" = "#238b45")) +  # Dark green # Dark green
  guides(color = guide_legend(title = NULL)) +  # Remove the legend title
  theme_minimal() +
  xlim(0, 1) +  # Set x-axis from 0 to 1
  ylim(0, 1) +  # Set y-axis from 0 to 1
  theme(legend.position = "bottom",
        plot.background = element_rect(fill = "white", color = NA),  # White plot background
        panel.background = element_rect(fill = "white", color = NA), # White panel background
        panel.grid = element_line(color = "gray90"),                 # Light gray grid
        plot.title = element_text(size = 16, face = "bold"),         # Increase title text size
        axis.title = element_text(size = 16),                        # Increase axis title text size
        axis.text = element_text(size = 16),                         # Increase axis labels text size
        legend.text = element_text(size = 16),                       # Increase legend text size
        legend.title = element_text(size = 16))                      # Increase legend title text size


