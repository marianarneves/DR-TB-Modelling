library(readxl)
library(dplyr)
library(ggplot2)
library(magrittr)
library(tidyr)
library(ggplot2)
library(gridExtra)

setwd(
  "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB"
)

#Read dataset
NMB_avg_data <- read_excel("Output/NMB_sus_res_varWTP.xlsx")

NMB_avg_data_long = NMB_avg_data %>%
  group_by(WTP) %>%
  filter(NMB_avg == max(NMB_avg)) %>%
  ungroup() %>%
  select (Threshold, WTP, NMB_avg_sd_r, NMB_avg_sd_s, NMB_avg) %>%
  pivot_longer(
    cols = c(NMB_avg_sd_r, NMB_avg_sd_s, NMB_avg),
    names_to = "group",
    values_to = "NMB"
  )
  
NMB_avg_data_long_loweric = NMB_avg_data %>%
  select (Threshold, WTP,
          NMB_avg_sd_r_loweric,
          NMB_avg_sd_s_loweric,
          NMB_avg_sd_loweric) %>%
  rename(
    "NMB_avg_sd_r" = "NMB_avg_sd_r_loweric",
    "NMB_avg_sd_s" = "NMB_avg_sd_s_loweric",
    "NMB_avg" = "NMB_avg_sd_loweric"
  )%>%
pivot_longer(
  cols = c(NMB_avg_sd_r, NMB_avg_sd_s, NMB_avg),
  names_to = "group",
  values_to = "lower_ic"
)
  
NMB_avg_data_long_upperic = NMB_avg_data %>%
  select (Threshold, WTP,
          NMB_avg_sd_r_upperic,
          NMB_avg_sd_s_upperic,
          NMB_avg_sd_upperic) %>%
  rename(
    "NMB_avg_sd_r" = "NMB_avg_sd_r_upperic",
    "NMB_avg_sd_s" = "NMB_avg_sd_s_upperic",
    "NMB_avg" = "NMB_avg_sd_upperic"
  )%>%
pivot_longer(
  cols = c(NMB_avg_sd_r, NMB_avg_sd_s, NMB_avg),
  names_to = "group",
  values_to = "upper_ic"
)

NMB_avg_data_long_ic = NMB_avg_data_long %>%
  left_join(NMB_avg_data_long_loweric, by = c("Threshold" = "Threshold", "WTP" = "WTP", "group" = "group")) %>%
  left_join(NMB_avg_data_long_upperic, by = c("Threshold" = "Threshold", "WTP" = "WTP", "group" = "group")) %>%
  mutate(new_wtp = case_when(
    WTP == 2857.215 ~ 0.5,
    WTP == 5714.430 ~ 1,
    WTP == 8571.645 ~ 1.5,
    WTP == 11428.860 ~ 2,
    WTP == 14286.075 ~ 2.5,
    WTP == 17143.290 ~ 3,
    TRUE ~ WTP  # Keep the original value if it doesn't match any condition
  )) %>%
  select(-WTP) %>%
  mutate(new_group = case_when(
    group == "NMB_avg_sd_r" ~ "Among patients with TB resistant \n to rifampicin and FLQ",
    group == "NMB_avg_sd_s" ~ "Among patients with TB resistant \n to rifampicin but susceptible to FLQ",
    group == "NMB_avg" ~ "Among all patients with TB \n resistant to rifampicin",
    TRUE ~ group  # Keep the original value if it doesn't match any condition
  )) %>%
  select(-group)

NMB_avg_data_long_ic$new_group = factor(NMB_avg_data_long_ic$new_group, levels = c("Among patients with TB resistant \n to rifampicin and FLQ", 
                                                    "Among patients with TB resistant \n to rifampicin but susceptible to FLQ",
                                                    "Among all patients with TB \n resistant to rifampicin"))


# Plot
plot_NMB_FLQres_sus_varyWTP = ggplot(NMB_avg_data_long_ic, aes(x = new_wtp, y = NMB, fill = new_group)) +
  geom_line() +
  geom_ribbon(aes(ymin = lower_ic, ymax = upper_ic), fill = "grey", alpha = 0.5) +  # Specify fill outside aes
  labs(x = "Willingness-to-pay value as portion of the Republic of Moldova’s gross domestic product per capita", y = "Gain in NMB") +
  theme(text = element_text(size = 18)) +
  ggtitle("Figure. Gain in net monetary benefit (NMB) from using the develop decision tool to inform treatment regimens compared \n to using the standardized regimen for all patients with RR-TB. The shaded regions show the 95% confidence intervals.\n") +
  facet_grid(. ~ new_group,
             scales = "free_y",
             labeller = labeller(new_group = function(labels) {
               paste0(LETTERS[seq_along(labels)], ". ", labels)
             })
             ) +  # Facetted plot with grid layout
  theme(legend.position = "none",
        strip.text = element_text(size = 22, face = "bold"),
        text = element_text(size = 22),
        plot.title=element_text(face="bold")) 

ggsave(
  filename = "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_sus_res_ci_varyWTP_withtitle.png",
  plot = plot_NMB_FLQres_sus_varyWTP,
  width = 22,
  height = 7
)
