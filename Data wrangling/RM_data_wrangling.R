#######################################
#
#       Edit TB data - Republic of Moldova


library(dplyr)
library(fastDummies)

setwd("/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/")

#Read dataset
tb_moldova <-
  read.csv(
    "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/journal.pdig.0000059.s002.csv"
  )


#
clean_data = tb_moldova %>%
  mutate_all(~ ifelse(. == "missing", NA, .)) %>%
  mutate(
    Age_Category = cut(
      Age,
      breaks = seq(0, max(Age, na.rm = TRUE) + 10, by = 10),
      labels = paste(seq(0, max(Age, na.rm = TRUE) , by = 10), seq(10, max(Age, na.rm = TRUE)  + 10, by = 10), sep = "-"),
      include.lowest = TRUE
    ),
    Age_Category = as.factor(Age_Category)
  ) %>%
  select(-Age)


#write.csv(
#  clean_data,
#  "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/moldova_dataset_genieversion.csv",
#  row.names = FALSE
#)


#Cleaning data for python

tb_moldova_DR = tb_moldova %>%
  mutate_at(
    vars(
      Microscopy,
      Xpert,
      Xpert_RIF,
      RIF_LJ,
      RIF_MGIT,
      OFX_LJ,
      OFX_MGIT,
      LFX_LJ,
      LFX_MGIT,
      MFX_LJ,
      MFX_MGIT
    ),
    ~ ifelse(. == 5, NA, .)
  ) %>%
  filter(
    !is.na(Xpert) & Xpert == 1 ,!is.na(Xpert_RIF) & Xpert_RIF == 1,!is.na(OFX_LJ) |
      !is.na(OFX_MGIT) |
      !is.na(LFX_LJ) |
      !is.na(LFX_MGIT) |
      !is.na(MFX_LJ) |
      !is.na(MFX_MGIT)
  ) %>%
  mutate(FLQ_R = case_when(
    OFX_LJ == 1 |
      OFX_MGIT == 1 |
      LFX_LJ == 1 |
      LFX_MGIT == 1 |
      MFX_LJ == 1 |
      MFX_MGIT == 1 ~ 1, 
    TRUE ~ 0)
  ) %>%
  select(-Xpert,
         -Xpert_RIF,
         -RIF_LJ,
         -RIF_MGIT,
         -OFX_LJ,
         -OFX_MGIT,
         -LFX_LJ,
         -LFX_MGIT,
         -MFX_LJ,
         -MFX_MGIT,
         -INH_LJ,
         -INH_MGIT,
         -E_LJ,
         -E_MGIT,
         -LZD_MGIT,
         -Z_MGIT) %>%
  mutate_at(vars(Family_size, Family_size18), ~ ifelse(. == "missing", NA, .)) %>% 
  mutate_at(vars(Family_size, Family_size18), ~ ifelse(is.na(.), round(mean(as.numeric(.), na.rm = TRUE)), .))%>%
  mutate(Family_size = ifelse(as.numeric(Family_size) >= 11, 11,as.numeric(Family_size))) %>%
  mutate(Family_size18 = ifelse(as.numeric(Family_size18) >= 8, 8,as.numeric(Family_size18)))
  
  
#Prevalence of FLQ resistance by residence 
FLQ_R_residence_p = tb_moldova_DR %>%
  group_by(Residence) %>%
  summarise(prevalencep = case_when(
    n() >= 5 ~ mean(FLQ_R),
    TRUE ~ NA
  ))

#Prevalence of FLQ resistance by residence 
FLQ_R_residence = tb_moldova_DR %>%
  group_by(Residence) %>%
  summarise(prevalence = case_when(
    mean(FLQ_R) <= 0.1 & n() >= 5 ~ "0",
    mean(FLQ_R) > 0.1 & mean(FLQ_R) <= 0.2 & n() >= 5 ~ "1",
    mean(FLQ_R) > 0.2 & n() >= 5 ~ "2",
    TRUE ~ "NA"
  ), n = n())


tb_moldova_FLQ_R_NN = tb_moldova_DR %>%
  left_join(., FLQ_R_residence_p, by = "Residence") %>%
  dummy_cols(
    select_columns = c(
      "Sex",
      "Occupation",
      "Education",
      "Living_condition",
      "Outside_moldova",
      "Urban",
      "Homeless",
      "Money_assistance",
      "Incarceration",
      "TB_main_location",
      "TB_type",
      "Microscopy"),
    #remove_first_dummy = TRUE,
    remove_selected_columns = TRUE
  ) %>%
  select(-Residence)%>%
  filter(complete.cases(.))

write.csv(tb_moldova_FLQ_R_NN, "DATA_tb_moldova_NN.csv", row.names = FALSE)


# Hierarchical model R

tb_moldova_FLQ_R_HM = tb_moldova_DR %>%
  mutate(TB_location_bin = case_when(
    TB_main_location == 1 ~ "Pulmonary",
    TB_main_location != 1 & !is.na(TB_main_location) ~ "Extrapulmonary",
    TRUE ~ "missing"
  )) %>%
  select(-TB_main_location) %>%
  dummy_cols(
    select_columns = c(
      "Sex",
      "Occupation",
      "Education",
      "Living_condition",
      "Outside_moldova",
      "Urban",
      "Homeless",
      "Money_assistance",
      "Incarceration",
      "TB_type",
      "TB_location_bin",
      "Microscopy",
      "prevalence"),
    remove_first_dummy = TRUE,
    remove_selected_columns = TRUE
  )

write.csv(tb_moldova_FLQ_R_HM, "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_HM.csv", row.names = FALSE)

# Hierarchical model R - Simplified

tb_moldova_FLQ_R_HM_simpler = tb_moldova_DR %>%
  mutate(TB_location_bin = case_when(
    TB_main_location == 1 ~ "Pulmonary",
    TB_main_location != 1 & !is.na(TB_main_location) ~ "Extrapulmonary",
    TRUE ~ "missing"
  ),
  Education_abovesecondary = ifelse(Education == 2|
                                    Education == 3|
                                    Education == 4, 1, 0)) %>%
  select(-TB_main_location) %>%
  dummy_cols(
    select_columns = c(
      "Sex",
      "Occupation",
      "Living_condition",
      "Outside_moldova",
      "Urban",
      "Homeless",
      "Money_assistance",
      "Incarceration",
      "TB_type",
      "TB_location_bin",
      "Microscopy",
      "prevalence"),
    remove_first_dummy = FALSE,
    remove_selected_columns = TRUE
  ) %>%
  select('FLQ_R',
         'Residence',
         'Age',
         'Sex_2',
         'Family_size',
         'Occupation_1',
         'Occupation_5',
         'Education_abovesecondary',
         'Living_condition_1',
         'Outside_moldova_1',
         'Urban_1',
         'Homeless_1',
         'Incarceration_1',
         'TB_type_1', 
         'Microscopy_1'
         )

write.csv(tb_moldova_FLQ_R_HM_simpler, "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_HM_simpler.csv", row.names = FALSE)

# Logistic Regression model R - Augmented

tb_moldova_FLQ_R_LR_augmented = tb_moldova_FLQ_R_HM %>%
  left_join(., FLQ_R_residence, by = "Residence") %>%
  dummy_cols(
    select_columns = 'prevalence',
    remove_first_dummy = TRUE,
    remove_selected_columns = TRUE
  )
write.csv(tb_moldova_FLQ_R_LR_augmented, "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_LR_Augumented.csv", row.names = FALSE)



#Bayesian Networks


tb_moldova_FLQ_R_BN = tb_moldova_DR %>%
  left_join(., FLQ_R_residence, by = "Residence") %>%
  mutate(
    Age_Category = cut(
      Age,
      breaks = seq(0, max(Age, na.rm = TRUE) + 10, by = 10),
      labels = paste(seq(0, max(Age, na.rm = TRUE) , by = 10), seq(10, max(Age, na.rm = TRUE)  + 10, by = 10), sep = "-"),
      include.lowest = TRUE
    ),
    Age_Category = as.factor(Age_Category)
  ) %>%
  select(-Age, -Residence, -Family_size, -Family_size18) %>%
  mutate_if(is.character, ~na_if(., "missing"))%>%
  mutate_all(as.factor)

write.csv(tb_moldova_FLQ_R_BN, "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_BN.csv", row.names = FALSE)



#Prevalence only

tb_moldova_FLQ_R_p = tb_moldova_DR %>%
  left_join(., FLQ_R_residence_p, by = "Residence") %>%
  select(prevalencep, FLQ_R)

write.csv(tb_moldova_FLQ_R_p, "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_FLQ_R_p.csv", row.names = FALSE)

