setwd('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/HM/Bootstrap/Bootstrap PM - optimism corrected/Fic data')

pos = rep(1,100)
predpos = rnorm(100, 0.6,0.1)

neg = rep(0,400)
predneg = rnorm(400, 0.5,0.1)

fic_data = data.frame(observed = c(pos, neg), x = c(predpos, predneg))

# Add a random 'age' column with ages between 18 and 80
fic_data$age <- sample(10:80, size = nrow(fic_data), replace = TRUE)

# Add a random 'sex' column with "Female" or "Male"
fic_data$sex <- sample(c("Female", "Male"), size = nrow(fic_data), replace = TRUE, prob = c(0.5, 0.5))

# Fit logistic regression model
model <- glm(observed ~ x, data = fic_data, family = binomial)

# Predict probabilities for the same data
fic_data$predicted <- predict(model, type = "response")

# Calculate ROC curve
roc_curve <- roc(fic_data$observed, fic_data$predicted)

# Print AUC (Area Under the Curve)
cat("AUC:", auc(roc_curve), "\n")

write.csv(fic_data, 'fic_data_mainpred_medium.csv', row.names = FALSE)

boots_ficdata = data.frame()

for (i in 1:30){
  set.seed(i)
  
  bootstrap_sample <- fic_data %>% sample_n(size = n(), replace = TRUE)
  # Fit logistic regression model
  model <- glm(observed ~ x, data = bootstrap_sample, family = binomial)
  
  predicted_bootstrap = predict(model, type = "response")
  
  # Calculate ROC curve
  roc_curve <- roc(bootstrap_sample$observed, predicted_bootstrap )
  
  # Print AUC (Area Under the Curve)
  cat("AUC boot:", auc(roc_curve), "\n")
  
  predicted_origdata = predict(model, newdata = fic_data , type = "response")
  
  # Calculate ROC curve
  roc_curve <- roc(fic_data$observed, predicted_origdata)
  
  # Print AUC (Area Under the Curve)
  cat("AUC orig:", auc(roc_curve), "\n")
  
  
  boots_ficdata = rbind(boots_ficdata, data.frame(bootstrap_sample = rep(i, dim(fic_data)[1]), predicted_bootstrap = predicted_bootstrap, observed_bootstrap = bootstrap_sample$observed, predicted_origdata = predicted_origdata, observed_origdata = fic_data$observed)) 
  
}

write.csv(boots_ficdata, 'fic_data_boots_medium.csv', row.names = FALSE)