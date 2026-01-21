

# Group by Threshold and calculate the overall proportion of Opt_Treat == 'Cfz'
Opt_treat_Cfz_overall_1wtp <- PMDT_sampled_1000_1wtp %>%
  group_by(Threshold) %>%
  summarise(Opt_treat_Cfz = mean(Opt_Treat == 'Cfz', na.rm = TRUE), .groups = 'drop') %>%
  mutate(WTP = "WTP = 1 GDP")
Opt_treat_Cfz_overall_2wtp <- PMDT_sampled_1000_2wtp %>%
  group_by(Threshold) %>%
  summarise(Opt_treat_Cfz = mean(Opt_Treat == 'Cfz', na.rm = TRUE), .groups = 'drop') %>%
  mutate(WTP = "WTP = 2 GDP")
Opt_treat_Cfz_overall_3wtp <- PMDT_sampled_1000_2wtp %>%
  group_by(Threshold) %>%
  summarise(Opt_treat_Cfz = mean(Opt_Treat == 'Cfz', na.rm = TRUE), .groups = 'drop') %>%
  mutate(WTP = "WTP = 3 GDP")

# Combine both data frames
Opt_treat_Cfz_overall <- bind_rows(Opt_treat_Cfz_overall_1wtp, 
                                   Opt_treat_Cfz_overall_2wtp,
                                   Opt_treat_Cfz_overall_3wtp) %>%
  mutate(FLQ_Status = "Overall")


# Group by Threshold and FLQ_Status, then calculate the proportion of Opt_Treat == 'Cfz'
Opt_treat_Cfz_byFLQ_1wtp <- PMDT_sampled_1000_1wtp %>%
  group_by(Threshold, FLQ_Status) %>%
  summarise(Opt_treat_Cfz = mean(Opt_Treat == 'Cfz', na.rm = TRUE), .groups = 'drop')%>%
  mutate(WTP = "WTP = 1 GDP")
Opt_treat_Cfz_byFLQ_2wtp <- PMDT_sampled_1000_2wtp %>%
  group_by(Threshold, FLQ_Status) %>%
  summarise(Opt_treat_Cfz = mean(Opt_Treat == 'Cfz', na.rm = TRUE), .groups = 'drop')%>%
  mutate(WTP = "WTP = 2 GDP")
Opt_treat_Cfz_byFLQ_3wtp <- PMDT_sampled_1000_3wtp %>%
  group_by(Threshold, FLQ_Status) %>%
  summarise(Opt_treat_Cfz = mean(Opt_Treat == 'Cfz', na.rm = TRUE), .groups = 'drop')%>%
  mutate(WTP = "WTP = 3 GDP")

# Combine both data frames
Opt_treat_Cfz_byFLQ <- bind_rows(Opt_treat_Cfz_byFLQ_1wtp, 
                                 Opt_treat_Cfz_byFLQ_2wtp,
                                 Opt_treat_Cfz_byFLQ_3wtp)

# Combine both data frames
Opt_treat_Cfz <- bind_rows(Opt_treat_Cfz_overall, 
                           Opt_treat_Cfz_byFLQ)


# Define a custom blue-toned color palette
custom_blue_colors <- c(
  "Overall" = "#004c6d",   # Medium blue
  "FLQ Resistant" = "#6baed6",  # Light blue
  "FLQ Susceptible" = "#3182bd"   # Darker blue
)

# Plot the results with custom blue colors and y-axis ticks by 0.05
Cfz_presc_prop_byFLQstatus_plot <- ggplot(Opt_treat_Cfz, aes(x = Threshold, y = Opt_treat_Cfz, color = FLQ_Status, group = FLQ_Status)) +
  geom_line(size = 0.7) +
  geom_point(size = 0.7) +
  scale_color_manual(values = custom_blue_colors) +  # Use custom blue colors
  labs(
    x = "Classification threshold",
    y = "Proportion of patients prescribed Cfz",
    color = "FLQ Status"
  ) +
  scale_y_continuous(breaks = seq(0, 0.3, by = 0.05), limits = c(0, 0.3)) +  # Set y-axis ticks by 0.05
  scale_x_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.1)) + # Set x-axis limits and breaks
  facet_grid(. ~ WTP, scales = "free_y") +  # Facetted plot with grid layout
  theme_minimal() +
  theme(
    legend.position = "bottom",   
    text = element_text(size = 18)
  )

# Save the plot
ggsave(
  filename =  'Cfz_presc_prop_byFLQstatus.png',
  plot = Cfz_presc_prop_byFLQstatus_plot,
  width = 16, height = 5
)


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
  ggtitle("Incremental NMB with respect to the standard of care and confidence intervals obtained using\nthe classification-based method and calibrated predictions") +
  # Add horizontal line at max Threshold for each facet
  geom_hline(data = max_points, aes(yintercept = NMB), color = "blue", linetype = "dashed") +
  # Add annotation for max Threshold, positioned to the right
  geom_text(data = max_points, 
            aes(x = Threshold + 0.025 ,  # Small offset to the right
                y = NMB + 100, 
                label = paste0("NMB = ", round(NMB, 0))), 
            hjust = 0,  # Left-aligned text to appear on the right side
            size = 5, 
            color = "blue")+
  # Add vertical line at max Threshold for each facet
  geom_vline(data = max_points, aes(xintercept = Threshold), color = "red", linetype = "dashed") +
  # Add annotation for max Threshold, positioned to the right
  geom_text(data = max_points, 
            aes(x = Threshold - 0.2 ,  # Small offset to the right
                y = NMB - 100, 
                label = paste0("t = ", round(Threshold, 3))), 
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







######################################
# Number of people prescribed Cfz


#cal
# Group by Threshold and calculate the overall proportion of Opt_Treat == 'Cfz'
Opt_treat_Cfz_overall_cal <- Prediction_PMDT_varwtp$output_list$wtp_2 %>%
  group_by(Threshold) %>%
  summarise(Opt_treat_Cfz = mean(Opt_Treat == 'Cfz', na.rm = TRUE), .groups = 'drop') %>%
  mutate(FLQ_Status = "Overall")

# Group by Threshold and FLQ_Status, then calculate the proportion of Opt_Treat == 'Cfz'
Opt_treat_Cfz_byFLQ_cal <- Prediction_PMDT_varwtp$output_list$wtp_2 %>%
  group_by(Threshold, FLQ_Status) %>%
  summarise(Opt_treat_Cfz = mean(Opt_Treat == 'Cfz', na.rm = TRUE), .groups = 'drop')

# Combine both data frames
Opt_treat_Cfz_combined_cal <- bind_rows(Opt_treat_Cfz_overall_cal, Opt_treat_Cfz_byFLQ_cal)



#No cal
# Group by Threshold and calculate the overall proportion of Opt_Treat == 'Cfz'
Opt_treat_Cfz_overall_nocal <- Prediction_PMDT_nocal_varwtp$output_list$wtp_2 %>%
  group_by(Threshold) %>%
  summarise(Opt_treat_Cfz = mean(Opt_Treat == 'Cfz', na.rm = TRUE), .groups = 'drop') %>%
  mutate(FLQ_Status = "Overall")

# Group by Threshold and FLQ_Status, then calculate the proportion of Opt_Treat == 'Cfz'
Opt_treat_Cfz_byFLQ_nocal <- Prediction_PMDT_nocal_varwtp$output_list$wtp_2 %>%
  group_by(Threshold, FLQ_Status) %>%
  summarise(Opt_treat_Cfz = mean(Opt_Treat == 'Cfz', na.rm = TRUE), .groups = 'drop')

# Combine both data frames
Opt_treat_Cfz_combined_nocal <- bind_rows(Opt_treat_Cfz_overall_nocal, Opt_treat_Cfz_byFLQ_nocal)


