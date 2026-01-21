# Function to read output for varying threshold
read_output_tolist_varyingwtp = function(output_loc, output_nameprefix, output_namesufix, n_wtp){
# NMB_DALY_Cost_PMDT_eachpt - NMB, DALYs and Costs for each patient
  output_list = vector(mode = "list", length = n_wtp)
  output_df = data.frame()
  names(output_list) = paste0("wtp_",seq(1:n_wtp))
  for (i in 1:n_wtp) {
    output_list[[i]] = read_excel(
      paste0(
        output_loc, 
        output_nameprefix,
        "wtp",
        toString(i),
        output_namesufix,
        ".xlsx"
      )
    )
    output_list[[i]]$wtp = i 
    output_df = bind_rows(output_df, output_list[[i]])
  }
  
  output = vector(mode = "list", length = 2)
  
  output[[1]] = output_df
  output[[2]] = output_list
  
  names(output) = c('output_df', 'output_list')
  
  return(output)
}

# Calculate confidence intervals for each dataset
compute_avg_nmb_ci <- function(data, data_column, group_columns, wtp_val = "NA") {
  if(wtp_val == "NA") {
    data %>%
      group_by(across({{group_columns}})) %>%
      summarise(NMB_avg = mean({{data_column}}), 
                NMB_avg_sd = sd({{data_column}}),
                sample_size = n()
      ) %>%
      mutate(
        lci_NMB_avg = NMB_avg - qt(0.975, df = sample_size - 1) * (NMB_avg_sd / sqrt(sample_size)),
        uci_NMB_avg = NMB_avg + qt(0.975, df = sample_size - 1) * (NMB_avg_sd / sqrt(sample_size))
      )
  }
  else{
    data %>%
      group_by(across({{group_columns}})) %>%
      summarise(NMB_avg = mean({{data_column}}), 
                NMB_avg_sd = sd({{data_column}}),
                sample_size = n()
      ) %>%
      mutate(
        lci_NMB_avg = NMB_avg - qt(0.975, df = sample_size - 1) * (NMB_avg_sd / sqrt(sample_size)),
        uci_NMB_avg = NMB_avg + qt(0.975, df = sample_size - 1) * (NMB_avg_sd / sqrt(sample_size))
      )%>%
      mutate(WTP = wtp_val)
  }
}
