setwd('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output')

source("/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Code/ROC_performance.R")

# Load the new dataset
data_path <-
  "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_LR_Augumented.csv"
moldova_data <- read.csv(data_path)
moldova_data$pt_id = seq(1:dim(moldova_data)[1])

# Read predictions for consD201, consD205, and logistic regression
pred_LR <- read.csv('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/LR_MainPM_platt_beta_compare.csv')

#### Performance of the LR - Platt calibration ####
HM_performance = roc_performance(pred_LR$predicted_platt_mainpred, moldova_data, moldova_data$FLQ_R)


# ROC plot
plot(
  HM_performance$roc_curve,
  main = "ROC Curve for Hierarchical Logistic Regression",
  col.main = "darkblue",
  lwd = 2
)
# Add legend with labels based on cv_results$roc_auc_fulldata
legend(
  "bottomright",
  legend = round(HM_performance$roc_curve$auc, 2),
  lwd = 2,
  title = "AUROC",
  cex = 0.8
)

sensitivity_specificity_df <- HM_performance$sens_spec %>%
  select(sensitivity, specificity, threshold) %>%
  rename(Sensitivity = sensitivity, Specificity = specificity)%>%
  pivot_longer(cols = c("Sensitivity", "Specificity"),    # Ensure column names match exactly
               names_to = "Metric", 
               values_to = "Value")


#### Plot sensitivity and specificity - Platt calibration ####
sensitivity_specificity_plot <- ggplot(data= sensitivity_specificity_df, aes(x = threshold, y = Value, color = Metric, group = Metric), linewidth = 0.8) +
  geom_line(size = 0.7) +
  geom_point(size = 0.7) +
  # Custom colors for sensitivity and specificity
  scale_color_manual(values = c("Sensitivity" = "#004c6d",  # Dark blue for sensitivity
                                "Specificity" = "#6baed6")) + # Light blue for specificity
  labs(
    y = "Value",
    x = "Classification threshold",
    color = "Metric"
  ) +
  guides(color = guide_legend(title = NULL)) +  # Remove the legend title
  theme_minimal() +
  xlim(0, 1) +  # Set x-axis from 0 to 1, adjust if needed
  ylim(0, 1) +  # Set y-axis from 0 to 1
  theme(
    legend.position = "bottom",
    plot.background = element_rect(fill = "white", color = NA),  # White plot background
    panel.background = element_rect(fill = "white", color = NA), # White panel background
    panel.grid = element_line(color = "gray90"),                 # Light gray grid
    axis.title = element_text(size = 16),                        # Increase axis title text size
    axis.text = element_text(size = 16),                         # Increase axis labels text size
    legend.text = element_text(size = 16)                        # Increase legend text size
  )

ggsave("Sens_Spec.png", plot = sensitivity_specificity_plot, width = 8, height = 6)


# Plot probabilities calculated with Bayes Theorem
ggplot(HM_performance$sens_spec, aes(x = threshold)) +
  geom_line(aes(y = P_S_R, color = "P_S_R")) +
  geom_line(aes(y = P_R_R, color = "P_R_R")) +
  scale_color_manual(values = c( "blue", "red"), name = "Variable") +
  labs(x = "Threshold", y = "Value") +
  theme_minimal() +
  theme(legend.position = "top")

ggplot(HM_performance$sens_spec, aes(x = threshold)) +
  geom_line(aes(y = P_S_S, color = "P_S_S")) +
  geom_line(aes(y = P_R_S, color = "P_R_S")) +
  scale_color_manual(values = c( "blue", "red"), name = "Variable") +
  labs(x = "Threshold", y = "Value") +
  theme_minimal() +
  theme(legend.position = "top")
