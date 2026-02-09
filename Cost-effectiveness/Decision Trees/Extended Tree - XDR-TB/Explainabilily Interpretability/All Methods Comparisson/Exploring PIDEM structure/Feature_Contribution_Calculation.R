feature_contributions_patient <- function(patient_row, feature_weights, predict_fn, formula) {
  library(dplyr)
  library(stringr)
  
  # ----------------------------
  # All unique variables
  # ----------------------------
  all_vars <- unique(feature_weights$variable)
  
  # Original calibrated prediction
  orig_pred <- predict_fn(model.matrix(formula, patient_row)[,-1])
  
  # Initialize output
  contributions <- numeric(length(all_vars))
  names(contributions) <- all_vars
  
  # Loop over each variable
  for (var_name in all_vars) {
    
    # Extract categories and weights
    var_weights <- feature_weights %>% filter(variable == var_name)
    
    # Detect if binned numeric (contains brackets) or categorical dummy
    is_binned <- any(str_detect(var_weights$category, "\\[|\\("))
    
    # Compute predictions for each category
    pred_per_cat <- sapply(var_weights$category, function(cat) {
      new_row <- patient_row
      
      if (is_binned) {
        # Continuous binned variable: use midpoint of interval
        nums <- str_extract_all(cat, "\\d+\\.*\\d*")[[1]]
        midpoint <- mean(as.numeric(nums))
        new_row[[var_name]] <- midpoint
        
      } else {
        # Categorical/dummy variable
        dummy_cols <- names(patient_row)[str_detect(names(patient_row), paste0("^", var_name, "_"))]
        
        if (length(dummy_cols) > 0) new_row[dummy_cols] <- 0
        
        if (cat != "ref") {
          new_row[[paste0(var_name, "_", cat)]] <- 1
        }
      }
      
      newx_mat <- model.matrix(formula, new_row)[,-1]
      predict_fn(newx_mat)
    })
    
    # Weighted average over categories
    weighted_pred <- sum(pred_per_cat * var_weights$weight)
    
    # Contribution = original - weighted
    contributions[var_name] <- orig_pred - weighted_pred
  }
  
  # ----------------------------
  # Convert to data.frame
  # ----------------------------
  contrib_df <- data.frame(
    Feature = names(contributions),
    Contribution = as.numeric(contributions)
  )
  
  # ----------------------------
  # Clean Feature names: underscores → spaces, capitalize words
  # ----------------------------
  contrib_df$Feature <- contrib_df$Feature %>%
    str_replace_all("_", " ") %>%
    str_to_title()
  
  # Sort from max → min contribution
  contrib_df <- contrib_df[order(-contrib_df$Contribution), ]
  
  return(contrib_df)
}
