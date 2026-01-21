import time
import csv
from PreliminaryDALYs import *
from PM_Performance_class import *

class DRTuberculosisDT:
    def __init__(self, par_sampler, DALY_individual_Moldova, pm_performance, mainpm_pred_data, diseaseprev_sampled, prob_data, cost_sampled_par, dalyweight_sampled_par, dalylength_sampled_par, par_samplesize, wtp):
        self.par_sampler = par_sampler
        self.DALY_individual_Moldova = DALY_individual_Moldova
        self.pm_performance = pm_performance
        self.mainpm_pred_data = mainpm_pred_data
        self.diseaseprev_sampled = diseaseprev_sampled
        self.probability_variables = dict(zip(prob_data['Probability Variable'], prob_data['Probability Value']))
        self.cost_sampled_par = cost_sampled_par
        self.dalyweight_sampled_par = dalyweight_sampled_par
        self.dalylength_sampled_par = dalylength_sampled_par
        self.par_samplesize = par_samplesize
        self.wtp = wtp



    def calculate_sample_averages(self, dataframe, excluded_cols, index_cols):
        include_columns = [col for col in dataframe.columns if col not in excluded_cols and col not in index_cols]
        sample_avg = dataframe.groupby(index_cols)[include_columns].mean().reset_index()
        FLQstatus_Class = dataframe.groupby(index_cols)[excluded_cols].first().reset_index()
        final_sample_avg = pd.merge(sample_avg, FLQstatus_Class, on=index_cols)
        return final_sample_avg

    def optimal_treat_pmdt_sample(self, pt, prediction, t, wtp, decisiontree_prob_df):

        FLQ_expected_cost_sample = []
        FLQ_expected_DALY_sample = []
        DLM_expected_cost_sample = []
        DLM_expected_DALY_sample = []

        for j in range(1, self.par_samplesize + 1):

            decisiontree_prob = self.pm_performance.evaluate_pm_sample_dic(decisiontree_prob_df, j)

            cost_daly_sampled = self.par_sampler.cost_daly_input_table(self.cost_sampled_par, self.dalyweight_sampled_par, self.dalylength_sampled_par, j)
            DALY_Death = self.DALY_individual_Moldova[pt]

            # Terminal Nodes
            CC_FLQsus = TerminalNode(name='CC_FLQsus', cost=cost_daly_sampled['Cost_CC_FLQsus'], daly=cost_daly_sampled['DALY_CC_FLQsus'])
            TF_FLQsus = TerminalNode(name='TF_FLQsus', cost=cost_daly_sampled['Cost_TF_FLQsus'], daly=cost_daly_sampled['DALY_TF_FLQsus'])
            CC_FLQres = TerminalNode(name='CC_FLQres', cost=cost_daly_sampled['Cost_CC_FLQres'], daly=cost_daly_sampled['DALY_CC_FLQres'])
            TF_FLQres = TerminalNode(name='TF_FLQres', cost=cost_daly_sampled['Cost_TF_FLQres'], daly=cost_daly_sampled['DALY_TF_FLQres'])
            CC_DLM = TerminalNode(name='CC_DLM', cost=cost_daly_sampled['Cost_CC_DLM'], daly=cost_daly_sampled['DALY_CC_DLM'])
            TF_DLM = TerminalNode(name='TF_DLM', cost=cost_daly_sampled['Cost_TF_DLM'], daly=cost_daly_sampled['DALY_TF_DLM'])

            DEATH_FLQsus = TerminalNode(name='D_FLQsus', cost=cost_daly_sampled['Cost_D_FLQsus'], daly=DALY_Death)
            DEATH_FLQres = TerminalNode(name='D_FLQres', cost=cost_daly_sampled['Cost_D_FLQres'], daly=DALY_Death)
            DEATH_DLM = TerminalNode(name='D_DLM', cost=cost_daly_sampled['Cost_D_DLM'], daly=DALY_Death)

            # Chance Nodes
            C_FLQsus = ChanceNode(name='C_FLQsus', cost=cost_daly_sampled['Cost_FLQ'],
                                  future_nodes=[CC_FLQsus, TF_FLQsus, DEATH_FLQsus],
                                  probs=[self.probability_variables['Prob_CC_FLQsus'], self.probability_variables['Prob_TF_FLQsus'],
                                         self.probability_variables['Prob_D_FLQsus']],
                                  daly=cost_daly_sampled['DALY_FLQ'])
            C_FLQres = ChanceNode(name='C_FLQres', cost=cost_daly_sampled['Cost_FLQ'],
                                  future_nodes=[CC_FLQres, TF_FLQres, DEATH_FLQres],
                                  probs=[self.probability_variables['Prob_CC_FLQres'], self.probability_variables['Prob_TF_FLQres'],
                                         self.probability_variables['Prob_D_FLQres']],
                                  daly=cost_daly_sampled['DALY_FLQ'])
            C_DLM = ChanceNode(name='C_DLM', cost=cost_daly_sampled['Cost_DLM'],
                               future_nodes=[CC_DLM, TF_DLM, DEATH_DLM],
                               probs=[self.probability_variables['Prob_CC_DLM'], self.probability_variables['Prob_TF_DLM'],
                                      self.probability_variables['Prob_D_DLM']], daly=cost_daly_sampled['DALY_DLM'])

            # Decision Node
            if prediction > t:
                C_FLQ = ChanceNode(name='C_FLQ', cost=0, daly=0,
                                   future_nodes=[C_FLQsus, C_FLQres], probs=[decisiontree_prob['P_S_R'], decisiontree_prob['P_R_R']])
            else:
                C_FLQ = ChanceNode(name='C_FLQ', cost=0, daly=0,
                                   future_nodes=[C_FLQsus, C_FLQres], probs=[decisiontree_prob['P_S_S'], decisiontree_prob['P_R_S']])

            D = DecisionNode(name='D', cost=0, daly=0, future_nodes=[C_FLQ, C_DLM])

            FLQ_expected_cost_sample.append(D.get_expected_cost()['C_FLQ'])
            FLQ_expected_DALY_sample.append(D.get_expected_daly()['C_FLQ'])
            DLM_expected_cost_sample.append(D.get_expected_cost()['C_DLM'])
            DLM_expected_DALY_sample.append(D.get_expected_daly()['C_DLM'])

        FLQ_expected_cost_avg = statistics.mean(FLQ_expected_cost_sample)
        FLQ_expected_DALY_avg = statistics.mean(FLQ_expected_DALY_sample)
        DLM_expected_cost_avg = statistics.mean(DLM_expected_cost_sample)
        DLM_expected_DALY_avg = statistics.mean(DLM_expected_DALY_sample)

        FLQ_LNMB = wtp * FLQ_expected_DALY_avg + FLQ_expected_cost_avg
        DLM_LNMB = wtp * DLM_expected_DALY_avg + DLM_expected_cost_avg

        Opt_Treat = 'DLM' if FLQ_LNMB > DLM_LNMB else 'FLQ'

        return {
            'Opt_Treat': Opt_Treat,
            'FLQ_expected_cost_sample_avg': FLQ_expected_cost_avg,
            'FLQ_expected_DALY_sample_avg': FLQ_expected_DALY_avg,
            'DLM_expected_cost_sample_avg': DLM_expected_cost_avg,
            'DLM_expected_DALY_sample_avg': DLM_expected_DALY_avg,
            'FLQ_LNMB': FLQ_LNMB,
            'DLM_LNMB': DLM_LNMB
        }

    def optimal_treat_dt_sample(self, pt, wtp):

        FLQ_expected_cost_sample = []
        FLQ_expected_DALY_sample = []
        DLM_expected_cost_sample = []
        DLM_expected_DALY_sample = []

        for j in range(1, self.par_samplesize + 1):
            cost_daly_sampled = self.par_sampler.cost_daly_input_table(self.cost_sampled_par, self.dalyweight_sampled_par, self.dalylength_sampled_par, j)
            diseaseprev_sampled_input = self.par_sampler.diseaseprev_input(self.diseaseprev_sampled, j)
            DALY_Death = self.DALY_individual_Moldova[pt]

            # Terminal Nodes
            CC_FLQsus = TerminalNode(name='CC_FLQsus', cost=cost_daly_sampled['Cost_CC_FLQsus'], daly=cost_daly_sampled['DALY_CC_FLQsus'])
            TF_FLQsus = TerminalNode(name='TF_FLQsus', cost=cost_daly_sampled['Cost_TF_FLQsus'], daly=cost_daly_sampled['DALY_TF_FLQsus'])
            CC_FLQres = TerminalNode(name='CC_FLQres', cost=cost_daly_sampled['Cost_CC_FLQres'], daly=cost_daly_sampled['DALY_CC_FLQres'])
            TF_FLQres = TerminalNode(name='TF_FLQres', cost=cost_daly_sampled['Cost_TF_FLQres'], daly=cost_daly_sampled['DALY_TF_FLQres'])
            CC_DLM = TerminalNode(name='CC_DLM', cost=cost_daly_sampled['Cost_CC_DLM'], daly=cost_daly_sampled['DALY_CC_DLM'])
            TF_DLM = TerminalNode(name='TF_DLM', cost=cost_daly_sampled['Cost_TF_DLM'], daly=cost_daly_sampled['DALY_TF_DLM'])

            DEATH_FLQsus = TerminalNode(name='D_FLQsus', cost=cost_daly_sampled['Cost_D_FLQsus'], daly=DALY_Death)
            DEATH_FLQres = TerminalNode(name='D_FLQres', cost=cost_daly_sampled['Cost_D_FLQres'], daly=DALY_Death)
            DEATH_DLM = TerminalNode(name='D_DLM', cost=cost_daly_sampled['Cost_D_DLM'], daly=DALY_Death)

            # Chance Nodes
            C_FLQsus = ChanceNode(name='C_FLQsus', cost=cost_daly_sampled['Cost_FLQ'],
                                  future_nodes=[CC_FLQsus, TF_FLQsus, DEATH_FLQsus],
                                  probs=[self.probability_variables['Prob_CC_FLQsus'], self.probability_variables['Prob_TF_FLQsus'],
                                         self.probability_variables['Prob_D_FLQsus']],
                                  daly=cost_daly_sampled['DALY_FLQ'])
            C_FLQres = ChanceNode(name='C_FLQres', cost=cost_daly_sampled['Cost_FLQ'],
                                  future_nodes=[CC_FLQres, TF_FLQres, DEATH_FLQres],
                                  probs=[self.probability_variables['Prob_CC_FLQres'], self.probability_variables['Prob_TF_FLQres'],
                                         self.probability_variables['Prob_D_FLQres']],
                                  daly=cost_daly_sampled['DALY_FLQ'])
            C_DLM = ChanceNode(name='C_DLM', cost=cost_daly_sampled['Cost_DLM'],
                               future_nodes=[CC_DLM, TF_DLM, DEATH_DLM],
                               probs=[self.probability_variables['Prob_CC_DLM'], self.probability_variables['Prob_TF_DLM'],
                                      self.probability_variables['Prob_D_DLM']], daly=cost_daly_sampled['DALY_DLM'])

            # Decision Node
            C_FLQ = ChanceNode(name='C_FLQ', cost=0, daly=0,
                               future_nodes=[C_FLQsus, C_FLQres], probs=[1-diseaseprev_sampled_input, diseaseprev_sampled_input])

            D = DecisionNode(name='D', cost=0, daly=0, future_nodes=[C_FLQ, C_DLM])

            FLQ_expected_cost_sample.append(D.get_expected_cost()['C_FLQ'])
            FLQ_expected_DALY_sample.append(D.get_expected_daly()['C_FLQ'])
            DLM_expected_cost_sample.append(D.get_expected_cost()['C_DLM'])
            DLM_expected_DALY_sample.append(D.get_expected_daly()['C_DLM'])

        FLQ_expected_cost_avg = statistics.mean(FLQ_expected_cost_sample)
        FLQ_expected_DALY_avg = statistics.mean(FLQ_expected_DALY_sample)
        DLM_expected_cost_avg = statistics.mean(DLM_expected_cost_sample)
        DLM_expected_DALY_avg = statistics.mean(DLM_expected_DALY_sample)

        FLQ_LNMB = wtp * FLQ_expected_DALY_avg + FLQ_expected_cost_avg
        DLM_LNMB = wtp * DLM_expected_DALY_avg + DLM_expected_cost_avg

        Opt_Treat = 'DLM' if FLQ_LNMB > DLM_LNMB else 'FLQ'

        return {
            'Opt_Treat': Opt_Treat,
            'FLQ_expected_cost_sample_avg': FLQ_expected_cost_avg,
            'FLQ_expected_DALY_sample_avg': FLQ_expected_DALY_avg,
            'DLM_expected_cost_sample_avg': DLM_expected_cost_avg,
            'DLM_expected_DALY_sample_avg': DLM_expected_DALY_avg,
            'FLQ_LNMB': FLQ_LNMB,
            'DLM_LNMB': DLM_LNMB
        }


    def dr_tb_pmdt_s(self, allthresholds, DALY_individual_Moldova, preliminary_daly_costs):
        start_time = time.time()
        NMB_DALY_Cost_SdTreat_PMDT_eachpt = []  # Results container

        for _, row in allthresholds.iterrows():
            threshold = row['threshold']

            start_time_t = time.time()

            pm_evaluation = self.pm_performance.evaluate_pm(threshold)
            decisiontree_prob_df = self.pm_performance.calculate_decisiontree_prob(self.diseaseprev_sampled,
                                                                                   pm_evaluation)

            for i, (DALY_Death, mainpm_prediction, obs) in enumerate(
                    zip(DALY_individual_Moldova, mainpm_pred_data['predicted'], mainpm_pred_data['observed'])):

                optimal_treat = self.optimal_treat_pmdt_sample(i, mainpm_prediction, threshold, self.wtp, decisiontree_prob_df)

                FLQ_status = 'FLQ Resistant' if obs == 1 else 'FLQ Susceptible'
                treatment_result = self._prepare_treatment_result(i,threshold, mainpm_prediction, FLQ_status, 'PMDT', optimal_treat,
                                                                      preliminary_daly_costs, self.wtp)

                NMB_DALY_Cost_SdTreat_PMDT_eachpt.append(treatment_result)

            elapsed_time_t = time.time() - start_time_t
            print(f"Threshold {threshold} done in {elapsed_time_t/60:.2f} minutes.")

        elapsed_time = time.time() - start_time
        print(f"Total running time: {elapsed_time/60:.2f} minutes.")

        return pd.DataFrame(NMB_DALY_Cost_SdTreat_PMDT_eachpt)

    def dr_tb_dt_s(self, preliminary_daly_costs, DALY_individual_Moldova):
        start_time = time.time()
        NMB_DALY_Cost_SdTreat_DT_eachpt = []  # Results container

        for i, (DALY_Death, pred, obs) in enumerate(
                zip(DALY_individual_Moldova, self.mainpm_pred_data['predicted'], self.mainpm_pred_data['observed'])):

            optimal_treat = self.optimal_treat_dt_sample(i, self.wtp, pred, DALY_individual_Moldova,
                                                         cost_sampled_par, dalyweight_sampled_par,
                                                         dalylength_sampled_par, par_samplesize)

            FLQ_status = 'FLQ Resistant' if obs == 1 else 'FLQ Susceptible'
            treatment_result = self._prepare_treatment_result(i, 'None', 'None', FLQ_status, 'DT', optimal_treat,
                                                              preliminary_daly_costs, self.wtp)

            NMB_DALY_Cost_SdTreat_DT_eachpt.append(treatment_result)

        elapsed_time = time.time() - start_time
        print(f"Total running time: {elapsed_time/60:.2f} minutes.")

        return pd.DataFrame(NMB_DALY_Cost_SdTreat_DT_eachpt)

    def _prepare_treatment_result(self, person_id, threshold, pred, FLQ_status, treatment_type, optimal_treat, preliminary_daly_costs, wtp):
        if optimal_treat['Opt_Treat'] == 'DLM':
            NMB_SdTreat_PMDT = preliminary_daly_costs.SdTreat_NMB[person_id] - preliminary_daly_costs.DLM_NMB[person_id]
            NMB_DM = preliminary_daly_costs.DLM_NMB[person_id]
            DALY_SdTreat_DM = preliminary_daly_costs.SdTreat_DALY[person_id] - preliminary_daly_costs.Exp_DLM_DALY[person_id]
            DALY_DM = preliminary_daly_costs.Exp_DLM_DALY[person_id]
            Cost_SdTreat_DM = preliminary_daly_costs.SdTreat_cost[person_id] - preliminary_daly_costs.Exp_DLM_cost[person_id]
            Cost_DM = preliminary_daly_costs.Exp_DLM_cost[person_id]
        else:
            NMB_SdTreat_PMDT = preliminary_daly_costs.SdTreat_NMB[person_id] - preliminary_daly_costs.FLQ_NMB[person_id]
            NMB_DM = preliminary_daly_costs.FLQ_NMB[person_id]
            DALY_SdTreat_DM = preliminary_daly_costs.SdTreat_DALY[person_id] - preliminary_daly_costs.Exp_FLQ_DALY[
                person_id]
            DALY_DM = preliminary_daly_costs.Exp_FLQ_DALY[person_id]
            Cost_SdTreat_DM = preliminary_daly_costs.SdTreat_cost[person_id] - preliminary_daly_costs.Exp_FLQ_cost[person_id]
            Cost_DM = preliminary_daly_costs.Exp_FLQ_cost[person_id]
        if pred == 'None':
            PM_classification = "None"
            PM_prediction = "None"
        else:
            PM_prediction = pred
            if pred > threshold:
                PM_classification = 'FLQ Resistant'
            else:
                PM_classification = 'FLQ Susceptible'
        return {
            'Person': person_id,
            'Threshold': threshold,
            'PM_prediction': PM_prediction,
            'PM_classification': PM_classification,
            'FLQ_Status': FLQ_status,
            'Treatment_Type': treatment_type,
            'Opt_Treat': optimal_treat['Opt_Treat'],
            'DALY_DLM': optimal_treat['DLM_expected_DALY_sample_avg'],
            'Cost_DLM': optimal_treat['DLM_expected_cost_sample_avg'],
            'DALY_FLQ': optimal_treat['FLQ_expected_DALY_sample_avg'],
            'Cost_FLQ': optimal_treat['FLQ_expected_cost_sample_avg'],
            'NMB_SdTreat_DM': NMB_SdTreat_PMDT,
            'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[person_id],
            'NMB_SdTreat_FLQ': wtp * preliminary_daly_costs.Exp_FLQ_SdTreat_DALY[person_id] + preliminary_daly_costs.Exp_FLQ_SdTreat_cost[person_id],
            'NMB_DM': NMB_DM,
            'NMB_DLM': optimal_treat['DLM_LNMB'],
            'NMB_FLQ': optimal_treat['FLQ_LNMB'],
            'DALY_SdTreat_DM':DALY_SdTreat_DM,
            'DALY_SdTreat': preliminary_daly_costs.SdTreat_DALY[person_id],
            'DALY_DM': DALY_DM,
            'Cost_SdTreat_DM': Cost_SdTreat_DM,
            'Cost_SdTreat': preliminary_daly_costs.SdTreat_cost[person_id],
            'Cost_DM': Cost_DM
        }


if __name__ == '__main__':

    np.random.seed(5)

    # WTP
    wtp_value = 1 * GDP_moldova

    i = 1

    par_samplesize = 500
    par_sampler = ParameterSampler(FLQ_Res_prev, cost_data_prior, dalyweight_data, dalylength_data,
                                   nsamples=par_samplesize)
    pm_performance = PMPerformance(booststrap_pred_data, par_sampler)

    # Sampling from the prior costs
    cost_sampled_par = par_sampler.sample_cost_parameters()
    # Sampling from the prior daly weights
    dalyweight_sampled_par = par_sampler.sample_dalyweight_parameters()
    # Sampling from the prior daly length
    dalylength_sampled_par = par_sampler.sample_dalylength_parameters()
    # Sampling from the prior disease prevalence
    diseaseprev_sampled_par = par_sampler.sample_disease_prevalence()

    # Generate the sequence from 0 to 1 with a step of 0.0025
    threshold_values = np.arange(0, 1.00, 0.25)

    # Create the DataFrame
    allthresholds = pd.DataFrame({'threshold': threshold_values})


    drtb_instance = DRTuberculosisDT(par_sampler, DALY_individual_Moldova, pm_performance, mainpm_pred_data,
                                     diseaseprev_sampled_par, prob_data, cost_sampled_par, dalyweight_sampled_par,
                                     dalylength_sampled_par, par_samplesize, wtp_value)

    ############ Preliminary Costs and DALY Calculation ############
    # Calculated expected costs and DALYs for each treatment depending on FLQ susceptibility
    preliminary_daly_costs = calculate_pre_daly_cost_s(par_sampler, mainpm_pred_data, DALY_individual_Moldova,
                                                       diseaseprev_sampled_par, prob_data, cost_sampled_par,
                                                       dalyweight_sampled_par, dalylength_sampled_par,
                                                       wtp_value, par_samplesize)

    ############ End Preliminary Costs and ############

    PMDT_sampled = drtb_instance.dr_tb_pmdt_s(allthresholds, DALY_individual_Moldova, preliminary_daly_costs)

    print(PMDT_sampled)

    print("Column names individually:")
    for col in PMDT_sampled.columns:
        print(col)

    # # Export test file
    # file_path_PMDT_sampled = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Tests/Test PM bootstraping/' + f'test_output.xlsx'
    # # Save the DataFrame to an Excel file
    # PMDT_sampled.to_excel(
    #     file_path_PMDT_sampled,
    #     index=False)
