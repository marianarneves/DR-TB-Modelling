library(dplyr)
library(ggplot2)

setwd(
  '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/Bootstrap/Bootstrap PM - 632 method/Recovered from opt corr/'
)

Maincalibratedpred = read.csv("HM_mainPM_calibrated_predictions.csv", header = TRUE)
Bootscalibratedpred = read.csv("oob_pred_all.csv", header = TRUE)

MainData_Sens_Spec = readxl::read_excel('MainData_Sens_Spec.xlsx')
Boot_Sens_Spec = readxl::read_excel('Booststrap_Sens_Spec.xlsx')
DT_prob = readxl::read_excel('DecisionTree_probs.xlsx')

# Create a function to generate plots
plot_parameter <- function(data, title) {
  ggplot(data, aes(x = threshold, y = Value)) +  # 'x' and 'Value' are placeholders for actual column names
    geom_line(color = "blue") +
    geom_point(color = "red") +
    ggtitle(title) +
    xlab("X-axis Label") +  # Replace with actual x-axis label
    ylab("Y-axis Label")    # Replace with actual y-axis label
}

#########################
#     Main dataset      #
#########################

#Filtering each parameter
TPR_MainData_Sens_Spec = MainData_Sens_Spec %>%
  filter(Variable == "TPR")
TNR_MainData_Sens_Spec = MainData_Sens_Spec %>%
  filter(Variable == "TNR")
FPR_MainData_Sens_Spec = MainData_Sens_Spec %>%
  filter(Variable == "FPR")
FNR_MainData_Sens_Spec = MainData_Sens_Spec %>%
  filter(Variable == "FNR")
positiveclass_proportion_MainData_Sens_Spec = MainData_Sens_Spec %>%
  filter(Variable == "positiveclass_proportion")
negativeclass_proportion_MainData_Sens_Spec = MainData_Sens_Spec %>%
  filter(Variable == "negativeclass_proportion")

# Plot each parameter and display
plot_TPR <- plot_parameter(TPR_MainData_Sens_Spec, "TPR over Threshold")
plot_TNR <- plot_parameter(TNR_MainData_Sens_Spec, "TNR over Threshold")
plot_FPR <- plot_parameter(FPR_MainData_Sens_Spec, "FPR over Threshold")
plot_FNR <- plot_parameter(FNR_MainData_Sens_Spec, "FNR over Threshold")
plot_positiveclass_proportion <- plot_parameter(positiveclass_proportion_MainData_Sens_Spec,
                                                "Positive Class Proportion over X")
plot_negativeclass_proportion <- plot_parameter(negativeclass_proportion_MainData_Sens_Spec,
                                                "Negative Class Proportion over X")

# Display all plots
plot_TPR
plot_TNR
plot_FPR
plot_FNR
plot_positiveclass_proportion
plot_negativeclass_proportion


#############################
#     Bootstrap sample      #
#############################


#Filtering each parameter
TPR_Boot_Sens_Spec = Boot_Sens_Spec %>%
  filter(Variable == "TPR") %>%
  select(Bootstrap_sample_195, threshold) %>%
  rename(Value = Bootstrap_sample_195)
TNR_Boot_Sens_Spec = Boot_Sens_Spec %>%
  filter(Variable == "TNR") %>%
  select(Bootstrap_sample_195, threshold) %>%
  rename(Value = Bootstrap_sample_195)
FPR_Boot_Sens_Spec = Boot_Sens_Spec %>%
  filter(Variable == "FPR") %>%
  select(Bootstrap_sample_195, threshold) %>%
  rename(Value = Bootstrap_sample_195)
FNR_Boot_Sens_Spec = Boot_Sens_Spec %>%
  filter(Variable == "FNR") %>%
  select(Bootstrap_sample_195, threshold) %>%
  rename(Value = Bootstrap_sample_195)
positiveclass_proportion_Boot_Sens_Spec = Boot_Sens_Spec %>%
  filter(Variable == "positiveclass_proportion") %>%
  select(Bootstrap_sample_195, threshold) %>%
  rename(Value = Bootstrap_sample_195)
negativeclass_proportion_Boot_Sens_Spec = Boot_Sens_Spec %>%
  filter(Variable == "negativeclass_proportion") %>%
  select(Bootstrap_sample_195, threshold) %>%
  rename(Value = Bootstrap_sample_195)

# Plot each parameter and display
plot_TPR <- plot_parameter(TPR_Boot_Sens_Spec, "TPR over Threshold")
plot_TNR <- plot_parameter(TNR_Boot_Sens_Spec, "TNR over Threshold")
plot_FPR <- plot_parameter(FPR_Boot_Sens_Spec, "FPR over Threshold")
plot_FNR <- plot_parameter(FNR_Boot_Sens_Spec, "FNR over Threshold")
plot_positiveclass_proportion <- plot_parameter(positiveclass_proportion_Boot_Sens_Spec,
                                                "Positive Class Proportion over X")
plot_negativeclass_proportion <- plot_parameter(negativeclass_proportion_Boot_Sens_Spec,
                                                "Negative Class Proportion over X")

# Display all plots
plot_TPR
plot_TNR
plot_FPR
plot_FNR
plot_positiveclass_proportion
plot_negativeclass_proportion


##########################
#     Decision Tree      #
##########################

P_R_R_boot195 = DT_prob %>%
  filter(Variable == "P_R_R") %>%
  select(Bootstrap_sample_195, threshold) %>%
  rename(Value = Bootstrap_sample_195)
P_S_S_boot195 = DT_prob %>%
  filter(Variable == "P_S_S") %>%
  select(Bootstrap_sample_195, threshold) %>%
  rename(Value = Bootstrap_sample_195)
P_R_S_boot195 = DT_prob %>%
  filter(Variable == "P_R_S") %>%
  select(Bootstrap_sample_195, threshold) %>%
  rename(Value = Bootstrap_sample_195)
P_S_R_boot195 = DT_prob %>%
  filter(Variable == "P_S_R") %>%
  select(Bootstrap_sample_195, threshold) %>%
  rename(Value = Bootstrap_sample_195)

# Plot each parameter and display
plot_P_R_R <- plot_parameter(P_R_R_boot195, "P_R_R over Threshold")
plot_P_S_S <- plot_parameter(P_S_S_boot195, "P_S_S over Threshold")
plot_P_R_S <- plot_parameter(P_R_S_boot195, "P_R_S over Threshold")
plot_P_S_R <- plot_parameter(P_S_R_boot195, "P_S_R over Threshold")

plot_P_R_R
plot_P_S_S
plot_P_R_S
plot_P_S_R


##################################
#     Recalculating DT prob      #
##################################

DT_prob_New = data.frame(matrix(ncol = 1, nrow = 401))

DT_prob_Newr = DT_prob_New %>%
  mutate(
    New_P_R_R_MainDataset = ifelse(
      positiveclass_proportion_MainData_Sens_Spec$Value > 0 , 
      TPR_MainData_Sens_Spec$Value * (1 - 0.812963) / positiveclass_proportion_MainData_Sens_Spec$Value,
      NA), 
    New_P_S_S_MainDataset = ifelse(
      negativeclass_proportion_MainData_Sens_Spec$Value > 0,
      TNR_MainData_Sens_Spec$Value * (0.812963) / negativeclass_proportion_MainData_Sens_Spec$Value,
      NA
    )
  ) %>%
  mutate(
    New_P_R_S_MainDataset = ifelse(is.na(New_P_S_S_MainDataset), NA, 1 - New_P_S_S_MainDataset),
    New_P_S_R_MainDataset = ifelse(is.na(New_P_R_R_MainDataset), NA, 1 - New_P_R_R_MainDataset)
  ) %>%
  mutate(
    New_P_R_R_Boot = ifelse(
      positiveclass_proportion_Boot_Sens_Spec$Value > 0, 
      TPR_Boot_Sens_Spec$Value * (1 - 0.812963) / positiveclass_proportion_Boot_Sens_Spec$Value,
      NA),
    New_P_S_S_Boot = ifelse(
      negativeclass_proportion_Boot_Sens_Spec$Value > 0,
      TNR_Boot_Sens_Spec$Value * (0.812963) / negativeclass_proportion_Boot_Sens_Spec$Value,
      NA
    )
  ) %>%
  mutate(
    New_P_R_S_Boot = ifelse(is.na(New_P_S_S_Boot), NA, 1 - New_P_S_S_Boot),
    New_P_S_R_Boot = ifelse(is.na(New_P_R_R_Boot), NA, 1 - New_P_R_R_Boot)
  ) %>%
  mutate(New_P_R_R = ifelse(is.na(New_P_R_R_MainDataset) | is.na(New_P_R_R_Boot), NA, 0.368 * New_P_R_R_MainDataset + (1 - 0.368) * New_P_R_R_Boot),
         New_P_S_S = ifelse(is.na(New_P_S_S_MainDataset) | is.na(New_P_S_S_Boot), NA, 0.368 * New_P_S_S_MainDataset + (1 - 0.368) * New_P_S_S_Boot),
         New_P_R_S = ifelse(is.na(New_P_S_S), NA, 1 - New_P_S_S),
         New_P_S_R = ifelse(is.na(New_P_R_R), NA, 1 - New_P_R_R)) %>%
  mutate(threshold = FPR_Boot_Sens_Spec$threshold) %>%
  select(-1)

ggplot(DT_prob_Newr, aes(x = threshold)) +
  # First line for New_P_R_R
  geom_line(aes(y = New_P_R_R, color = "New_P_R_R")) + 
  # Second line for New_P_S_R
  geom_line(aes(y = New_P_S_R, color = "New_P_S_R")) + 
  # Customize the colors if desired
  scale_color_manual(values = c("New_P_R_R" = "blue", "New_P_S_R" = "red")) +
  # Add labels and a title
  labs(x = "Threshold", y = "Probability", title = "New_P_R_R and New_P_S_R Lines") +
  theme_minimal()

ggplot(DT_prob_Newr, aes(x = threshold)) +
  # First line for New_P_S_S
  geom_line(aes(y = New_P_S_S, color = "New_P_S_S")) + 
  # Second line for New_P_R_S
  geom_line(aes(y = New_P_R_S, color = "New_P_R_S")) + 
  # Customize the colors if desired
  scale_color_manual(values = c("New_P_S_S" = "blue", "New_P_R_S" = "red")) +
  # Add labels and a title
  labs(x = "Threshold", y = "Probability", title = "New_P_S_S and New_P_R_S Lines") +
  theme_minimal()