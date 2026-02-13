setwd("/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/Bootstrap/Bootstrap PM - optimism corrected/Tests/Logistic Regression/")
library(dplyr)
library(pROC)
library(brms)
library(caret)
library(ggplot2)
library(rms)
library(betacal)


set.seed(1)

# Load the new dataset
data_path <-
  "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_HM.csv"
moldova_data <- read.csv(data_path)

#Model definition
formula = FLQ_R ~ Age + Family_size + Family_size18 + Sex_2 + Family_size +
  Occupation_2 + Occupation_3 + Occupation_4 + Occupation_5 +
  Education_2 + Education_3 + Education_4 + Education_5 + Education_missing +
  Living_condition_1 + Living_condition_missing + Outside_moldova_1 +
  Outside_moldova_missing + Urban_1 + Homeless_1 + Homeless_missing +
  Money_assistance_1 + Money_assistance_missing + Incarceration_1 +
  Incarceration_missing + TB_location_bin_Pulmonary + TB_type_2 +
  TB_type_3 + TB_type_4 + TB_type_6 

# Fit the logistic regression model
model <- glm(
  formula = formula,
  data = moldova_data,
  family = binomial(link = "logit")
)

# Predict probabilities for the same data
mainpred <- predict(model, type = "response")

# Calculate ROC curve
roc_curve <- roc(moldova_data$FLQ_R, mainpred)

# Plot calibration curve
rms::val.prob(mainpred, moldova_data$FLQ_R)

#### Using a beta calibration curve ####
bc <- beta_calibration(mainpred, moldova_data$FLQ_R, parameters = "abm")
beta = beta_predict(mainpred, bc)
rms::val.prob(beta, moldova_data$FLQ_R)

# Calculate ROC curve
roc_curve_calibrated <- roc(moldova_data$FLQ_R, beta)

# Create a data frame for the sensitivity and specificity data
sens_spec_data <- data.frame(
  Threshold = roc_curve_calibrated$thresholds,
  Sensitivity = roc_curve_calibrated$sensitivities,
  Specificity = roc_curve_calibrated$specificities
)

# Convert data to long format for ggplot2
sens_spec_data_long <- sens_spec_data %>%
  gather(key = "Metric", value = "Value", -Threshold)

# Create the ggplot2 plot with transparent shaded area between 0.1 and 0.15
sen_spec_cal_model_plot <- ggplot(sens_spec_data_long, aes(x = Threshold, y = Value)) +
  geom_line(aes(color = Metric, linetype = Metric), linewidth = 0.8) +  # Set color and linetype within geom_line
  labs(title = "Sensitivity and Specificity Across Thresholds",
       x = "Threshold",
       y = "Value") +
  scale_color_manual(values = c("Sensitivity" = "#2171b5", "Specificity" = "#fdae6b")) +  # Blue for Sensitivity, Orange for Specificity
  guides(color = guide_legend(title = NULL), linetype = guide_legend(title = NULL)) +  # Remove legend titles
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

# Save the plot with similar style
ggsave("sens_spec_calibrated_plot.png", plot = sen_spec_cal_model_plot, width = 8, height = 6, dpi = 300)


mainpred_data =  data.frame(predicted = beta, observed = moldova_data$FLQ_R, age = moldova_data$Age, sex = ifelse(moldova_data$Sex == 1, "Female", "Male" ))
write.csv(mainpred_data, file.path("main_pred.csv"), row.names = FALSE)

boots_pred = data.frame()

for (i in 1:200){
  set.seed(i)
  
  bootstrap_sample <- moldova_data %>% sample_n(size = n(), replace = TRUE)
  # Fit logistic regression model
  model <- glm(
    formula = formula,
    data = bootstrap_sample,
    family = binomial(link = "logit")
  )
  
  predicted_bootstrap = predict(model, type = "response")
  
  
  #### Using a beta calibration curve ####
  bc_bootstrap <- beta_calibration(predicted_bootstrap, bootstrap_sample$FLQ_R, parameters = "abm")
  beta_bootstrap = beta_predict(predicted_bootstrap, bc_bootstrap)
  
  # Calculate ROC curve
  roc_curve <- roc(bootstrap_sample$FLQ_R, predicted_bootstrap )
  
  # Print AUC (Area Under the Curve)
  cat("AUC boot:", auc(roc_curve), "\n")
  
  predicted_origdata = predict(model, newdata = moldova_data , type = "response")
  
  #### Using a beta calibration curve ####
  bc_origdata <- beta_calibration(predicted_origdata, moldova_data$FLQ_R, parameters = "ab")
  beta_origdata = beta_predict(predicted_origdata, bc_origdata)
  
  
  # Calculate ROC curve
  roc_curve2 <- roc(moldova_data$FLQ_R, predicted_origdata)
  
  # Print AUC (Area Under the Curve)
  cat("AUC orig:", auc(roc_curve2), "\n")
  
  
  boots_pred = rbind(boots_pred, data.frame(bootstrap_sample = rep(i, dim(moldova_data)[1]), predicted_bootstrap = beta_bootstrap, observed_bootstrap = bootstrap_sample$FLQ_R, predicted_origdata = beta_origdata, observed_origdata = moldova_data$FLQ_R)) 
  
}

write.csv(boots_pred, 'bootstrap_pred.csv', row.names = FALSE)