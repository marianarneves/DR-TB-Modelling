# =============================================================
# Logistic Regression (No Regularization) + CV + Explanations
# =============================================================

library(dplyr)
library(ggplot2)
library(pROC)

set.seed(123)

# External function: main contribution
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/All Methods Comparisson/main_contribution_LR_surrogate.R')

# =============================================================
# 1. Load Data
# =============================================================

PIDEMp_input_path <- '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/Decision Tree ML/No Calibration/PM input Only/Input/ModLE/Moldova_data_opt_treat_prediction_allthresholds_wtp2.csv'

PIDEMp_PMDT <- read.csv(PIDEMp_input_path)

PIDEMp_PMDT_maxNMB <- PIDEMp_PMDT %>%
  mutate(Opt_Treat_n = ifelse(Opt_Treat == "FLQ", 0, 1))

df <- PIDEMp_PMDT_maxNMB %>%
  select(-c(Person, Pt_id, FLQ_R, n, Residence, Opt_Treat))

# Design matrix
x <- model.matrix(Opt_Treat_n ~ ., df)[, -1]
y <- df$Opt_Treat_n
n <- nrow(x)

df_model <- data.frame(y = y, x)

# =============================================================
# 2. Fit Logistic Model
# =============================================================

fit_logit <- glm(
  y ~ .,
  data = df_model,
  family = binomial()
)

summary(fit_logit)

# =============================================================
# 3. Apparent Performance
# =============================================================

df$pred_prob <- predict(fit_logit, type = "response")
df$pred_class <- ifelse(df$pred_prob > 0.5, 1, 0)

roc_app <- roc(y, df$pred_prob)
auc_app <- auc(roc_app)

cat("Apparent AUC:", round(auc_app, 3), "\n")

# =============================================================
# 4. 5-Fold Cross-Validation
# =============================================================

k <- 5
fold_id <- sample(rep(1:k, length.out = n))

pred_prob_cv <- rep(NA, n)
auc_values <- numeric(k)

for (fold in 1:k) {
  
  test_index  <- which(fold_id == fold)
  train_index <- setdiff(1:n, test_index)
  
  train_data <- data.frame(y = y[train_index], x[train_index, ])
  test_data  <- data.frame(y = y[test_index],  x[test_index, ])
  
  fit_cv <- glm(
    y ~ .,
    data = train_data,
    family = binomial()
  )
  
  pred_prob <- predict(fit_cv, newdata = test_data, type = "response")
  
  pred_prob_cv[test_index] <- pred_prob
  
  auc_values[fold] <- auc(roc(test_data$y, pred_prob))
}

cat("Fold AUCs:", round(auc_values, 3), "\n")
cat("Mean CV AUC:", round(mean(auc_values), 3),
    "SD:", round(sd(auc_values), 3), "\n")

roc_cv <- roc(y, pred_prob_cv)
cat("Pooled CV AUC:", round(auc(roc_cv), 3), "\n")

df$pred_prob_cv <- pred_prob_cv

# =============================================================
# 5. Main Contribution for ALL Patients
# =============================================================

main_contrib_all <- do.call(
  rbind,
  lapply(1:n, function(i) {
    get_main_contribution(
      fit = fit_logit,
      x_matrix = x,
      y_vector = y,
      patient_id = i
    )
  })
)

# Optional: frequency of main drivers
driver_freq <- main_contrib_all %>%
  count(main_variable, sort = TRUE)

print(head(driver_freq, 10))

# =============================================================
# 6. Example Explanation: Patient 38
# =============================================================

patient_id <- 38

result_38 <- get_main_contribution(
  fit = fit_logit,
  x_matrix = x,
  y_vector = y,
  patient_id = patient_id
)

print(result_38$main_driver)

# =============================================================
# 7. Detailed Contribution Table (Patient 38)
# =============================================================

coef_vector <- coef(fit_logit)
beta <- coef_vector[-1]
beta <- beta[colnames(x)]

x_patient <- x[patient_id, ]
contrib <- x_patient * beta

contrib_df <- data.frame(
  Variable = colnames(x),
  Value = as.numeric(x_patient),
  Contribution = as.numeric(contrib)
) %>%
  filter(Value != 0) %>%
  arrange(desc(abs(Contribution)))

# =============================================================
# 8. Negative Contributions (toward FQ)
# =============================================================

neg_contrib <- contrib_df %>%
  filter(Contribution < 0) %>%
  mutate(
    Abs_Contribution = abs(Contribution),
    Weight = Abs_Contribution / sum(Abs_Contribution)
  ) %>%
  arrange(desc(Weight))

# =============================================================
# 9. Plot
# =============================================================

neg_plot <- neg_contrib %>%
  rename(Feature = Variable) %>%
  mutate(RelImportance = Weight) %>%
  arrange(RelImportance)

patient38_neg_plot <- ggplot(
  neg_plot,
  aes(
    x = RelImportance,
    y = reorder(Feature, RelImportance),
    fill = RelImportance
  )
) +
  geom_col(width = 0.8) +
  scale_fill_gradient(
    low = "#bdd7e7",
    high = "#6baed6",
    name = "Relative Importance"
  ) +
  labs(
    title = paste("Patient", patient_id,
                  "- Factors reducing probability of non-FQ"),
    x = "Relative Importance",
    y = "Patient Characteristic"
  ) +
  theme_minimal(base_size = 14)

ggsave(
  'patient38_negative_contributions.png',
  patient38_neg_plot,
  width = 12,
  height = 6,
  dpi = 300
)