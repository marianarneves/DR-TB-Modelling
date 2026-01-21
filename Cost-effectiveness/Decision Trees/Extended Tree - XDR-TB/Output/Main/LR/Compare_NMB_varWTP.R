#Temporarily avoid saving the graphs
ggsave <- function(...) { invisible(NULL) }

#Remove the temporary block on saving the graphs
rm(ggsave)

library(readxl)
library(dplyr)
library(tidyr)
library(ggplot2)
library(gridExtra)
library(patchwork)
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Analysis/DR_TB_PMDT_Analysis_Functions.R')


setwd('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Results Comparison/')

# === Read dataset - with Calibration===

#Classification
Classification_PMDT = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx')
Classification_PMDT_output_loc = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/Input_V10/')
Classification_PMDT_varwtp = read_output_tolist_varyingwtp(Classification_PMDT_output_loc, "PMDT_","bootstrapping_samplesize200", 6)

#Prediction
Prediction_PMDT = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM input Only/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx')
Prediction_PMDT_output_loc = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM input Only/Input_V10/')
Prediction_PMDT_varwtp = read_output_tolist_varyingwtp(Prediction_PMDT_output_loc, "PMDT_","bootstrapping_samplesize200", 6)

#Prediction model without DT
PMnoDT = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM without DM/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx')
PMnoDT_output_loc = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM without DM/Input_V10/')
PMnoDT_varwtp = read_output_tolist_varyingwtp(PMnoDT_output_loc, "PMDT_","bootstrapping_samplesize200", 6)

# === Read dataset - No Calibration===

#Classification
Classification_PMDT_nocal = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM Bootstrap/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx')
Classification_PMDT_output_loc_nocal = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM Bootstrap/Input_V10/')
Classification_PMDT_varwtp_nocal = read_output_tolist_varyingwtp(Classification_PMDT_output_loc_nocal, "PMDT_","bootstrapping_samplesize200", 6)

#Prediction
Prediction_PMDT_nocal = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM input Only/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx')
Prediction_PMDT_output_loc_nocal = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM input Only/Input_V10/')
Prediction_PMDT_varwtp_nocal = read_output_tolist_varyingwtp(Prediction_PMDT_output_loc_nocal, "PMDT_","bootstrapping_samplesize200", 6)

#Prediction model without DT
PMnoDT_nocal = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM without DM/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx')
PMnoDT_output_loc_nocal = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/No Calibration/PM without DM/Input_V10/')
PMnoDT_varwtp_nocal = read_output_tolist_varyingwtp(PMnoDT_output_loc_nocal, "PMDT_","bootstrapping_samplesize200", 6)

#########################
#     Calibration       #
#########################

# === Classification ===

Classification_PMDT_NMBavg_overall = Classification_PMDT_varwtp$output_df %>%
  compute_avg_nmb_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

Classification_PMDT_max_Thresholds <- Classification_PMDT_NMBavg_overall %>%
  slice_max(NMB_avg, with_ties = FALSE) %>%  # Get the maximum NMB_avg across all Thresholds
  pull(Threshold) %>%
  as.data.frame()

Classification_PMDT_max_Thresholds$wtp = seq(1:6)
colnames(Classification_PMDT_max_Thresholds) = c("Threshold", "wtp")

Classification_PMDT_NMBavg_FLQstatus = Classification_PMDT_varwtp$output_df %>%
  compute_avg_nmb_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

Classification_PMDT_NMB_avg = bind_rows(Classification_PMDT_NMBavg_FLQstatus, Classification_PMDT_NMBavg_overall)%>%
  group_by(wtp, FLQ_Status) 

Classification_PMDT_NMB_avg_max = data.frame()
for (i in 1:length(Classification_PMDT_max_Thresholds$wtp)){
  
  ax = Classification_PMDT_NMB_avg %>%
    filter(Threshold == Classification_PMDT_max_Thresholds$Threshold[i] & wtp == Classification_PMDT_max_Thresholds$wtp[i])
  
  Classification_PMDT_NMB_avg_max = bind_rows(Classification_PMDT_NMB_avg_max, ax)
  
}

Classification_PMDT_NMB_avg_max = Classification_PMDT_NMB_avg_max %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQs',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQs',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))


# Plot
Classification_PMDT_plot_NMB_wtp = ggplot(Classification_PMDT_NMB_avg_max, 
                                          aes(x = wtp_real, y = NMB_avg)) +
  geom_line(color = "#3BA3A2") +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg), fill = "#3BA3A2", alpha = 0.2) +
  labs(x = "Willingness-to-pay value as a portion of the Republic of Moldova's gross domestic product per capita",
       y = "Change in NMB",
       title = "NMB and 95% Confidence Interval") +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ FLQ_Status_m, scales = "free_y") +
  theme(legend.position = "none",
        text = element_text(size = 18),
        plot.title = element_text(size = 16, face = "bold"),
        axis.title = element_text(size = 16),
        axis.text = element_text(size = 16),
        legend.text = element_text(size = 16),
        legend.title = element_text(size = 16)) +
  ggtitle("Figure. Gain in NMB for varying willingness-to-pay thresholds when the classification-based method\nis used to inform treatment regimens compared to using the standard FLQ-containing regimen for all\npatients with RR-TB. The shaded regions show the 95% confidence intervals.")

# Save the final plot
ggsave(filename = "Classification_PMDT_plot_NMB_wtp.png", plot = Classification_PMDT_plot_NMB_wtp, width = 12, height = 6)


# Plot
Classification_PMDT_plot_NMB_wtp = ggplot(Classification_PMDT_NMB_avg_max, aes(x = wtp_real, y = NMB_avg))  +
  geom_line(size = 0.8, color = "#3BA3A2") +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg), fill = "#3BA3A2", alpha = 0.2) +
  geom_hline(yintercept = 0, color = "black") +
  geom_vline(xintercept = 0.5, color = "black") +
  guides(
    color = guide_legend(nrow = 1, title = NULL),
    fill = guide_legend(title = NULL)
  ) + 
  labs(x = "Willingness-to-pay value as a portion of the Republic of Moldova's gross domestic product per capita",
       y = "Change in NMB") +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ FLQ_Status_m, scales = "free_y") +
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    panel.background = element_blank(),
    plot.background = element_blank(),
    panel.grid.major = element_line(color = "grey80"),
    panel.grid.minor = element_line(color = "grey90"),
    axis.line = element_blank(),
    plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 16),
    axis.text = element_text(size = 16),
    legend.text = element_text(size = 16),
    legend.title = element_text(size = 16),strip.text = element_text(size = 18,  color = "black"),  # Text color
    strip.background = element_blank()  # ❌ This removes the grey background box
  ) 


# Save the final plot
ggsave(filename = "Classification_PMDT_plot_NMB_wtp.png", plot = Classification_PMDT_plot_NMB_wtp, width = 12, height = 6)


#Prediction

Prediction_PMDT_NMBavg_overall = Prediction_PMDT_varwtp$output_df %>%
  compute_avg_nmb_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

Prediction_PMDT_max_Thresholds <- Prediction_PMDT_NMBavg_overall %>%
  slice_max(NMB_avg, with_ties = FALSE) %>%  # Get the maximum NMB_avg across all Thresholds
  pull(Threshold) %>%
  as.data.frame()

Prediction_PMDT_max_Thresholds$wtp = seq(1:6)
colnames(Prediction_PMDT_max_Thresholds) = c("Threshold", "wtp")

Prediction_PMDT_NMBavg_FLQstatus = Prediction_PMDT_varwtp$output_df %>%
  compute_avg_nmb_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

Prediction_PMDT_NMB_avg = bind_rows(Prediction_PMDT_NMBavg_FLQstatus, Prediction_PMDT_NMBavg_overall)%>%
  group_by(wtp, FLQ_Status) 

Prediction_PMDT_NMB_avg_max = data.frame()
for (i in 1:length(Prediction_PMDT_max_Thresholds$wtp)){
  
  ax = Prediction_PMDT_NMB_avg %>%
    filter(Threshold == Prediction_PMDT_max_Thresholds$Threshold[i] & wtp == Prediction_PMDT_max_Thresholds$wtp[i])
  
  Prediction_PMDT_NMB_avg_max = bind_rows(Prediction_PMDT_NMB_avg_max, ax)
  
}

Prediction_PMDT_NMB_avg_max = Prediction_PMDT_NMB_avg_max %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQs',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQs',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))

#PM without DT - threshold 0.5 and max sense and spec opt corr
PMnoDT_NMBavg_overall = PMnoDT_varwtp$output_df %>%
  compute_avg_nmb_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

PMnoDT_NMBavg_FLQstatus = PMnoDT_varwtp$output_df %>%
  compute_avg_nmb_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

PMnoDT_NMB_avg = bind_rows(PMnoDT_NMBavg_FLQstatus, PMnoDT_NMBavg_overall)%>%
  group_by(wtp, FLQ_Status) 

# Function to find and filter the closest thresholds
filter_closest_thresholds <- function(data, column, targets) {
  closest_thresholds <- sapply(targets, function(t) data[[column]][which.min(abs(data[[column]] - t))])
  filtered_data <- data %>%
    filter(!!sym(column) %in% closest_thresholds)
  return(filtered_data)
}

PMnoDT_selected_Threshold_0.5 = filter_closest_thresholds(PMnoDT_NMBavg_overall, 'Threshold', 0.5)
PMnoDT_selected_Threshold_maxoptcorrsensspec = filter_closest_thresholds(PMnoDT_NMBavg_overall, 'Threshold', 0.154)

PMnoDT_NMB_selected_Threshold_0.5 = data.frame()
PMnoDT_NMB_selected_Threshold_maxoptcorrsensspec = data.frame()
for (i in 1:length(PMnoDT_selected_Threshold_0.5$wtp)){
  
  ax1 = PMnoDT_NMB_avg %>%
    filter(Threshold == PMnoDT_selected_Threshold_0.5$Threshold[i] & wtp == PMnoDT_selected_Threshold_0.5$wtp[i])
  PMnoDT_NMB_selected_Threshold_0.5 = bind_rows(PMnoDT_NMB_selected_Threshold_0.5, ax1)
  
  ax2 = PMnoDT_NMB_avg %>%
    filter(Threshold == PMnoDT_selected_Threshold_maxoptcorrsensspec$Threshold[i] & wtp == PMnoDT_selected_Threshold_maxoptcorrsensspec$wtp[i])
  PMnoDT_NMB_selected_Threshold_maxoptcorrsensspec = bind_rows(PMnoDT_NMB_selected_Threshold_maxoptcorrsensspec, ax2)
  
}

PMnoDT_NMB_selected_Threshold_0.5 = PMnoDT_NMB_selected_Threshold_0.5 %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQs',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQs',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))

PMnoDT_NMB_selected_Threshold_maxoptcorrsensspec = PMnoDT_NMB_selected_Threshold_maxoptcorrsensspec %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQs',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQs',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))


# Plot
PMnoDT_plot_NMB_wtp = ggplot(PMnoDT_NMB_selected_Threshold_maxoptcorrsensspec, aes(x = wtp_real, y = NMB_avg, fill = FLQ_Status)) +
  geom_line() +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg), fill = "grey", alpha = 0.5) +  # Specify fill outside aes
  labs(x = "Willingness-to-pay value as a portion of the Republic of Moldova's gross domestic product per capita", y = "Change in NMB", title = "NMB and 95% Confidence Interval") +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ FLQ_Status_m, scales = "free_y") +  # Facetted plot with grid layout
  theme(legend.position = "none") +  # Remove legend
  ggtitle("Incremental NMB with respect to the standard of care and 95% confidence intervals")  # Add title


#Combining plots

Classification_NMB = Classification_PMDT_NMB_avg_max %>%
  mutate(Model = "PIDEMc: Classification-based method")

Prediction_NMB = Prediction_PMDT_NMB_avg_max%>%
  mutate(Model = "PIDEMp: Probability-based method")

Threshold_0.5_NMB = PMnoDT_NMB_selected_Threshold_0.5%>%
  mutate(Model = "Prediction model: Classification threshold 0.5")

Threshold_maxoptcorrsensspec_NMB = PMnoDT_NMB_selected_Threshold_maxoptcorrsensspec%>%
  mutate(Model = "Prediction model: Classification threshold that maximizes the Youden's index")

NMB = rbind(Classification_NMB, Prediction_NMB, Threshold_0.5_NMB,Threshold_maxoptcorrsensspec_NMB
            )

plot_NMB_wtp = ggplot(NMB, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line() +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Model), alpha = 0.5) +  # Map fill to Model
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's gross domestic product per capita", 
    y = "Change in NMB", 
    #title = "Incremental NMB with respect to the standard of care and 95% confidence intervals",
    color = "DT Input",  # Change legend title for line colors
    fill = "DT Input"    # Change legend title for ribbon fill
  ) +
  facet_grid(. ~ FLQ_Status_m, scales = "free_y") +  # Facetted plot with grid layout
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    legend.text = element_text(size = 18),
    strip.text = element_text(face = "bold")  # Make facet titles bold
  ) 
  #ggtitle("Incremental NMB with respect to the standard of care and 95% confidence intervals")  # Add title


# Save the final plot
ggsave(filename = "plot_NMB_wtp.png", plot = plot_NMB_wtp, width = 18, height = 6)


### Average NMB Only

# Filter for Panel A data
NMB_panel_A_calibrated <- NMB %>%
  filter(FLQ_Status_m == "A. Among all patients with TB\nresistant to rifampicin")

# Reorder the levels of Model in NMB_panel_A
NMB_panel_A_calibrated$Model <- factor(NMB_panel_A_calibrated$Model, levels = c("PIDEMp: Probability-based method", "PIDEMc: Classification-based method", "Prediction model: Classification threshold 0.5", "Prediction model: Classification threshold that maximizes the Youden's index"))

# Plot only Panel A without panel titles
plot_NMB_wtp_panel_A <- ggplot(NMB_panel_A_calibrated, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line(size = 1) +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Model), alpha = 0.15, color = NA) +
  geom_hline(yintercept = 0, color = "black") +
  geom_vline(xintercept = 0.5, color = "black") +
  guides(
    color = guide_legend(nrow = 4, title = NULL),
    fill = guide_legend(title = NULL)
  ) + 
  scale_y_continuous(breaks = seq(-2000, 2000, by = 500)) +
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's\ngross domestic product per capita", 
    y = "Average change in NMB\nper patient with RR-TB", 
    color = "Method",
    fill = "Method"
  ) +
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    panel.background = element_blank(),
    plot.background = element_blank(),
    panel.grid.major = element_line(color = "grey80"),
    panel.grid.minor = element_line(color = "grey90"),
    axis.line = element_blank(),
    plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 16),
    axis.text = element_text(size = 16),
    legend.text = element_text(size = 16),
    legend.title = element_text(size = 16)
  ) 
  #ggtitle("Figure. Gain in NMB for varying willingness-to-pay thresholds when proposed methods are used to inform\ntreatment regimens compared to using the standard FLQ-containing regimen for all patients with RR-TB.\nThe shaded regions show the 95% confidence intervals.")


# Save the final plot
ggsave(filename = "plot_NMB_wtp_average_allmethods.png", plot = plot_NMB_wtp_panel_A, width = 10, height = 8)

# Filter for Panel A data - PIDEM methods only
NMB_panel_A_calibrated_PIDEMonly <- NMB_panel_A_calibrated %>%
  filter(Model == "PIDEMp: Probability-based method" | Model == "PIDEMc: Classification-based method")

# Define the colors for the methods
colors <- c(
  "PIDEMp: Probability-based method" = "steelblue",  # Light blue
  "PIDEMc: Classification-based method" = "coral2",  # Darker blue
  "Prediction model: Classification threshold 0.5" = "orange1",  # Darkest blue
  "Prediction model: Classification threshold that maximizes the Youden's index" = "seagreen"  # Green
)


# === Panel A: PIDEM only with CI ===
plot_NMB_wtp_panel_A_PIDEMonly <- ggplot(NMB_panel_A_calibrated_PIDEMonly, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line(size = 1) +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Model), alpha = 0.15, color = NA) +
  geom_hline(yintercept = 0, color = "black") +
  geom_vline(xintercept = 0.5, color = "black") +
  guides(
    color = guide_legend(nrow = 2, title = NULL),
    fill = guide_legend(title = NULL)
  ) + 
  scale_y_continuous(breaks = seq(-250, 2000, by = 250), limits = c(-250, 2000)) +
  scale_color_manual(values = colors) +  # Manually set the colors
  scale_fill_manual(values = colors) +  # Manually set the fill colors
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's\ngross domestic product per capita", 
    y = "Average change in NMB per patient with RR-TB\ncompared to the standardized regimen"
  ) +
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    panel.background = element_blank(),
    plot.background = element_blank(),
    panel.grid.major = element_line(color = "grey80"),
    panel.grid.minor = element_line(color = "grey90"),
    axis.line = element_blank(),
    plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 16),
    axis.text = element_text(size = 16),
    legend.text = element_text(size = 16),
    legend.title = element_text(size = 16)
  ) 

#  ggtitle("Figure. Gain in NMB for varying willingness-to-pay thresholds when proposed methods are used\nto inform treatment regimens compared to using the standard FLQ-containing regimen for all\npatients with RR-TB. The shaded regions show the 95% confidence intervals.")

# Save the final plot
ggsave(filename = "plot_NMB_wtp_average_PIDEMonly.png", plot = plot_NMB_wtp_panel_A_PIDEMonly, width = 12, height = 7)


# === Panel A: All methods, no CI ===
plot_NMB_wtp_panel_A_noCI <- ggplot(NMB_panel_A_calibrated, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line(size = 1) +
  geom_hline(yintercept = 0, color = "black") +
  geom_vline(xintercept = 0.5, color = "black") +
  guides(
    color = guide_legend(nrow = 4, title = NULL),
    fill = guide_legend(title = NULL)
  ) + 
  scale_y_continuous(breaks = seq(-250, 1750, by = 500), limits = c(-250, 1750)) +
  scale_color_manual(values = colors) +  # Manually set the colors
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's\ngross domestic product per capita", 
    y = "Average change in NMB per patient with RR-TB\ncompared to the standardized regimen"
  ) +
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    panel.background = element_blank(),
    plot.background = element_blank(),
    panel.grid.major = element_line(color = "grey80"),
    panel.grid.minor = element_line(color = "grey90"),
    axis.line = element_blank(),
    plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 16),
    axis.text = element_text(size = 16),
    legend.text = element_text(size = 16),
    legend.title = element_text(size = 16)
  )


# Save the final plot
ggsave(filename = "plot_NMB_wtp_average_allmethods_noCI.png", plot = plot_NMB_wtp_panel_A_noCI, width = 12, height = 7)

#### Plot only Prediction and classification


NMB_pred_class = rbind(Classification_NMB, Prediction_NMB)

plot_NMB_pred_class_wtp = ggplot(NMB_pred_class, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line(size = 0.8) +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Model), alpha = 0.3) +  # Map fill to Model
  geom_hline(yintercept = 0, color = "black") +
  geom_vline(xintercept = 0.5, color = "black") +
  scale_y_continuous(breaks = seq(-5000, 40000, by = 5000)) +
  guides(
    color = guide_legend(nrow = 1, title = NULL),
    fill = guide_legend(title = NULL)
  ) + 
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's\ngross domestic product per capita in year 2022", 
    y = "Gain in NMB per patient", 
    #title = "Incremental NMB with respect to the standard of care and 95% confidence intervals"
  ) +
  facet_grid(. ~ FLQ_Status_m, scales = "free_y") +  # Facetted plot with grid layout
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    panel.background = element_blank(),
    plot.background = element_blank(),
    panel.grid.major = element_line(color = "grey80"),
    panel.grid.minor = element_line(color = "grey90"),
    axis.line = element_blank(),
    plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 16),
    axis.text = element_text(size = 16),
    legend.text = element_text(size = 16),
    legend.title = element_text(size = 16),strip.text = element_text(size = 18,  color = "black"),  # Text color
    strip.background = element_blank()  # ❌ This removes the grey background box
  ) 
#ggtitle("Incremental NMB with respect to the standard of care and 95% confidence intervals")  # Add title

# Save the final plot
ggsave(filename = "plot_NMB_pred_class_wtp.png", plot = plot_NMB_pred_class_wtp, width = 12, height = 6)


############################
#     No Calibration       #
############################

# === Classification ===

Classification_PMDT_NMBavg_overall_nocal = Classification_PMDT_varwtp_nocal$output_df %>%
  compute_avg_nmb_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

Classification_PMDT_max_Thresholds_nocal <- Classification_PMDT_NMBavg_overall_nocal %>%
  slice_max(NMB_avg, with_ties = FALSE) %>%  # Get the maximum NMB_avg across all Thresholds
  pull(Threshold) %>%
  as.data.frame()

Classification_PMDT_max_Thresholds_nocal$wtp = seq(1:6)
colnames(Classification_PMDT_max_Thresholds_nocal) = c("Threshold", "wtp")

Classification_PMDT_NMBavg_FLQstatus_nocal = Classification_PMDT_varwtp_nocal$output_df %>%
  compute_avg_nmb_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

Classification_PMDT_NMB_avg_nocal = bind_rows(Classification_PMDT_NMBavg_FLQstatus_nocal, Classification_PMDT_NMBavg_overall_nocal)%>%
  group_by(wtp, FLQ_Status) 

Classification_PMDT_NMB_avg_max_nocal = data.frame()
for (i in 1:length(Classification_PMDT_max_Thresholds_nocal$wtp)){
  
  ax_nocal = Classification_PMDT_NMB_avg_nocal %>%
    filter(Threshold == Classification_PMDT_max_Thresholds_nocal$Threshold[i] & wtp == Classification_PMDT_max_Thresholds_nocal$wtp[i])
  
  Classification_PMDT_NMB_avg_max_nocal = bind_rows(Classification_PMDT_NMB_avg_max_nocal, ax_nocal)
  
}

Classification_PMDT_NMB_avg_max_nocal = Classification_PMDT_NMB_avg_max_nocal %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQs',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQs',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))


# Plot
Classification_PMDT_plot_NMB_wtp_nocal = ggplot(Classification_PMDT_NMB_avg_max_nocal, aes(x = wtp_real, y = NMB_avg, fill = FLQ_Status)) +
  geom_line() +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg), fill = "grey", alpha = 0.5) +  # Specify fill outside aes
  labs(x = "Willingness-to-pay value as a portion of the Republic of Moldova's gross domestic product per capita", y = "Change in NMB", title = "NMB and 95% Confidence Interval") +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ FLQ_Status_m, scales = "free_y") +  # Facetted plot with grid layout
  theme(legend.position = "none") +  # Remove legend
  ggtitle("Incremental NMB with respect to the standard of care and 95% confidence intervals")  # Add title


#Prediction

Prediction_PMDT_NMBavg_overall_nocal = Prediction_PMDT_varwtp_nocal$output_df %>%
  compute_avg_nmb_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

Prediction_PMDT_max_Thresholds_nocal <- Prediction_PMDT_NMBavg_overall_nocal %>%
  slice_max(NMB_avg, with_ties = FALSE) %>%  # Get the maximum NMB_avg across all Thresholds
  pull(Threshold) %>%
  as.data.frame()

Prediction_PMDT_max_Thresholds_nocal$wtp = seq(1:6)
colnames(Prediction_PMDT_max_Thresholds_nocal) = c("Threshold", "wtp")

Prediction_PMDT_NMBavg_FLQstatus_nocal = Prediction_PMDT_varwtp_nocal$output_df %>%
  compute_avg_nmb_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

Prediction_PMDT_NMB_avg_nocal = bind_rows(Prediction_PMDT_NMBavg_FLQstatus_nocal, Prediction_PMDT_NMBavg_overall_nocal)%>%
  group_by(wtp, FLQ_Status) 

Prediction_PMDT_NMB_avg_max_nocal = data.frame()
for (i in 1:length(Prediction_PMDT_max_Thresholds$wtp)){
  
  ax_nocal = Prediction_PMDT_NMB_avg_nocal %>%
    filter(Threshold == Prediction_PMDT_max_Thresholds_nocal$Threshold[i] & wtp == Prediction_PMDT_max_Thresholds_nocal$wtp[i])
  
  Prediction_PMDT_NMB_avg_max_nocal = bind_rows(Prediction_PMDT_NMB_avg_max_nocal, ax_nocal)
  
}

Prediction_PMDT_NMB_avg_max_nocal = Prediction_PMDT_NMB_avg_max_nocal %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQs',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQs',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))


#Prediction cal no cal

Prediction_NMB_calnocal = Prediction_PMDT_NMB_avg_max %>%
  mutate(Calibration = "Calibration") %>%
  bind_rows(Prediction_PMDT_NMB_avg_max_nocal %>%
  mutate(Calibration = "No Calibration")
  )

# Plot only Panel A without panel titles
plot_NMB_wtp_prediction_calnocal <- ggplot(Prediction_NMB_calnocal, aes(x = wtp_real, y = NMB_avg, color = Calibration)) +
  geom_line(size = 0.8) +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Calibration), alpha = 0.15, color = NA) +
  geom_hline(yintercept = 0, color = "black") +
  geom_vline(xintercept = 0.5, color = "black") +
  guides(
    color = guide_legend(nrow = 1, title = NULL),
    fill = guide_legend(title = NULL)
  ) + 
  #scale_y_continuous(breaks = seq(-3000, 2000, by = 500)) +
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's\ngross domestic product per capita", 
    y = "Average change in NMB\nper patient with RR-TB", 
    color = "Method",
    fill = "Method"
  ) +
  facet_grid(. ~ FLQ_Status_m, scales = "free_y") + 
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    panel.background = element_blank(),
    plot.background = element_blank(),
    panel.grid.major = element_line(color = "grey80"),
    panel.grid.minor = element_line(color = "grey90"),
    axis.line = element_blank(),
    plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 16),
    axis.text = element_text(size = 16),
    legend.text = element_text(size = 16),
    legend.title = element_text(size = 16),strip.text = element_text(size = 18,  color = "black"),  # Text color
    strip.background = element_blank()  # ❌ This removes the grey background box
  ) 

ggsave(filename = "plot_NMB_wtp_prediction_calnocal.png", plot = plot_NMB_wtp_prediction_calnocal, width = 12, height = 6)


Prediction_NMB_calnocal_panel_A = Prediction_NMB_calnocal %>%
  filter(FLQ_Status_m == "A. Among all patients with TB\nresistant to rifampicin")
  
ggplot(Prediction_NMB_calnocal_panel_A, aes(x = wtp_real, y = NMB_avg, color = Calibration)) +
  geom_line(size = 1) +  # Increase the line thickness
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Calibration), alpha = 0.15, color = NA) +  # Remove ribbon border lines
  geom_hline(yintercept = 0, color = "black") +  # Stronger line at y = 0
  geom_vline(xintercept = 0.5, color = "black") +  # Stronger line at x = 0.5
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's gross domestic product per capita", 
    y = "Average change in NMB\nper patient with RR-TB", 
    color = "Method",  # Change legend title for line colors
    fill = "Method"    # Change legend title for ribbon fill
  ) +
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
#ggtitle("Figure. Gain in NMB for varying willingness-to-pay thresholds when proposed methods are used to inform\ntreatment regimens compared to using the standard FLQ-containing regimen for all patients with RR-TB.\nThe shaded regions show the 95% confidence intervals.")


#PM without DT - threshold 0.5 and max sense and spec opt corr
PMnoDT_NMBavg_overall_nocal = PMnoDT_varwtp_nocal$output_df %>%
  compute_avg_nmb_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

PMnoDT_NMBavg_FLQstatus_nocal = PMnoDT_varwtp_nocal$output_df %>%
  compute_avg_nmb_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

PMnoDT_NMB_avg_nocal = bind_rows(PMnoDT_NMBavg_FLQstatus_nocal, PMnoDT_NMBavg_overall_nocal)%>%
  group_by(wtp, FLQ_Status) 

# Function to find and filter the closest thresholds
filter_closest_thresholds <- function(data, column, targets) {
  closest_thresholds <- sapply(targets, function(t) data[[column]][which.min(abs(data[[column]] - t))])
  filtered_data <- data %>%
    filter(!!sym(column) %in% closest_thresholds)
  return(filtered_data)
}

PMnoDT_selected_Threshold_0.5_nocal = filter_closest_thresholds(PMnoDT_NMBavg_overall_nocal, 'Threshold', 0.5)
PMnoDT_selected_Threshold_maxoptcorrsensspec_nocal = filter_closest_thresholds(PMnoDT_NMBavg_overall_nocal, 'Threshold',  0.154)

PMnoDT_NMB_selected_Threshold_0.5_nocal = data.frame()
PMnoDT_NMB_selected_Threshold_maxoptcorrsensspec_nocal = data.frame()
for (i in 1:length(PMnoDT_selected_Threshold_0.5_nocal$wtp)){
  
  ax1_nocal = PMnoDT_NMB_avg_nocal %>%
    filter(Threshold == PMnoDT_selected_Threshold_0.5_nocal$Threshold[i] & wtp == PMnoDT_selected_Threshold_0.5_nocal$wtp[i])
  PMnoDT_NMB_selected_Threshold_0.5_nocal = bind_rows(PMnoDT_NMB_selected_Threshold_0.5_nocal, ax1_nocal)
  
  ax2_nocal = PMnoDT_NMB_avg_nocal %>%
    filter(Threshold == PMnoDT_selected_Threshold_maxoptcorrsensspec_nocal$Threshold[i] & wtp == PMnoDT_selected_Threshold_maxoptcorrsensspec_nocal$wtp[i])
  PMnoDT_NMB_selected_Threshold_maxoptcorrsensspec_nocal = bind_rows(PMnoDT_NMB_selected_Threshold_maxoptcorrsensspec_nocal, ax2_nocal)
  
}

PMnoDT_NMB_selected_Threshold_0.5_nocal = PMnoDT_NMB_selected_Threshold_0.5_nocal %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQs',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQs',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))

PMnoDT_NMB_selected_Threshold_maxoptcorrsensspec_nocal = PMnoDT_NMB_selected_Threshold_maxoptcorrsensspec_nocal %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB\nresistant to rifampicin\nand FLQs',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB\nresistant to rifampicin\nbut susceptible to FLQs',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB\nresistant to rifampicin'
  ))


# Plot
PMnoDT_plot_NMB_wtp_nocal = ggplot(PMnoDT_NMB_selected_Threshold_maxoptcorrsensspec_nocal, aes(x = wtp_real, y = NMB_avg, fill = FLQ_Status)) +
  geom_line() +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg), fill = "grey", alpha = 0.5) +  # Specify fill outside aes
  labs(x = "Willingness-to-pay value as a portion of the Republic of Moldova's gross domestic product per capita", y = "Change in NMB", title = "NMB and 95% Confidence Interval") +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ FLQ_Status_m, scales = "free_y") +  # Facetted plot with grid layout
  theme(legend.position = "none") +  # Remove legend
  ggtitle("Incremental NMB with respect to the standard of care and 95% confidence intervals")  # Add title


#Combining plots

Classification_NMB_nocal = Classification_PMDT_NMB_avg_max_nocal %>%
  mutate(Model = "PIDEMc: Classification-based method")

Prediction_NMB_nocal = Prediction_PMDT_NMB_avg_max_nocal %>%
  mutate(Model = "PIDEMp: Probability-based method")

Threshold_0.5_NMB_nocal = PMnoDT_NMB_selected_Threshold_0.5_nocal %>%
  mutate(Model = "Prediction model: Classification threshold 0.5")

Threshold_maxoptcorrsensspec_NMB_nocal = PMnoDT_NMB_selected_Threshold_maxoptcorrsensspec_nocal %>%
  mutate(Model = "Prediction model: Classification threshold that maximizes the Youden's index")

NMB_nocal = rbind(Classification_NMB_nocal, Prediction_NMB_nocal, Threshold_0.5_NMB_nocal,Threshold_maxoptcorrsensspec_NMB_nocal
)

plot_NMB_wtp_nocal = ggplot(NMB_nocal, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line() +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Model), alpha = 0.5) +  # Map fill to Model
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's gross domestic product per capita", 
    y = "Change in NMB", 
    #title = "Incremental NMB with respect to the standard of care and 95% confidence intervals",
    color = "DT Input",  # Change legend title for line colors
    fill = "DT Input"    # Change legend title for ribbon fill
  ) +
  facet_grid(. ~ FLQ_Status_m, scales = "free_y") +  # Facetted plot with grid layout
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    legend.text = element_text(size = 18),
    strip.text = element_text(face = "bold")  # Make facet titles bold
  ) 
#ggtitle("Incremental NMB with respect to the standard of care and 95% confidence intervals")  # Add title


# Save the final plot
ggsave(filename = "plot_NMB_wtp_nocal.png", plot = plot_NMB_wtp_nocal, width = 18, height = 6)

### Average NMB Only

# Filter for Panel A data
NMB_panel_A_nocal <- NMB_nocal %>%
  filter(FLQ_Status_m == "A. Among all patients with TB\nresistant to rifampicin")

# Reorder the levels of Model in NMB_panel_A
NMB_panel_A_nocal$Model <- factor(NMB_panel_A_nocal$Model, levels = c("PIDEMc: Classification-based method", "PIDEMp: Probability-based method", "Prediction model: Classification threshold 0.5", "Prediction model: Classification threshold that maximizes the Youden's index"))

# Plot only Panel A without panel titles
plot_NMB_wtp_panel_A_nocal <- ggplot(NMB_panel_A_nocal, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line(size = 1) +  # Increase the line thickness
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Model), alpha = 0.15, color = NA) +  # Remove ribbon border lines
  geom_hline(yintercept = 0, color = "black") +  # Stronger line at y = 0
  geom_vline(xintercept = 0.5, color = "black") +  # Stronger line at x = 0.5
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's gross domestic product per capita", 
    y = "Average change in NMB\nper patient with RR-TB", 
    color = "Method",  # Change legend title for line colors
    fill = "Method"    # Change legend title for ribbon fill
  ) +
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
  #ggtitle("Figure. Gain in NMB for varying willingness-to-pay thresholds when proposed methods are used to inform\ntreatment regimens compared to using the standard FLQ-containing regimen for all patients with RR-TB.\nThe shaded regions show the 95% confidence intervals.")


# Save the final plot
ggsave(filename = "plot_NMB_wtp_average_nocal.png", plot = plot_NMB_wtp_panel_A_nocal, width = 18, height = 6)

# Plot only Panel A without CI
plot_NMB_wtp_panel_A_noCI_nocal <- ggplot(NMB_panel_A_nocal, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line() +  # Increase the line thickness
  geom_hline(yintercept = 0, color = "black") +  # Stronger line at y = 0
  geom_vline(xintercept = 0.5, color = "black") +  # Stronger line at x = 0.5
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's gross domestic product per capita", 
    y = "Average change in NMB\nper patient with RR-TB", 
    color = "Method",  # Change legend title for line colors
    fill = "Method"    # Change legend title for ribbon fill
  ) +
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    legend.text = element_text(size = 18),
    panel.background = element_blank(),  # Remove panel background color
    plot.background = element_blank(),   # Remove plot background color
    panel.grid.major = element_line(color = "grey80"),  # Lighter major grid lines
    panel.grid.minor = element_line(color = "grey90"),  # Even lighter minor grid lines
    axis.line = element_blank()  # Remove default axis lines (handled by hline/vline)
  )+
  ggtitle("Figure. Gain in NMB for varying willingness-to-pay thresholds when proposed methods are used to inform\ntreatment regimens compared to using the standard FLQ-containing regimen for all patients with RR-TB.\nThe shaded regions show the 95% confidence intervals.")


# Save the final plot
ggsave(filename = "plot_NMB_wtp_average_allmethods_noCI_nocal.png", plot = plot_NMB_wtp_panel_A_noCI_nocal, width = 18, height = 6)


#### Plot only Prediction and classification


NMB_pred_class_nocal = rbind(Classification_NMB_nocal, Prediction_NMB_nocal) %>%
  mutate(Model2 = ifelse(Model == 'Classification-based method', 'PIDEMc', 'PIDEMp'))

plot_NMB_pred_class_wtp_nocal = ggplot(NMB_pred_class_nocal, aes(x = wtp_real, y = NMB_avg, color = Model2)) +
  geom_line() +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Model2), alpha = 0.5) +  # Map fill to Model
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's gross domestic product per capita", 
    y = "Change in NMB\nper patient", 
    #title = "Incremental NMB with respect to the standard of care and 95% confidence intervals",
    color = "Method",  # Change legend title for line colors
    fill = "Method"    # Change legend title for ribbon fill
  ) +
  facet_grid(. ~ FLQ_Status_m, scales = "free_y") +  # Facetted plot with grid layout
  theme(
    legend.position = "bottom", 
    text = element_text(size = 25),
    legend.text = element_text(size = 25),
    strip.text = element_text(face = "bold")  # Make facet titles bold
  ) 
#ggtitle("Incremental NMB with respect to the standard of care and 95% confidence intervals")  # Add title

ggsave(filename = "plot_NMB_pred_class_wtp_nocal.png", plot = plot_NMB_pred_class_wtp_nocal, width = 18, height = 6)

 ggplot(Classification_PMDT_NMB_avg_max, aes(x = wtp_real, y = NMB_avg))  +
  geom_line(size = 0.8, color = "#3BA3A2") +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg), fill = "#3BA3A2", alpha = 0.2) +
  geom_hline(yintercept = 0, color = "black") +
  geom_vline(xintercept = 0.5, color = "black") +
  guides(
    color = guide_legend(nrow = 1, title = NULL),
    fill = guide_legend(title = NULL)
  ) + 
  labs(x = "Willingness-to-pay value as a portion of the Republic of Moldova's gross domestic product per capita",
       y = "Change in NMB") +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ FLQ_Status_m, scales = "free_y") +
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    panel.background = element_blank(),
    plot.background = element_blank(),
    panel.grid.major = element_line(color = "grey80"),
    panel.grid.minor = element_line(color = "grey90"),
    axis.line = element_blank(),
    plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 16),
    axis.text = element_text(size = 16),
    legend.text = element_text(size = 16),
    legend.title = element_text(size = 16),strip.text = element_text(size = 18,  color = "black"),  # Text color
    strip.background = element_blank()  # ❌ This removes the grey background box
  ) 



#### All methods - Calibration versus No Calibration

NMB_panel_A_all = NMB_panel_A_calibrated %>%
  mutate(Calibration = "A. Using Calibrated Predictions") %>%
  bind_rows(NMB_panel_A_nocal%>%
              mutate(Calibration = "B. Using Uncalibrated Predictions") )

NMB_panel_A_all$Model <- factor(NMB_panel_A_all$Model, levels = c(
  "PIDEMc: Classification-based method", "PIDEMp: Probability-based method", 
  "Prediction model: Classification threshold 0.5", 
  "Prediction model: Classification threshold that maximizes the Youden's index"
))




 ggplot(NMB_panel_A_calibrated_PIDEMonly, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line(size = 1) +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Model), alpha = 0.15, color = NA) +
  geom_hline(yintercept = 0, color = "black") +
  geom_vline(xintercept = 0.5, color = "black") +
  guides(
    color = guide_legend(nrow = 2, title = NULL),
    fill = guide_legend(title = NULL)
  ) + 
  scale_y_continuous(breaks = seq(-500, 3000, by = 500), limits = c(-500, 3000)) +
  scale_color_manual(values = colors) +  # Manually set the colors
  scale_fill_manual(values = colors) +  # Manually set the fill colors
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's\ngross domestic product per capita", 
    y = "Average change in NMB per patient with RR-TB\ncompared to the standardized regimen"
  ) +
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    panel.background = element_blank(),
    plot.background = element_blank(),
    panel.grid.major = element_line(color = "grey80"),
    panel.grid.minor = element_line(color = "grey90"),
    axis.line = element_blank(),
    plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 16),
    axis.text = element_text(size = 16),
    legend.text = element_text(size = 16),
    legend.title = element_text(size = 16)
  ) 


# Plot only Panel A without panel titles
plot_NMB_wtp_panel_A_calnocal <- ggplot(NMB_panel_A_all, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line(size = 1) +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Model), alpha = 0.15, color = NA) +
  geom_hline(yintercept = 0, color = "black") +
  geom_vline(xintercept = 0.5, color = "black") +
  guides(
    color = guide_legend(nrow = 4, title = NULL),
    fill = guide_legend(title = NULL)
  ) + 
  scale_y_continuous(breaks = seq(-3000, 2000, by = 500)) +
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's\ngross domestic product per capita in year 2022", 
    y = "Average change in NMB\nper patient with RR-TB", 
    color = "Method",
    fill = "Method"
  ) +
  facet_grid(. ~ Calibration, scales = "free_y") + 
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    panel.background = element_blank(),
    plot.background = element_blank(),
    panel.grid.major = element_line(color = "grey80"),
    panel.grid.minor = element_line(color = "grey90"),
    axis.line = element_blank(),
    plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 16),
    axis.text = element_text(size = 16),
    legend.text = element_text(size = 16),
    legend.title = element_text(size = 16),strip.text = element_text(size = 18,  color = "black"),  # Text color
    strip.background = element_blank()  # ❌ This removes the grey background box
    ) 


ggsave(filename = "plot_NMB_pred_class_wtp_calnocal.png", plot = plot_NMB_wtp_panel_A_calnocal, width = 10, height = 8)

#### All methods - Calibration versus No Calibration - No CI

# Plot only Panel A without panel titles
plot_NMB_wtp_panel_A_calnocal_noci <- ggplot(NMB_panel_A_all, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line(size = 1) +
  #geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Model), alpha = 0.15, color = NA) +
  geom_hline(yintercept = 0, color = "black") +
  geom_vline(xintercept = 0.5, color = "black") +
  guides(
    color = guide_legend(nrow = 4, title = NULL),
    fill = guide_legend(title = NULL)
  ) + 
  scale_y_continuous(breaks = seq(-3000, 2000, by = 500)) +
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's\ngross domestic product per capita in year 2022", 
    y = "Gain in NMB per patient with RR-TB", 
    color = "Method",
    fill = "Method"
  ) +
  facet_grid(. ~ Calibration, scales = "free_y") + 
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    panel.background = element_blank(),
    plot.background = element_blank(),
    panel.grid.major = element_line(color = "grey80"),
    panel.grid.minor = element_line(color = "grey90"),
    axis.line = element_blank(),
    plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 16),
    axis.text = element_text(size = 16),
    legend.text = element_text(size = 16),
    legend.title = element_text(size = 16),strip.text = element_text(size = 18,  color = "black"),  # Text color
    strip.background = element_blank()  # ❌ This removes the grey background box
  ) 


ggsave(filename = "plot_NMB_pred_class_wtp_calnocal_noci.png", plot = plot_NMB_wtp_panel_A_calnocal_noci, width = 10, height = 8)


#--- Alternative:

# Prepare the dataset with line breaks in model names for facets
NMB_panel_A_all <- NMB_panel_A_calibrated %>%
  mutate(Calibration = "A. Using Calibrated Predictions") %>%
  bind_rows(NMB_panel_A_nocal %>%
              mutate(Calibration = "B. Using Uncalibrated Predictions")) %>%
  mutate(Model_facet = case_when(
    Model == "PIDEMc: Classification-based method" ~ "PIDEMc:\nClassification-based method",
    Model == "PIDEMp: Probability-based method" ~ "PIDEMp:\nProbability-based method",
    Model == "Prediction model: Classification threshold 0.5" ~ "Based on classification\nthreshold = 0.5",
    Model == "Prediction model: Classification threshold that maximizes the Youden's index" ~ "Based on classification\nthreshold that maximizes\nthe optmism-corrected\nYouden's index"
  ))

# Plot with separate panels for each model and calibration status
plot_NMB_wtp_panel_A_calnocal <- ggplot(NMB_panel_A_all, aes(x = wtp_real, y = NMB_avg, color = Model)) +
  geom_line(size = 1) +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg, fill = Model), alpha = 0.15, color = NA) +
  geom_hline(yintercept = 0, color = "black") +
  guides(
    color = guide_legend(nrow = 4, title = NULL),
    fill = guide_legend(title = NULL)
  ) + 
  scale_y_continuous(breaks = seq(-1500, 2000, by = 500)) +
  scale_x_continuous(
    breaks = seq(1, max(NMB_panel_A_all$wtp_real), by = 1),
    expand = c(0, 0)  # Remove padding around the x-axis
  ) + 
  labs(
    x = "Willingness-to-pay value as a portion of the Republic of Moldova's\ngross domestic product per capita", 
    y = "Average change in NMB\nper patient with RR-TB", 
    color = "Method",
    fill = "Method"
  ) +
  facet_grid(Model_facet ~ Calibration, scales = "fixed", space = "fixed") +  # Use Model_facet for row labels
  theme(
    legend.position = "bottom", 
    text = element_text(size = 18),
    panel.background = element_blank(),
    plot.background = element_blank(),
    panel.grid.major = element_line(color = "grey80"),
    panel.grid.minor = element_line(color = "grey90"),
    axis.line = element_blank(),
    plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 16),
    axis.text = element_text(size = 16),
    legend.text = element_text(size = 16),
    legend.title = element_text(size = 16),
    strip.text.x = element_text(size = 18, color = "black"),  # Customize column titles
    strip.text.y = element_text(size = 18, color = "black", angle = 0, hjust = 0),  # Customize row titles
    strip.background = element_blank(),  # Remove background box
    panel.border = element_rect(color = "black", fill = NA, size = 1),  # Add borders around each panel
    panel.spacing = unit(1.5, "lines")  # Increase spacing between panels
  ) +
  coord_cartesian(xlim = c(0.5, max(NMB_panel_A_all$wtp_real)), ylim = c(-1500, 2000))  # Set x and y-axis limits without removing data

# Print the plot
print(plot_NMB_wtp_panel_A_calnocal)

