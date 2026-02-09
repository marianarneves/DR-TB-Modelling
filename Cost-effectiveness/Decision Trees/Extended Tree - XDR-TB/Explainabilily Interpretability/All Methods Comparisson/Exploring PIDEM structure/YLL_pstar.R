# -------------------------------
# Load Libraries
# -------------------------------
library(readxl)
library(dplyr)
library(ggplot2)
library(scales)
library(dplyr)
library(tidyr)
library(stringr)
library(purrr)

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

# -------------------------------
# Load Data
# -------------------------------
file_path <- "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/DT Only/Input_V10/Test age x NMB/test_output.xlsx"

data <- read_excel(file_path)

# -------------------------------
# Calculate NMB & p*
# -------------------------------

wtp = 5714.43

data_m = data %>%
  mutate(NMB_FLQ_R = wtp * DALY_FLQres + Cost_FLQres,
         NMB_FLQ_S = wtp * DALY_FLQsus + Cost_FLQsus,
         pstar =  (NMB_DLM - NMB_FLQ_S)/ (NMB_FLQ_R - NMB_FLQ_S))

# Ensure data is sorted
data_m <- data_m %>% arrange(Person)

# -------------------------------
# Find crossing point p* ≈ 1
# -------------------------------
cross_x <- data_m %>%
  slice(which.min(abs(pstar - 1))) %>%
  pull(Person)

cross_x <- data_m$Person[which.min(abs(data_m$pstar - 1))]

# -------------------------------
# Build Plot
# -------------------------------

Prob_YLL = ggplot(data_m, aes(x = Person, y = pstar)) +
  
  # --- RIBBONS FIRST (background layer) ---
  geom_ribbon(aes(ymin = 0, ymax = pstar, fill = "FQ"), alpha = 0.25) +
  geom_ribbon(aes(ymin = pstar, ymax = max(pstar, na.rm = TRUE), fill = "CFZ"), alpha = 0.20) +
  
  # --- REFERENCE LINE (draw AFTER ribbons so it stays visible) ---
  geom_hline(yintercept = 1, linetype = "dotted", color = "gray40", linewidth = 1) +
  
  # --- MAIN LINE (draw AFTER EVERYTHING so it is always visible) ---
  geom_line(color = "#1f4e79", linewidth = 1.4) +
  # add a white outline to make it visible near 0
  geom_line(color = "white", linewidth = 2, alpha = 0.4) +
  geom_point(color = "#163758", size = 1) +
  
  # Crossing marker
  geom_vline(xintercept = cross_x, linetype = "dashed", color = "#d62728", linewidth = 1.1) +
  
  # Annotation
  annotate(
    "label",
    x = cross_x + 10,
    y = max(data_m$pstar, na.rm = TRUE) * 0.9,
    label = paste0("YLL ≈ ", round(cross_x, 1)),
    size = 4.5,
    fill = "white",
    color = "#d62728",
    label.size = 0
  ) +
  
  labs(
    #title = "Probability Threshold p* as a Function of Years of Life Lost",
    x = "Years of Life Lost",
    y = "Probability Threshold p*",
    fill = "Optimal Treatment"
  ) +
  
  scale_x_continuous(
    breaks = seq(0, ceiling(max(data_m$Person, na.rm = TRUE)), by = 5),
    labels = scales::number_format(accuracy = 1),
    expand = expansion(mult = c(0.02, 0.02))
  ) +
  scale_y_continuous(
    breaks = seq(0, ceiling(max(data_m$pstar, na.rm = TRUE)), by = 0.25),
    labels = scales::number_format(accuracy = 0.01),
    expand = expansion(mult = c(0, 0.002))
  ) +
  
  scale_fill_manual(values = c("FQ" = "#7eb6ff", "CFZ" = "#ffb866")) +
  
  theme_minimal(base_size = 15) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0, size = 16),
    axis.text.y = element_text(size = 14,  face = "bold"),
    axis.text.x = element_text(size = 14),
    axis.title.x = element_text(size = 16, face = "bold"),
    axis.title.y = element_text(size = 16, face = "bold"),
    panel.grid.major = element_line(color = "grey85", linewidth = 0.4),
    panel.grid.minor = element_blank(),
    axis.title = element_text(face = "bold"),
    legend.position = "bottom",
    legend.title = element_text(size = 14,face = "bold"),
    legend.text = element_text(size = 14),
    legend.key.width = unit(1, "cm")
  )

ggsave('Prob_YLL.png', Prob_YLL, width = 12, height = 6, dpi = 300)

### YLL dependent on LE

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

# Ensure data is sorted
YLL_LE_output_female <- YLL_LE_output_m %>% slice(1:19) %>%
  cbind(LE_data %>%filter(Dim1 =='Female', Period ==2019) %>%
    select(Dim2, Value) %>% arrange(Value) %>% rename(Ageband = Dim2, YLL=Value)) %>%
  select(pstar, Ageband, YLL) %>%
  mutate(age = map(Ageband, expand_ageband)) %>%
  unnest(age)

YLL_LE_output_male <- YLL_LE_output_m %>% slice(20:38) %>%
  cbind(LE_data %>%filter(Dim1 =='Male', Period ==2019) %>%
          select(Dim2, Value) %>% arrange(Value) %>% rename(Ageband = Dim2, YLL=Value)) %>%
  select(pstar, Ageband, YLL) %>%
  mutate(age = map(Ageband, expand_ageband)) %>%
  unnest(age)


# -------------------------------
# Build Plot
# -------------------------------

Prob_YLL_female = ggplot(YLL_LE_output_female, aes(x = 100 - age, y = pstar)) +
  
  # --- RIBBONS FIRST (background layer) ---
  geom_ribbon(
    aes(ymin = 0, ymax = pstar, fill = "FQ"),
    alpha = 0.25
  ) +
  geom_ribbon(
    aes(ymin = pstar, ymax = 1, fill = "CFZ"),   # ← CHANGED HERE
    alpha = 0.20
  ) +
  
  # --- REFERENCE LINE ---
  geom_hline(
    yintercept = 1,
    linetype = "dotted",
    color = "gray40",
    linewidth = 1
  ) +
  
  # --- MAIN LINE ---
  geom_line(color = "#1f4e79", linewidth = 1.4) +
  geom_line(color = "white", linewidth = 2, alpha = 0.4) +
  geom_point(color = "#163758", size = 1) +
  
  labs(
    x = "100 - Age",
    y = "Probability Threshold p*",
    fill = "Optimal Treatment"
  ) +
  
  scale_x_continuous(
    breaks = seq(0, ceiling(max(data_m$Person, na.rm = TRUE)), by = 5),
    labels = scales::number_format(accuracy = 1),
    expand = expansion(mult = c(0.02, 0.02))
  ) +
  scale_y_continuous(
    breaks = seq(0, 1, by = 0.25),
    labels = scales::number_format(accuracy = 0.01),
    limits = c(0, 1),
    expand = expansion(mult = c(0, 0))
  ) +
  
  scale_fill_manual(values = c("FQ" = "#7eb6ff", "CFZ" = "#ffb866")) +
  
  theme_minimal(base_size = 15) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0, size = 16),
    axis.text.y = element_text(size = 14, face = "bold"),
    axis.text.x = element_text(size = 14),
    axis.title.x = element_text(size = 16, face = "bold"),
    axis.title.y = element_text(size = 16, face = "bold"),
    panel.grid.major = element_line(color = "grey85", linewidth = 0.4),
    panel.grid.minor = element_blank(),
    legend.position = "bottom",
    legend.title = element_text(size = 14, face = "bold"),
    legend.text = element_text(size = 14),
    legend.key.width = unit(1, "cm")
  )


ggsave('Prob_YLL_female.png', Prob_YLL_female, width = 12, height = 6, dpi = 300)


Prob_YLL_male = ggplot(YLL_LE_output_male, aes(x = 100 - age, y = pstar)) +
  
  # --- RIBBONS FIRST (background layer) ---
  geom_ribbon(
    aes(ymin = 0, ymax = pstar, fill = "FQ"),
    alpha = 0.25
  ) +
  geom_ribbon(
    aes(ymin = pstar, ymax = 1, fill = "CFZ"),   # ← CHANGED HERE
    alpha = 0.20
  ) +
  
  # --- REFERENCE LINE ---
  geom_hline(
    yintercept = 1,
    linetype = "dotted",
    color = "gray40",
    linewidth = 1
  ) +
  
  # --- MAIN LINE ---
  geom_line(color = "#1f4e79", linewidth = 1.4) +
  geom_line(color = "white", linewidth = 2, alpha = 0.4) +
  geom_point(color = "#163758", size = 1) +
  
  labs(
    x = "100 - Age",
    y = "Probability Threshold p*",
    fill = "Optimal Treatment"
  ) +
  
  scale_x_continuous(
    breaks = seq(0, ceiling(max(data_m$Person, na.rm = TRUE)), by = 5),
    labels = scales::number_format(accuracy = 1),
    expand = expansion(mult = c(0.02, 0.02))
  ) +
  scale_y_continuous(
    breaks = seq(0, 1, by = 0.25),
    labels = scales::number_format(accuracy = 0.01),
    limits = c(0, 1),
    expand = expansion(mult = c(0, 0))
  ) +
  
  scale_fill_manual(values = c("FQ" = "#7eb6ff", "CFZ" = "#ffb866")) +
  
  theme_minimal(base_size = 15) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0, size = 16),
    axis.text.y = element_text(size = 14, face = "bold"),
    axis.text.x = element_text(size = 14),
    axis.title.x = element_text(size = 16, face = "bold"),
    axis.title.y = element_text(size = 16, face = "bold"),
    panel.grid.major = element_line(color = "grey85", linewidth = 0.4),
    panel.grid.minor = element_blank(),
    legend.position = "bottom",
    legend.title = element_text(size = 14, face = "bold"),
    legend.text = element_text(size = 14),
    legend.key.width = unit(1, "cm")
  )

ggsave('Prob_YLL_male.png', Prob_YLL_male, width = 12, height = 6, dpi = 300)




##########-----------


 
# ------------------------------------------------------------
# 1. Load data
# ------------------------------------------------------------
# Input data should contain at least:
#   - Threshold   : willingness-to-pay threshold
#   - Opt_Treat   : optimal treatment at each (Threshold, YLL)
#   - Rows ordered by Threshold, then YLL
# ------------------------------------------------------------

file_path <- '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/DT Only/Input_V10/Test age x NMB/PIDEMc/PIDEMc_YLL_test_output.xlsx'
data <- read_excel(file_path)


# ------------------------------------------------------------
# 2. Prepare analysis-ready dataset
# ------------------------------------------------------------
# YLL is reconstructed assuming 101 severity levels per threshold.
# Opt_Treat is coerced to a factor to ensure correct counting.
# ------------------------------------------------------------

data_ax <- data %>%
  filter(Threshold == Threshold[which.min(abs(Threshold - 0.308))]) %>%
  mutate(
    YLL = (row_number() - 1) %% 101,
    Opt_Treat = factor(Opt_Treat, levels = c("FLQ", "DLM")),
    Opt_Treat_m = ifelse(Opt_Treat == "FLQ", "FQ", "CFZ"),
    Opt_Treat_m = factor(Opt_Treat_m, levels = c("FQ", "CFZ")),
    Class = ifelse(PM_prediction == 0.0001, 'FQ Susceptible', 'FQ Resistant'),
    y_pos = as.numeric(Opt_Treat_m) +
      ifelse(Class == "FQ Susceptible", -0.05, 0.05)
  )

opt_treat_PIDEMc_opt_thre = ggplot(data_ax, aes(
  x = YLL,
  y = y_pos,
  colour = Class,
  shape = Class
)) +
  geom_point(size = 2.5) +
  scale_y_continuous(
    breaks = seq_along(levels(data_ax$Opt_Treat_m)),
    labels = levels(data_ax$Opt_Treat_m)
  ) +
  scale_x_continuous(
    breaks = seq(0, max(data_ax$YLL, na.rm = TRUE), by = 5),
    expand = expansion(mult = c(0.02, 0.02))
  ) +
  scale_colour_manual(
    values = c(
      "FQ Susceptible" = "#7eb6ff",  # blue
      "FQ Resistant" = "#ffb866"   # orange
    )
  ) +
  scale_shape_manual(
    values = c(
      "FQ Susceptible" = 15,  # square
      "FQ Resistant" = 16   # circle
    )
  ) +
  labs(
    x = "Years of Life Lost (YLL)",
    y = "Optimal Treatment",
    colour = "Classification",
    shape = "Classification"
  ) +
  theme_minimal(base_size = 15) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0, size = 16),
    axis.text.y = element_text(size = 14,  face = "bold"),
    axis.text.x = element_text(size = 14),
    axis.title.x = element_text(size = 16, face = "bold"),
    axis.title.y = element_text(size = 16, face = "bold"),
    panel.grid.major.x = element_line(color = "grey85", linewidth = 0.4),
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title = element_text(face = "bold"),
    legend.position = "bottom",
    legend.title = element_text(size = 14,face = "bold"),
    legend.text = element_text(size = 14),
    legend.key.width = unit(1, "cm")
  )


ggsave('opt_treat_PIDEMc_opt_thre.png', opt_treat_PIDEMc_opt_thre, width = 12, height = 6, dpi = 300)

