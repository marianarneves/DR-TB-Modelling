library(readxl)

boot_sens_spec = readxl::read_xlsx('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Tests/Test PM bootstraping/Booststrap_Sens_Spec.xlsx')

# Assuming the dataset boot_sens_spec is already loaded

# Extract the columns that start with 'boot'
boot_columns <- boot_sens_spec[, grepl("^Boot", names(boot_sens_spec))]

# Calculate variance for each row
row_variance <- apply(boot_columns, 1, var)

# Calculate mean for each row
row_mean <- apply(boot_columns, 1, mean)

# Add the row variance and mean as new columns to the dataset (optional)
boot_sens_spec$row_variance <- row_variance
boot_sens_spec$row_mean <- row_mean

# View the updated dataset (optional)
head(boot_sens_spec)

#Plot average sensitivity by threshold
TPR_mean_var_df = boot_sens_spec %>%
  filter(Variable == "TPR") %>%
  select(Variable,row_variance, row_mean, threshold) 

plot(TPR_mean_var_df$threshold, TPR_mean_var_df$row_variance)



