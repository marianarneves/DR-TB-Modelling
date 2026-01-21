#### HM model

#Model definition
formula = FLQ_R ~ Age + Family_size + Sex_2 + Occupation_1 + Occupation_5 +
  Education_abovesecondary + Living_condition_1 + Outside_moldova_1 +  Urban_1 + Homeless_1 + 
  Incarceration_1 + TB_type_1 + Microscopy_1 + (1 | Residence)