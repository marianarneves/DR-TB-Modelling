# Regularization
# Lasso Regression
# Load libraries, get data & set
# seed for reproducibility
set.seed(123)
library(glmnet)
library(dplyr)
library(pROC)
library(ROCR)
library(caret)  

# Load the new dataset
data_path <- "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_NN.csv"
moldova_data <- read.csv(data_path)

# Select relevant columns
selected_columns <- c("Age", "Family_size", "Family_size18")
y <- moldova_data %>% select(FLQ_R) %>% as.matrix()
X <- moldova_data %>% select(-Residence, -FLQ_R, selected_columns) %>% as.matrix()

# Split the data into training and testing sets (80% training, 20% testing)
set_split <- createDataPartition(y, p = 0.8, list = FALSE)
X_train <- X[set_split, ]
y_train <- y[set_split, ]
X_test <- X[-set_split, ]
y_test <- y[-set_split, ]

# Perform 10-fold cross-validation on the training set to select lambda
lambdas_to_try <- 10^seq(-3, 5, length.out = 100)
lasso_cv <- cv.glmnet(X_train, y_train, alpha = 1,
                      lambda = lambdas_to_try,
                      standardize = TRUE, nfolds = 10)

# Best cross-validated lambda
lambda_cv <- lasso_cv$lambda.min

# Fit final model on the training set
model_cv <- glmnet(X_train, y_train, alpha = 1, lambda = lambda_cv,
                   standardize = TRUE)

# Extract coefficients
coefficients <- as.matrix(coef(model_cv, s = lambda_cv))
nonzero_indices <- which(coefficients != 0, arr.ind = TRUE)
selected_features <- rownames(coefficients)[nonzero_indices[, "row"]]

# Print selected features
cat("Selected Features:", selected_features, "\n")

# Predict probabilities on the testing set
y_prob <- predict(model_cv, newx = X_test, s = lambda_cv, type = "response")

# Create a ROC curve for the testing set
roc_curve <- roc(response = y_test, predictor = y_prob)

# Plot the ROC curve
plot(roc_curve, col = "blue", main = "ROC Curve for Lasso Regression", col.main = "darkblue", lwd = 2)

# Add AUC to the plot
text(0.8, 0.2, paste("AUC =", round(auc(roc_curve), 2)), col = "darkred", cex = 1.2)

# Add legend
legend("bottomright", legend = "Lasso Model", col = "blue", lwd = 2)
