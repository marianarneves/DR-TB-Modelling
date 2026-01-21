library(readxl)
library(dplyr)
library(tidyr)
library(ggplot2)
library(gridExtra)
library(patchwork)

setwd('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM Boostrap/Optimism Correction/Adjusted/')
#1000 samples

PMDT_sampled_1000_05wtp = readxl::read_xlsx('PMDT_wtp1bootstrapping_samplesize200.xlsx')
PMDT_sampled_1000_1wtp = readxl::read_xlsx('PMDT_wtp2bootstrapping_samplesize200.xlsx')
PMDT_sampled_1000_15wtp = readxl::read_xlsx('PMDT_wtp3bootstrapping_samplesize200.xlsx')
PMDT_sampled_1000_2wtp = readxl::read_xlsx('PMDT_wtp4bootstrapping_samplesize200.xlsx')
PMDT_sampled_1000_25wtp = readxl::read_xlsx('PMDT_wtp5bootstrapping_samplesize200.xlsx')
PMDT_sampled_1000_3wtp = readxl::read_xlsx('PMDT_wtp6bootstrapping_samplesize200.xlsx')

# Function to compute summary statistics with WTP column
compute_summary_stats <- function(data, wtp_value, alpha = 0.05) {
  data %>%
    group_by(Threshold) %>%
    summarise(
      NMB = mean(NMB_SdTreat_DM),
      uciNMB = NMB + qt(0.975, df = length(NMB_SdTreat_DM) - 1) * sd(NMB_SdTreat_DM) / sqrt(length(NMB_SdTreat_DM)),
      lciNMB = NMB - qt(0.975, df = length(NMB_SdTreat_DM) - 1) * sd(NMB_SdTreat_DM) / sqrt(length(NMB_SdTreat_DM))
    ) %>%
    mutate(WTP = wtp_value)  # Add WTP value for the group
}

find_max_nmb_threshold <- function(data) {
  data %>%
    filter(NMB == max(NMB, na.rm = TRUE)) %>%
    select(Threshold) %>%
    as.numeric()
}

#############################
#   Overall change in NMB   #
#############################

#wtp = 1
PMDT_sampled_1000_1wtp_avg = compute_summary_stats(PMDT_sampled_1000_1wtp, wtp_value = 1)
maxNMB_threshold_1wtp = find_max_nmb_threshold(PMDT_sampled_1000_1wtp_avg)

#wtp = 2
PMDT_sampled_1000_2wtp_avg = compute_summary_stats(PMDT_sampled_1000_2wtp, wtp_value = 2)
maxNMB_threshold_2wtp = find_max_nmb_threshold(PMDT_sampled_1000_2wtp_avg)

#wtp = 3
PMDT_sampled_1000_3wtp_avg = compute_summary_stats(PMDT_sampled_1000_3wtp, wtp_value = 3)
maxNMB_threshold_3wtp = find_max_nmb_threshold(PMDT_sampled_1000_3wtp_avg)

###################################
#   Change in NMB - varying wtp   #
###################################

# Define the minimum and maximum threshold
min_threshold <- min(PMDT_sampled_1000_1wtp_avg$Threshold[!is.na(PMDT_sampled_1000_1wtp_avg$NMB)])  # Adjust this to your desired minimum threshold
max_threshold <- max(PMDT_sampled_1000_1wtp_avg$Threshold[!is.na(PMDT_sampled_1000_1wtp_avg$NMB)])  # Adjust this to your desired maximum threshold

PMDT_sampled_1000_1wtp_avg_graph <- 
  ggplot(PMDT_sampled_1000_1wtp_avg, aes(x = Threshold, y = NMB)) +
  # Add semi-transparent shaded areas outside the min and max thresholds using annotate
  annotate("rect", xmin = -Inf, xmax = min_threshold, ymin = -Inf, ymax = Inf, 
           fill = "grey", alpha = 0.5) +  # Set alpha to make it see through
  annotate("rect", xmin = max_threshold, xmax = Inf, ymin = -Inf, ymax = Inf, 
           fill = "grey", alpha = 0.5) +  # Set alpha to make it see through
  geom_line(color = "#004c6d", size = 0.7) + # Set color within geom_line
  scale_y_continuous(breaks = seq(-750, 1000, by = 50), limits = c(-750, 1000)) +  # Set y-axis ticks by 0.05
  scale_x_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.1)) + # Set x-axis limits and breaks
  ylab("Change in NMB") +
  xlab("Classification threshold") +
  theme_minimal() +
  theme(
    legend.position = "bottom",
    text = element_text(size = 18)
  )

ggsave(
  filename = 'PMDT_sampled_1000_1wtp_avgNMB.png',
  plot = PMDT_sampled_1000_1wtp_avg_graph,
  width = 8,
  height = 6,
  bg = "white"
)

PMDT_sampled_1000_2wtp_avg_graph <- 
  ggplot(PMDT_sampled_1000_2wtp_avg, aes(x = Threshold, y = NMB)) +
  # Add semi-transparent shaded areas outside the min and max thresholds using annotate
  annotate("rect", xmin = -Inf, xmax = min_threshold, ymin = -Inf, ymax = Inf, 
           fill = "grey", alpha = 0.5) +  # Set alpha to make it see through
  annotate("rect", xmin = max_threshold, xmax = Inf, ymin = -Inf, ymax = Inf, 
           fill = "grey", alpha = 0.5) +  # Set alpha to make it see through
  geom_line(color = "#004c6d", size = 0.7) + # Set color within geom_line
  scale_y_continuous(breaks = seq(-750, 1000, by = 50), limits = c(-750, 1000)) +  # Set y-axis ticks by 0.05
  scale_x_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.1)) + # Set x-axis limits and breaks
  ylab("Change in NMB") +
  xlab("Classification threshold") +
  theme_minimal() +
  theme(
    legend.position = "bottom",
    text = element_text(size = 18)
  )

PMDT_sampled_1000_3wtp_avg_graph <- 
  ggplot(PMDT_sampled_1000_3wtp_avg, aes(x = Threshold, y = NMB)) +
  # Add semi-transparent shaded areas outside the min and max thresholds using annotate
  annotate("rect", xmin = -Inf, xmax = min_threshold, ymin = -Inf, ymax = Inf, 
           fill = "grey", alpha = 0.5) +  # Set alpha to make it see through
  annotate("rect", xmin = max_threshold, xmax = Inf, ymin = -Inf, ymax = Inf, 
           fill = "grey", alpha = 0.5) +  # Set alpha to make it see through
  geom_line(color = "#004c6d", size = 0.7) + # Set color within geom_line
  scale_y_continuous(breaks = seq(-750, 1000, by = 50), limits = c(-750, 1000)) +  # Set y-axis ticks by 0.05
  scale_x_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.1)) + # Set x-axis limits and breaks
  ylab("Change in NMB") +
  xlab("Classification threshold") +
  theme_minimal() +
  theme(
    legend.position = "bottom",
    text = element_text(size = 18)
  )

# Joint comparison wtp 

PMDT_sampled_1000_wtpcompare = PMDT_sampled_1000_1wtp_avg %>%
  bind_rows(PMDT_sampled_1000_2wtp_avg) %>%
  bind_rows(PMDT_sampled_1000_3wtp_avg)%>%
  mutate(WTP_m = case_when(
    WTP == 1 ~ 'WTP = 1 GDP',
    WTP == 2 ~ 'WTP = 2 GDP',
    WTP == 3  ~ 'WTP = 3 GDP'
  ))

PMDT_sampled_1000_wtpcompare_adj = PMDT_sampled_1000_wtpcompare %>%
  bind_rows(
    PMDT_sampled_1000_wtpcompare %>%
      group_by(WTP) %>%
      slice_max(Threshold, n = 1) %>%
      mutate(Threshold = 1),  # Assign Threshold = 1
    
    PMDT_sampled_1000_wtpcompare %>%
      group_by(WTP) %>%
      slice_min(Threshold, n = 1) %>%
      mutate(Threshold = 0)   # Assign Threshold = 0
  )

max_points <- PMDT_sampled_1000_wtpcompare_adj %>%
  group_by(WTP_m) %>%
  slice_max(order_by = NMB, n = 1)

# Plot
plot_NMB_wtp = ggplot(PMDT_sampled_1000_wtpcompare_adj, aes(x = Threshold, y = NMB, fill = WTP)) +
  geom_line() +
  geom_ribbon(aes(ymin = lciNMB, ymax = uciNMB), alpha = 0.3, fill = "grey") +
  labs(x = "Classification threshold", y = "Change in NMB", title = "NMB and 95% Confidence Interval") +
  # Set x-axis limits from 0 to 1
  scale_x_continuous(limits = c(0, 1)) +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ WTP_m, scales = "free_y") +  # Facetted plot with grid layout
  theme(legend.position = "none") +  # Remove legend
  ggtitle("Incremental NMB with respect to the standard of care and\n95% confidence intervals") +
  # Add vertical line at max Threshold for each facet
  geom_vline(data = max_points, aes(xintercept = Threshold), color = "red", linetype = "dashed") +
  # Add annotation for max Threshold, positioned to the right
  geom_text(data = max_points, 
            aes(x = Threshold + 0.05 ,  # Small offset to the right
                y = NMB + 100, 
                label = paste0("t = ", round(Threshold, 2))), 
            hjust = 0,  # Left-aligned text to appear on the right side
            size = 5, 
            color = "red")+
  theme_minimal(base_size = 16) +  # Set a base font size (adjust as needed)
  theme(
    legend.position = "top",
    text = element_text(size = 16),  # Increase font size for all text elements
    axis.title = element_text(size = 18),  # Increase axis labels
    axis.text = element_text(size = 16),  # Increase axis tick labels
    plot.title = element_text(size = 20, face = "bold"),  # Increase and bold the title
    legend.text = element_text(size = 16),  # Increase legend text size
    legend.title = element_text(size = 18)  # Increase legend title size
  ) 

# Save the final plot
ggsave(filename = "NMB_varyingWTP.png", plot = plot_NMB_wtp, width = 13, height = 5)

####################################################################
#   Number of people for whom DLM would be the optimal treatment   #
####################################################################

# Group by Threshold and calculate the overall proportion of Opt_Treat == 'DLM'
Opt_treat_DLM_overall <- PMDT_sampled_1000_1wtp %>%
  group_by(Threshold) %>%
  summarise(Opt_treat_DLM = mean(Opt_Treat == 'DLM', na.rm = TRUE), .groups = 'drop') %>%
  mutate(FLQ_Status = "Overall")

# Group by Threshold and FLQ_Status, then calculate the proportion of Opt_Treat == 'DLM'
Opt_treat_DLM_byFLQ <- PMDT_sampled_1000_1wtp %>%
  group_by(Threshold, FLQ_Status) %>%
  summarise(Opt_treat_DLM = mean(Opt_Treat == 'DLM', na.rm = TRUE), .groups = 'drop')

# Combine both data frames
Opt_treat_DLM_combined <- bind_rows(Opt_treat_DLM_overall, Opt_treat_DLM_byFLQ)

# Define a custom blue-toned color palette
custom_blue_colors <- c(
  "Overall" = "#004c6d",   # Medium blue
  "FLQ Resistant" = "#6baed6",  # Light blue
  "FLQ Susceptible" = "#3182bd"   # Darker blue
)

# Plot the results with custom blue colors and y-axis ticks by 0.05
DLM_presc_prop_byFLQstatus_plot <- ggplot(Opt_treat_DLM_combined, aes(x = Threshold, y = Opt_treat_DLM, color = FLQ_Status, group = FLQ_Status)) +
  geom_line(size = 0.7) +
  geom_point(size = 0.7) +
  scale_color_manual(values = custom_blue_colors) +  # Use custom blue colors
  labs(
    x = "Classification threshold",
    y = "Proportion of patients prescribed DLM",
    color = "FLQ Status"
  ) +
  scale_y_continuous(breaks = seq(0, 0.3, by = 0.05), limits = c(0, 0.3)) +  # Set y-axis ticks by 0.05
  scale_x_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.1)) + # Set x-axis limits and breaks
  theme_minimal() +
  theme(
    legend.position = "bottom",   
    text = element_text(size = 18)
  )

# Save the plot
ggsave(
  filename = 'DLM_presc_prop_byFLQstatus.png',
  plot = DLM_presc_prop_byFLQstatus_plot,
  width = 8, height = 6
)

##########################################
#   Change in NMB by PM classification   #
##########################################

PMDT_sampled_1000_1wtp_avg_FLQstatus = PMDT_sampled_1000_1wtp%>%
  group_by(Threshold, PM_classification)%>%
  summarise(NMB = mean(NMB_SdTreat_DM)) 

ts=12

#DALY
PMDT_sampled_1000_1wtp_avgDALY_class = PMDT_sampled_1000_1wtp%>%
  group_by(Threshold, PM_classification) %>%
  summarise(FLQ = mean(DALY_FLQ), DLM = mean(DALY_DLM)) 

# Plot
plot_daly = ggplot(PMDT_sampled_1000_1wtp_avgDALY_class, aes(x = Threshold, y = FLQ, color = "FLQ", group = PM_classification)) +
  geom_line() +
  geom_line(aes(y = DLM, color = "DLM")) +  # Different color for the second line
  labs(color = "Treatment", x = "Threshold", y = "Disability-adjusted life years", title = "Disability-adjusted life years depending on treatment and the prediction model classification") +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ PM_classification, scales = "free_y") +  # Facetted plot with grid layout
  scale_color_manual(values = c("DLM" = "#84ceff", "FLQ" = "#004c6d"), labels = c("Clofazimine", "Fluoroquinolone")) +  # Manual color and label assignment
  theme(legend.position = "right")  # Adjust legend position


#Cost
PMDT_sampled_1000_1wtp_avgCost_class = PMDT_sampled_1000_1wtp%>%
  group_by(Threshold, PM_classification) %>%
  summarise(FLQ = mean(Cost_FLQ), DLM = mean(Cost_DLM)) 

# Plot
plot_cost = ggplot(PMDT_sampled_1000_1wtp_avgCost_class, aes(x = Threshold, y = FLQ, color = "FLQ", group = PM_classification)) +
  geom_line() +
  geom_line(aes(y = DLM, color = "DLM")) +  # Different color for the second line
  labs(color = "Treatment", x = "Threshold", y = "Increase in cost", title = "Increase in cost depending on treatment and the prediction model classification") +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ PM_classification, scales = "free_y") +  # Facetted plot with grid layout
  scale_color_manual(values = c("DLM" = "#84ceff", "FLQ" = "#004c6d"), labels = c("Clofazimine", "Fluoroquinolone")) +  # Manual color and label assignment
  theme(legend.position = "right")  # Adjust legend position

#NMB

# # #NMB
# PMDT_sampled_1000_1wtp_avgNMB_class = PMDT_sampled_1000_1wtp%>%
#   group_by(Threshold, PM_classification) %>%
#   summarise(NMB_SdTreat_FLQ = mean(NMB),
#             NMB_DLM = mean(NMB_DLM)) %>%
#   mutate(NMB_FLQ_DLM = NMB_SdTreat_FLQ - NMB_DLM)
# 
# # # Plot
# plot_nmb = ggplot(PMDT_sampled_1000_1wtp_avgNMB_class, aes(x = Threshold, y = NMB_SdTreat_FLQ, color = "NMB FLQ", group = PM_classification)) +
#   geom_line() +
#   geom_line(aes(y = NMB_DLM, color = "NMB DLM")) +
#   geom_line(aes(y = NMB_FLQ_DLM, color = "NMB FLQ - NMB DLM")) +# Different color for the second line
#   geom_hline(yintercept = 0, linetype = "dashed", color = "red") +
#   labs(color = "", x = "Threshold", y = "Change in NMB", title = "Incremental NMB with respect to the standard of care depending on the prediction model classification") +
#   theme(text = element_text(size = 18)) +
#   facet_grid(. ~ PM_classification, scales = "free_y") +  # Facetted plot with grid layout
#   theme()  # Adjust legend position

NMB_Cost_DALY_classification_plot = grid.arrange(plot_daly, plot_cost, ncol = 1)

ggsave(
  filename = 'NMB_Cost_DALY_classification.png',
  plot = NMB_Cost_DALY_classification_plot,
  width = 15,
  height = 10
)


###################################
#   Change in NMB by FLQ status   #
###################################

PMDT_sampled_1000_1wtp_avg_allpatients = PMDT_sampled_1000_1wtp%>%
  group_by(Threshold)%>%
  summarise(Cost_SdTreat = mean(Cost_SdTreat),
            Cost_PMDT = mean(Cost_DM),
            Cost_SdTreat_PMDT = mean(Cost_SdTreat_DM),
            DALY_SdTreat = mean(DALY_SdTreat),
            DALY_PMDT = mean(DALY_DM),
            DALY_SdTreat_PMDT = mean(DALY_SdTreat_DM),
            NMB_SdTreat = mean(NMB_SdTreat),
            NMB_PMDT = mean(NMB_DM),
            NMB_SdTreat_PMDT = mean(NMB_SdTreat_DM)) %>%
  mutate(FLQ_Status = "All patients")


PMDT_sampled_1000_1wtp_avg_FLQstatus = PMDT_sampled_1000_1wtp%>%
  group_by(Threshold, FLQ_Status)%>%
  summarise(Cost_SdTreat = mean(Cost_SdTreat),
            Cost_PMDT = mean(Cost_DM),
            Cost_SdTreat_PMDT = mean(Cost_SdTreat_DM),
            DALY_SdTreat = mean(DALY_SdTreat),
            DALY_PMDT = mean(DALY_DM),
            DALY_SdTreat_PMDT = mean(DALY_SdTreat_DM),
            NMB_SdTreat = mean(NMB_SdTreat),
            NMB_PMDT = mean(NMB_DM),
            NMB_SdTreat_PMDT = mean(NMB_SdTreat_DM)) 

PMDT_sampled_1000_1wtp_avg = rbind(PMDT_sampled_1000_1wtp_avg_allpatients, PMDT_sampled_1000_1wtp_avg_FLQstatus) %>%
  pivot_wider(
    names_from = FLQ_Status,
    values_from = c(Cost_SdTreat, Cost_PMDT, Cost_SdTreat_PMDT, DALY_SdTreat, DALY_PMDT, DALY_SdTreat_PMDT, NMB_SdTreat, NMB_PMDT, NMB_SdTreat_PMDT)
  )


# Define a function to create each plot
create_plot <- function(data, y1, y2, y3, title, y_label) {
  ggplot(data, aes(x = Threshold)) +
    geom_line(aes(y = {{y1}}, colour = "(Sd Regimen - PMDT)")) +
    geom_line(aes(y = {{y2}}, colour = "PMDT")) +
    geom_line(aes(y = {{y3}}, colour = "Sd Regimen")) +
    labs(title = title, x = "Threshold", y = y_label, colour = "Model") +
    theme(text = element_text(size = 14))
}

# Create a list of dataframes and corresponding plot titles
plots_data <- list(
  list(data = PMDT_sampled_1000_1wtp_avg, 
       title = "DALY - FLQ resistant", 
       y_label = "DALY",
       y1 = PMDT_sampled_1000_1wtp_avg$'DALY_SdTreat_PMDT_FLQ Resistant', 
       y2 = PMDT_sampled_1000_1wtp_avg$'DALY_PMDT_FLQ Resistant', 
       y3 = PMDT_sampled_1000_1wtp_avg$'DALY_SdTreat_FLQ Resistant'),
  list(data = PMDT_sampled_1000_1wtp_avg, 
       title = "DALY - FLQ susceptible", 
       y_label = "DALY",
       y1 = PMDT_sampled_1000_1wtp_avg$'DALY_SdTreat_PMDT_FLQ Susceptible', 
       y2 = PMDT_sampled_1000_1wtp_avg$'DALY_PMDT_FLQ Susceptible', 
       y3 = PMDT_sampled_1000_1wtp_avg$'DALY_SdTreat_FLQ Susceptible'),
  list(data = PMDT_sampled_1000_1wtp_avg, 
       title = "DALY - All patients", 
       y_label = "DALY",
       y1 = PMDT_sampled_1000_1wtp_avg$'DALY_SdTreat_PMDT_All patients', 
       y2 = PMDT_sampled_1000_1wtp_avg$'DALY_PMDT_All patients', 
       y3 = PMDT_sampled_1000_1wtp_avg$'DALY_SdTreat_All patients'),
  list(data = PMDT_sampled_1000_1wtp_avg, 
       title = "Cost - FLQ resistant", 
       y_label = "Cost",
       y1 = PMDT_sampled_1000_1wtp_avg$'Cost_SdTreat_PMDT_FLQ Resistant', 
       y2 = PMDT_sampled_1000_1wtp_avg$'Cost_PMDT_FLQ Resistant', 
       y3 = PMDT_sampled_1000_1wtp_avg$'Cost_SdTreat_FLQ Resistant'),
  list(data = PMDT_sampled_1000_1wtp_avg, 
       title = "Cost - FLQ susceptible", 
       y_label = "Cost",
       y1 = PMDT_sampled_1000_1wtp_avg$'Cost_SdTreat_PMDT_FLQ Susceptible', 
       y2 = PMDT_sampled_1000_1wtp_avg$'Cost_PMDT_FLQ Susceptible', 
       y3 = PMDT_sampled_1000_1wtp_avg$'Cost_SdTreat_FLQ Susceptible'),
  list(data = PMDT_sampled_1000_1wtp_avg, 
       title = "Cost - All patients", 
       y_label = "Cost",
       y1 = PMDT_sampled_1000_1wtp_avg$'Cost_SdTreat_PMDT_All patients', 
       y2 = PMDT_sampled_1000_1wtp_avg$'Cost_PMDT_All patients', 
       y3 = PMDT_sampled_1000_1wtp_avg$'Cost_SdTreat_All patients'),
  list(data = PMDT_sampled_1000_1wtp_avg, 
       title = "NMB - FLQ resistant", 
       y_label = "NMB",
       y1 = PMDT_sampled_1000_1wtp_avg$'NMB_SdTreat_PMDT_FLQ Resistant', 
       y2 = PMDT_sampled_1000_1wtp_avg$'NMB_PMDT_FLQ Resistant', 
       y3 = PMDT_sampled_1000_1wtp_avg$'NMB_SdTreat_FLQ Resistant'),
  list(data = PMDT_sampled_1000_1wtp_avg, 
       title = "NMB - FLQ susceptible", 
       y_label = "NMB",
       y1 = PMDT_sampled_1000_1wtp_avg$'NMB_SdTreat_PMDT_FLQ Susceptible', 
       y2 = PMDT_sampled_1000_1wtp_avg$'NMB_PMDT_FLQ Susceptible', 
       y3 = PMDT_sampled_1000_1wtp_avg$'NMB_SdTreat_FLQ Susceptible'),
  list(data = PMDT_sampled_1000_1wtp_avg, 
       title = "NMB - All patients", 
       y_label = "NMB",
       y1 = PMDT_sampled_1000_1wtp_avg$'NMB_SdTreat_PMDT_All patients', 
       y2 = PMDT_sampled_1000_1wtp_avg$'NMB_PMDT_All patients', 
       y3 = PMDT_sampled_1000_1wtp_avg$'NMB_SdTreat_All patients')
)

# Create the plots
plots <- lapply(plots_data, function(plot_data) {
  create_plot(plot_data$data, plot_data$y1, plot_data$y2, plot_data$y3, plot_data$title, plot_data$y_label)
})

# Combine the plots into a single panel with shared legend at the bottom
NMB_COST_DALY_plots <- wrap_plots(plots, ncol = 3) +
  plot_layout(guides = "collect") +
  plot_annotation(tag_levels = "A", tag_suffix = ". ", title = "", theme = theme(legend.position = "right"))


# Save the final plot
ggsave(filename = "NMB_COST_DALY_plots_FLQStatus.png", plot = NMB_COST_DALY_plots, width = 14, height = 10)


###########################################################
#   Change in NMB - Optimal Threshold only- varying wtp   #
###########################################################

source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Analysis/DR_TB_PMDT_Analysis_Functions.R')
output_loc = ('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Platt Calibration/PM Boostrap/Optimism Correction/Adjusted/')

PMDT_1000sampled_varwtp = read_output_tolist_varyingwtp(output_loc, "PMDT_","bootstrapping_samplesize200", 6)

NMBavg_overall = PMDT_1000sampled_varwtp$output_df %>%
  compute_avg_nmb_ci(NMB_SdTreat_DM, c(wtp,Threshold)) %>%
  mutate(FLQ_Status = "All patients")

max_Thresholds <- NMBavg_overall %>%
  slice_max(NMB_avg, with_ties = FALSE) %>%  # Get the maximum NMB_avg_mean across all Thresholds
  pull(Threshold) %>%
  as.data.frame()

max_Thresholds$wtp = seq(1:6)
colnames(max_Thresholds) = c("Threshold", "wtp")

NMBavg_FLQstatus = PMDT_1000sampled_varwtp$output_df %>%
  compute_avg_nmb_ci(NMB_SdTreat_DM, c(wtp,FLQ_Status, Threshold))

NMB_avg = bind_rows(NMBavg_FLQstatus, NMBavg_overall)%>%
  group_by(wtp, FLQ_Status) 

NMB_avg_max = data.frame()
for (i in 1:length(max_Thresholds$wtp)){

ax = NMB_avg %>%
    filter(Threshold == max_Thresholds$Threshold[i] & wtp == max_Thresholds$wtp[i])

NMB_avg_max = bind_rows(NMB_avg_max, ax)

}

NMB_avg_max = NMB_avg_max %>%
  mutate(wtp_real = 
           case_when(wtp == 1 ~ 0.5,
                     wtp == 2 ~ 1,
                     wtp == 3 ~ 1.5,
                     wtp == 4 ~ 2,
                     wtp == 5 ~ 2.5,
                     wtp == 6 ~ 3)) %>%
  mutate(FLQ_Status_m = case_when(
    FLQ_Status == 'FLQ Resistant' ~ 'B. Among patients with TB resistant \n to rifampicin and FLQ',
    FLQ_Status == 'FLQ Susceptible' ~ 'C. Among patients with TB resistant \n to rifampicin but susceptible to FLQ',
    FLQ_Status == 'All patients' ~ 'A. Among all patients with TB \n resistant to rifampicin'
  ))


# Plot
plot_NMB_wtp = ggplot(NMB_avg_max, aes(x = wtp_real, y = NMB_avg, fill = FLQ_Status)) +
  geom_line() +
  geom_ribbon(aes(ymin = lci_NMB_avg, ymax = uci_NMB_avg), fill = "grey", alpha = 0.5) +  # Specify fill outside aes
  labs(x = "Willingness-to-pay value as a portion of the Republic of Moldova's gross domestic product per capita", y = "Change in NMB", title = "NMB and 95% Confidence Interval") +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ FLQ_Status_m, scales = "free_y") +  # Facetted plot with grid layout
  theme(legend.position = "none") +  # Remove legend
  ggtitle("Incremental NMB with respect to the standard of care and 95% confidence intervals")  # Add title


# Save the final plot
ggsave(filename = "NMB_WTP.png", plot = plot_NMB_wtp, width = 14, height = 6)


# Plot
 
NMBavg_FLQstatus %>%
  filter(FLQ_Status == "FLQ Resistant") %>%
  ggplot(aes(x = Threshold, y = NMB_avg_mean, colour = as.factor(wtp))) +
  ylab("Change in NMB")+
  xlab("Threshold")+
  geom_line()+
  theme(legend.position = "bottom",   
        text = element_text(size = 18))  # Move legend to the top

