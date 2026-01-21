# Define the function for cross-validation
hierarchical_cv <-
  function(data,
           response,
           formula,
           nfolds = 5,
           iter = 10000,
           chains = 4,
           regularization = "No",
           cons_D2 = "NA") {
    # Create folds for cross-validation
    folds <- createFolds(data[[response]], k = nfolds)
    cv_results <- list()
    roc_curve <- list()
    roc_auc <- list()
    y_prob <- list()
    y_true <- list()
    
    # Perform cross-validation
    for (i in 1:nfolds) {
      # Split data into training and testing sets
      train_indices <- unlist(folds[-folds[[i]]])
      test_indices <- unlist(folds[[i]])
      train_data <- data[train_indices, ]
      test_data <- data[test_indices,]
      y_true[[i]] <- data[[response]][test_indices]
      
      if (regularization == "Yes") {
        # Fit the hierarchical logistic regression model
        hierarchical_model <- brm(
          formula = formula,
          data = train_data,
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
          iter = iter,
          chains = chains,
          control = list(adapt_delta = 0.999)
        )
      } else{
        # Fit the hierarchical logistic regression model
        hierarchical_model <- brm(
          formula = formula,
          data = train_data,
          family = bernoulli(link = "logit"),
          iter = iter,
          chains = chains,
          control = list(adapt_delta = 0.999)
        )
      }
      
      # Predict on test data
      predictions <-
        posterior_epred(hierarchical_model,
                        newdata = test_data,
                        allow_new_levels = TRUE)
      # Store results
      cv_results[[i]] <-
        list("model" = hierarchical_model, "predictions" = predictions)
      #Calculate the mean
      y_prob[[i]] <-
        apply(cv_results[[i]]$predictions, 2,  function(x)
          mean(x))
      # Create a ROC curve for the testing set
      roc_curve[[i]] <-
        roc(response = y_true[[i]], predictor = y_prob[[i]])
      roc_auc[[i]] <- roc_curve[[i]]$auc
    }
    
    return(
      list(
        "cv_results" = cv_results,
        "y_true" = y_true,
        "y_prob" = y_prob,
        "roc_curve" = roc_curve,
        "roc_auc" = roc_auc
      )
    )
  }

