#### HM model

#Model definition
formula = FLQ_R ~ Age + Family_size + Family_size18 + Sex_2 + Family_size +
  Occupation_2 + Occupation_3 + Occupation_4 + Occupation_5 +
  Education_2 + Education_3 + Education_4 + Education_5 + Education_missing +
  Living_condition_1 + Living_condition_missing + Outside_moldova_1 +
  Outside_moldova_missing + Urban_1 + Homeless_1 + Homeless_missing +
  Money_assistance_1 + Money_assistance_missing + Incarceration_1 +
  Incarceration_missing + TB_location_bin_Pulmonary + TB_type_2 +
  TB_type_3 + TB_type_4 + TB_type_6 + (1 | Residence)