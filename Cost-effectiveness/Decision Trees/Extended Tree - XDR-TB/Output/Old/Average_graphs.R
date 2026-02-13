library(readxl)
library(dplyr)
library(ggplot2)
library(magrittr)
library(tidyr)
library(ggplot2)
library(gridExtra)

test = read_excel("/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Code/DR_TB_DT_MDRTree test/Test/NMB_DALY_Cost_FLQ_DLM_class_PMDT_avg_wtp1.xlsx")
test2 = read_excel("/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Code/DR_TB_DT_MDRTree test/Test/df_NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg_wtp1.xlsx")


ts=12

#DALY
FLQres_class_DALY_data = test %>%
  select(threshold, DALY_FLQ_positiveclass, DALY_DLM_positiveclass) %>%
  rename("FLQ" = "DALY_FLQ_positiveclass", "DLM" = "DALY_DLM_positiveclass") %>%
  mutate(Classification = "Classified FLQ resistant")

FLQsus_class_DALY_data = test %>%
  select(threshold, DALY_FLQ_negativeclass, DALY_DLM_negativeclass) %>%
  rename("FLQ" = "DALY_FLQ_negativeclass", "DLM" = "DALY_DLM_negativeclass") %>%
  mutate(Classification = "Classified FLQ susceptible")

all_data_DALY = bind_rows(FLQres_class_DALY_data, FLQsus_class_DALY_data)

# Plot
plot_daly = ggplot(all_data_DALY, aes(x = threshold, y = FLQ, color = "FLQ", group = Classification)) +
  geom_line() +
  geom_line(aes(y = DLM, color = "DLM")) +  # Different color for the second line
  labs(color = "Treatment", x = "Threshold", y = "Disability-adjusted life years", title = "Disability-adjusted life years depending on treatment and the prediction model classification") +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ Classification, scales = "free_y") +  # Facetted plot with grid layout
  scale_color_manual(values = c("DLM" = "#84ceff", "FLQ" = "#004c6d"), labels = c("Delamanid", "Fluoroquinolone")) +  # Manual color and label assignment
  theme(legend.position = "right")  # Adjust legend position



#Cost
FLQres_class_Cost_data = test %>%
  select(threshold, Cost_FLQ_positiveclass, Cost_DLM_positiveclass) %>%
  rename("FLQ" = "Cost_FLQ_positiveclass", "DLM" = "Cost_DLM_positiveclass") %>%
  mutate(Classification = "Classified FLQ resistant")

FLQsus_class_Cost_data = test %>%
  select(threshold, Cost_FLQ_negativeclass, Cost_DLM_negativeclass) %>%
  rename("FLQ" = "Cost_FLQ_negativeclass", "DLM" = "Cost_DLM_negativeclass") %>%
  mutate(Classification = "Classified FLQ susceptible")

all_data_Cost = bind_rows(FLQres_class_Cost_data, FLQsus_class_Cost_data)

# Plot
plot_cost = ggplot(all_data_Cost, aes(x = threshold, y = FLQ, color = "FLQ", group = Classification)) +
  geom_line() +
  geom_line(aes(y = DLM, color = "DLM")) +  # Different color for the second line
  labs(color = "Treatment", x = "Threshold", y = "Increase in cost", title = "Increase in cost depending on treatment and the prediction model classification") +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ Classification, scales = "free_y") +  # Facetted plot with grid layout
  scale_color_manual(values = c("DLM" = "#84ceff", "FLQ" = "#004c6d"), labels = c("Delamanid", "Fluoroquinolone")) +  # Manual color and label assignment
  theme(legend.position = "right")  # Adjust legend position

#NMB

#Cost
NMB_ResClass_data =test %>%
  select(threshold, NMB_FLQ_positiveclass, NMB_DLM_positiveclass) %>%
  rename("FLQ" = "NMB_FLQ_positiveclass", "DLM" = "NMB_DLM_positiveclass") %>%
  mutate(Classification = "Classified FLQ resistant")

#Cost
NMB_SusClass_data = test %>%
  select(threshold, NMB_FLQ_negativeclass, NMB_DLM_negativeclass) %>%
  rename("FLQ" = "NMB_FLQ_negativeclass", "DLM" = "NMB_DLM_negativeclass") %>%
  mutate(Classification = "Classified FLQ susceptible")

all_data_NMB = bind_rows(NMB_ResClass_data, NMB_SusClass_data)

# Plot
plot_nmb = ggplot(all_data_NMB, aes(x = threshold, y = FLQ, group = Classification)) +
  geom_line() +
  geom_line(aes(y = DLM, color = "DLM")) +  # Different color for the second line
  geom_hline(yintercept = 0, linetype = "dashed", color = "red") + 
  labs(color = "", x = "Threshold", y = "Change in NMB", title = "Incremental NMB with respect to the standard of care depending on the prediction model classification") +
  theme(text = element_text(size = 18)) +
  facet_grid(. ~ Classification, scales = "free_y") +  # Facetted plot with grid layout
  theme()  # Adjust legend position

NMB_Cost_DALY_classification_plot = grid.arrange(plot_daly, plot_cost, plot_nmb, ncol = 1)

ggsave(
  filename = "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_Cost_DALY_classification.png",
  plot = NMB_Cost_DALY_classification_plot,
  width = 15,
  height = 10
)

### 

#Cost, DALY and NMB for each DT depending on classification
ts=12

DALY_class_FLQres = test2 %>%
  select(threshold, DALY_SdTreat_PMDT_FLQ_Res, DALY_SdTreat_FLQ_Res, DALY_PMDT_FLQ_Res) %>%
  pivot_longer(
    cols = c(DALY_SdTreat_PMDT_FLQ_Res, DALY_SdTreat_FLQ_Res, DALY_PMDT_FLQ_Res),
    names_to = "group",
    values_to = "DALY"
  )


DALY_class_FLQres_plot = ggplot(DALY_class_FLQres, aes(x = threshold)) +
  geom_line(aes(y = DALY_SdTreat_PMDT_FLQ_Res, color = "Sd_PMDT")) +
  geom_line(aes(y = DALY_SdTreat_FLQ_Res, color = "Sd"))+
  geom_line(aes(y = DALY_PMDT_FLQ_Res, color = "PMDT"))+
  labs(
    color = "",
    title = "DALY of FLQ and DLM for patients classified FLQ resistant",
    x = "Threshold",
    y = "DALY"
  )+
  theme(text = element_text(size = ts))

DALY_class_FLQSus = test2 %>%
  select(threshold, DALY_SdTreat_PMDT_FLQ_Sus, DALY_SdTreat_FLQ_Sus, DALY_PMDT_FLQ_Sus) %>%
  pivot_longer(
    cols = c(DALY_SdTreat_PMDT_FLQ_Sus, DALY_SdTreat_FLQ_Sus, DALY_PMDT_FLQ_Sus),
    names_to = "group",
    values_to = "DALY"
  )

DALY_class_FLQsus_plot = ggplot(DALY_class_FLQSus, aes(x = threshold)) +
  geom_line(aes(y = DALY_SdTreat_PMDT_FLQ_Sus, color = "Sd_PMDT")) +
  geom_line(aes(y = DALY_SdTreat_FLQ_Sus, color = "Sd"))+
  geom_line(aes(y = DALY_PMDT_FLQ_Sus, color = "PMDT"))+
  labs(
    color = "",
    title = "DALY of FLQ and DLM for patients classified FLQ susceptible",
    x = "Threshold",
    y = "DALY"
  )+
  theme(text = element_text(size = ts))

Cost_class_FLQres_plot = ggplot(PMDT_performance_sus_res, aes(x = Threshold)) +
  geom_line(aes(y = Exp_FLQ_Cost_ResClass, color = "FLQ")) +
  geom_line(aes(y = Exp_DLM_Cost, color = "DLM"))+
  labs(
    color = "",
    title = "Cost of FLQ and DLM for patients classified FLQ resistant",
    x = "Threshold",
    y = "Cost"
  )+
  theme(text = element_text(size = ts))

Cost_class_FLQsus_plot = ggplot(PMDT_performance_sus_res, aes(x = Threshold)) +
  geom_line(aes(y = Exp_FLQ_Cost_SusClass, color = "FLQ")) +
  geom_line(aes(y = Exp_DLM_Cost, color = "DLM"))+
  labs(
    color = "",
    title = "Cost of FLQ and DLM for patients classified FLQ susceptible",
    x = "Threshold",
    y = "Cost"
  )+
  theme(text = element_text(size = ts))

NMB_class_FLQres_plot = ggplot(PMDT_performance_sus_res, aes(x = Threshold)) +
  geom_line(aes(y = NMB_ResClass, colour = "(NMB FLQ - NMB DLM)")) +
  geom_line(aes(y = NMB_FLQ_ResClass, colour = "NMB FLQ")) +
  geom_line(aes(y = NMB_DLM_ResClass, colour = "NMB DLM"))+
  labs(
    color = "",
    title = "NMB of FLQ and DLM for patients classified FLQ resistant",
    x = "Threshold",
    y = "NMB"
  )+
  ylim(c(-12000,25000))+
  theme(text = element_text(size = ts))

NMB_class_FLQsus_plot = ggplot(PMDT_performance_sus_res, aes(x = Threshold)) +
  geom_line(aes(y = NMB_SusClass, colour = "(NMB FLQ - NMB DLM)")) +
  geom_line(aes(y = NMB_FLQ_SusClass, colour = "NMB FLQ")) +
  geom_line(aes(y = NMB_DLM_SusClass, colour = "NMB DLM"))+
  labs(
    color = "",
    title = "NMB of FLQ and DLM for patients classified FLQ susceptible",
    x = "Threshold",
    y = "NMB"
  )+
  ylim(c(-12000,25000))+
  theme(text = element_text(size = ts))

# Arrange plots in a 2x3 grid
NMB_DALY_Cost_class_FLQ = grid.arrange(
  DALY_class_FLQres_plot, DALY_class_FLQsus_plot,
  Cost_class_FLQres_plot, Cost_class_FLQsus_plot,
  NMB_class_FLQres_plot, NMB_class_FLQsus_plot,
  ncol = 2
)


