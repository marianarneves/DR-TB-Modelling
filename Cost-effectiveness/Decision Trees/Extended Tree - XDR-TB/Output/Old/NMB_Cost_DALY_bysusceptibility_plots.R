library(ggplot2)
library(gridExtra)
library(patchwork)

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
  list(data = PMDT_performance_sus_res, 
       title = "DALY - FLQ resistant", 
       y_label = "DALY",
       y1 = PMDT_performance_sus_res$Daly_Tx_truth_avg_sd_r, 
       y2 = PMDT_performance_sus_res$Daly_Tx_truth_avg_r, 
       y3 = PMDT_performance_sus_res$StTreat_DALY_res),
  list(data = PMDT_performance_sus_res, 
       title = "DALY - FLQ susceptible", 
       y_label = "DALY",
       y1 = PMDT_performance_sus_res$Daly_Tx_truth_avg_sd_s, 
       y2 = PMDT_performance_sus_res$Daly_Tx_truth_avg_s, 
       y3 = PMDT_performance_sus_res$StTreat_DALY_sus),
  list(data = PMDT_performance_sus_res, 
       title = "DALY - All patients", 
       y_label = "DALY",
       y1 = PMDT_performance_sus_res$Daly_Tx_truth_sd, 
       y2 = PMDT_performance_sus_res$Daly_Tx_truth, 
       y3 = PMDT_performance_sus_res$StTreat_DALY),
  list(data = PMDT_performance_sus_res, 
       title = "Cost - FLQ resistant", 
       y_label = "Cost",
       y1 = PMDT_performance_sus_res$Cost_Tx_truth_avg_sd_r, 
       y2 = PMDT_performance_sus_res$Cost_Tx_truth_avg_r, 
       y3 = PMDT_performance_sus_res$StTreat_cost_res),
  list(data = PMDT_performance_sus_res, 
       title = "Cost - FLQ susceptible", 
       y_label = "Cost",
       y1 = PMDT_performance_sus_res$Cost_Tx_truth_avg_sd_s, 
       y2 = PMDT_performance_sus_res$Cost_Tx_truth_avg_s, 
       y3 = PMDT_performance_sus_res$StTreat_cost_sus),
  list(data = PMDT_performance_sus_res, 
       title = "Cost - All patients", 
       y_label = "Cost",
       y1 = PMDT_performance_sus_res$Cost_Tx_truth_sd, 
       y2 = PMDT_performance_sus_res$Cost_Tx_truth, 
       y3 = PMDT_performance_sus_res$StTreat_cost),
  list(data = PMDT_performance_sus_res, 
       title = "NMB - FLQ resistant", 
       y_label = "NMB",
       y1 = PMDT_performance_sus_res$NMB_avg_sd_r, 
       y2 = PMDT_performance_sus_res$NMB_avg_r, 
       y3 = PMDT_performance_sus_res$StTreat_NMB_res),
  list(data = PMDT_performance_sus_res, 
       title = "NMB - FLQ susceptible", 
       y_label = "NMB",
       y1 = PMDT_performance_sus_res$NMB_avg_sd_s, 
       y2 = PMDT_performance_sus_res$NMB_avg_s, 
       y3 = PMDT_performance_sus_res$StTreat_NMB_sus),
  list(data = PMDT_performance_sus_res, 
       title = "NMB - All patients", 
       y_label = "NMB",
       y1 = PMDT_performance_sus_res$NMB, 
       y2 = PMDT_performance_sus_res$NMB_PMDT, 
       y3 = PMDT_performance_sus_res$StTreat_NMB)
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
ggsave(filename = "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/panel_plots_shared_legend.png", plot = NMB_COST_DALY_plots, width = 14, height = 10)
