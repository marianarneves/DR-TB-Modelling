library(readxl)
library(dplyr)
library(ggplot2)
library(magrittr)
library(tidyr)
library(ggplot2)
library(gridExtra)

setwd("/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Analysis/")
source("DR_TB_PMDT_Analysis_Functions.R")

#### Read Output - DR-TB ####

# Output location
output_loc = "/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/"

# Number of varying WTP
n_wtp = 5

#### PM + DT ####

# NMB_DALY_Cost_PMDT_eachpt - NMB, DALYs and Costs for each patient
NMB_DALY_Cost_PMDT_eachpt = read_output_tolist_varyingwtp(output_loc, "NMB_DALY_Cost_PMDT_eachpt", n_wtp)

# NMB_DALY_Cost_FLQ_DLM_class_PMDT_avg - NMB, DALYs and Costs of FLQ and DLM depending on the prediction model classification
NMB_DALY_Cost_FLQ_DLM_class_PMDT_avg = read_output_tolist_varyingwtp(output_loc, "NMB_DALY_Cost_FLQ_DLM_class_PMDT_avg", n_wtp)

# NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg - NMB, DALYs and Costs depending on FLQ susceptibility
NMB_DALY_Cost_FLQ_Res_Sus_PM_avg = read_output_tolist_varyingwtp(output_loc, "NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg", n_wtp)


#### PM only ####

# NMB_DALY_Cost_PM_eachpt - NMB, DALYs and Costs for each patient
NMB_DALY_Cost_PM_eachpt = read_output_tolist_varyingwtp(output_loc, "NMB_DALY_Cost_PM_eachpt", n_wtp)

# NMB_DALY_Cost_FLQ_Res_Sus_PM_avg - NMB, DALYs and Costs depending on FLQ susceptibility
NMB_DALY_Cost_FLQ_Res_Sus_PM_avg = read_output_tolist_varyingwtp(output_loc, "NMB_DALY_Cost_FLQ_Res_Sus_PM_avg", n_wtp)


#### DT only ####

# NMB_DALY_Cost_DT_eachpt - NMB, DALYs and Costs for each patient
NMB_DALY_Cost_DT_eachpt = read_output_tolist_varyingwtp(output_loc, "NMB_DALY_Cost_DT_eachpt", n_wtp)

# NMB_DALY_Cost_FLQ_Res_Sus_DT_avg - NMB, DALYs and Costs depending on FLQ susceptibility
NMB_DALY_Cost_FLQ_Res_Sus_DT_avg = read_output_tolist_varyingwtp(output_loc, "NMB_DALY_Cost_FLQ_Res_Sus_DT_avg", n_wtp)


#### DR-TB: PMDT ####

#### DALYs, Costs and NMB depending on PM classification
a= unlist(NMB_DALY_Cost_PMDT_eachpt)

