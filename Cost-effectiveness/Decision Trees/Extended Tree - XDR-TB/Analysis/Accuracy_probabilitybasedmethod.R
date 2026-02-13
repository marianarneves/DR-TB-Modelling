library(dplyr)
library(tidyr)
library(purrr)

# Function to compute confusion matrix counts from each WTP-level dataframe
generate_cm_table <- function(df, wtp_value, model_label) {
  df %>%
    mutate(CM = case_when(
      FLQ_Status == "FLQ Resistant" & Opt_Treat == "FLQ" ~ "FN",
      FLQ_Status == "FLQ Resistant" & Opt_Treat == "DLM" ~ "TP",
      FLQ_Status == "FLQ Susceptible" & Opt_Treat == "FLQ" ~ "TN",
      FLQ_Status == "FLQ Susceptible" & Opt_Treat == "DLM" ~ "FP"
    )) %>%
    count(CM) %>%
    pivot_wider(names_from = CM, values_from = n, values_fill = 0) %>%
    mutate(WTP = wtp_value, Model = model_label)
}

# Wrapper to apply over all WTPs for a given model
get_cm_tables_by_wtp <- function(wtp_output_df_list, model_label) {
  map2_dfr(
    wtp_output_df_list,
    names(wtp_output_df_list),
    ~ generate_cm_table(.x, wtp_value = .y, model_label = model_label)
  )
}

# ---- APPLY TO YOUR OBJECTS ----

# For calibrated model
cm_tables_calibrated <- get_cm_tables_by_wtp(Prediction_PMDT_varwtp$output_list, "Calibrated")

# For uncalibrated model
cm_tables_uncalibrated <- get_cm_tables_by_wtp(Prediction_PMDT_varwtp_nocal$output_list, "Uncalibrated")

# Combine both into a final table
all_cm_tables <- bind_rows(cm_tables_calibrated, cm_tables_uncalibrated) %>% 
  mutate(Accuracy = (TP+TN)/(FN+FP+TN+TP))

# View
print(all_cm_tables)

# Save to CSV
write.csv(
  all_cm_tables,
  "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Output/cm_summary_by_wtp.csv",
  row.names = FALSE
)
