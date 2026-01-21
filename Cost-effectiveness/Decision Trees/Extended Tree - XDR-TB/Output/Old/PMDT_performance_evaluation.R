library(readxl)
library(dplyr)
library(ggplot2)
library(magrittr)
library(tidyr)
library(ggplot2)
library(gridExtra)


setwd(
  "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB"
)

FLQ_Res_prev = 1 - 0.812963
GDP_moldova = 5714.43

# Probabilities, DALYs and Cost assumptions
daly <- read_excel("Cost_DALY_Prob_asumptions.xlsx", sheet = "DALY") %>%
  {
    setNames(object = .$`DALY Value`,
             nm = .$`DALY Variable`)
  }
cost <- read_excel("Cost_DALY_Prob_asumptions.xlsx", sheet = "Costs") %>%
  {
    setNames(object = .$`Cost Value`,
             nm = .$`Cost Variable`)
  }
probabilities <- read_excel("Cost_DALy_Prob_asumptions.xlsx", sheet = "Probabilities") %>%
  {
    setNames(object = .$`Probability Value`,
             nm = .$`Probability Variable`)
  }

# Probabilities in the tree for FLQ resistance and susceptibility
DT_probabilities = read.csv(
  "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/HM Output/sens_spec_calibrated_model.csv",
  header =  TRUE
)

#Read dataset
PMDT_performance <-
  read_excel("Output/PMDT_performance.xlsx")

#Read dataset
PMDT_performance_sus_res <-
  read_excel("Output/PMDT_sus_res.xlsx")

#Read dataset
PMDT_individual_performance <-
  read_excel("Output/PMDT_individual_performance.xlsx")

# Change in DALY by threshold compared to Sd treatment
ggplot(PMDT_performance, aes(x = Threshold, y = (StTreat_DALY - Daly_Tx_truth_all))) +
  geom_line() +
  labs(title = "Change in DALY - PM+DT vs Standard Tx", x = "Threshold", y = "Change in DALY")

# Change in Cost by threshold compared to Sd treatment
ggplot(PMDT_performance, aes(x = Threshold, y = (Cost_Tx_truth_all - StTreat_Cost))) +
  geom_line() +
  labs(title = "Change in Cost - PM+DT vs Standard Tx", x = "Threshold", y = "Change in cost")

# Calculating sensitivity and specificity
PMDT_performance_Sens_Spec = PMDT_performance %>%
  mutate(
    sensitivity = TP_DTPM / (TP_DTPM + FN_DTPM),
    specificity = TN_DTPM / (TN_DTPM + FP_DTPM)
  )

# ROC
ggplot(PMDT_performance_Sens_Spec,
       aes(x = specificity, y = sensitivity)) +
  geom_point() +
  labs(title = "ROC", x = "X Axis Label", y = "Y Axis Label")

# Sensitivity and Specificity by threshold
ggplot(PMDT_performance_Sens_Spec, aes(x = Threshold)) +
  geom_line(aes(y = sensitivity, color = "Sensisitivity")) +
  geom_line(aes(y = specificity, color = "Specificity")) +
  scale_color_manual(values = c(
    "Sensisitivity" = "red",
    "Specificity" = "blue"
  )) +
  labs(
    title = "Sensisitivity and Specificity",
    x = "Threshold",
    y = "Value",
    color = "Lines"
  ) +
  theme_minimal()

#Cost
FLQ_res_Cost = cost["Cost_FLQ"] + (probabilities["Prob_CC_FLQres"] * cost["Cost_CC_FLQres"] + probabilities["Prob_TF_FLQres"] * cost["Cost_TF_FLQres"] + probabilities["Prob_D_FLQres"] * cost["Cost_D_FLQres"])
FLQ_sus_Cost =  cost["Cost_FLQ"] + (probabilities["Prob_CC_FLQsus"] *  cost["Cost_CC_FLQsus"] + probabilities["Prob_TF_FLQsus"] *  cost["Cost_TF_FLQsus"] + probabilities["Prob_D_FLQsus"] * cost["Cost_D_FLQsus"])
DLM_Cost = cost["Cost_DLM"] + (probabilities["Prob_CC_DLM"] * cost["Cost_CC_DLM"] + probabilities["Prob_TF_DLM"] * cost["Cost_TF_DLM"] + probabilities["Prob_D_DLM"] * cost["Cost_D_DLM"])

# Impact of each classification
assumed_death_daly = seq(0, 50, by = 5)

t = PMDT_performance_Sens_Spec$Threshold
StTreat_DALY = NA
StTreat_Cost = NA
FLQ_res_DALY = NA
FLQ_sus_DALY = NA
DLM_DALY = NA
FLQres_DALY_ind = NA
FLQsus_DALY_ind = NA
DLM_DALY_ind = NA
FLQ_Cost_ind = matrix(nrow = length(t), ncol = length(assumed_death_daly))
FLQ_DALY_ind = matrix(nrow = length(t), ncol = length(assumed_death_daly))
CNMB = matrix(nrow = length(t), ncol = length(assumed_death_daly))
DALYloss_FLQsus = NA
IncreaseCost_FLQsus = NA
DALYloss_FLQres = NA
IncreaseCost_FLQres = NA

for (j in seq_along(assumed_death_daly)) {
  #Daly
  FLQ_res_DALY[j] = daly["DALY_FLQ"] + (probabilities["Prob_CC_FLQres"] * daly["DALY_CC_FLQres"] + probabilities["Prob_CC_FLQres"] * daly["DALY_TF_FLQres"] + probabilities["Prob_D_FLQres"] * assumed_death_daly[j])
  FLQ_sus_DALY[j] =  daly["DALY_FLQ"] + (probabilities["Prob_CC_FLQsus"] *  daly["DALY_CC_FLQsus"] + probabilities["Prob_CC_FLQsus"] *  daly["DALY_TF_FLQsus"] + probabilities["Prob_D_FLQsus"] * assumed_death_daly[j])
  DLM_DALY[j] = daly["DALY_DLM"] + (probabilities["Prob_CC_DLM"] * daly["DALY_CC_DLM"] + probabilities["Prob_CC_DLM"] * daly["DALY_TF_DLM"] + probabilities["Prob_D_DLM"] * assumed_death_daly[j])
  
  #DALY loss if the patient is FLQ susceptible
  DALYloss_FLQsus[j] = FLQ_sus_DALY[j] - DLM_DALY[j]
  
  #Increase in Cost if patient is susceptible
  IncreaseCost_FLQsus[j] = DLM_Cost - FLQ_sus_Cost
  
  #DALY loss if the patient is FLQ susceptible
  DALYloss_FLQres[j] = FLQ_res_DALY[j] - DLM_DALY[j]
  
  #Increase in Cost if patient is susceptible
  IncreaseCost_FLQres[j] = DLM_Cost - FLQ_res_Cost
  
  # Standard Treatment
  StTreat_DALY[j] = FLQ_Res_prev * FLQ_res_DALY[j] + (1 - FLQ_Res_prev) * FLQ_sus_DALY[j]
  StTreat_Cost[j] = FLQ_Res_prev * FLQ_res_Cost + (1 - FLQ_Res_prev) * FLQ_sus_Cost
  
  for (i in seq_along(t)) {
    FLQ_Cost_ind[i, j] = DT_probabilities$P_R_P[DT_probabilities$threshold ==
                                                  t[i]] * FLQ_res_Cost + DT_probabilities$P_NR_P[DT_probabilities$threshold ==
                                                                                                   t[i]]  * FLQ_sus_Cost
    FLQ_DALY_ind[i, j] = DT_probabilities$P_R_P[DT_probabilities$threshold ==
                                                  t[i]] * FLQ_res_DALY[j] + DT_probabilities$P_NR_P[DT_probabilities$threshold ==
                                                                                                      t[i]]  * FLQ_sus_DALY[j]
    
    #NMB
    CNMB[i, j] = GDP_moldova * (FLQ_DALY_ind[i, j] - DLM_DALY[j]) - (DLM_Cost - FLQ_Cost_ind[i, j])
  }
}

# Change in NMB depending on DALY Death
CNMB_long  = CNMB %>%
  as_tibble(.) %>%
  rename_with(.fn = ~ paste0("DD_", assumed_death_daly),
              .cols = everything()) %>%
  mutate(DD_05 = DD_5, threshold = t) %>%
  select(-DD_5) %>%
  pivot_longer(cols = -threshold,
               names_to = "DALY_Death",
               values_to = "CNMB")

# Reorder levels of DALY_Death in alphabetical order
CNMB_long$DALY_Death <- factor(CNMB_long$DALY_Death, levels = sort(unique(CNMB_long$DALY_Death)))

# Plot the data with ggplot
ggplot(CNMB_long, aes(x = threshold, y = CNMB, color = DALY_Death)) +
  geom_point() +  # Add points
  geom_hline(yintercept = 0, color = "red") +  # Add horizontal line at y = 0
  labs(x = "t", y = "CNMB", color = "DALY_Death") +  # Set axis and legend labels
  ggtitle("CNMB vs Thresholds for different DALY incurred from death")  # Set plot title

# Change in Health from FLQ susceptible and resistant
changedaly_dalydeath = data.frame(
  daly_death = paste0("DD_", assumed_death_daly),
  FLQ_sus = DALYloss_FLQsus,
  FLQ_res = DALYloss_FLQres
) %>%
  mutate(daly_death = replace(daly_death, daly_death == "DD_5", "DD_05")) %>%
  pivot_longer(cols = -daly_death,
               names_to = "FLQ_status",
               values_to = "Loss")

# Reorder levels of DALY_Death in alphabetical order
changedaly_dalydeath$daly_death <- factor(changedaly_dalydeath$daly_death, levels = sort(unique(changedaly_dalydeath$daly_death)))

# Plot the data with ggplot
ggplot(changedaly_dalydeath,
       aes(x = daly_death, y = Loss, color = FLQ_status)) +
  geom_point() +  # Add points
  labs(x = "DALY death", y = "Change in DALYs", color = "DALY_Death") +  # Set axis and legend labels
  ggtitle("Change in DALYS for different DALY incurred from death") +
  theme(text = element_text(size = 14))

# Change in Cost from FLQ susceptible and resistant
increasecost_dalydeath = data.frame(
  daly_death = paste0("DD_", assumed_death_daly),
  FLQ_sus = IncreaseCost_FLQsus,
  FLQ_res = IncreaseCost_FLQres
) %>%
  mutate(daly_death = replace(daly_death, daly_death == "DD_5", "DD_05")) %>%
  pivot_longer(cols = -daly_death,
               names_to = "FLQ_status",
               values_to = "Loss")

# Reorder levels of DALY_Death in alphabetical order
increasecost_dalydeath$daly_death <- factor(increasecost_dalydeath$daly_death, levels = sort(unique(increasecost_dalydeath$daly_death)))

# Plot the data with ggplot
ggplot(increasecost_dalydeath,
       aes(x = daly_death, y = Loss, color = FLQ_status)) +
  geom_point() +  # Add points
  labs(x = "DALY death", y = "Change in Cost", color = "DALY_Death") +  # Set axis and legend labels
  ggtitle("Increase in Cost for different DALY incurred from death") +
  theme(text = element_text(size = 14))


# Minimun NMB change
PMDT_performance[PMDT_performance$NMB_change == min(PMDT_performance$NMB_change), ]
PMDT_performance[PMDT_performance$NMB_change == max(PMDT_performance$NMB_change), ]


###################################
#     Individual performance      #
###################################

# Look at people who are classified resistant not being resistant
PT_FP_above03 = PMDT_individual_performance %>%
  filter(observed == 0, PM_classification == 1, threshold > 0.3) %>%
  select(Patient)
PT_FP_above03 = unlist(unique(PT_FP_above03))

PMDT_individual_performance %>%
  filter(Patient %in% PT_FP_above03) %>%
  ggplot(aes(x = threshold, y = NMB, color = Patient)) +
  geom_point()

PMDT_individual_performance %>%
  filter(Patient %in% PT_FP_above03) %>%
  mutate(
    NMB_individual = GDP_moldova * (StTreat_DALY - Daly_Tx_truth) - (Cost_Tx_truth - StTreat_cost),
    health_increase = (StTreat_DALY - Daly_Tx_truth)
  ) %>%
  ggplot(aes(x = threshold, y = NMB_individual, color = Patient)) +
  geom_point()


#Health change depending on the correct classsification and NMB
PMDT_individual_performance_correct_class = PMDT_individual_performance %>%
  mutate(
    health_increase = (StTreat_DALY - Daly_Tx_truth),
    correct_class = ifelse(observed == PMDTPM_classification, 1, 0)
  ) %>%
  group_by(threshold, correct_class) %>%
  summarise(cum_health_increase = sum(health_increase)) %>%
  right_join(PMDT_performance, by = c("threshold" = "Threshold"))


# Convert "observed" to factor with levels "0" and "1"
PMDT_individual_performance_correct_class$correct_class <- factor(PMDT_individual_performance_correct_class$correct_class,
                                                                  levels = c("0", "1"))

ggplot(
  PMDT_individual_performance_correct_class,
  aes(
    x = threshold,
    y = cum_health_increase,
    group = correct_class,
    fill = correct_class
  )
) +
  geom_area() +
  scale_fill_discrete(labels = c("No", "Yes")) +
  geom_line(aes(y = NMB_change, color = "Change in NMB"), size = 0.5) +
  labs(y = "Change in NMB/Health",
       x = "Threshold",
       fill = "Correct treatment?",
       color = "NMB") +
  theme(text = element_text(size = 14)) +
  scale_color_manual(values = "black", labels = c("Change in NMB")) +
  theme(text = element_text(size = 14))


#Health change depending on the correct classsification and NMB - RATIO
PMDT_individual_performance_correct_class_ratio = PMDT_individual_performance %>%
  mutate(
    health_increase = (StTreat_DALY - Daly_Tx_truth),
    correct_class = ifelse(observed == PMDTPM_classification, 1, 0)
  ) %>%
  group_by(threshold, correct_class) %>%
  summarise(cum_health_increase = sum(health_increase)) %>%
  right_join(PMDT_performance, by = c("threshold" = "Threshold")) %>%
  spread(key = correct_class, value = cum_health_increase) %>%
  mutate(ratio = ifelse(`0` == 0, 0, abs(`1` / `0`) * 100))

ggplot(PMDT_individual_performance_correct_class_ratio,
       aes(x = threshold, y = ratio)) +
  geom_area(colour = "lightblue", fill = "lightblue") +
  geom_line(aes(y = NMB_change), colour = "black", size = 0.5) +
  # Add a horizontal line at y = 0
  geom_hline(yintercept = 100,
             linetype = "dashed",
             color = "red") +
  scale_y_continuous(# Features of the first axis
    name = "Change in NMB°)",
    
    # Add a second axis and specify its features
    sec.axis = sec_axis( ~ . / 100, name = "Change in Health Ratio")) +
  theme(text = element_text(size = 14))



# Correct Tx prescribed?

PMDT_correct_treatment_threshold  = PMDT_individual_performance %>%
  mutate(PMDT_correct_treatment = ifelse(observed == PMDTPM_classification, 1, 0)) %>%
  group_by(threshold) %>%
  summarise(n = sum(PMDT_correct_treatment) / 540)

# Create a ggplot with horizontal line
ggplot(PMDT_correct_treatment_threshold, aes(x = threshold, y = n)) +
  geom_line() +
  geom_hline(aes(yintercept = 1 - FLQ_Res_prev, linetype = "Threshold"),
             color = "red") +
  labs(x = "Threshold", y = "Proportion patients who would be prescribed the correct treatment", linetype = "") +
  scale_linetype_manual(values = "dashed", labels = "Standard Treatment") +
  theme(text = element_text(size = 14))

# Correct Tx prescribed? Stratified

PMDT_correct_treatment_threshold_strat  = PMDT_individual_performance %>%
  mutate(PMDT_correct_treatment = ifelse(observed == PMDTPM_classification, 1, 0)) %>%
  group_by(threshold, observed) %>%
  summarise(n = sum(PMDT_correct_treatment) / n()) %>%
  right_join(PMDT_performance, by = c("threshold" = "Threshold"))

# Convert "observed" to factor with levels "0" and "1"
PMDT_correct_treatment_threshold_strat$observed <- factor(PMDT_correct_treatment_threshold_strat$observed,
                                                          levels = c("0", "1"))

# Plot
ggplot(
  PMDT_correct_treatment_threshold_strat,
  aes(
    x = threshold,
    y = n,
    group = observed,
    colour =  observed
  )
) +
  geom_line() +
  labs(x = "Threshold", y = "Count (n)", fill = "Observed Group") +
  theme_minimal()

ggplot(PMDT_correct_treatment_threshold_strat, aes(x = threshold)) +
  geom_line(aes(y = NMB_change), size = 2) +
  geom_line(aes(
    y = n * 200,
    group = observed,
    colour = observed
  ), size = 2) +
  
  scale_y_continuous(# Features of the first axis
    name = "Temperature (Celsius °)",
    
    # Add a second axis and specify its features
    sec.axis = sec_axis( ~ . / 200, name = "Price ($)"))



### Performance by FLQ susceptibility profile
source("Output/NMB_Cost_DALY_bysusceptibility_plots.R")
NMB_COST_DALY_plots

### People receiving DLM
DLM_prop_plot = ggplot(PMDT_performance_sus_res, aes(x = Threshold)) +
  geom_line(aes(y = Treat_DLM, color = "All patients")) +
  geom_line(aes(y = Treat_DLM_res, color = "FLQ Resistant")) +
  geom_line(aes(y = Treat_DLM_sus, color = "FLQ Susceptible")) +
  labs(
    color = "",
    title = "Proportion of patients prescribed DLM",
    x = "Threshold",
    y = "Proportion"
  )+
  theme(text = element_text(size = 18))
# Save the final plot
ggsave(
  filename = "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/DLM_proportion.png",
  plot = DLM_prop_plot,
  width = 14,
  height = 10
)


# People classified FLQ Resistant by the model
#Read dataset
PM_performance <-
  read.csv("/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/HM Output/sens_spec_calibrated_model.csv", header = TRUE)%>%
  select(threshold, sensitivity, FPR, positive)

PM_class_FLQres_plot = ggplot(PM_performance, aes(x = threshold)) +
  geom_line(aes(y = sensitivity, color = "FLQ Resistant - Classified FLQ Resistant (TPR)")) +
  geom_line(aes(y = FPR, color = "FLQ Susceptible - Classified FLQ Resistant (FPR)"))+
  geom_line(aes(y = positive, color = "All - Classified FLQ Resistant")) +
  labs(
    color = "",
    title = "Proportion of patients classified FLQ resistant",
    x = "Threshold",
    y = "Proportion"
  )+
  theme(text = element_text(size = 18))
# Save the final plot
ggsave(
  filename = "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/PM_class_FLQres_plot.png",
  plot = PM_class_FLQres_plot,
  width = 14,
  height = 10
)

#Cost, DALY and NMB for each DT depending on classification
ts=12

DALY_class_FLQres_plot = ggplot(PMDT_performance_sus_res, aes(x = Threshold)) +
  geom_line(aes(y = Exp_FLQ_DALY_ResClass, color = "FLQ")) +
  geom_line(aes(y = Exp_DLM_DALY_ResClass, color = "DLM"))+
  labs(
    color = "",
    title = "DALY of FLQ and DLM for patients classified FLQ resistant",
    x = "Threshold",
    y = "DALY"
  )+
  ylim(c(0,4))+
  theme(text = element_text(size = ts))

DALY_class_FLQsus_plot = ggplot(PMDT_performance_sus_res, aes(x = Threshold)) +
  geom_line(aes(y = Exp_FLQ_DALY_SusClass, color = "FLQ")) +
  geom_line(aes(y = Exp_DLM_DALY_SusClass, color = "DLM"))+
  labs(
    color = "",
    title = "DALY of FLQ and DLM for patients classified FLQ susceptible",
    x = "Threshold",
    y = "DALY"
  )+
  ylim(c(0,4))+
  theme(text = element_text(size = ts))

Cost_class_FLQres_plot = ggplot(PMDT_performance_sus_res, aes(x = Threshold)) +
  geom_line(aes(y = Exp_FLQ_Cost_ResClass, color = "FLQ")) +
  geom_line(aes(y = Exp_DLM_Cost, color = "DLM"))+
  labs(
    color = "",
    title = "Cost of FLQ and DLM for patients classified FLQ resistant",
    x = "Threshold",
    y = "Cost"
  )+
  theme(text = element_text(size = ts))

Cost_class_FLQsus_plot = ggplot(PMDT_performance_sus_res, aes(x = Threshold)) +
  geom_line(aes(y = Exp_FLQ_Cost_SusClass, color = "FLQ")) +
  geom_line(aes(y = Exp_DLM_Cost, color = "DLM"))+
  labs(
    color = "",
    title = "Cost of FLQ and DLM for patients classified FLQ susceptible",
    x = "Threshold",
    y = "Cost"
  )+
  theme(text = element_text(size = ts))

NMB_class_FLQres_plot = ggplot(PMDT_performance_sus_res, aes(x = Threshold)) +
  geom_line(aes(y = NMB_ResClass, colour = "(NMB FLQ - NMB DLM)")) +
  geom_line(aes(y = NMB_FLQ_ResClass, colour = "NMB FLQ")) +
  geom_line(aes(y = NMB_DLM_ResClass, colour = "NMB DLM"))+
  labs(
    color = "",
    title = "NMB of FLQ and DLM for patients classified FLQ resistant",
    x = "Threshold",
    y = "NMB"
  )+
  ylim(c(-12000,25000))+
  theme(text = element_text(size = ts))

NMB_class_FLQsus_plot = ggplot(PMDT_performance_sus_res, aes(x = Threshold)) +
  geom_line(aes(y = NMB_SusClass, colour = "(NMB FLQ - NMB DLM)")) +
  geom_line(aes(y = NMB_FLQ_SusClass, colour = "NMB FLQ")) +
  geom_line(aes(y = NMB_DLM_SusClass, colour = "NMB DLM"))+
  labs(
    color = "",
    title = "NMB of FLQ and DLM for patients classified FLQ susceptible",
    x = "Threshold",
    y = "NMB"
  )+
  ylim(c(-12000,25000))+
  theme(text = element_text(size = ts))

# Arrange plots in a 2x3 grid
NMB_DALY_Cost_class_FLQ = grid.arrange(
  DALY_class_FLQres_plot, DALY_class_FLQsus_plot,
  Cost_class_FLQres_plot, Cost_class_FLQsus_plot,
  NMB_class_FLQres_plot, NMB_class_FLQsus_plot,
  ncol = 2
)

# Save the final plot
ggsave(
  filename = "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_DALY_Cost_class_FLQ_plot.png",
  plot = NMB_DALY_Cost_class_FLQ,
  width = 14,
  height = 10
)

#### Confidence intervals
#Read dataset
# Read datasets
NMB_avg_sd_r_data <- read_excel("Output/NMB_avg_r_eachind.xlsx")
NMB_avg_sd_s_data <- read_excel("Output/NMB_avg_s_eachind.xlsx")
NMB_avg_data <- read_excel("Output/NMB_avg_eachind.xlsx")

# Calculate confidence intervals for each dataset
calculate_ci <- function(data, data_column) {
  data %>%
    group_by(Threshold) %>%
    summarise(NMB_avg_mean = mean({{data_column}}), 
              NMB_avg_sd = sd({{data_column}}),
              n = n()
    ) %>%
    mutate(
      t_interval_lower = NMB_avg_mean - qt(0.975, df = n - 1) * (NMB_avg_sd / sqrt(n)),
      t_interval_upper = NMB_avg_mean + qt(0.975, df = n - 1) * (NMB_avg_sd / sqrt(n))
    )
}

# Calculate confidence intervals for each dataset
NMB_avg_sd_r_ci <- calculate_ci(NMB_avg_sd_r_data, NMB_avg_sd_r)
NMB_avg_sd_s_ci <- calculate_ci(NMB_avg_sd_s_data, NMB_avg_sd_s)
NMB_avg_ci <- calculate_ci(NMB_avg_data, NMB_avg)

# Add group labels
NMB_avg_sd_r_ci$group <- "FLQ resistant patients"
NMB_avg_sd_s_ci$group <- "FLQ susceptible patients"
NMB_avg_ci$group <- "All patients"

# Combine datasets
combined_data <- bind_rows(NMB_avg_sd_r_ci, NMB_avg_sd_s_ci, NMB_avg_ci)

# Plot
plot_NMB_FLQres_sus = ggplot(combined_data, aes(x = Threshold, y = NMB_avg_mean, fill = group)) +
  geom_line() +
  geom_ribbon(aes(ymin = t_interval_lower, ymax = t_interval_upper), fill = "grey", alpha = 0.5) +  # Specify fill outside aes
  labs(x = "Threshold", y = "Change in NMB", title = "NMB and 95% Confidence Interval") +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ group, scales = "free_y") +  # Facetted plot with grid layout
  theme(legend.position = "none") +  # Remove legend
  ggtitle("Incremental NMB with respect to the standard of care and 95% confidence intervals")  # Add title


ggsave(
  filename = "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_sus_res_ci.png",
  plot = plot_NMB_FLQres_sus,
  width = 15,
  height = 4
)

#### SMDM abstract figures

ts=12

#DALY
FLQres_class_DALY_data = PMDT_performance_sus_res %>%
  select(Threshold, Exp_FLQ_DALY_ResClass, Exp_DLM_DALY_ResClass) %>%
  rename("FLQ" = "Exp_FLQ_DALY_ResClass", "DLM" = "Exp_DLM_DALY_ResClass") %>%
  mutate(Classification = "Classified FLQ resistant")

FLQsus_class_DALY_data = PMDT_performance_sus_res %>%
  select(Threshold, Exp_FLQ_DALY_SusClass, Exp_DLM_DALY_SusClass) %>%
  rename("FLQ" = "Exp_FLQ_DALY_SusClass", "DLM" = "Exp_DLM_DALY_SusClass") %>%
  mutate(Classification = "Classified FLQ susceptible")

all_data_DALY = bind_rows(FLQres_class_DALY_data, FLQsus_class_DALY_data)

# Plot
plot_daly = ggplot(all_data_DALY, aes(x = Threshold, y = FLQ, color = "FLQ", group = Classification)) +
  geom_line() +
  geom_line(aes(y = DLM, color = "DLM")) +  # Different color for the second line
  labs(color = "Treatment", x = "Threshold", y = "Disability-adjusted life years", title = "Disability-adjusted life years depending on treatment and the prediction model classification") +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ Classification, scales = "free_y") +  # Facetted plot with grid layout
  scale_color_manual(values = c("DLM" = "#84ceff", "FLQ" = "#004c6d"), labels = c("Delamanid", "Fluoroquinolone")) +  # Manual color and label assignment
  theme(legend.position = "right")  # Adjust legend position



#Cost
FLQres_class_Cost_data = PMDT_performance_sus_res %>%
  select(Threshold, Exp_FLQ_Cost_ResClass, Exp_DLM_Cost) %>%
  rename("FLQ" = "Exp_FLQ_Cost_ResClass", "DLM" = "Exp_DLM_Cost") %>%
  mutate(Classification = "Classified FLQ resistant")

FLQsus_class_Cost_data = PMDT_performance_sus_res %>%
  select(Threshold, Exp_FLQ_Cost_SusClass, Exp_DLM_Cost) %>%
  rename("FLQ" = "Exp_FLQ_Cost_SusClass", "DLM" = "Exp_DLM_Cost") %>%
  mutate(Classification = "Classified FLQ susceptible")

all_data_Cost = bind_rows(FLQres_class_Cost_data, FLQsus_class_Cost_data)

# Plot
plot_cost = ggplot(all_data_Cost, aes(x = Threshold, y = FLQ, color = "FLQ", group = Classification)) +
  geom_line() +
  geom_line(aes(y = DLM, color = "DLM")) +  # Different color for the second line
  labs(color = "Treatment", x = "Threshold", y = "Increase in cost", title = "Increase in cost depending on treatment and the prediction model classification") +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ Classification, scales = "free_y") +  # Facetted plot with grid layout
  scale_color_manual(values = c("DLM" = "#84ceff", "FLQ" = "#004c6d"), labels = c("Delamanid", "Fluoroquinolone")) +  # Manual color and label assignment
  theme(legend.position = "right")  # Adjust legend position

#NMB

#Cost
NMB_ResClass_data = PMDT_performance_sus_res %>%
  select(Threshold, NMB_ResClass) %>%
  rename("NMB" = "NMB_ResClass") %>%
  mutate(Classification = "Classified FLQ resistant")

#Cost
NMB_SusClass_data = PMDT_performance_sus_res %>%
  select(Threshold, NMB_SusClass) %>%
  rename("NMB" = "NMB_SusClass") %>%
  mutate(Classification = "Classified FLQ susceptible")

all_data_NMB = bind_rows(NMB_ResClass_data, NMB_SusClass_data)

# Plot
plot_nmb = ggplot(all_data_NMB, aes(x = Threshold, y = NMB, group = Classification)) +
  geom_line() +
  geom_hline(yintercept = 0, linetype = "dashed", color = "red") + 
  labs(color = "", x = "Threshold", y = "Change in NMB", title = "Incremental NMB with respect to the standard of care depending on the prediction model classification") +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ Classification, scales = "free_y") +  # Facetted plot with grid layout
  theme()  # Adjust legend position

NMB_Cost_DALY_classification_plot = grid.arrange(plot_daly, plot_cost, plot_nmb, ncol = 1)

ggsave(
  filename = "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_Cost_DALY_classification.png",
  plot = NMB_Cost_DALY_classification_plot,
  width = 15,
  height = 10
)

