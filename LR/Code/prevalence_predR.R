library(glmnet)
library(dplyr)
library(pROC)
library(ROCR)
library(brms)

set.seed(3)

# Load the new dataset

#Read dataset
tb_moldova <-
  read.csv(
    "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_HM.csv"
  )

# data with prevalence
data_path <- "/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_FLQ_R_p.csv"
moldova_data_prev <- read.csv(data_path)

#complete cases
moldova_data_c = moldova_data_prev[complete.cases(moldova_data_prev),]

#### Complete data ####
# This calculates the prevalence using everyone in the distric and uses as a prediction

threshold = seq(0, 1, by = 0.01)
cm = matrix(nrow = dim(moldova_data_c)[1], ncol= length(threshold))

for(i in 1: length(threshold)){
 cm[,i] = ifelse(moldova_data_c$prevalencep >threshold[i], 1, 0)
    
}

TR = cbind(moldova_data_c$FLQ_R, cm)
CM_TPFN = matrix(nrow = 2, ncol = dim(TR)[2]-1)

for(i in 2:dim(TR)[2]) {
  
  CM_TPFN[1,i-1] = sum(TR[,i] == 1 & TR[,1] == 1)/sum(TR[,1] == 1)
  CM_TPFN[2,i-1] = sum(TR[,i] == 0 & TR[,1] == 0)/sum(TR[,1] == 0)
}

plot(1-CM_TPFN[2,],CM_TPFN[1,])
roc(moldova_data_c$FLQ_R, moldova_data_c$prevalencep)


#### District size and prevalence ####
#This calculates the prevalence using 2/3 of the data in the district 
#and uses as a prediction for the last 1/3

#Prevalence of FLQ resistance by residence 
FLQ_R_residence_p = tb_moldova %>%
  group_by(Residence) %>%
  summarise(n = n()) %>%
  filter(n>10)

predic_district <- data.frame(Residence = numeric(), FLQ_R = numeric(), pred = numeric())

for (i in 1:18){
  temp = tb_moldova%>%
    filter(Residence == FLQ_R_residence_p$Residence[i])
  
  random = sample(1:nrow(temp), round(nrow(temp)*2/3), replace = FALSE)
  
  prev = temp %>%
    slice(random) %>%
    group_by(Residence) %>%
    summarise(prevalencen = mean(FLQ_R))
  
  predic_district_temp = temp %>%
    slice(-random) %>%
    select(Residence, FLQ_R) %>%
    mutate(pred = prev$prevalencen)
  
  predic_district = rbind(predic_district, predic_district_temp)
}
roc(predic_district$FLQ_R, predic_district$pred )


