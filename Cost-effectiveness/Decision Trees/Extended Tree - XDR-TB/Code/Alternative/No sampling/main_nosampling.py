from DR_TB_XTree_fun_nosampling import *
import numpy as np

# Assuming dr_tb_tree is a predefined function and the other variables are already defined
wtp_mult = np.arange(0.5, 3, 0.5)

value = GDP_moldova
# Iterate through each value in wtp
# for value, i in zip(wtp_mult*GDP_moldova, np.arange(1,len(wtp_mult)+1)):

############ Preliminary Costs and DALY Calculation ############
# Calculated expected costs and DALYs for ach treatment depending on FLQ susceptibility
preliminary_daly_costs = calculate_pre_daly_cost(pred_data, DALY_individual_Moldova, prob_data, cost_data_prior, daly_data_prior, value)
############ End Preliminary Costs and ############

### Apply the function dr_tb_pm_dt to the current value of wtp ###
output_PMDT = dr_tb_pm_dt(preliminary_daly_costs, sens_spec_PM, pred_data, DALY_individual_Moldova, prob_data, cost_data_prior, daly_data_prior, value)

# NMB, DALYs and Costs for each patient
# Create a dynamic file path
file_path_NMB_DALY_Cost_SdTreat_PMDT_eachpt = f"/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Alternative/NMB_DALY_Cost_PMDT_eachpt.xlsx"
# Convert the dictionary to a pandas DataFrame
df_DT_NMB_DALY_Cost_SdTreat_PMDT_eachpt = pd.DataFrame(output_PMDT.NMB_DALY_Cost_SdTreat_PMDT_eachpt)
# Save the DataFrame to an Excel file
df_DT_NMB_DALY_Cost_SdTreat_PMDT_eachpt.to_excel(file_path_NMB_DALY_Cost_SdTreat_PMDT_eachpt, index=False)

#     # NMB, Cost and DALYS for DLM And FLQ depending on classification
#     # Create a dynamic file path
#     file_path_NMB_DALY_Cost_FLQ_DLM_class_PMDT = f"/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_DALY_Cost_FLQ_DLM_class_PMDT_avg_wtp{i}.xlsx"
#     # Convert the dictionary to a pandas DataFrame
#     NMB_DALY_Cost_FLQ_DLM_class_PMDT_avg = pd.DataFrame(output_PMDT.NMB_DALY_Cost_FLQ_DLM_class_avg)
#     # Save the DataFrame to an Excel file
#     NMB_DALY_Cost_FLQ_DLM_class_PMDT_avg.to_excel(file_path_NMB_DALY_Cost_FLQ_DLM_class_PMDT, index=False)
#
#     # NMB, Cost and DALYs by FLQ susceptibility
#     # Create a dynamic file path
#     file_path_df_NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg = f"/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg_wtp{i}.xlsx"
#     # Convert the dictionary to a pandas DataFrame
#     df_NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg = pd.DataFrame(output_PMDT.NMB_DALY_Cost_FLQ_Res_Sus_avg)
#     # Save the DataFrame to an Excel file
#     df_NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg.to_excel(file_path_df_NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg, index=False)
#
#
#     ### Apply the function dr_tb_pm_dt to the current value of wtp ###
#     output_PM = dr_tb_pm(preliminary_daly_costs, sens_spec_PM, pred_data)
#
#     # NMB, DALYs and Costs for each patient
#     # Create a dynamic file path
#     file_path_NMB_DALY_Cost_SdTreat_PM_eachpt = f"/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_DALY_Cost_PM_eachpt_wtp{i}.xlsx"
#     # Convert the dictionary to a pandas DataFrame
#     df_DT_NMB_DALY_Cost_SdTreat_PM_eachpt = pd.DataFrame(output_PM.NMB_DALY_Cost_SdTreat_PM_eachpt)
#     # Save the DataFrame to an Excel file
#     df_DT_NMB_DALY_Cost_SdTreat_PM_eachpt.to_excel(file_path_NMB_DALY_Cost_SdTreat_PM_eachpt, index=False)
#
#     # NMB, Cost and DALYs by FLQ susceptibility
#     # Create a dynamic file path
#     file_path_df_NMB_DALY_Cost_FLQ_Res_Sus_PM_avg = f"/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_DALY_Cost_FLQ_Res_Sus_PM_avg_wtp{i}.xlsx"
#     # Convert the dictionary to a pandas DataFrame
#     df_NMB_DALY_Cost_FLQ_Res_Sus_PM_avg = pd.DataFrame(output_PM.NMB_DALY_Cost_FLQ_Res_Sus_PM_avg)
#     # Save the DataFrame to an Excel file
#     df_NMB_DALY_Cost_FLQ_Res_Sus_PM_avg.to_excel(file_path_df_NMB_DALY_Cost_FLQ_Res_Sus_PM_avg, index=False)
#
#     ### Apply the function dr_tb_dt to the current value of wtp ###
#     output_DT = dr_tb_dt(preliminary_daly_costs, pred_data, DALY_individual_Moldova, prob_data, cost_data_prior, daly_data_prior, wtp)
#
#     # NMB, DALYs and Costs for each patient
#     # Create a dynamic file path
#     file_path_NMB_DALY_Cost_SdTreat_DT_eachpt = f"/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_DALY_Cost_DT_eachpt_wtp{i}.xlsx"
#     # Convert the dictionary to a pandas DataFrame
#     df_DT_NMB_DALY_Cost_SdTreat_DT_eachpt = pd.DataFrame(output_DT.NMB_DALY_Cost_SdTreat_DT_eachpt)
#     # Save the DataFrame to an Excel file
#     df_DT_NMB_DALY_Cost_SdTreat_DT_eachpt.to_excel(file_path_NMB_DALY_Cost_SdTreat_DT_eachpt, index=False)
#
#     # NMB, Cost and DALYs by FLQ susceptibility
#     # Create a dynamic file path
#     file_path_df_NMB_DALY_Cost_FLQ_Res_Sus_DT_avg = f"/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/NMB_DALY_Cost_FLQ_Res_Sus_DT_avg_wtp{i}.xlsx"
#     # Convert the dictionary to a pandas DataFrame
#     df_NMB_DALY_Cost_FLQ_Res_Sus_DT_avg = pd.DataFrame(output_DT.NMB_DALY_Cost_FLQ_Res_Sus_DT_avg)
#     # Save the DataFrame to an Excel file
#     df_NMB_DALY_Cost_FLQ_Res_Sus_DT_avg.to_excel(file_path_df_NMB_DALY_Cost_FLQ_Res_Sus_DT_avg, index=False)
#
# # The results dictionary now contains the output of dr_tb_tree for each value of wtp
# # print(results['test_1'].NMB_DALY_Cost_FLQ_Res_Sus_avg['NMB_SdTreat_PMDT_FLQ_Res'])
