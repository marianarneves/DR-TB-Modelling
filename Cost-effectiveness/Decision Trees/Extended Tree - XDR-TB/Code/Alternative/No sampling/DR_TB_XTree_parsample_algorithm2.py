import pandas as pd

from SampleParameters import *
import time
import csv
from collections import namedtuple
from PreliminaryDALYs import *

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


def dr_tb_pm_dt_s(sens_spec_PM, pred_data, DALY_individual_Moldova, prob_data, cost_data_prior,
               dalyweigth_data, dalylength_data, wtp, par_samplesize=2):

    for index, row in prob_data.iterrows():
        globals()[row['Probability Variable']] = row['Probability Value']

    # Sampling from the prior costs
    cost_sampled_par = cost_parameter_sampler(cost_data_prior, par_samplesize)

    # Sampling from the prior daly weights
    dalyweight_sampled_par = dalyweight_parameter_sampler(dalyweigth_data, par_samplesize)
    # Sampling from the prior daly length
    dalylength_sampled_par = dalylength_parameter_sampler(dalylength_data, par_samplesize)

    # Initiating the vectors that store output
    NMB_DALY_Cost_SdTreat_PMDT_sampleavg = pd.DataFrame()  # Change in NMB, DALYs and Cost when the optimal treatment (PM + DT) is used in comparison to the standard treatment and separately

    for j in range(1, par_samplesize + 1):

        start_time = time.time()

        # Generate the sampled tables for cost and daly in the appropriate format (2 columns)
        cost_daly_sampled = cost_daly_input_table(cost_sampled_par, dalyweight_sampled_par,
                                                  dalylength_sampled_par, j)
        cost_data_sampled = pd.DataFrame(cost_daly_sampled.cost_data_sampled)
        daly_data_sampled = pd.DataFrame(cost_daly_sampled.daly_data_sampled)

        # Make the table variables to be used - Costs in the tree
        for index, row in cost_data_sampled.iterrows():
            globals()[row['Cost Variable']] = row['Cost Value']

        # Make the table variables to be used - DALYs in the tree
        for index, row in daly_data_sampled.iterrows():
            globals()[row['DALY Variable']] = row['DALY Value']

        ############ Preliminary Costs and DALY Calculation ############
        # Calculated expected costs and DALYs for ach treatment depending on FLQ susceptibility
        preliminary_daly_costs = calculate_pre_daly_cost(pred_data, DALY_individual_Moldova, prob_data,
                                                         cost_data_sampled,
                                                         daly_data_sampled, wtp)
        ############ End Preliminary Costs and ############

        # Terminal nodes
        CC_FLQsus = TerminalNode(name='CC_FLQsus', cost=Cost_CC_FLQsus, daly=DALY_CC_FLQsus)
        TF_FLQsus = TerminalNode(name='TF_FLQsus', cost=Cost_TF_FLQsus, daly=DALY_TF_FLQsus)
        CC_FLQres = TerminalNode(name='CC_FLQres', cost=Cost_CC_FLQres, daly=DALY_CC_FLQres)
        TF_FLQres = TerminalNode(name='TF_FLQres', cost=Cost_TF_FLQres, daly=DALY_TF_FLQres)
        CC_DLM = TerminalNode(name='CC_DLM', cost=Cost_CC_DLM, daly=DALY_CC_DLM)
        TF_DLM = TerminalNode(name='TF_DLM', cost=Cost_TF_DLM, daly=DALY_TF_DLM)

        # Initiating the vectors that store output
        NMB_DALY_Cost_SdTreat_PMDT_eachpt = [] # Change in NMB, DALYs and Cost when the optimal treatment (PM + DT) is used in comparison to the standard treatment and separatel

        with open(sens_spec_PM, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                P_S_R = float(row['P_S_R'])
                P_R_R = float(row['P_R_R'])
                P_S_S = float(row['P_S_S'])
                P_R_S = float(row['P_R_S'])
                t = float(row['threshold'])

                for i, (DALY_Death, pred, obs) in enumerate(
                        zip(DALY_individual_Moldova, pred_data['pred'], pred_data['obs'])):
                    ############ DALY ############

                    DEATH_FLQsus = TerminalNode(name='D_FLQsus', cost=Cost_D_FLQsus, daly=DALY_Death)
                    DEATH_FLQres = TerminalNode(name='D_FLQres', cost=Cost_D_FLQres, daly=DALY_Death)
                    DEATH_DLM = TerminalNode(name='D_DLM', cost=Cost_D_DLM, daly=DALY_Death)

                    # Chance nodes
                    C_FLQsus = ChanceNode(name='C_FLQsus', cost=0,
                                          future_nodes=[CC_FLQsus, TF_FLQsus, DEATH_FLQsus],
                                          probs=[Prob_CC_FLQsus, Prob_TF_FLQsus, Prob_D_FLQsus], daly=0)
                    C_FLQres = ChanceNode(name='C_FLQres', cost=0,
                                          future_nodes=[CC_FLQres, TF_FLQres, DEATH_FLQres],
                                          probs=[Prob_CC_FLQres, Prob_TF_FLQres, Prob_D_FLQres], daly=0)
                    C_DLM = ChanceNode(name='C_DLM', cost=Cost_DLM,
                                       future_nodes=[CC_DLM, TF_DLM, DEATH_DLM],
                                       probs=[Prob_CC_DLM, Prob_TF_DLM, Prob_D_DLM], daly=DALY_DLM)

                    # NMB, Cost and DALYs by FLQ susceptibility
                    if obs == 1:
                        FLQ_status = 'FLQ Resistant'
                    else:
                        FLQ_status = 'FLQ Susceptible'

                    if pred > t:
                        ### Positive DT ###
                        # Chance Node
                        C_FLQ_p = ChanceNode(name='C_FLQ_p', cost=Cost_FLQ, daly=DALY_FLQ,
                                             future_nodes=[C_FLQsus, C_FLQres], probs=[P_S_R, P_R_R])
                        # Decision Node
                        D_p = DecisionNode(name='D_p', cost=0, daly=0, future_nodes=[C_FLQ_p, C_DLM])

                        # Decision Tree
                        DT_p = DecisionTree(name='DT_p', decision_nodes=D_p, willingness_to_pay=wtp)

                        # Optimal Treatment
                        Opt_Treat_p = DT_p.get_optimal_decision()[0]

                        # Select Optimal Treatment
                        if Opt_Treat_p == 'C_DLM':

                            # NMB, DALYs and Costs for each patient
                            NMB_DALY_Cost_SdTreat_PMDT_eachpt.append(
                                {'threshold': t,
                                 'Sample': j,
                                 'Person': i,
                                 'FLQ_Status': FLQ_status,
                                 'Prediction_Model_Classification': 'FLQ Resistant',
                                 'DALY_DLM': D_p.get_expected_daly()['C_DLM'],
                                 'Cost_DLM': D_p.get_expected_cost()['C_DLM'],
                                 'DALY_FLQ': D_p.get_expected_daly()['C_FLQ_p'],
                                 'Cost_FLQ': D_p.get_expected_cost()['C_FLQ_p'],
                                 'NMB_SdTreat_PMDT': preliminary_daly_costs.SdTreat_NMB[i] -
                                                     preliminary_daly_costs.DLM_NMB[
                                                         i],
                                 'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[i],
                                 'NMB_SdTreat_FLQ': wtp * preliminary_daly_costs.Exp_FLQ_SdTreat_DALY[i] +
                                                    preliminary_daly_costs.Exp_FLQ_SdTreat_cost[i],
                                 'NMB_DLM': wtp * D_p.get_expected_daly()['C_DLM'] + D_p.get_expected_cost()['C_DLM'],
                                 'NMB_PMDT': preliminary_daly_costs.DLM_NMB[i],
                                 'DALY_SdTreat_PMDT': preliminary_daly_costs.SdTreat_DALY[i] -
                                                      preliminary_daly_costs.Exp_DLM_DALY[i],
                                 'DALY_SdTreat': preliminary_daly_costs.SdTreat_DALY[i],
                                 'DALY_PMDT': preliminary_daly_costs.Exp_DLM_DALY[i],
                                 'Cost_SdTreat_PMDT': preliminary_daly_costs.SdTreat_cost[i] -
                                                      preliminary_daly_costs.Exp_DLM_cost[i],
                                 'Cost_SdTreat': preliminary_daly_costs.SdTreat_cost[i],
                                 'Cost_PMDT': preliminary_daly_costs.Exp_DLM_cost[i]
                                 }
                            )

                        else:

                            # NMB, DALYs and Costs for each patient
                            NMB_DALY_Cost_SdTreat_PMDT_eachpt.append(
                                {'threshold': t,
                                 'Sample': j,
                                 'Person': i,
                                 'FLQ_Status': FLQ_status,
                                 'Prediction_Model_Classification': 'FLQ Resistant',
                                 'DALY_DLM': D_p.get_expected_daly()['C_DLM'],
                                 'Cost_DLM': D_p.get_expected_cost()['C_DLM'],
                                 'DALY_FLQ': D_p.get_expected_daly()['C_FLQ_p'],
                                 'Cost_FLQ': D_p.get_expected_cost()['C_FLQ_p'],
                                 'NMB_SdTreat_PMDT': preliminary_daly_costs.SdTreat_NMB[i] -
                                                     preliminary_daly_costs.FLQ_NMB[
                                                         i],
                                 'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[i],
                                 'NMB_SdTreat_FLQ': wtp * preliminary_daly_costs.Exp_FLQ_SdTreat_DALY[i] +
                                                    preliminary_daly_costs.Exp_FLQ_SdTreat_cost[i],
                                 'NMB_DLM': wtp * D_p.get_expected_daly()['C_DLM'] + D_p.get_expected_cost()['C_DLM'],
                                 'NMB_PMDT': preliminary_daly_costs.FLQ_NMB[i],
                                 'DALY_SdTreat_PMDT': preliminary_daly_costs.SdTreat_DALY[i] -
                                                      preliminary_daly_costs.Exp_FLQ_DALY[i],
                                 'DALY_SdTreat': preliminary_daly_costs.SdTreat_DALY[i],
                                 'DALY_PMDT': preliminary_daly_costs.Exp_FLQ_DALY[i],
                                 'Cost_SdTreat_PMDT': preliminary_daly_costs.SdTreat_cost[i] -
                                                      preliminary_daly_costs.Exp_FLQ_cost[i],
                                 'Cost_SdTreat': preliminary_daly_costs.SdTreat_cost[i],
                                 'Cost_PMDT': preliminary_daly_costs.Exp_FLQ_cost[i]
                                 }
                            )

                        ### End Positive DT ###
                    else:
                        ### Negative DT ###
                        # Chance Node
                        C_FLQ_n = ChanceNode(name='C_FLQ_n', cost=Cost_FLQ, daly=DALY_FLQ,
                                             future_nodes=[C_FLQsus, C_FLQres], probs=[P_S_S, P_R_S])
                        # Decision Node
                        D_n = DecisionNode(name='D_n', cost=0, daly=0, future_nodes=[C_FLQ_n, C_DLM])

                        # Decision Tree
                        DT_n = DecisionTree(name='DT_n', decision_nodes=D_n, willingness_to_pay=wtp)

                        # Optimal Treatment
                        Opt_Treat_n = DT_n.get_optimal_decision()[0]

                        # Select Optimal Treatment
                        if Opt_Treat_n == 'C_DLM':

                            # NMB, DALYs and Costs for each patient
                            NMB_DALY_Cost_SdTreat_PMDT_eachpt.append(
                                {'threshold': t,
                                 'Sample': j,
                                 'Person': i,
                                 'FLQ_Status': FLQ_status,
                                 'Prediction_Model_Classification': 'FLQ Susceptible',
                                 'DALY_DLM': D_n.get_expected_daly()['C_DLM'],
                                 'Cost_DLM': D_n.get_expected_cost()['C_DLM'],
                                 'DALY_FLQ': D_n.get_expected_daly()['C_FLQ_n'],
                                 'Cost_FLQ': D_n.get_expected_cost()['C_FLQ_n'],
                                 'NMB_SdTreat_PMDT': preliminary_daly_costs.SdTreat_NMB[i] -
                                                     preliminary_daly_costs.DLM_NMB[
                                                         i],
                                 'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[i],
                                 'NMB_SdTreat_FLQ': wtp * preliminary_daly_costs.Exp_FLQ_SdTreat_DALY[i] +
                                                    preliminary_daly_costs.Exp_FLQ_SdTreat_cost[i],
                                 'NMB_DLM': wtp * D_n.get_expected_daly()['C_DLM'] + D_n.get_expected_cost()['C_DLM'],
                                 'NMB_PMDT': preliminary_daly_costs.DLM_NMB[i],
                                 'DALY_SdTreat_PMDT': preliminary_daly_costs.SdTreat_DALY[i] -
                                                      preliminary_daly_costs.Exp_DLM_DALY[i],
                                 'DALY_SdTreat': preliminary_daly_costs.SdTreat_DALY[i],
                                 'DALY_PMDT': preliminary_daly_costs.Exp_DLM_DALY[i],
                                 'Cost_SdTreat_PMDT': preliminary_daly_costs.SdTreat_cost[i] -
                                                      preliminary_daly_costs.Exp_DLM_cost[i],
                                 'Cost_SdTreat': preliminary_daly_costs.SdTreat_cost[i],
                                 'Cost_PMDT': preliminary_daly_costs.Exp_DLM_cost[i]
                                 }
                            )

                        else:

                            # NMB, DALYs and Costs for each patient
                            NMB_DALY_Cost_SdTreat_PMDT_eachpt.append(
                                {'threshold': t,
                                 'Sample': j,
                                 'Person': i,
                                 'FLQ_Status': FLQ_status,
                                 'Prediction_Model_Classification': 'FLQ Susceptible',
                                 'DALY_DLM': D_n.get_expected_daly()['C_DLM'],
                                 'Cost_DLM': D_n.get_expected_cost()['C_DLM'],
                                 'DALY_FLQ': D_n.get_expected_daly()['C_FLQ_n'],
                                 'Cost_FLQ': D_n.get_expected_cost()['C_FLQ_n'],
                                 'NMB_SdTreat_PMDT': preliminary_daly_costs.SdTreat_NMB[i] -
                                                     preliminary_daly_costs.FLQ_NMB[
                                                         i],
                                 'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[i],
                                 'NMB_SdTreat_FLQ': wtp * preliminary_daly_costs.Exp_FLQ_SdTreat_DALY[i] +
                                                    preliminary_daly_costs.Exp_FLQ_SdTreat_cost[i],
                                 'NMB_DLM': wtp * D_n.get_expected_daly()['C_DLM'] + D_n.get_expected_cost()['C_DLM'],
                                 'NMB_PMDT': preliminary_daly_costs.FLQ_NMB[i],
                                 'DALY_SdTreat_PMDT': preliminary_daly_costs.SdTreat_DALY[i] -
                                                      preliminary_daly_costs.Exp_FLQ_DALY[i],
                                 'DALY_SdTreat': preliminary_daly_costs.SdTreat_DALY[i],
                                 'DALY_PMDT': preliminary_daly_costs.Exp_FLQ_DALY[i],
                                 'Cost_SdTreat_PMDT': preliminary_daly_costs.SdTreat_cost[i] -
                                                      preliminary_daly_costs.Exp_FLQ_cost[i],
                                 'Cost_SdTreat': preliminary_daly_costs.SdTreat_cost[i],
                                 'Cost_PMDT': preliminary_daly_costs.Exp_FLQ_cost[i]
                                 }
                            )

                            ### End Negative DT ###



            # NMB, DALYs and Costs for each patient
            NMB_DALY_Cost_SdTreat_PMDT_sampleavg = pd.concat([NMB_DALY_Cost_SdTreat_PMDT_sampleavg, (calculate_sample_averages(
                pd.DataFrame(NMB_DALY_Cost_SdTreat_PMDT_eachpt), ['FLQ_Status', 'Prediction_Model_Classification'],
                ['Sample', 'threshold']))], ignore_index=True )

            print(NMB_DALY_Cost_SdTreat_PMDT_sampleavg)

            print(f"Threshold {t} done.")

        # Record the end time
        end_time = time.time()
        # Calculate the elapsed time
        elapsed_time = end_time - start_time
        print(f"Sample {j} elapsed time: {elapsed_time} seconds")

    df_NMB_DALY_Cost_SdTreat_PMDT_sampleavg = pd.DataFrame(NMB_DALY_Cost_SdTreat_PMDT_sampleavg)

    return df_NMB_DALY_Cost_SdTreat_PMDT_sampleavg

base_path = '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/'
cost_effectiveness_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'

# Read data
cost_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'Costs')
dalyweigth_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'DALY Weight')
dalylength_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'DALY Lenght')

wtp_mult = np.arange(0.5, 3, 0.5)

wtp = 1 *GDP_moldova

test = dr_tb_pm_dt_s(sens_spec_PM, pred_data, DALY_individual_Moldova, prob_data, cost_data_prior,
           dalyweigth_data, dalylength_data, wtp, par_samplesize=1000)

print(test)

# PM + DT
# Create a dynamic file path
file_path_NMB_DALY_Cost_SdTreat_PMDT_eachpt = f"/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/test/test.xlsx"
# Save the DataFrame to an Excel file
test.to_excel(
    file_path_NMB_DALY_Cost_SdTreat_PMDT_eachpt,
    index=False)
# End PM + DT