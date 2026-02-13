import numpy as np
from DR_TB_XTree_fun import *
from SampleParameters import *

def cost_daly_input_table(cost_sampled_par, dalyweight_sampled_par, dalylength_sampled_par, j):
    """ Processes sampled cost and DALY data to create structured outputs in the form of named tuples.

    :param cost_sampled_par: DataFrame containing sampled cost parameters.
                             'Cost Variable' contains the names/types of cost variables.
                             'Sample_{j}' contains the sampled values for these cost variables in the j-th sample.
    :param dalyweight_sampled_par: DataFrame containing sampled DALY weight parameters.
                                   'DALY Weight Variable' contains the names/types of DALY weight variables.
                                   'Sample_{j}' contains the sampled values for these DALY weights in the j-th sample.
    :param dalylength_sampled_par: DataFrame containing sampled DALY length parameters.
                                   'Sample_{j}' contains the sampled values for DALY lengths in the j-th sample.
    :param j: Integer representing the index of the sample to be processed. This index is used to select the appropriate sampled data from the input DataFrames.
    :return: A named tuple containing:
             - cost_data_sampled: DataFrame with 'Cost Variable' and 'Cost Value' columns for the j-th sample.
             - daly_data_sampled: DataFrame with 'DALY Variable' and 'DALY Value' columns, where 'DALY Value' is the product of sampled DALY weights and lengths for the j-th sample.
    """

    # Create the sampled Cost data
    cost_data_sampled = pd.DataFrame({
        'Cost Variable': cost_sampled_par['Cost Variable'],
        'Cost Value': cost_sampled_par[f'Sample_{j}']
    })

    # Create the sampled DALY data
    # Extract the necessary columns
    sample_j_dalyweight = dalyweight_sampled_par[f'Sample_{j}']
    sample_j_dalylength = dalylength_sampled_par[f'Sample_{j}']
    # Perform the calculation
    daly_data_sampled = pd.DataFrame({
        'DALY Variable': dalyweight_sampled_par['DALY Weight Variable'],
        'DALY Value': sample_j_dalyweight * sample_j_dalylength
    })

    # Define the named tuple with fields that will hold dictionaries
    cost_daly_input_table_t = namedtuple('cost_daly_input_table',
                                     ['cost_data_sampled', 'daly_data_sampled'])

    # Create an instance of the named tuple
    cost_daly_input_table = cost_daly_input_table_t(cost_data_sampled=cost_data_sampled,
                                            daly_data_sampled=daly_data_sampled)

    return cost_daly_input_table

def calculate_sample_averages(dataframe, excluded_cols, index_cols):
    # Specify the columns to exclude from the mean calculation
    exclude_columns = excluded_cols

    # Columns to include in the mean calculation
    include_columns = [col for col in dataframe.columns if
                       col not in exclude_columns and col not in index_cols]

    # Group by 'Person' and 'threshold' and calculate the mean for the included columns
    sample_avg = dataframe.groupby(index_cols)[include_columns].mean().reset_index()

    # Extract the first occurrence of the excluded columns for each group
    FLQstatus_Class = dataframe.groupby(index_cols)[exclude_columns].first().reset_index()

    # Merge the averaged data with the first occurrence data
    final_sample_avg = pd.merge(sample_avg, FLQstatus_Class, on=index_cols)

    return final_sample_avg


def output_gen(sens_spec_PM, pred_data, DALY_individual_Moldova, prob_data, cost_data_prior,
               dalyweigth_data, dalylength_data, wtp, par_samplesize=2):
    if par_samplesize > 0:

        # Sampling from the prior costs
        cost_sampled_par = cost_parameter_sampler(cost_data_prior, par_samplesize)
        # Sampling from the prior daly weights
        dalyweight_sampled_par = dalyweight_parameter_sampler(dalyweigth_data, par_samplesize)
        # Sampling from the prior daly length
        dalylength_sampled_par = dalylength_parameter_sampler(dalylength_data, par_samplesize)

        if len(wtp) > 1:
            for value, i in zip(wtp, np.arange(1, len(wtp) + 1)):

                NMB_DALY_Cost_SdTreat_PMDT_eachpt = pd.DataFrame()
                NMB_DALY_Cost_FLQ_DLM_class_PMDT_avg = pd.DataFrame()
                NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg = pd.DataFrame()
                NMB_DALY_Cost_SdTreat_PM_eachpt = pd.DataFrame()
                NMB_DALY_Cost_FLQ_Res_Sus_PM_avg = pd.DataFrame()

                for j in range(1, par_samplesize + 1):

                    # Generate the sampled tables for cost and daly in the appropriate format (2 columns)
                    cost_daly_sampled = cost_daly_input_table(cost_sampled_par, dalyweight_sampled_par, dalylength_sampled_par, j)
                    cost_data_sampled = pd.DataFrame(cost_daly_sampled.cost_data_sampled)
                    daly_data_sampled = pd.DataFrame(cost_daly_sampled.daly_data_sampled)

                    ############ Preliminary Costs and DALY Calculation ############
                    # Calculated expected costs and DALYs for ach treatment depending on FLQ susceptibility
                    preliminary_daly_costs = calculate_pre_daly_cost(pred_data, DALY_individual_Moldova, prob_data,
                                                                     cost_data_sampled,
                                                                     daly_data_sampled, value)
                    ############ End Preliminary Costs and ############

                    # PM + DT
                    ### Apply the function dr_tb_pm_dt to the current value of wtp ###
                    output_PMDT = dr_tb_pm_dt(preliminary_daly_costs, sens_spec_PM, pred_data, DALY_individual_Moldova,
                                              prob_data,
                                              cost_data_sampled, daly_data_sampled, value)

                    # # NMB, DALYs and Costs for each patient
                    # Joining the output (converted to a dataframe) with the results from the previous samples
                    NMB_DALY_Cost_SdTreat_PMDT_eachpt = pd.concat(
                        [NMB_DALY_Cost_SdTreat_PMDT_eachpt,  pd.DataFrame(output_PMDT.NMB_DALY_Cost_SdTreat_PMDT_eachpt)],
                        ignore_index=True)
                    # NMB, Cost and DALYS for DLM And FLQ depending on classification
                    # Joining the output (converted to a dataframe) with the results from the previous samples
                    NMB_DALY_Cost_FLQ_DLM_class_PMDT_avg = pd.concat(
                        [NMB_DALY_Cost_FLQ_DLM_class_PMDT_avg, pd.DataFrame(output_PMDT.NMB_DALY_Cost_FLQ_DLM_class_avg)],
                        ignore_index=True)
                    # NMB, Cost and DALYs by FLQ susceptibility
                    # Joining the output (converted to a dataframe) with the results from the previous samples
                    NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg = pd.concat(
                        [NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg, pd.DataFrame(output_PMDT.NMB_DALY_Cost_FLQ_Res_Sus_avg)],
                        ignore_index=True)
                    # End PM + DT


                    # PM 
                    ### Apply the function dr_tb_pm to the current value of wtp ###
                    output_PM = dr_tb_pm(preliminary_daly_costs, sens_spec_PM, pred_data)
                    # NMB, DALYs and Costs for each patient
                    # Joining the output (converted to a dataframe) with the results from the previous samples
                    NMB_DALY_Cost_SdTreat_PM_eachpt = pd.concat(
                        [NMB_DALY_Cost_SdTreat_PM_eachpt,  pd.DataFrame(output_PM.NMB_DALY_Cost_SdTreat_PM_eachpt)],
                        ignore_index=True)
                    # NMB, Cost and DALYs by FLQ susceptibility
                    # Joining the output (converted to a dataframe) with the results from the previous samples
                    NMB_DALY_Cost_FLQ_Res_Sus_PM_avg = pd.concat(
                        [NMB_DALY_Cost_FLQ_Res_Sus_PM_avg,  pd.DataFrame(output_PM.NMB_DALY_Cost_FLQ_Res_Sus_PM_avg)],
                        ignore_index=True)
                    # End PM

                # PM + DT
                # NMB, DALYs and Costs for each patient
                final_sampleavg_NMB_DALY_Cost_SdTreat_PMDT_eachpt = calculate_sample_averages(NMB_DALY_Cost_SdTreat_PMDT_eachpt, ['FLQ_Status', 'Class'], ['Person', 'threshold'])
                # Create a dynamic file path
                file_path_NMB_DALY_Cost_SdTreat_PMDT_eachpt = f"/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/test/sampleavg_NMB_DALY_Cost_PMDT_eachpt_wtp{i}.xlsx"
                # Save the DataFrame to an Excel file
                final_sampleavg_NMB_DALY_Cost_SdTreat_PMDT_eachpt.to_excel(
                    file_path_NMB_DALY_Cost_SdTreat_PMDT_eachpt,
                    index=False)

                # NMB, Cost and DALYS for DLM And FLQ depending on classification
                sampleavg_NMB_DALY_Cost_FLQ_DLM_class_PMDT_avg = \
                NMB_DALY_Cost_FLQ_DLM_class_PMDT_avg.groupby('threshold').mean().reset_index()
                # Create a dynamic file path
                file_path_NMB_DALY_Cost_FLQ_DLM_class_PMDT = f"/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/test/sampleavg_NMB_DALY_Cost_FLQ_DLM_class_PMDT_avg_wtp{i}.xlsx"
                # Save the DataFrame to an Excel file
                sampleavg_NMB_DALY_Cost_FLQ_DLM_class_PMDT_avg.to_excel(file_path_NMB_DALY_Cost_FLQ_DLM_class_PMDT, index=False)

                # NMB, Cost and DALYs by FLQ susceptibility
                sampleavg_NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg = \
                    NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg.groupby('threshold').mean().reset_index()
                # Create a dynamic file path
                file_path_df_NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg = f"/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/test/sampleavg_NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg_wtp{i}.xlsx"
                # Save the DataFrame to an Excel file
                sampleavg_NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg.to_excel(file_path_df_NMB_DALY_Cost_FLQ_Res_Sus_PMDT_avg,
                                                                        index=False)
                # End PM + DT

if __name__ == '__main__':
    # Common directory paths
    base_path = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/'
    cost_effectiveness_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'

    # Read data
    cost_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'Costs')
    dalyweigth_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'DALY Weight')
    dalylength_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'DALY Lenght')

    # Assuming dr_tb_tree is a predefined function and the other variables are already defined
    wtp = [1, 2]

    output_gen(sens_spec_PM, pred_data, DALY_individual_Moldova, prob_data, cost_data_prior,
               dalyweigth_data, dalylength_data, wtp, par_samplesize=2)
