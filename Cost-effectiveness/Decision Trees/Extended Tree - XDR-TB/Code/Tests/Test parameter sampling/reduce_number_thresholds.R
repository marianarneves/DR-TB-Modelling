library(readxl)
library(dplyr)

sens_spec_calibrated_model = read.csv("/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/HM Output/sens_spec_calibrated_model.csv")

sens_spec_calibrated_model_m = sens_spec_calibrated_model %>%
filter(row_number() %% 5 == 0)

write.csv(sens_spec_calibrated_model_m, "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Tests/Test parameter sampling/sens_spec_calibrated_model_m5.csv", row.names = FALSE)

sens_spec_calibrated_model_max = sens_spec_calibrated_model %>%
  filter(threshold > 0.350881229 & threshold < 0.350881231)
write.csv(sens_spec_calibrated_model_max, "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Tests/Test parameter sampling/sens_spec_calibrated_model_max.csv", row.names = FALSE)
