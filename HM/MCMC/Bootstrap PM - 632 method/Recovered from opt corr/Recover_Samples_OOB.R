library(dplyr)

setwd('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/Bootstrap/Bootstrap PM - 632 method/Recovered from opt corr/')

opt_pred = read.csv('HM_bootstrap_calibrated_predictions_copy.csv')

opt_pred$origdata_pt_id = rep(seq(1:540),500)

origdata_pred = data.frame(bootstrap_sample = opt_pred$bootstrap_sample, origdata_pt_id = opt_pred$origdata_pt_id, predicted_origdata = opt_pred$predicted_origdata, observed_origdata = opt_pred$observed_origdata)

boots_pt = data.frame(bootstrap_sample = opt_pred$bootstrap_sample, bootstrap_pt_id = opt_pred$bootstrap_pt_id)

pt_id_data = data.frame(pt_id = seq(1:540))

oob_pred_all = data.frame()

for(i in 1:500){
  
  boots_pt_b = boots_pt %>%
    filter(bootstrap_sample == i)
  
  origdata_pred_b = origdata_pred %>%
    filter(bootstrap_sample == i)
  
  oob_id = anti_join(pt_id_data, boots_pt_b, by = c("pt_id" = "bootstrap_pt_id"))
  
  oob_pred = oob_id %>%
    left_join(origdata_pred_b, by = c("pt_id" = "origdata_pt_id") ) %>%
    rename(predicted_oob_sample = predicted_origdata, observed_oob_sample = observed_origdata)
  
  oob_pred_all = rbind(oob_pred, oob_pred_all)
}

write.csv(oob_pred_all, "oob_pred_all.csv", row.names = FALSE)
