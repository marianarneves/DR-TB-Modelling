library(ggplot2)
library(dplyr)
library(tidyverse)

DecisionTree_probs_original  = readxl::read_xlsx('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM Boostrap/Optimism Correction/Original/DecisionTree_probs_alt.xlsx')
DecisionTree_probs_adjusted  = readxl::read_xlsx('/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM Boostrap/Optimism Correction/Adjusted/DecisionTree_probs_alt.xlsx')


# Extract the class size
positiveclass_all = DecisionTree_probs_original %>%
  filter(str_detect(Variable, "positiveclass"))

thresholds = unique(positiveclass_all$threshold)

positiveclass_small = matrix(nrow = length(thresholds), ncol = 200)

for(i in 1:length(thresholds)){
  positiveclass_all_ax = positiveclass_all %>%
    filter(threshold == thresholds[i])

  print(positiveclass_all_ax)
  
  for (j in 1:(dim(positiveclass_all_ax)[2]-2)) {
    positiveclass_small[i,j] = ifelse(sum(positiveclass_all_ax[j+1]<27)> 1, 1, 0)
  }  
}
  

negativeclass_all = DecisionTree_probs_original %>%
  filter(str_detect(Variable, "negativeclass"))

thresholds = unique(negativeclass_all$threshold)

negativeclass_small = matrix(nrow = length(thresholds), ncol = 200)

for(i in 1:length(thresholds)){
  negativeclass_all_ax = negativeclass_all %>%
    filter(threshold == thresholds[i])
  
  print(negativeclass_all_ax)
  
  for (j in 1:(dim(negativeclass_all_ax)[2]-2)) {
    negativeclass_small[i,j] = ifelse(sum(negativeclass_all_ax[j+1]<27)> 1, 1, 0)
  }  
}


#Comparing the probabilities calculated with traditional and alternative
P_R_R_original = DecisionTree_probs_original %>%
  filter(Variable == 'P_R_R') %>%
  select(-Variable) %>%
  pivot_longer(cols = -threshold, names_to = "metric", values_to = "value") %>%
  bind_rows(DecisionTree_probs_original %>%
              filter(Variable == 'P_R_R_main') %>%
              select(threshold, Bootstrap_sample_1) %>%
              rename(value = Bootstrap_sample_1) %>%
              mutate(metric = "mainPM"),
            DecisionTree_probs_original %>%
              filter(Variable == 'P_R_R') %>%
              select(-Variable) %>%
              pivot_longer(cols = -threshold, names_to = "metric", values_to = "value") %>%
              group_by(threshold) %>%
              summarise(value = mean(value)) %>%
              mutate(metric = 'meanBootstrap')
            ) %>%
  # Create a new column in the dataset for legend grouping
  mutate(Source = ifelse(metric == "mainPM", "Main Prediction Model", ifelse(metric == "meanBootstrap", "Mean of Bootstrap Samples", "Bootstrap Samples")), Method = "A. P(D+|T+) - Original")


P_S_S_original = DecisionTree_probs_original %>%
  filter(Variable == 'P_S_S') %>%
  select(-Variable) %>%
  pivot_longer(cols = -threshold, names_to = "metric", values_to = "value") %>%
  bind_rows(DecisionTree_probs_original %>%
              filter(Variable == 'P_S_S_main') %>%
              select(threshold, Bootstrap_sample_1) %>%
              rename(value = Bootstrap_sample_1) %>%
              mutate(metric = "mainPM"),
            DecisionTree_probs_original %>%
              filter(Variable == 'P_S_S') %>%
              select(-Variable) %>%
              pivot_longer(cols = -threshold, names_to = "metric", values_to = "value") %>%
              group_by(threshold) %>%
              summarise(value = mean(value)) %>%
              mutate(metric = 'meanBootstrap')
  ) %>%
  # Create a new column in the dataset for legend grouping
  mutate(Source = ifelse(metric == "mainPM", "Main Prediction Model", ifelse(metric == "meanBootstrap", "Mean of Bootstrap Samples", "Bootstrap Samples")), Method = "C. P(D-|T-) - Original")

P_R_R_adjusted = DecisionTree_probs_adjusted %>%
  filter(Variable == 'P_R_R') %>%
  select(-Variable) %>%
  pivot_longer(cols = -threshold, names_to = "metric", values_to = "value") %>%
  bind_rows(DecisionTree_probs_adjusted %>%
              filter(Variable == 'P_R_R_main') %>%
              select(threshold, Bootstrap_sample_1) %>%
              rename(value = Bootstrap_sample_1) %>%
              mutate(metric = "mainPM"),
            DecisionTree_probs_adjusted %>%
              filter(Variable == 'P_R_R') %>%
              select(-Variable) %>%
              pivot_longer(cols = -threshold, names_to = "metric", values_to = "value") %>%
              group_by(threshold) %>%
              summarise(value = mean(value)) %>%
              mutate(metric = 'meanBootstrap')
  ) %>%
  # Create a new column in the dataset for legend grouping
  mutate(Source = ifelse(metric == "mainPM", "Main Prediction Model", ifelse(metric == "meanBootstrap", "Mean of Bootstrap Samples", "Bootstrap Samples")), Method = "B. P(D+|T+) - Adjusted")

P_S_S_adjusted = DecisionTree_probs_adjusted %>%
  filter(Variable == 'P_S_S') %>%
  select(-Variable) %>%
  pivot_longer(cols = -threshold, names_to = "metric", values_to = "value")%>%
  bind_rows(DecisionTree_probs_adjusted %>%
              filter(Variable == 'P_S_S_main') %>%
              select(threshold, Bootstrap_sample_1) %>%
              rename(value = Bootstrap_sample_1) %>%
              mutate(metric = "mainPM"),
            DecisionTree_probs_adjusted %>%
              filter(Variable == 'P_S_S') %>%
              select(-Variable) %>%
              pivot_longer(cols = -threshold, names_to = "metric", values_to = "value") %>%
              group_by(threshold) %>%
              summarise(value = mean(value)) %>%
              mutate(metric = 'meanBootstrap')
  ) %>%
  # Create a new column in the dataset for legend grouping
  mutate(Source = ifelse(metric == "mainPM", "Main Prediction Model", ifelse(metric == "meanBootstrap", "Mean of Bootstrap Samples", "Bootstrap Samples")), Method = "D. P(D-|T-) - Adjusted")

DT_probs_combined = P_R_R_original %>%
  bind_rows(P_S_S_original, 
            P_R_R_adjusted, 
            P_S_S_adjusted)

DT_probs_combined_adj =  DT_probs_combined %>%
  bind_rows(
    DT_probs_combined %>%
      group_by(metric, Method) %>%
      slice_max(threshold, n = 1) %>%
      mutate(threshold = 1),  # Assign Threshold = 1
    
    DT_probs_combined %>%
      group_by(metric, Method) %>%
      slice_min(threshold, n = 1) %>%
      mutate(threshold = 0)   # Assign Threshold = 0
  )


# Plot the graph
trajectory_plot <- ggplot(DT_probs_combined_adj, aes(x = threshold, y = value, group = metric)) +
  geom_line(aes(color = Source), 
            data = DT_probs_combined_adj %>% filter(metric != "mainPM"), alpha = 0.3) +  # Semi-transparency for others
  geom_line(aes(color = Source), 
            data = DT_probs_combined_adj %>% filter(metric == "mainPM"), alpha = 1) +  # Full opacity for mainPM
  scale_color_manual(values = c("Main Prediction Model" = "#FF0000", "Mean of Bootstrap Samples" = "black", "Bootstrap Samples" = "darkgrey")) +  # Custom legend colors
  scale_x_continuous(limits = c(0, 1))+
  labs(x = "Classification Threshold", y = "Decision Tree Probability") +
  #ggtitle(title = "Trajectory of the Decision Tree Probabilities Calculated Using the\nMain Prediction Model and Bootstrap Samples by Threshold")+
  facet_wrap(~ Method, nrow = 2, ncol = 2) +  # Facetted plot with grid layout
  theme_minimal(base_size = 16) +
  xlim(0, 1) +
  ylim(0, 1) +
  theme(legend.position = "bottom",
        plot.background = element_rect(fill = "white", color = NA),
        panel.background = element_rect(fill = "white", color = NA),
        panel.grid = element_line(color = "gray90"),
        plot.title = element_text(size = 16, face = "bold"),
        axis.title = element_text(size = 16),
        axis.text = element_text(size = 16),
        legend.text = element_text(size = 16),
        legend.title = element_text(size = 16)) +
  guides(color = guide_legend(override.aes = list(alpha = 1), title = NULL))  # Keep legend colors fully visible

ggsave(
  filename = '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM Boostrap/Optimism Correction/DecisionTreeProb_comparison.png',
  plot = trajectory_plot,
  width = 10,
  height = 8,
  bg = "white"
)


# === Only adjusted graph ===


P_R_R_adjusted_m = DecisionTree_probs_adjusted %>%
  filter(Variable == 'P_R_R') %>%
  select(-Variable) %>%
  pivot_longer(cols = -threshold, names_to = "metric", values_to = "value") %>%
  bind_rows(DecisionTree_probs_adjusted %>%
              filter(Variable == 'P_R_R_main') %>%
              select(threshold, Bootstrap_sample_1) %>%
              rename(value = Bootstrap_sample_1) %>%
              mutate(metric = "mainPM"),
            DecisionTree_probs_adjusted %>%
              filter(Variable == 'P_R_R') %>%
              select(-Variable) %>%
              pivot_longer(cols = -threshold, names_to = "metric", values_to = "value") %>%
              group_by(threshold) %>%
              summarise(value = mean(value)) %>%
              mutate(metric = 'meanBootstrap')
  ) %>%
  # Create a new column in the dataset for legend grouping
  mutate(Source = ifelse(metric == "mainPM", "Main Prediction Model", ifelse(metric == "meanBootstrap", "Mean of Bootstrap Samples", "Bootstrap Samples")), Method = "A. P(D+|T+) - Adjusted")

P_S_S_adjusted_m = DecisionTree_probs_adjusted %>%
  filter(Variable == 'P_S_S') %>%
  select(-Variable) %>%
  pivot_longer(cols = -threshold, names_to = "metric", values_to = "value")%>%
  bind_rows(DecisionTree_probs_adjusted %>%
              filter(Variable == 'P_S_S_main') %>%
              select(threshold, Bootstrap_sample_1) %>%
              rename(value = Bootstrap_sample_1) %>%
              mutate(metric = "mainPM"),
            DecisionTree_probs_adjusted %>%
              filter(Variable == 'P_S_S') %>%
              select(-Variable) %>%
              pivot_longer(cols = -threshold, names_to = "metric", values_to = "value") %>%
              group_by(threshold) %>%
              summarise(value = mean(value)) %>%
              mutate(metric = 'meanBootstrap')
  ) %>%
  # Create a new column in the dataset for legend grouping
  mutate(Source = ifelse(metric == "mainPM", "Main Prediction Model", ifelse(metric == "meanBootstrap", "Mean of Bootstrap Samples", "Bootstrap Samples")), Method = "B. P(D-|T-) - Adjusted")



DT_probs_combined_adjusted = P_R_R_adjusted_m %>%
  bind_rows(P_S_S_adjusted_m)

DT_probs_combined_adjusted_adj =  DT_probs_combined_adjusted %>%
  bind_rows(
    DT_probs_combined_adjusted %>%
      group_by(metric, Method) %>%
      slice_max(threshold, n = 1) %>%
      mutate(threshold = 1),  # Assign Threshold = 1
    
    DT_probs_combined_adjusted %>%
      group_by(metric, Method) %>%
      slice_min(threshold, n = 1) %>%
      mutate(threshold = 0)   # Assign Threshold = 0
  ) %>%
  mutate(method_m = gsub(" - Adjusted", "", Method),
         Source = recode(Source,
                         "Main Prediction Model" = "Apparent Estimate",
                         "Mean of Bootstrap Samples" = "Bias-Adjusted Estimates"))

# Plot the graph
trajectory_plot_adjustedonly <- ggplot(DT_probs_combined_adjusted_adj, aes(x = threshold, y = value, group = metric)) +
  # Bootstrap samples (lighter grey lines)
  geom_line(aes(color = Source),
            data = DT_probs_combined_adjusted_adj %>% 
              filter(metric != "mainPM", Source == "Bootstrap Samples"), 
            alpha = 0.3) +
  
  # Main prediction model (red line)
  geom_line(aes(color = Source),
            data = DT_probs_combined_adjusted_adj %>% 
              filter(metric == "mainPM"), 
            alpha = 1, size = 0.8) +
  
  # Mean of bootstrap samples (black line, thick and opaque)
  geom_line(aes(color = Source),
            data = DT_probs_combined_adjusted_adj %>% 
              filter(Source == "Bias-Adjusted Estimates"), 
            alpha = 1, size = 0.8) +  # <-- Adjust thickness here
  
  scale_color_manual(values = c("Apparent Estimate" = "#FF0000",
                                "Bias-Adjusted Estimates" = "black",
                                "Bootstrap Samples" = "darkgrey")) +
  scale_x_continuous(limits = c(0, 1)) +
  labs(x = "Classification Threshold", y = "") +
  facet_wrap(~ method_m, nrow = 1, ncol = 2) +
  theme_minimal(base_size = 16) +
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
    legend.text = element_text(size = 16),
    legend.title = element_text(size = 16),
    strip.text = element_text(size = 18,  color = "black"),  # Text color
    #strip.background = element_rect(fill = "black", color = "white", linewidth = 1)  # Background fill and border
  )+
  guides(color = guide_legend(override.aes = list(alpha = 1), title = NULL))

ggsave(
  filename = '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM Boostrap/Optimism Correction/DecisionTreeProb_comparison_adjustedonly.png',
  plot = trajectory_plot_adjustedonly,
  width = 10,
  height = 6,
  bg = "white"
)


