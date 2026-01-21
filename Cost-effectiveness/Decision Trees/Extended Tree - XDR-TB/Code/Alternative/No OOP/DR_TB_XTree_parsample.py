
import time
import csv
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

def optimal_treat_pmdt_sample(pt, pred, t, wtp, DALY_individual_Moldova, prob_data, cost_sampled_par, dalyweight_sampled_par,
                                                 dalylength_sampled_par, P_S_R, P_R_R, P_S_S, P_R_S, par_samplesize):

    probability_variables = dict(zip(prob_data['Probability Variable'], prob_data['Probability Value']))

    FLQ_expected_cost_sample = []
    FLQ_expected_DALY_sample = []
    DLM_expected_cost_sample = []
    DLM_expected_DALY_sample = []

    sampler = ParameterSampler(cost_data_prior, dalyweight_data, dalylength_data, nsamples=par_samplesize)

    # Specify the columns to exclude from the mean calculation
    for j in range(1, par_samplesize + 1):

        # Generate the sampled tables for cost and daly in the appropriate format (2 columns)
        cost_daly_sampled = sampler.cost_daly_input_table(cost_sampled_par, dalyweight_sampled_par,
                                                  dalylength_sampled_par, j)

        # Terminal nodes
        CC_FLQsus = TerminalNode(name='CC_FLQsus', cost=cost_daly_sampled['Cost_CC_FLQsus'], daly=cost_daly_sampled['DALY_CC_FLQsus'])
        TF_FLQsus = TerminalNode(name='TF_FLQsus', cost=cost_daly_sampled['Cost_TF_FLQsus'], daly=cost_daly_sampled['DALY_TF_FLQsus'])
        CC_FLQres = TerminalNode(name='CC_FLQres', cost=cost_daly_sampled['Cost_CC_FLQres'], daly=cost_daly_sampled['DALY_CC_FLQres'])
        TF_FLQres = TerminalNode(name='TF_FLQres', cost=cost_daly_sampled['Cost_TF_FLQres'], daly=cost_daly_sampled['DALY_TF_FLQres'])
        CC_DLM = TerminalNode(name='CC_DLM', cost=cost_daly_sampled['Cost_CC_DLM'], daly=cost_daly_sampled['DALY_CC_DLM'])
        TF_DLM = TerminalNode(name='TF_DLM', cost=cost_daly_sampled['Cost_TF_DLM'], daly=cost_daly_sampled['DALY_TF_DLM'])

        # DALYs incurred from death for patient pt
        DALY_Death = DALY_individual_Moldova[pt]

        ############ DALY ############
        DEATH_FLQsus = TerminalNode(name='D_FLQsus', cost=cost_daly_sampled['Cost_D_FLQsus'], daly=DALY_Death)
        DEATH_FLQres = TerminalNode(name='D_FLQres', cost=cost_daly_sampled['Cost_D_FLQres'], daly=DALY_Death)
        DEATH_DLM = TerminalNode(name='D_DLM', cost=cost_daly_sampled['Cost_D_DLM'], daly=DALY_Death)

        # Chance nodes
        C_FLQsus = ChanceNode(name='C_FLQsus', cost=cost_daly_sampled['Cost_FLQ'],
                              future_nodes=[CC_FLQsus, TF_FLQsus, DEATH_FLQsus],
                              probs=[probability_variables['Prob_CC_FLQsus'], probability_variables['Prob_TF_FLQsus'],
                                     probability_variables['Prob_D_FLQsus']],
                              daly=cost_daly_sampled['DALY_FLQ'])
        C_FLQres = ChanceNode(name='C_FLQres', cost=cost_daly_sampled['Cost_FLQ'],
                              future_nodes=[CC_FLQres, TF_FLQres, DEATH_FLQres],
                              probs=[probability_variables['Prob_CC_FLQres'], probability_variables['Prob_TF_FLQres'],
                                     probability_variables['Prob_D_FLQres']],
                              daly=cost_daly_sampled['DALY_FLQ'])
        C_DLM = ChanceNode(name='C_DLM', cost=cost_daly_sampled['Cost_DLM'],
                           future_nodes=[CC_DLM, TF_DLM, DEATH_DLM],
                           probs=[probability_variables['Prob_CC_DLM'], probability_variables['Prob_TF_DLM'],
                                  probability_variables['Prob_D_DLM']], daly=cost_daly_sampled['DALY_DLM'])

        if pred > t:
            ### Positive DT ###
            # Chance Node
            C_FLQ = ChanceNode(name='C_FLQ', cost=0, daly=0,
                                 future_nodes=[C_FLQsus, C_FLQres], probs=[P_S_R, P_R_R])
            # Decision Node
            D = DecisionNode(name='D', cost=0, daly=0, future_nodes=[C_FLQ, C_DLM])

            # FLQ
            FLQ_expected_cost_sample.append(D.get_expected_cost()['C_FLQ'])
            FLQ_expected_DALY_sample.append(D.get_expected_daly()['C_FLQ'])

            # DLM
            DLM_expected_cost_sample.append(D.get_expected_cost()['C_DLM'])
            DLM_expected_DALY_sample.append(D.get_expected_daly()['C_DLM'])


        else:
            ### Negative DT ###
            # Chance Node
            C_FLQ = ChanceNode(name='C_FLQ', cost=0, daly=0,
                                 future_nodes=[C_FLQsus, C_FLQres], probs=[P_S_S, P_R_S])
            # Decision Node
            D = DecisionNode(name='D', cost=0, daly=0, future_nodes=[C_FLQ, C_DLM])

            # FLQ
            FLQ_expected_cost_sample.append(D.get_expected_cost()['C_FLQ'])
            FLQ_expected_DALY_sample.append(D.get_expected_daly()['C_FLQ'])

            # DLM
            DLM_expected_cost_sample.append(D.get_expected_cost()['C_DLM'])
            DLM_expected_DALY_sample.append(D.get_expected_daly()['C_DLM'])

    # Expected cost - Average
    FLQ_expected_cost_avg = statistics.mean(FLQ_expected_cost_sample)
    FLQ_expected_DALY_avg = statistics.mean(FLQ_expected_DALY_sample)

    # Expected DALY - Average
    DLM_expected_cost_avg = statistics.mean(DLM_expected_cost_sample)
    DLM_expected_DALY_avg = statistics.mean(DLM_expected_DALY_sample)

    # Loss in NMB
    FLQ_LNMB = wtp * FLQ_expected_DALY_avg + FLQ_expected_cost_avg
    DLM_LNMB = wtp * DLM_expected_DALY_avg + DLM_expected_cost_avg

    # print(FLQ_LNMB)
    # print(DLM_LNMB)

    if FLQ_LNMB > DLM_LNMB:
        Opt_Treat = 'DLM'
    else:
        Opt_Treat = 'FLQ'

    # print(f"Optimal treatment found: {Opt_Treat}.")

    return ({
            'Opt_Treat': Opt_Treat,
            'FLQ_expected_cost_sample_avg': FLQ_expected_cost_avg,
            'FLQ_expected_DALY_sample_avg': FLQ_expected_DALY_avg,
            'DLM_expected_cost_sample_avg': DLM_expected_cost_avg,
            'DLM_expected_DALY_sample_avg': DLM_expected_DALY_avg,
            'FLQ_LNMB': FLQ_LNMB,
            'DLM_LNMB': DLM_LNMB}
    )

def optimal_treat_dt_sample(pt, wtp, FLQ_Res_prev, DALY_individual_Moldova, cost_sampled_par, dalyweight_sampled_par,
                                                 dalylength_sampled_par, par_samplesize):

    probability_variables = dict(zip(prob_data['Probability Variable'], prob_data['Probability Value']))

    FLQ_expected_cost_sample = []
    FLQ_expected_DALY_sample = []
    DLM_expected_cost_sample = []
    DLM_expected_DALY_sample = []

    sampler = ParameterSampler(cost_data_prior, dalyweight_data, dalylength_data, nsamples=par_samplesize)

    # Specify the columns to exclude from the mean calculation
    for j in range(1, par_samplesize + 1):

        # Generate the sampled tables for cost and daly in the appropriate format (2 columns)
        cost_daly_sampled = sampler.cost_daly_input_table(cost_sampled_par, dalyweight_sampled_par,
                                                  dalylength_sampled_par, j)

        # Terminal nodes
        CC_FLQsus = TerminalNode(name='CC_FLQsus', cost=cost_daly_sampled['Cost_CC_FLQsus'],
                                 daly=cost_daly_sampled['DALY_CC_FLQsus'])
        TF_FLQsus = TerminalNode(name='TF_FLQsus', cost=cost_daly_sampled['Cost_TF_FLQsus'],
                                 daly=cost_daly_sampled['DALY_TF_FLQsus'])
        CC_FLQres = TerminalNode(name='CC_FLQres', cost=cost_daly_sampled['Cost_CC_FLQres'],
                                 daly=cost_daly_sampled['DALY_CC_FLQres'])
        TF_FLQres = TerminalNode(name='TF_FLQres', cost=cost_daly_sampled['Cost_TF_FLQres'],
                                 daly=cost_daly_sampled['DALY_TF_FLQres'])
        CC_DLM = TerminalNode(name='CC_DLM', cost=cost_daly_sampled['Cost_CC_DLM'], daly=cost_daly_sampled['DALY_CC_DLM'])
        TF_DLM = TerminalNode(name='TF_DLM', cost=cost_daly_sampled['Cost_TF_DLM'], daly=cost_daly_sampled['DALY_TF_DLM'])

        # DALYs incurred from death for patient pt
        DALY_Death = DALY_individual_Moldova[pt]

        ############ DALY ############
        DEATH_FLQsus = TerminalNode(name='D_FLQsus', cost=cost_daly_sampled['Cost_D_FLQsus'], daly=DALY_Death)
        DEATH_FLQres = TerminalNode(name='D_FLQres', cost=cost_daly_sampled['Cost_D_FLQres'], daly=DALY_Death)
        DEATH_DLM = TerminalNode(name='D_DLM', cost=cost_daly_sampled['Cost_D_DLM'], daly=DALY_Death)

        # Chance nodes
        C_FLQsus = ChanceNode(name='C_FLQsus', cost=cost_daly_sampled['Cost_FLQ'],
                              future_nodes=[CC_FLQsus, TF_FLQsus, DEATH_FLQsus],
                              probs=[probability_variables['Prob_CC_FLQsus'], probability_variables['Prob_TF_FLQsus'],
                                     probability_variables['Prob_D_FLQsus']],
                              daly=cost_daly_sampled['DALY_FLQ'])
        C_FLQres = ChanceNode(name='C_FLQres', cost=cost_daly_sampled['Cost_FLQ'],
                              future_nodes=[CC_FLQres, TF_FLQres, DEATH_FLQres],
                              probs=[probability_variables['Prob_CC_FLQres'], probability_variables['Prob_TF_FLQres'],
                                     probability_variables['Prob_D_FLQres']],
                              daly=cost_daly_sampled['DALY_FLQ'])
        C_DLM = ChanceNode(name='C_DLM', cost=cost_daly_sampled['Cost_DLM'],
                           future_nodes=[CC_DLM, TF_DLM, DEATH_DLM],
                           probs=[probability_variables['Prob_CC_DLM'], probability_variables['Prob_TF_DLM'],
                                  probability_variables['Prob_D_DLM']], daly=cost_daly_sampled['DALY_DLM'])

        # Chance Node
        C_FLQ = ChanceNode(name='C_FLQ', cost=0, daly=0,
                             future_nodes=[C_FLQsus, C_FLQres], probs=[(1-FLQ_Res_prev), FLQ_Res_prev])
        # Decision Node
        D = DecisionNode(name='D', cost=0, daly=0, future_nodes=[C_FLQ, C_DLM])

        # FLQ
        FLQ_expected_cost_sample.append(D.get_expected_cost()['C_FLQ'])
        FLQ_expected_DALY_sample.append(D.get_expected_daly()['C_FLQ'])

        # DLM
        DLM_expected_cost_sample.append(D.get_expected_cost()['C_DLM'])
        DLM_expected_DALY_sample.append(D.get_expected_daly()['C_DLM'])


    # Expected cost - Average
    FLQ_expected_cost_avg = statistics.mean(FLQ_expected_cost_sample)
    FLQ_expected_DALY_avg = statistics.mean(FLQ_expected_DALY_sample)

    # Expected DALY - Average
    DLM_expected_cost_avg = statistics.mean(DLM_expected_cost_sample)
    DLM_expected_DALY_avg = statistics.mean(DLM_expected_DALY_sample)

    # Loss in NMB
    FLQ_LNMB = wtp * FLQ_expected_DALY_avg + FLQ_expected_cost_avg
    DLM_LNMB = wtp * DLM_expected_DALY_avg + DLM_expected_cost_avg

    print(FLQ_LNMB)
    # print(DLM_LNMB)

    if FLQ_LNMB > DLM_LNMB:
        Opt_Treat = 'DLM'
    else:
        Opt_Treat = 'FLQ'

    # print(f"Optimal treatment found: {Opt_Treat}.")

    return ({
            'Opt_Treat': Opt_Treat,
            'FLQ_expected_cost_sample_avg': FLQ_expected_cost_avg,
            'FLQ_expected_DALY_sample_avg': FLQ_expected_DALY_avg,
            'DLM_expected_cost_sample_avg': DLM_expected_cost_avg,
            'DLM_expected_DALY_sample_avg': DLM_expected_DALY_avg,
            'FLQ_LNMB': FLQ_LNMB,
            'DLM_LNMB': DLM_LNMB}
    )



def dr_tb_pmdt_s(sens_spec_PM, pred_data, DALY_individual_Moldova, preliminary_daly_costs, prob_data, cost_sampled_par, dalyweight_sampled_par,
                                                 dalylength_sampled_par, wtp, par_samplesize=2):

    start_time = time.time()

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

            start_time_t = time.time()

            for i, (DALY_Death, pred, obs) in enumerate(
                    zip(DALY_individual_Moldova, pred_data['pred'], pred_data['obs'])):

                optimal_treat_pmdt_sample_pt = optimal_treat_pmdt_sample(i, pred, t, wtp, DALY_individual_Moldova, prob_data, cost_sampled_par, dalyweight_sampled_par,
                                                 dalylength_sampled_par, P_S_R, P_R_R, P_S_S, P_R_S, par_samplesize)

                # NMB, Cost and DALYs by FLQ susceptibility
                if obs == 1:
                    FLQ_status = 'FLQ Resistant'
                else:
                    FLQ_status = 'FLQ Susceptible'

                if optimal_treat_pmdt_sample_pt['Opt_Treat'] == 'DLM':

                    # NMB, DALYs and Costs for each patient
                    NMB_DALY_Cost_SdTreat_PMDT_eachpt.append(
                        {'threshold': t,
                         'Person': i,
                         'FLQ_Status': FLQ_status,
                         'Prediction_Model_Classification': 'FLQ Resistant',
                         'Opt_Treat': optimal_treat_pmdt_sample_pt['Opt_Treat'],
                         'DALY_DLM': optimal_treat_pmdt_sample_pt['DLM_expected_DALY_sample_avg'],
                         'Cost_DLM': optimal_treat_pmdt_sample_pt['DLM_expected_cost_sample_avg'],
                         'DALY_FLQ': optimal_treat_pmdt_sample_pt['FLQ_expected_DALY_sample_avg'],
                         'Cost_FLQ': optimal_treat_pmdt_sample_pt['FLQ_expected_cost_sample_avg'],
                         'NMB_SdTreat_PMDT': preliminary_daly_costs.SdTreat_NMB[i] -
                                             preliminary_daly_costs.DLM_NMB[
                                                 i],
                         'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[i],
                         'NMB_SdTreat_FLQ': wtp * preliminary_daly_costs.Exp_FLQ_SdTreat_DALY[i] +
                                            preliminary_daly_costs.Exp_FLQ_SdTreat_cost[i],
                         'NMB_DLM': optimal_treat_pmdt_sample_pt['DLM_LNMB'],
                         'NMB_FLQ': optimal_treat_pmdt_sample_pt['FLQ_LNMB'],
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
                         'Person': i,
                         'FLQ_Status': FLQ_status,
                         'Prediction_Model_Classification': 'FLQ Susceptible',
                         'Opt_Treat': optimal_treat_pmdt_sample_pt['Opt_Treat'],
                         'DALY_DLM': optimal_treat_pmdt_sample_pt['DLM_expected_DALY_sample_avg'],
                         'Cost_DLM': optimal_treat_pmdt_sample_pt['DLM_expected_cost_sample_avg'],
                         'DALY_FLQ': optimal_treat_pmdt_sample_pt['FLQ_expected_DALY_sample_avg'],
                         'Cost_FLQ': optimal_treat_pmdt_sample_pt['FLQ_expected_cost_sample_avg'],
                         'NMB_SdTreat_PMDT': preliminary_daly_costs.SdTreat_NMB[i] -
                                             preliminary_daly_costs.FLQ_NMB[
                                                 i],
                         'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[i],
                         'NMB_SdTreat_FLQ': wtp * preliminary_daly_costs.Exp_FLQ_SdTreat_DALY[i] +
                                            preliminary_daly_costs.Exp_FLQ_SdTreat_cost[i],
                         'NMB_DLM': optimal_treat_pmdt_sample_pt['DLM_LNMB'],
                         'NMB_FLQ': optimal_treat_pmdt_sample_pt['FLQ_LNMB'],
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

            # Record the end time
            end_time_t = time.time()
            # Calculate the elapsed time
            elapsed_time_t = end_time_t - start_time_t

            print(f"Threshold {t} done in {elapsed_time_t/60:.2f} minutes.")

        # Record the end time
        end_time = time.time()
        # Calculate the elapsed time
        elapsed_time = end_time - start_time

    print(f"Running time: {elapsed_time/60:.2f} minutes.")

    df_NMB_DALY_Cost_SdTreat_PMDT_eachpt = pd.DataFrame(NMB_DALY_Cost_SdTreat_PMDT_eachpt)

    return df_NMB_DALY_Cost_SdTreat_PMDT_eachpt



def dr_tb_dt_s(preliminary_daly_costs, DALY_individual_Moldova,  cost_sampled_par, dalyweight_sampled_par,
                                                 dalylength_sampled_par, wtp, par_samplesize=2):

    start_time = time.time()

    # Initiating the vectors that store output
    NMB_DALY_Cost_SdTreat_DT_eachpt = [] # Change in NMB, DALYs and Cost when the optimal treatment (PM + DT) is used in comparison to the standard treatment and separatel

    for i, (DALY_Death, pred, obs) in enumerate(
            zip(DALY_individual_Moldova, pred_data['pred'], pred_data['obs'])):

        optimal_treat_dt_pt = optimal_treat_dt_sample(i, wtp, FLQ_Res_prev, DALY_individual_Moldova, cost_sampled_par, dalyweight_sampled_par,
                                                 dalylength_sampled_par, par_samplesize)

        # print("Finding optimal treatment")

        # NMB, Cost and DALYs by FLQ susceptibility
        if obs == 1:
            FLQ_status = 'FLQ Resistant'
        else:
            FLQ_status = 'FLQ Susceptible'

        if optimal_treat_dt_pt['Opt_Treat'] == 'DLM':

            # NMB, DALYs and Costs for each patient
            NMB_DALY_Cost_SdTreat_DT_eachpt.append(
                {'Person': i,
                 'FLQ_Status': FLQ_status,
                 'DT_opt_treat': 'DLM',
                 'Opt_Treat': optimal_treat_dt_pt['Opt_Treat'],
                 'DALY_DLM': optimal_treat_dt_pt['DLM_expected_DALY_sample_avg'],
                 'Cost_DLM': optimal_treat_dt_pt['DLM_expected_cost_sample_avg'],
                 'DALY_FLQ': optimal_treat_dt_pt['FLQ_expected_DALY_sample_avg'],
                 'Cost_FLQ': optimal_treat_dt_pt['FLQ_expected_cost_sample_avg'],
                 'NMB_SdTreat_DT': preliminary_daly_costs.SdTreat_NMB[i] -
                                     preliminary_daly_costs.DLM_NMB[
                                         i],
                 'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[i],
                 'NMB_SdTreat_FLQ': wtp * preliminary_daly_costs.Exp_FLQ_SdTreat_DALY[i] +
                                    preliminary_daly_costs.Exp_FLQ_SdTreat_cost[i],
                 'NMB_DLM': optimal_treat_dt_pt['DLM_LNMB'],
                 'NMB_FLQ': optimal_treat_dt_pt['FLQ_LNMB'],
                 'NMB_DT': preliminary_daly_costs.DLM_NMB[i],
                 'DALY_SdTreat_DT': preliminary_daly_costs.SdTreat_DALY[i] -
                                      preliminary_daly_costs.Exp_DLM_DALY[i],
                 'DALY_SdTreat': preliminary_daly_costs.SdTreat_DALY[i],
                 'DALY_DT': preliminary_daly_costs.Exp_DLM_DALY[i],
                 'Cost_SdTreat_DT': preliminary_daly_costs.SdTreat_cost[i] -
                                      preliminary_daly_costs.Exp_DLM_cost[i],
                 'Cost_SdTreat': preliminary_daly_costs.SdTreat_cost[i],
                 'Cost_DT': preliminary_daly_costs.Exp_DLM_cost[i]
                 }
            )

        else:

            # NMB, DALYs and Costs for each patient
            NMB_DALY_Cost_SdTreat_DT_eachpt.append(
                {'Person': i,
                 'FLQ_Status': FLQ_status,
                 'DT_opt_treat': 'FLQ',
                 'Opt_Treat': optimal_treat_dt_pt['Opt_Treat'],
                 'DALY_DLM': optimal_treat_dt_pt['DLM_expected_DALY_sample_avg'],
                 'Cost_DLM': optimal_treat_dt_pt['DLM_expected_cost_sample_avg'],
                 'DALY_FLQ': optimal_treat_dt_pt['FLQ_expected_DALY_sample_avg'],
                 'Cost_FLQ': optimal_treat_dt_pt['FLQ_expected_cost_sample_avg'],
                 'NMB_SdTreat_DT': preliminary_daly_costs.SdTreat_NMB[i] -
                                     preliminary_daly_costs.FLQ_NMB[
                                         i],
                 'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[i],
                 'NMB_SdTreat_FLQ': wtp * preliminary_daly_costs.Exp_FLQ_SdTreat_DALY[i] +
                                    preliminary_daly_costs.Exp_FLQ_SdTreat_cost[i],
                 'NMB_DLM': optimal_treat_dt_pt['DLM_LNMB'],
                 'NMB_FLQ': optimal_treat_dt_pt['FLQ_LNMB'],
                 'NMB_DT': preliminary_daly_costs.FLQ_NMB[i],
                 'DALY_SdTreat_DT': preliminary_daly_costs.SdTreat_DALY[i] -
                                      preliminary_daly_costs.Exp_FLQ_DALY[i],
                 'DALY_SdTreat': preliminary_daly_costs.SdTreat_DALY[i],
                 'DALY_DT': preliminary_daly_costs.Exp_FLQ_DALY[i],
                 'Cost_SdTreat_DT': preliminary_daly_costs.SdTreat_cost[i] -
                                      preliminary_daly_costs.Exp_FLQ_cost[i],
                 'Cost_SdTreat': preliminary_daly_costs.SdTreat_cost[i],
                 'Cost_DT': preliminary_daly_costs.Exp_FLQ_cost[i]
                 }
            )

    # Record the end time
    end_time = time.time()
    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    print(elapsed_time)

    df_NMB_DALY_Cost_SdTreat_DT_eachpt = pd.DataFrame(NMB_DALY_Cost_SdTreat_DT_eachpt)

    return df_NMB_DALY_Cost_SdTreat_DT_eachpt



if __name__ == "__main__":
    base_path = '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/'
    cost_effectiveness_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'

    # Read data
    cost_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'Costs')
    dalyweight_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'DALY Weight')
    dalylength_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'DALY Lenght')

    wtp_mult = np.arange(0.5, 3, 0.5)

    wtp = 1 *GDP_moldova
    # #
    # # test = dr_tb_pm_dt_s(sens_spec_PM, pred_data, DALY_individual_Moldova, prob_data, cost_data_prior,
    # #            dalyweight_data, dalylength_data, wtp, par_samplesize=5)
    #
    # for index, row in prob_data.iterrows():
    #     globals()[row['Probability Variable']] = row['Probability Value']
    #
    # par_samplesize = 5
    #
    #     # Sampling from the prior costs
    # cost_sampled_par = cost_parameter_sampler(cost_data_prior, par_samplesize)
    #
    # # Sampling from the prior daly weights
    # dalyweight_sampled_par = dalyweight_parameter_sampler(dalyweight_data, par_samplesize)
    # # Sampling from the prior daly length
    # dalylength_sampled_par = dalylength_parameter_sampler(dalylength_data, par_samplesize)
    #
    # ############ Preliminary Costs and DALY Calculation ############
    # # Calculated expected costs and DALYs for ach treatment depending on FLQ susceptibility
    # preliminary_daly_costs = calculate_pre_daly_cost_s(pred_data, DALY_individual_Moldova, prob_data, cost_sampled_par,
    #                                                    dalyweight_sampled_par,dalylength_sampled_par,
    #                                                    wtp, par_samplesize)
    # ############ End Preliminary Costs and ############
    #
    # with open(sens_spec_PM, 'r') as file:
    #     reader = csv.DictReader(file)
    #     for row in reader:
    #         P_S_R = float(row['P_S_R'])
    #         P_R_R = float(row['P_R_R'])
    #         P_S_S = float(row['P_S_S'])
    #         P_R_S = float(row['P_R_S'])
    #         t = float(row['threshold'])
    #
    #         for i, (DALY_Death, pred, obs) in enumerate(
    #                 zip(DALY_individual_Moldova, pred_data['pred'], pred_data['obs'])):
    #
    #             a = optimal_treat_pmdt_sample(i, pred, t, wtp, DALY_individual_Moldova, cost_sampled_par, dalyweight_sampled_par,
    #                                              dalylength_sampled_par, P_S_R, P_R_R, P_S_S, P_R_S, par_samplesize)
    #
    #             print(a.Opt_Treat)
    #             # print(f"Patient {i} done.")

        # print(f"Threshold {t} done.")


    # # PM + DT
    # # Create a dynamic file path
    # file_path_NMB_DALY_Cost_SdTreat_PMDT_eachpt = f"/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/test/test.xlsx"
    # # Save the DataFrame to an Excel file
    # test.to_excel(
    #     file_path_NMB_DALY_Cost_SdTreat_PMDT_eachpt,
    #     index=False)

    par_samplesize = 1000

    sampler = ParameterSampler(cost_data_prior, dalyweight_data, dalylength_data, nsamples=par_samplesize)

    # Sampling from the prior costs
    cost_sampled_par = sampler.sample_cost_parameters()
    # Sampling from the prior daly weights
    dalyweight_sampled_par =sampler.sample_dalyweight_parameters()
    # Sampling from the prior daly length
    dalylength_sampled_par = sampler.sample_dalylength_parameters()

    ############ Preliminary Costs and DALY Calculation ############
    # Calculated expected costs and DALYs for ach treatment depending on FLQ susceptibility
    preliminary_daly_costs = calculate_pre_daly_cost_s(pred_data, DALY_individual_Moldova, prob_data, cost_sampled_par, dalyweight_sampled_par, dalylength_sampled_par,
                              wtp, par_samplesize)
    ############ End Preliminary Costs and ############
    #
    # test = dr_tb_pmdt_s(sens_spec_PM, pred_data, DALY_individual_Moldova, preliminary_daly_costs, prob_data, cost_sampled_par, dalyweight_sampled_par,
    #                                              dalylength_sampled_par, wtp, par_samplesize=par_samplesize)


    test2 = dr_tb_dt_s(preliminary_daly_costs, DALY_individual_Moldova, cost_sampled_par, dalyweight_sampled_par,
                                                 dalylength_sampled_par, wtp, par_samplesize=par_samplesize)

    # # PM + DT
    # # Create a dynamic file path
    # file_path_NMB_DALY_Cost_SdTreat_DT_eachpt = f"/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/test/test2.xlsx"
    # # Save the DataFrame to an Excel file
    # test2.to_excel(
    #     file_path_NMB_DALY_Cost_SdTreat_DT_eachpt,
    #     index=False)
