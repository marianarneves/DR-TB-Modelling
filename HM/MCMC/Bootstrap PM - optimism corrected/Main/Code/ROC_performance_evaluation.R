# HM predictions
# Predict on test data
predictions <-
  posterior_epred(hierarchical_model,
                  newdata = moldova_data,
                  allow_new_levels = TRUE)
# Average of the simulated 
y_prob <-
  apply(predictions, 2,  function(x)
    mean(x))

#### Performance of the HM ####
HM_performance = roc_performance(y_prob, moldova_data, moldova_data$FLQ_R)

# Write Predictions in CSV
moldovaSex = ifelse(moldova_data$Sex == 1, "Female", "Male" )
write.csv(data.frame(pred = y_prob, obs = moldova_data$FLQ_R, age = moldova_data$Age, sex = moldovaSex), file.path("HM Output", "pred_obs.csv"), row.names = FALSE)
# Write Rates in CSV
write.csv(HM_performance$sens_spec, file.path("HM Output","sens_spec_adjusted.csv"), row.names = FALSE)

# ROC plot
plot(
  HM_performance$roc_curve,
  main = "ROC Curve for Hierarchical Logistic Regression",
  col.main = "darkblue",
  lwd = 2
)
# Add legend with labels based on cv_results$roc_auc_fulldata
legend(
  "bottomright",
  legend = round(HM_performance$roc_curve$auc, 2),
  lwd = 2,
  title = "AUROC",
  cex = 0.8
)

#### Plot sensitivity and specificity ####
plot(HM_performance$sens_spec$threshold, HM_performance$sens_spec$sensitivity, type = "l", col = "blue",
     xlab = "Threshold", ylab = "Sensitivity", ylim = c(0, 1), lwd = 2)
lines(HM_performance$sens_spec$threshold, HM_performance$sens_spec$specificity, col = "red", lty = 2, lwd = 2)
legend("bottomright", legend = c("Sensitivity", "Specificity"), col = c("blue", "red"), lty = c(1, 2), lwd = 2)

# Plot probabilities calculated with Bayes Theorem
ggplot(HM_performance$sens_spec, aes(x = threshold)) +
  geom_line(aes(y = P_S_R, color = "P_S_R")) +
  geom_line(aes(y = P_R_R, color = "P_R_R")) +
  scale_color_manual(values = c( "blue", "red"), name = "Variable") +
  labs(x = "Threshold", y = "Value") +
  theme_minimal() +
  theme(legend.position = "top")

ggplot(HM_performance$sens_spec, aes(x = threshold)) +
  geom_line(aes(y = P_S_S, color = "P_S_S")) +
  geom_line(aes(y = P_R_S, color = "P_R_S")) +
  scale_color_manual(values = c( "blue", "red"), name = "Variable") +
  labs(x = "Threshold", y = "Value") +
  theme_minimal() +
  theme(legend.position = "top")
