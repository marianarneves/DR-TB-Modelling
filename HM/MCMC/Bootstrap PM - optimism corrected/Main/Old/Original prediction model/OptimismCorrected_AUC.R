
# Step 2: Bootstrap resampling
num_bootstrap_samples <- 10
bootstrap_performances <- numeric(num_bootstrap_samples)

start.time <- Sys.time()
for (i in 1:num_bootstrap_samples) {
  # Create a bootstrap sample
  bootstrap_indices <-
    sample(1:nrow(moldova_data), nrow(moldova_data), replace = TRUE)
  moldova_data_bootstrap <- moldova_data[bootstrap_indices, ]
  
  # Develop bootstrap predictive model
  hierarchical_model_bootstrap <- brm(
    formula = FLQ_R ~ Age + Family_size + Family_size18 + Sex_2 + Family_size +
      Occupation_2 + Occupation_3 + Occupation_4 + Occupation_5 +
      Education_2 + Education_3 + Education_4 + Education_5 + Education_missing +
      Living_condition_1 + Living_condition_missing + Outside_moldova_1 +
      Outside_moldova_missing + Urban_1 + Homeless_1 + Homeless_missing +
      Money_assistance_1 + Money_assistance_missing + Incarceration_1 +
      Incarceration_missing + TB_location_bin_Pulmonary + TB_type_2 +
      TB_type_3 + TB_type_4 + TB_type_6 + (1 | Residence),
    data = moldova_data_bootstrap,
    family = bernoulli(link = "logit"),
    prior = set_prior(
      R2D2(
        mean_R2 = 0.8,
        prec_R2 = 10,
        cons_D2 = 0.5,
        main = TRUE
      ),
      class = "b"
    ),
    iter = 1000,
    chains = 4,
    control = list(adapt_delta = 0.999)
  )
  
  # Calculate bootstrap performance on bootstrap sample
  y_pred_bootstrap <-
    posterior_epred(hierarchical_model_bootstrap, newdata = moldova_data_bootstrap)
  roc_curve_bootstrap <-
    roc(moldova_data_bootstrap$FLQ_R,
        apply(y_pred_bootstrap, 2, mean))
  bootstrap_performance <- roc_curve_bootstrap$auc
  
  # Calculate bootstrap performance on the original sample
  y_pred_orig <-
    posterior_epred(hierarchical_model_bootstrap,
                    newdata = moldova_data,
                    allow_new_levels = T)
  roc_curve_orig <-
    roc(moldova_data$FLQ_R, apply(y_pred_orig, 2, mean))
  orig_performance <- roc_curve_orig$auc
  
  # Calculate optimism
  optimism <- bootstrap_performance - orig_performance
  bootstrap_performances[i] <- optimism
}
end.time <- Sys.time()
# Step 3: Calculate the average optimism
average_optimism <- mean(bootstrap_performances)

# Step 4: Calculate optimism-corrected performance and confidence interval
alpha <- 0.05
p_corrected <- HM_cal_performance$roc_curve$auc- average_optimism
percentiles <-
  quantile(bootstrap_performances, c(alpha / 2, 1 - alpha / 2))
ci_low <- HM_cal_performance$roc_curve$auc - percentiles[2]
ci_high <- HM_cal_performance$roc_curve$auc - percentiles[1]

print(paste("Optimism-Corrected Performance:", p_corrected))
print(paste("Bootstrap Confidence Interval:", ci_low, ci_high))