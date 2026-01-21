calculate_sens_spec <- function(observed, predicted) {
  # Ensure inputs are factors with levels 0 and 1
  confusion_matrix <- table(
    Observed = factor(observed, levels = c(0, 1)),
    Predicted = factor(predicted, levels = c(0, 1))
  )
  
  # Extract values from confusion matrix
  true_positive <- confusion_matrix["1", "1"]
  true_negative <- confusion_matrix["0", "0"]
  false_positive <- confusion_matrix["0", "1"]
  false_negative <- confusion_matrix["1", "0"]
  
  # Calculate sensitivity and specificity with zero-division protection
  sensitivity <- ifelse((true_positive + false_negative) > 0,
                        true_positive / (true_positive + false_negative),
                        NA)
  specificity <- ifelse((true_negative + false_positive) > 0,
                        true_negative / (true_negative + false_positive),
                        NA)
  
  # Return results as a list
  return(list(Sensitivity = sensitivity, Specificity = specificity))
}