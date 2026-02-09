library(readxl)
library(dplyr)
library(ggplot2)
library(scales)

expand_ageband <- function(ageband) {
  ageband <- str_trim(ageband)
  
  if (ageband == "<1 year") {
    return(0)
  }
  
  if (str_detect(ageband, "\\+")) {
    # e.g. "85+ years"
    lower <- as.numeric(str_extract(ageband, "\\d+"))
    return(seq(100, lower, by = -1))
  }
  
  # e.g. "80-84 years"
  bounds <- str_extract_all(ageband, "\\d+")[[1]]
  low  <- as.numeric(bounds[1])
  high <- as.numeric(bounds[2])
  
  seq(high, low, by = -1)
}

setwd('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/R01 TB/Papers/Inter Exp PMDT')

source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/All Methods Comparisson/Exploring PIDEM structure/Training_Calibrating_LR.R')

# -------------------------------
# 2) Calculate Feature weights
# -------------------------------
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/All Methods Comparisson/Exploring PIDEM structure/Feature_Weight_Calculation.R')

#Features contribution Function
source('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Explainabilily Interpretability/All Methods Comparisson/Exploring PIDEM structure/Feature_Contribution_Calculation.R')


############################################################
## Individual predictions and DALY (YLL) lookup
## ---------------------------------------------------------
## This script:
##  1. Loads individual-level prediction outputs
##  2. Maps each individual to an age group and sex
##  3. Extracts remaining life expectancy (used here as YLL)
##  4. Selects representative patients based on YLL and risk
##  5. Extracts corresponding PIDEM probability and
##     classification outputs for those patients
############################################################

############################################################
## 1. Input data
############################################################

# Logistic regression individual predictions
LR_pred <- read.csv(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/LR/Output/LR_MainPM_platt_beta_compare.csv'
)

# Life expectancy table (used to derive YLL)
LE_data <- read.csv(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/LE_Moldova.csv'
)

############################################################
## 2. Helper function: individual YLL lookup
############################################################

# For each individual, this function:
#  - Classifies age into WHO-style age bands
#  - Matches age band, sex, and year in the LE table
#  - Returns the corresponding life expectancy value
#    (interpreted here as YLL)

compute_daly_individual <- function(data, le_data, year = 2019) {
  
  daly_list <- numeric(nrow(data))
  
  for (idx in seq_len(nrow(data))) {
    
    ## ---- Age classification ----
    age <- data$age[idx]
    
    age_s <- if (age < 1) {
      '<1 year'
    } else if (age <= 4) {
      '1-4 years'
    } else if (age <= 9) {
      '5-9 years'
    } else if (age <= 14) {
      '10-14 years'
    } else if (age <= 19) {
      '15-19 years'
    } else if (age <= 24) {
      '20-24 years'
    } else if (age <= 29) {
      '25-29 years'
    } else if (age <= 34) {
      '30-34 years'
    } else if (age <= 39) {
      '35-39 years'
    } else if (age <= 44) {
      '40-44 years'
    } else if (age <= 49) {
      '45-49 years'
    } else if (age <= 54) {
      '50-54 years'
    } else if (age <= 59) {
      '55-59 years'
    } else if (age <= 64) {
      '60-64 years'
    } else if (age <= 69) {
      '65-69 years'
    } else if (age <= 74) {
      '70-74 years'
    } else if (age <= 79) {
      '75-79 years'
    } else if (age <= 84) {
      '80-84 years'
    } else {
      '85+ years'
    }
    
    ## ---- Match LE table ----
    sex_s <- data$sex[idx]
    
    matched <- le_data[
      le_data$Dim2   == age_s &
        le_data$Dim1 == sex_s &
        le_data$Period == year,
    ]
    
    ## ---- Extract YLL ----
    daly_list[idx] <- if (nrow(matched) > 0) {
      matched$Value[1]
    } else {
      NA_real_
    }
  }
  
  return(daly_list)
}

############################################################
## 3. Compute YLL for all individuals
############################################################

LR_pred$YLL <- compute_daly_individual(
  data   = LR_pred,
  le_data = LE_data
)

# Empirical note:
# No patients have YLL < 4 in this dataset

####
# Calculating the weighted average of predictions considering YLL distribution

# -------------------------------
# Load Data
# -------------------------------
LE_data <- read.csv('/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/LE_Moldova.csv')

file_path <- "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/DT Only/Input_V10/Test age x NMB/PIDEMp/PIDEMp_YLLLE_test_output.xlsx"

YLL_LE_output <- read_excel(file_path)

# -------------------------------
# Calculate NMB & p*
# -------------------------------

wtp = 5714.43

YLL_LE_output_m = YLL_LE_output %>%
  mutate(NMB_FLQ_R = wtp * DALY_FLQres + Cost_FLQres,
         NMB_FLQ_S = wtp * DALY_FLQsus + Cost_FLQsus,
         pstar =  (NMB_DLM - NMB_FLQ_S)/ (NMB_FLQ_R - NMB_FLQ_S))

#Female
YLL_dist_female <- LR_pred %>%
  filter(sex == "Female") %>%
  group_by(YLL) %>%
  summarise(weight = n() / nrow(.), .groups = "drop")
                   
YLL_LE_output_female <- YLL_LE_output_m %>% slice(1:19) %>%
  cbind(LE_data %>%filter(Dim1 =='Female', Period ==2019) %>%
          select(Dim2, Value) %>% arrange(Value) %>% rename(Ageband = Dim2, YLL=Value)) %>%
  select(pstar, Ageband, YLL) %>%
  left_join(YLL_dist_female, by = 'YLL')

YLL_LE_output_female_allages = YLL_LE_output_female%>%
  mutate(age = map(Ageband, expand_ageband)) %>%
  unnest(age)

pstar_average_female = YLL_LE_output_female %>%
  mutate(weighted_pstar  = pstar * weight) %>%
  summarise(pstar_average  = sum(weighted_pstar, na.rm = TRUE))

#male
YLL_dist_male <- LR_pred %>%
  filter(sex == "Male") %>%
  group_by(YLL) %>%
  summarise(weight = n() / nrow(.), .groups = "drop")

YLL_LE_output_male <- YLL_LE_output_m %>% slice(20:38) %>%
  cbind(LE_data %>%filter(Dim1 =='Male', Period ==2019) %>%
          select(Dim2, Value) %>% arrange(Value) %>% rename(Ageband = Dim2, YLL=Value)) %>%
  select(pstar, Ageband, YLL)%>%
  left_join(YLL_dist_male, by = 'YLL')

YLL_LE_output_male_allages = YLL_LE_output_male%>%
  mutate(age = map(Ageband, expand_ageband)) %>%
  unnest(age)

pstar_average_male = YLL_LE_output_male %>%
  mutate(weighted_pstar  = pstar * weight) %>%
  summarise(pstar_average  = sum(weighted_pstar, na.rm = TRUE))

############################################################
## 4. Select representative patients
############################################################

# Low YLL (< 13) and lowest predicted risk
Pt_demo1 <- LR_pred %>%
  filter(YLL < 13) %>%
  slice_min(predicted_beta_mainpred, n = 1)

# Low YLL (< 13) and highest predicted risk
Pt_demo2 <- LR_pred %>%
  filter(YLL < 13) %>%
  slice_max(predicted_beta_mainpred, n = 1)

# High YLL (> 13) and lowest predicted risk
Pt_demo3 <- LR_pred %>%
  filter(YLL > 13) %>%
  slice_min(predicted_beta_mainpred, n = 1)

# High YLL (> 13) and highest predicted risk
# (restricted to be below the max risk observed in low-YLL)
Pt_demo4 <- LR_pred %>%
  slice(142)
  
  # LR_pred %>%
  # filter(YLL > 13 &
  #          predicted_beta_mainpred < Pt_demo2$predicted_beta_mainpred) %>%
  # slice_max(predicted_beta_mainpred, n = 10)

############################################################
## 5. Original PIDEM probability outputs (PIDEMp)
############################################################

Probability_PIDEM <- read_xlsx(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM input Only/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx'
)

# Note: PIDEM Person index is zero-based, hence pt_id - 1
PIDEMp_Pt_demo1 <- Probability_PIDEM %>% filter(Person == Pt_demo1$pt_id - 1)
PIDEMp_Pt_demo2 <- Probability_PIDEM %>% filter(Person == Pt_demo2$pt_id - 1)
PIDEMp_Pt_demo3 <- Probability_PIDEM %>% filter(Person == Pt_demo3$pt_id - 1)
PIDEMp_Pt_demo4 <- Probability_PIDEM %>% filter(Person == Pt_demo4$pt_id - 1)

############################################################
## 6. Original PIDEM classification outputs (PIDEMc)
############################################################

Classification_PIDEM <- read_xlsx(
  '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/LR/Beta Calibration/PM Bootstrap/Input_V10/PMDT_wtp2bootstrapping_samplesize200.xlsx'
) %>%
  # Select threshold closest to the optimal value (0.308)
  filter(Threshold == Threshold[which.min(abs(Threshold - 0.308))])

PIDEMc_Pt_demo1 <- Classification_PIDEM %>% filter(Person == Pt_demo1$pt_id - 1)
PIDEMc_Pt_demo2 <- Classification_PIDEM %>% filter(Person == Pt_demo2$pt_id - 1)
PIDEMc_Pt_demo3 <- Classification_PIDEM %>% filter(Person == Pt_demo3$pt_id - 1)
PIDEMc_Pt_demo4 <- Classification_PIDEM %>% filter(Person == Pt_demo4$pt_id - 1)

############################################################
## 7. Next steps
############################################################
# These selected patients can now be used for:
#  - Individual-level decision tree walkthroughs
#  - Comparison of calibrated vs uncalibrated decisions
#  - Illustrative examples in figures or appendices
############################################################

#####
# Pt Demo 1
patient_demo1 <- moldova_data %>%
  slice( Pt_demo1$pt_id) %>%
  select(-Pt_id) %>%
  as.data.frame()

# Compute contributions for all features
patient_demo1_contribs <- feature_contributions_patient(
  patient_row = patient_demo1,
  feature_weights = feature_weights,
  predict_fn = predict_calibrated,
  formula = formula
)

patient_demo1_YLLcontrib <- YLL_LE_output_male_allages %>%
  filter(age == patient_demo1$Age) %>%
  mutate(YLLcontrib = as.numeric(pstar_average_male)- pstar) %>%
  pull(YLLcontrib)

#Selecting only contributors towards treatment recomended
patient_demo1_allcontrib = patient_demo1_contribs %>%
  rbind(tibble(Feature = "YLL", Contribution = patient_demo1_YLLcontrib)) %>%
  filter(Contribution < 0) %>%
  mutate(RelImportance = abs(Contribution) / sum(abs(Contribution)))  %>%
  arrange(RelImportance)

patient_demo1_allcontrib_plot = ggplot(
  patient_demo1_allcontrib,
  aes(
    x = RelImportance,
    y = reorder(Feature, RelImportance),
    fill = RelImportance   # <-- use absolute value for fill
  )
) +
  geom_col(width = 0.8) +
  scale_fill_gradient(
    low = "#bdd7e7",
    high = "#6baed6",
    name = "Relative Importance"
  ) +
  labs(
    # title = "Top 10 Variables",
    x = "Relative Importance",
    y = "Patient Characteristic"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold", size = 20, hjust = 0.5),
    legend.position = "right"
  ) +
  scale_x_continuous(
    limits = c(0, 0.6)
  )

ggsave('patient_demo1_allcontrib_plot.png', patient_demo1_allcontrib_plot, width = 12, height = 6, dpi = 300)


# Calculate the 
patient_demo2 <- moldova_data %>%
  slice( Pt_demo2$pt_id) %>%
  select(-Pt_id) %>%
  as.data.frame()

# Compute contributions for all features
patient_demo2_contribs <- feature_contributions_patient(
  patient_row = patient_demo2,
  feature_weights = feature_weights,
  predict_fn = predict_calibrated,
  formula = formula
)

patient_demo2_YLLcontrib <- YLL_LE_output_female_allages %>%
  filter(age == patient_demo2$Age) %>%
  mutate(YLLcontrib = as.numeric(pstar_average_female)- pstar) %>%
  pull(YLLcontrib)

#Selecting only contributors towards treatment recommended
patient_demo2_allcontrib = patient_demo2_contribs %>%
  filter(Contribution > 0) %>%
  mutate(RelImportance = abs(Contribution) / sum(abs(Contribution)))  %>%
  arrange(RelImportance)

patient_demo2_allcontrib_plot = ggplot(
  patient_demo2_allcontrib,
  aes(
    x = RelImportance,
    y = reorder(Feature, RelImportance),
    fill = RelImportance   # <-- use absolute value for fill
  )
) +
  geom_col(width = 0.8) +
  scale_fill_gradient(
    low = "#bdd7e7",
    high = "#6baed6",
    name = "Relative Importance"
  ) +
  labs(
    # title = "Top 10 Variables",
    x = "Relative Importance",
    y = "Patient Characteristic"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold", size = 20, hjust = 0.5),
    legend.position = "right"
  ) +
  scale_x_continuous(
    limits = c(0, 0.6)
  )

ggsave('patient_demo2_allcontrib_plot.png', patient_demo2_allcontrib_plot, width = 12, height = 6, dpi = 300)

# Calculate the 
patient_demo3 <- moldova_data %>%
  slice( Pt_demo3$pt_id) %>%
  select(-Pt_id) %>%
  as.data.frame()

# Compute contributions for all features
patient_demo3_contribs <- feature_contributions_patient(
  patient_row = patient_demo3,
  feature_weights = feature_weights,
  predict_fn = predict_calibrated,
  formula = formula
)

patient_demo3_YLLcontrib <- YLL_LE_output_male_allages %>%
  filter(age == patient_demo3$Age) %>%
  mutate(YLLcontrib = as.numeric(pstar_average_male)- pstar) %>%
  pull(YLLcontrib)

#Selecting only contributors towards treatment recommended
patient_demo3_allcontrib = patient_demo3_contribs %>%
  filter(Contribution < 0) %>%
  mutate(RelImportance = abs(Contribution) / sum(abs(Contribution)))  %>%
  arrange(RelImportance)

patient_demo3_allcontrib_plot = ggplot(
  patient_demo3_allcontrib,
  aes(
    x = RelImportance,
    y = reorder(Feature, RelImportance),
    fill = RelImportance   # <-- use absolute value for fill
  )
) +
  geom_col(width = 0.8) +
  scale_fill_gradient(
    low = "#bdd7e7",
    high = "#6baed6",
    name = "Relative Importance"
  ) +
  labs(
    # title = "Top 10 Variables",
    x = "Relative Importance",
    y = "Patient Characteristic"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold", size = 20, hjust = 0.5),
    legend.position = "right"
  ) +
  scale_x_continuous(
    limits = c(0, 0.6)
  )

ggsave('patient_demo3_allcontrib_plot.png', patient_demo3_allcontrib_plot, width = 12, height = 6, dpi = 300)


# Calculate the 
patient_demo4 <- moldova_data %>%
  slice( Pt_demo4$pt_id) %>%
  select(-Pt_id) %>%
  as.data.frame()

# Compute contributions for all features
patient_demo4_contribs <- feature_contributions_patient(
  patient_row = patient_demo4,
  feature_weights = feature_weights,
  predict_fn = predict_calibrated,
  formula = formula
)

patient_demo4_YLLcontrib <- YLL_LE_output_female_allages %>%
  filter(age == patient_demo4$Age) %>%
  mutate(YLLcontrib = as.numeric(pstar_average_female)- pstar) %>%
  pull(YLLcontrib)

#Selecting only contributors towards treatment recommended
patient_demo4_allcontrib = patient_demo4_contribs %>%
  rbind(tibble(Feature = "YLL", Contribution = patient_demo1_YLLcontrib)) %>%
  filter(Contribution > 0) %>%
  mutate(RelImportance = abs(Contribution) / sum(abs(Contribution)))  %>%
  arrange(RelImportance)

patient_demo4_allcontrib_plot = ggplot(
  patient_demo4_allcontrib,
  aes(
    x = RelImportance,
    y = reorder(Feature, RelImportance),
    fill = RelImportance   # <-- use absolute value for fill
  )
) +
  geom_col(width = 0.8) +
  scale_fill_gradient(
    low = "#bdd7e7",
    high = "#6baed6",
    name = "Relative Importance"
  ) +
  labs(
    # title = "Top 10 Variables",
    x = "Relative Importance",
    y = "Patient Characteristic"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold", size = 20, hjust = 0.5),
    legend.position = "right"
  ) +
  scale_x_continuous(
    limits = c(0, 0.6)
  )

ggsave('patient_demo4_allcontrib_plot.png', patient_demo4_allcontrib_plot, width = 12, height = 6, dpi = 300)

