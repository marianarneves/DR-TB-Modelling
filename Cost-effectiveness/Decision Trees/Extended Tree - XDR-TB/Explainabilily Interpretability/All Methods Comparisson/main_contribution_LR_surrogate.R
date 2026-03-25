get_main_contribution <- function(fit, x_matrix, y_vector, patient_id) {
  
  x_patient <- x_matrix[patient_id, ]
  
  coef_vector <- coef(fit)
  intercept <- coef_vector[1]
  beta <- coef_vector[-1]
  beta <- beta[colnames(x_matrix)]
  
  contrib <- x_patient * beta
  
  contrib_df <- data.frame(
    Variable = colnames(x_matrix),
    Contribution = as.numeric(contrib),
    Value = as.numeric(x_patient)
  )
  
  # Keep active variables
  contrib_df <- contrib_df[contrib_df$Value != 0, ]
  
  y_patient <- y_vector[patient_id]
  
  if (y_patient == 1) {
    main_row <- contrib_df[which.max(contrib_df$Contribution), ]
    direction <- "positive"
  } else {
    main_row <- contrib_df[which.min(contrib_df$Contribution), ]
    direction <- "negative"
  }
  
  # Predicted probability
  logit_total <- intercept + sum(contrib_df$Contribution)
  prob_total <- 1 / (1 + exp(-logit_total))
  
  data.frame(
    patient_id = patient_id,
    observed_class = y_patient,
    predicted_probability = prob_total,
    main_variable = main_row$Variable,
    contribution = main_row$Contribution,
    direction = direction
  )
}