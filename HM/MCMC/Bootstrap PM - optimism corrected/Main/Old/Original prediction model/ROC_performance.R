roc_performance = function(y_prob, data, response) {
 
  # Create a ROC curve for the testing set
  roc_curve <-
    roc(response = response, predictor = y_prob)
  
  # Get sensitivity and specificity at different thresholds
  sens_spec <- coords(roc_curve)
  sens_spec = sens_spec[-1, ] #Remove row with specificity 0
  sens_spec = sens_spec[-nrow(sens_spec), ]
  sens_spec$positive = NA
  sens_spec$negative = NA
  
  for (i in 1:dim(sens_spec)[1]) {
    sens_spec$positive[i] = sum(y_prob >= sens_spec$threshold[i]) / length(y_prob)
    sens_spec$negative[i] = sum(y_prob < sens_spec$threshold[i]) / length(y_prob)
  }
  
  #### Calculating P using Bayes Theorem for DT ####
  
  #Resistance to FLQ prevalence in the dataset
  sens_spec$FLQ_R_prev = sum(moldova_data$FLQ_R==1)/dim(moldova_data)[1]
  sens_spec$FLQ_NR_prev = 1 - sens_spec$FLQ_R_prev
  sens_spec$FNR = 1- sens_spec$sensitivity
  sens_spec$FPR = 1- sens_spec$specificity
  
  sens_spec$P_S_R = sens_spec$FPR * sens_spec$FLQ_NR_prev/sens_spec$positive #Probability that Not FLQ resistance | p>1
  sens_spec$P_R_R = sens_spec$sensitivity * sens_spec$FLQ_R_prev/sens_spec$positive# Probability that FLQ resistance | p>1
  sens_spec$P_S_S = sens_spec$specificity * sens_spec$FLQ_NR_prev/sens_spec$negative #Probability that Not FLQ resistance | p<=1
  sens_spec$P_R_S = sens_spec$FNR * sens_spec$FLQ_R_prev/sens_spec$negative # Probability that FLQ resistance | p<=1
  
  perf = list(roc_curve = roc_curve, sens_spec = sens_spec)
  
  return(perf)
}