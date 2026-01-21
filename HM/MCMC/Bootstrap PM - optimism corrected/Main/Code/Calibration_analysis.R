# Read predictions for consD201, consD205, and logistic regression
pred_consd201 <- read.csv('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/Bootstrap PM - optimism corrected/Main/Output/cons_D201/HM_MainPM_d2_01_platt_beta_compare_1000000runs.csv', header = TRUE)


# Fit logistic regression to recalibrate
platt_model <- glm(moldova_data$FLQ_R ~ y_prob, family = binomial(link = "logit"))
# Get recalibrated probabilities
recalibrated_pred <- predict(platt_model, newdata = data.frame(y_prob), type = "response")

#### Using a beta calibration curve ####
bc <- beta_calibration(y_prob, moldova_data$FLQ_R, parameters = "abm")
beta = beta_predict(y_prob, bc)


calibration_data= data.frame(platt_pred = recalibrated_pred, beta_pred = beta , original_pred = y_prob, moldova_data$FLQ_R) 

mean_actual_plat = NA
mean_actual_beta = NA
mean_actual_original = NA
mean_platt_pred = NA
mean_beta_pred = NA
mean_original_pred = NA

for(i in 1:length(bins)){
  
  bin_data_plat = calibration_data %>%
    mutate(bin = cut(platt_pred, breaks = seq(0, 1, by = 0.1), include.lowest = TRUE)) %>%
    filter(bin ==bins[i]) %>%
    select(platt_pred, moldova_data.FLQ_R ) 
  
  bin_data_beta = calibration_data %>%
    mutate(bin = cut(beta_pred, breaks = seq(0, 1, by = 0.1), include.lowest = TRUE)) %>%
    filter(bin ==bins[i]) %>%
    select(beta_pred, moldova_data.FLQ_R )
  
  bin_data_original = calibration_data %>%
    mutate(bin = cut(original_pred, breaks = seq(0, 1, by = 0.1), include.lowest = TRUE)) %>%
    filter(bin ==bins[i]) %>%
    select(original_pred, moldova_data.FLQ_R )
  
  mean_actual_plat[i] = mean(bin_data_plat$moldova_data.FLQ_R)
  mean_actual_beta[i] = mean(bin_data_beta$moldova_data.FLQ_R)
  mean_actual_original[i] = mean(bin_data_original$moldova_data.FLQ_R)
  mean_platt_pred[i] = mean(bin_data_plat$platt_pred)
  mean_beta_pred[i]  = mean(bin_data_beta$beta_pred)
  mean_original_pred[i]  = mean(bin_data_original$original_pred)
  
}

cal = data.frame(bins = bins, mean_actual_plat = mean_actual_plat, mean_platt_pred = mean_platt_pred, mean_actual_beta = mean_actual_beta, mean_beta_pred = mean_beta_pred, mean_actual_original = mean_actual_original, mean_original_pred = mean_original_pred)

calibration_plot = ggplot() +
  geom_abline(intercept = 0, slope = 1, linetype = "dashed", color = "#de2d26", linewidth = 0.8, aes(label = "Diagonal (y=x)")) +  # Neutral gray dashed diagonal line
  geom_line(data = cal, aes(x = mean_actual_original, y = mean_original_pred, color = "Original Prediction", group = 1), linewidth = 0.8) +  # Dark green
  geom_line(data = cal, aes(x = mean_actual_plat, y = mean_platt_pred, color = "Platt Calibration", group = 1), linewidth = 0.8) +  # Medium blue
  geom_line(data = cal, aes(x = mean_actual_beta, y = mean_beta_pred, color = "Beta Calibration", group = 1), linewidth = 0.8) +  # Dark purple
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



ggsave(file.path("HM Output","Calibration_Plot_DR_TB.png"), plot = calibration_plot, width = 8, height = 6)
