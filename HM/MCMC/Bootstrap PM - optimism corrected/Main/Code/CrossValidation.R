# Call the cross-validation function
cv_results_reg <- hierarchical_cv(
  moldova_data,
  response = "FLQ_R",
  FLQ_R ~ Age + Family_size + Family_size18 + Sex_2 +
    Occupation_2 + Occupation_3 + Occupation_4 + Occupation_5 +
    Education_2 + Education_3 + Education_4 + Education_5 + Education_missing +
    Living_condition_1 + Living_condition_missing + Outside_moldova_1 +
    Outside_moldova_missing + Urban_1 + Homeless_1 + Homeless_missing +
    Money_assistance_1 + Money_assistance_missing + Incarceration_1 +
    Incarceration_missing + TB_location_bin_Pulmonary + TB_type_2 +
    TB_type_3 + TB_type_4 + TB_type_6 + (1 |
                                           Residence),
  nfolds = 5,
  iter = 10000,
  chains = 4,
  regularization = "Yes",
  cons_D2 = 0.1
)

# Mean AUC for all folds
mean(unlist((lapply(cv_results_reg$roc_curve, "[", "auc"))))

# SD for all folds
sd(unlist((lapply(cv_results_reg$roc_curve, "[", "auc"))))

# Call the cross-validation function
cv_results_alldata <- hierarchical_cv(
  moldova_data,
  response = "FLQ_R",
  FLQ_R ~ Age + Family_size + Family_size18 + Sex_2 + Family_size +
    Occupation_2 + Occupation_3 + Occupation_4 + Occupation_5 +
    Education_2 + Education_3 + Education_4 + Education_5 + Education_missing +
    Living_condition_1 + Living_condition_missing + Outside_moldova_1 +
    Outside_moldova_missing + Urban_1 + Homeless_1 + Homeless_missing +
    Money_assistance_1 + Money_assistance_missing + Incarceration_1 +
    Incarceration_missing + TB_location_bin_Pulmonary + TB_type_2 +
    TB_type_3 + TB_type_4 + TB_type_6 + (1 |
                                           Residence),
  nfolds = 5,
  iter = 100000,
  chains = 4,
  regularization = "No"
)

# Mean AUC for all folds
mean(unlist((lapply(cv_results_alldata$roc_curve, "[", "auc"))))

# SD for all folds
sd(unlist((lapply(cv_results_alldata$roc_curve, "[", "auc"))))

# Generate colors
colors <- rainbow(5)

#### No regularization priors
# Initialize the plot
plot(
  cv_results_alldata$roc_curve[[1]],
  col = colors[1],
  main = "ROC Curve for Hierarchical Logistic Regression - No Regularization",
  col.main = "darkblue",
  lwd = 2
)
# Add ROC curves for other folds
for (j in 2:5) {
  lines(cv_results_alldata$roc_curve[[j]],
        col = colors[j],
        lwd = 2)
}
# Add legend with labels based on cv_results$roc_auc_fulldata
legend(
  "bottomright",
  legend = lapply(cv_results_alldata$roc_auc, function(x)
    round(x, 2)),
  col = colors,
  lwd = 2,
  title = "AUROC",
  cex = 0.8
)


# Plotting ROC curve
ggplot(cv_results_alldata$roc_curve[[1]], aes(x = 1 - specificity, y = sensitivity)) +
  geom_line(aes(color = "Fold 1"), size = 1) +
  geom_line(data = cv_results_alldata$roc_curve[[2]], aes(x = 1 - specificity, y = sensitivity, color = "Fold 2"), size = 1) +
  geom_line(data = cv_results_alldata$roc_curve[[3]], aes(x = 1 - specificity, y = sensitivity, color = "Fold 3"), size = 1) +
  geom_line(data = cv_results_alldata$roc_curve[[4]], aes(x = 1 - specificity, y = sensitivity, color = "Fold 4"), size = 1) +
  geom_line(data = cv_results_alldata$roc_curve[[5]], aes(x = 1 - specificity, y = sensitivity, color = "Fold 5"), size = 1) +
  scale_color_manual(values = colors) +
  labs(x = "1 - Specificity", y = "Sensitivity", 
       title = "ROC Curve for Hierarchical Logistic Regression - No Regularization",
       color = "Fold") +
  theme_minimal() +
  theme(legend.position = "bottom",
        plot.title = element_text(size = 16, hjust = 0.5),
        axis.text = element_text(size = 12),
        axis.title = element_text(size = 14),
        legend.text = element_text(size = 14))

#### With regularization priors
# Initialize the plot
plot(
  cv_results_reg$roc_curve[[1]],
  col = colors[1],
  main = "ROC Curve for Hierarchical Logistic Regression - Regularization",
  col.main = "darkblue",
  lwd = 2
)
# Add ROC curves for other folds
for (j in 2:5) {
  lines(cv_results_reg$roc_curve[[j]], col = colors[j], lwd = 2)
}
# Add legend with labels based on cv_results$roc_auc_fulldata
legend(
  "bottomright",
  legend = lapply(cv_results_reg$roc_auc, function(x)
    round(x, 2)),
  col = colors,
  lwd = 2,
  title = "AUROC",
  cex = 0.8
)


