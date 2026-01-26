import time
import csv
import math
from Preliminary_DALY_Class import *
from PM_Performance_class import *


class DRTuberculosisDT:
    def __init__(self, par_sampler, DALY_individual_Moldova, pm_performance, pred_data, diseaseprev_sampled,
                 prob_sampled_par, cost_sampled_par, dalyweight_sampled_par, dalylength_sampled_par, sideeffectdaly_sampled_par, sideeffectfreq_sampled_par, sideeffectlength_sampled_par, par_samplesize, wtp):
        self.par_sampler = par_sampler
        self.DALY_individual_Moldova = DALY_individual_Moldova
        self.pm_performance = pm_performance
        self.pred_data = pred_data
        self.diseaseprev_sampled = diseaseprev_sampled
        self.prob_sampled_par = prob_sampled_par
        self.cost_sampled_par = cost_sampled_par
        self.dalyweight_sampled_par = dalyweight_sampled_par
        self.dalylength_sampled_par = dalylength_sampled_par
        self.sideeffectdaly_sampled_par = sideeffectdaly_sampled_par
        self.sideeffectfreq_sampled_par = sideeffectfreq_sampled_par
        self.sideeffectlength_sampled_par = sideeffectlength_sampled_par
        self.par_samplesize = par_samplesize
        self.wtp = wtp

    def calculate_sample_averages(self, dataframe, excluded_cols, index_cols):
        include_columns = [col for col in dataframe.columns if col not in excluded_cols and col not in index_cols]
        sample_avg = dataframe.groupby(index_cols)[include_columns].mean().reset_index()
        FLQstatus_Class = dataframe.groupby(index_cols)[excluded_cols].first().reset_index()
        final_sample_avg = pd.merge(sample_avg, FLQstatus_Class, on=index_cols)
        return final_sample_avg

    def optimal_treat_pmdt_sample(self, pt, prediction, t, wtp, decisiontree_prob_df):

        FLQres_expected_cost_sample = []
        FLQres_expected_DALY_sample = []
        FLQsus_expected_cost_sample = []
        FLQsus_expected_DALY_sample = []
        FLQ_expected_cost_sample = []
        FLQ_expected_DALY_sample = []
        DLM_expected_cost_sample = []
        DLM_expected_DALY_sample = []

        for j in range(1, self.par_samplesize + 1):

            decisiontree_prob = self.pm_performance.evaluate_pm_sample_dic(decisiontree_prob_df, data='None', j=j)

            prob_cost_daly_sampled = self.par_sampler.prob_cost_daly_input_table(self.prob_sampled_par,
                                                                                 self.cost_sampled_par,
                                                                                 self.dalyweight_sampled_par,
                                                                                 self.dalylength_sampled_par,
                                                                                 self.sideeffectdaly_sampled_par,
                                                                                 self.sideeffectfreq_sampled_par,
                                                                                 self.sideeffectlength_sampled_par,j)
            DALY_Death = self.DALY_individual_Moldova[pt]

            # Terminal Nodes
            Cure_FLQsus = TerminalNode(name='Cure_FLQsus', cost=prob_cost_daly_sampled['Cost_Cure_FLQsus'],
                                       daly=prob_cost_daly_sampled['DALY_Cure_FLQsus'])
            Recurrence_FLQsus = TerminalNode(name='Recurrence_FLQsus',
                                             cost=prob_cost_daly_sampled['Cost_Recurrence_FLQsus'],
                                             daly=prob_cost_daly_sampled['DALY_Recurrence_FLQsus']+ prob_cost_daly_sampled['DALY_DLM'])
            TF_FLQsus = TerminalNode(name='TF_FLQsus', cost=prob_cost_daly_sampled['Cost_TF_FLQsus'],
                                     daly=prob_cost_daly_sampled['DALY_TF_FLQsus']+ prob_cost_daly_sampled['DALY_DLM'])
            Cure_FLQres = TerminalNode(name='Cure_FLQres', cost=prob_cost_daly_sampled['Cost_Cure_FLQres'],
                                       daly=prob_cost_daly_sampled['DALY_Cure_FLQres'])
            Recurrence_FLQres = TerminalNode(name='Recurrence_FLQres',
                                             cost=prob_cost_daly_sampled['Cost_Recurrence_FLQres'],
                                             daly=prob_cost_daly_sampled['DALY_Recurrence_FLQres']+ prob_cost_daly_sampled['DALY_DLM'])
            TF_FLQres = TerminalNode(name='TF_FLQres', cost=prob_cost_daly_sampled['Cost_TF_FLQres'],
                                     daly=prob_cost_daly_sampled['DALY_TF_FLQres']+ prob_cost_daly_sampled['DALY_DLM'])
            Cure_DLM = TerminalNode(name='Cure_DLM', cost=prob_cost_daly_sampled['Cost_Cure_DLM'],
                                    daly=prob_cost_daly_sampled['DALY_Cure_DLM'])
            Recurrence_DLM = TerminalNode(name='Recurrence_DLM',
                                          cost=prob_cost_daly_sampled['Cost_Recurrence_DLM'],
                                          daly=prob_cost_daly_sampled['DALY_Recurrence_DLM']+ prob_cost_daly_sampled['DALY_DLM'])
            TF_DLM = TerminalNode(name='TF_DLM', cost=prob_cost_daly_sampled['Cost_TF_DLM'],
                                  daly=prob_cost_daly_sampled['DALY_TF_DLM']+ prob_cost_daly_sampled['DALY_DLM'])

            DEATH_FLQsus = TerminalNode(name='D_FLQsus', cost=prob_cost_daly_sampled['Cost_D_FLQsus'], daly=DALY_Death)
            DEATH_FLQres = TerminalNode(name='D_FLQres', cost=prob_cost_daly_sampled['Cost_D_FLQres'], daly=DALY_Death)
            DEATH_DLM = TerminalNode(name='D_DLM', cost=prob_cost_daly_sampled['Cost_D_DLM'], daly=DALY_Death)

            # Chance Nodes
            CC_FLQsus = ChanceNode(name='CC_FLQsus', cost=0,
                                     daly=0,
                                   future_nodes=[Cure_FLQsus, Recurrence_FLQsus],
                                   probs=[prob_cost_daly_sampled['ProbCure_CCFLQsus'],
                                          prob_cost_daly_sampled['ProbRecurrence_CCFLQsus']])

            CC_FLQres = ChanceNode(name='CC_FLQres', cost=0,
                                     daly=0,
                                   future_nodes=[Cure_FLQres, Recurrence_FLQres],
                                   probs=[prob_cost_daly_sampled['ProbCure_CCFLQres'],
                                          prob_cost_daly_sampled['ProbRecurrence_CCFLQres']])

            CC_DLM = ChanceNode(name='CC_DLM', cost=0,
                                  daly=0,
                                   future_nodes=[Cure_DLM, Recurrence_DLM],
                                   probs=[prob_cost_daly_sampled['ProbCure_CCDLM'],
                                          prob_cost_daly_sampled['ProbRecurrence_CCDLM']])

            C_FLQsus = ChanceNode(name='C_FLQsus', cost=0,
                                  future_nodes=[CC_FLQsus, TF_FLQsus, DEATH_FLQsus],
                                  probs=[prob_cost_daly_sampled['ProbCC_FLQsus'],
                                         prob_cost_daly_sampled['ProbTF_FLQsus'],
                                         prob_cost_daly_sampled['ProbD_FLQsus']],
                                  daly=prob_cost_daly_sampled['DALY_FLQ'])

            C_FLQres = ChanceNode(name='C_FLQres', cost=0,
                                  future_nodes=[CC_FLQres, TF_FLQres, DEATH_FLQres],
                                  probs=[prob_cost_daly_sampled['ProbCC_FLQres'],
                                         prob_cost_daly_sampled['ProbTF_FLQres'],
                                         prob_cost_daly_sampled['ProbD_FLQres']],
                                  daly=prob_cost_daly_sampled['DALY_FLQ'])

            C_DLM = ChanceNode(name='C_DLM', cost=prob_cost_daly_sampled['Cost_DLM'],
                               future_nodes=[CC_DLM, TF_DLM, DEATH_DLM],
                               probs=[prob_cost_daly_sampled['ProbCC_DLM'],
                                      prob_cost_daly_sampled['ProbTF_DLM'],
                                      prob_cost_daly_sampled['ProbD_DLM']], daly=prob_cost_daly_sampled['DALY_DLM'])

            # Decision Node
            if prediction > t:
                C_FLQ = ChanceNode(name='C_FLQ', cost=prob_cost_daly_sampled['Cost_FLQ'], daly=0,
                                   future_nodes=[C_FLQsus, C_FLQres],
                                   probs=[decisiontree_prob['P_S_R'], decisiontree_prob['P_R_R']])
            else:
                C_FLQ = ChanceNode(name='C_FLQ', cost=prob_cost_daly_sampled['Cost_FLQ'], daly=0,
                                   future_nodes=[C_FLQsus, C_FLQres],
                                   probs=[decisiontree_prob['P_S_S'], decisiontree_prob['P_R_S']])

            D = DecisionNode(name='D', cost=0, daly=0, future_nodes=[C_FLQ, C_DLM])

            FLQres_expected_cost_sample.append(C_FLQres.get_expected_cost())
            FLQres_expected_DALY_sample.append(C_FLQres.get_expected_daly())
            FLQsus_expected_cost_sample.append(C_FLQsus.get_expected_cost())
            FLQsus_expected_DALY_sample.append(C_FLQsus.get_expected_daly())
            FLQ_expected_cost_sample.append(D.get_expected_cost()['C_FLQ'])
            FLQ_expected_DALY_sample.append(D.get_expected_daly()['C_FLQ'])
            DLM_expected_cost_sample.append(D.get_expected_cost()['C_DLM'])
            DLM_expected_DALY_sample.append(D.get_expected_daly()['C_DLM'])

        FLQres_expected_cost_avg = statistics.mean(FLQres_expected_cost_sample)
        FLQres_expected_DALY_avg = statistics.mean(FLQres_expected_DALY_sample)
        FLQsus_expected_cost_avg = statistics.mean(FLQsus_expected_cost_sample)
        FLQsus_expected_DALY_avg = statistics.mean(FLQsus_expected_DALY_sample)
        FLQ_expected_cost_avg = statistics.mean(FLQ_expected_cost_sample)
        FLQ_expected_DALY_avg = statistics.mean(FLQ_expected_DALY_sample)
        DLM_expected_cost_avg = statistics.mean(DLM_expected_cost_sample)
        DLM_expected_DALY_avg = statistics.mean(DLM_expected_DALY_sample)

        FLQ_LNMB = wtp * FLQ_expected_DALY_avg + FLQ_expected_cost_avg
        DLM_LNMB = wtp * DLM_expected_DALY_avg + DLM_expected_cost_avg

        if FLQ_LNMB > DLM_LNMB:
            Opt_Treat = 'DLM'
        elif FLQ_LNMB <= DLM_LNMB:
            Opt_Treat = 'FLQ'
        else:
            Opt_Treat = float('nan')

        return {
            'Opt_Treat': Opt_Treat,
            'FLQres_expected_cost_sample_avg': FLQres_expected_cost_avg,
            'FLQres_expected_DALY_sample_avg': FLQres_expected_DALY_avg,
            'FLQsus_expected_cost_sample_avg': FLQsus_expected_cost_avg,
            'FLQsus_expected_DALY_sample_avg': FLQsus_expected_DALY_avg,
            'FLQ_expected_cost_sample_avg': FLQ_expected_cost_avg,
            'FLQ_expected_DALY_sample_avg': FLQ_expected_DALY_avg,
            'DLM_expected_cost_sample_avg': DLM_expected_cost_avg,
            'DLM_expected_DALY_sample_avg': DLM_expected_DALY_avg,
            'FLQ_LNMB': FLQ_LNMB,
            'DLM_LNMB': DLM_LNMB
        }

    def optimal_treat_pmdt_predonly(self, pt, prediction, wtp):

        FLQres_expected_cost_sample = []
        FLQres_expected_DALY_sample = []
        FLQsus_expected_cost_sample = []
        FLQsus_expected_DALY_sample = []
        FLQ_expected_cost_sample = []
        FLQ_expected_DALY_sample = []
        DLM_expected_cost_sample = []
        DLM_expected_DALY_sample = []

        for j in range(1, self.par_samplesize + 1):

            prob_cost_daly_sampled = self.par_sampler.prob_cost_daly_input_table(self.prob_sampled_par,
                                                                                 self.cost_sampled_par,
                                                                                 self.dalyweight_sampled_par,
                                                                                 self.dalylength_sampled_par,
                                                                                 self.sideeffectdaly_sampled_par,
                                                                                 self.sideeffectfreq_sampled_par,
                                                                                 self.sideeffectlength_sampled_par,j)
            DALY_Death = self.DALY_individual_Moldova[pt]

            # Terminal Nodes
            Cure_FLQsus = TerminalNode(name='Cure_FLQsus', cost=prob_cost_daly_sampled['Cost_Cure_FLQsus'],
                                       daly=prob_cost_daly_sampled['DALY_Cure_FLQsus'])
            Recurrence_FLQsus = TerminalNode(name='Recurrence_FLQsus',
                                             cost=prob_cost_daly_sampled['Cost_Recurrence_FLQsus'],
                                             daly=prob_cost_daly_sampled['DALY_Recurrence_FLQsus']+ prob_cost_daly_sampled['DALY_DLM'])
            TF_FLQsus = TerminalNode(name='TF_FLQsus', cost=prob_cost_daly_sampled['Cost_TF_FLQsus'],
                                     daly=prob_cost_daly_sampled['DALY_TF_FLQsus']+ prob_cost_daly_sampled['DALY_DLM'])
            Cure_FLQres = TerminalNode(name='Cure_FLQres', cost=prob_cost_daly_sampled['Cost_Cure_FLQres'],
                                       daly=prob_cost_daly_sampled['DALY_Cure_FLQres'])
            Recurrence_FLQres = TerminalNode(name='Recurrence_FLQres',
                                             cost=prob_cost_daly_sampled['Cost_Recurrence_FLQres'],
                                             daly=prob_cost_daly_sampled['DALY_Recurrence_FLQres']+ prob_cost_daly_sampled['DALY_DLM'])
            TF_FLQres = TerminalNode(name='TF_FLQres', cost=prob_cost_daly_sampled['Cost_TF_FLQres'],
                                     daly=prob_cost_daly_sampled['DALY_TF_FLQres']+ prob_cost_daly_sampled['DALY_DLM'])
            Cure_DLM = TerminalNode(name='Cure_DLM', cost=prob_cost_daly_sampled['Cost_Cure_DLM'],
                                    daly=prob_cost_daly_sampled['DALY_Cure_DLM'])
            Recurrence_DLM = TerminalNode(name='Recurrence_DLM',
                                          cost=prob_cost_daly_sampled['Cost_Recurrence_DLM'],
                                          daly=prob_cost_daly_sampled['DALY_Recurrence_DLM']+ prob_cost_daly_sampled['DALY_DLM'])
            TF_DLM = TerminalNode(name='TF_DLM', cost=prob_cost_daly_sampled['Cost_TF_DLM'],
                                  daly=prob_cost_daly_sampled['DALY_TF_DLM']+ prob_cost_daly_sampled['DALY_DLM'])

            DEATH_FLQsus = TerminalNode(name='D_FLQsus', cost=prob_cost_daly_sampled['Cost_D_FLQsus'], daly=DALY_Death)
            DEATH_FLQres = TerminalNode(name='D_FLQres', cost=prob_cost_daly_sampled['Cost_D_FLQres'], daly=DALY_Death)
            DEATH_DLM = TerminalNode(name='D_DLM', cost=prob_cost_daly_sampled['Cost_D_DLM'], daly=DALY_Death)


            # Chance Nodes
            CC_FLQsus = ChanceNode(name='CC_FLQsus', cost=0,
                                     daly=0,
                                   future_nodes=[Cure_FLQsus, Recurrence_FLQsus],
                                   probs=[prob_cost_daly_sampled['ProbCure_CCFLQsus'],
                                          prob_cost_daly_sampled['ProbRecurrence_CCFLQsus']])

            CC_FLQres = ChanceNode(name='CC_FLQres', cost=0,
                                     daly=0,
                                   future_nodes=[Cure_FLQres, Recurrence_FLQres],
                                   probs=[prob_cost_daly_sampled['ProbCure_CCFLQres'],
                                          prob_cost_daly_sampled['ProbRecurrence_CCFLQres']])

            CC_DLM = ChanceNode(name='CC_DLM', cost=0,
                                  daly=0,
                                   future_nodes=[Cure_DLM, Recurrence_DLM],
                                   probs=[prob_cost_daly_sampled['ProbCure_CCDLM'],
                                          prob_cost_daly_sampled['ProbRecurrence_CCDLM']])

            C_FLQsus = ChanceNode(name='C_FLQsus', cost=0,
                                  future_nodes=[CC_FLQsus, TF_FLQsus, DEATH_FLQsus],
                                  probs=[prob_cost_daly_sampled['ProbCC_FLQsus'],
                                         prob_cost_daly_sampled['ProbTF_FLQsus'],
                                         prob_cost_daly_sampled['ProbD_FLQsus']],
                                  daly=prob_cost_daly_sampled['DALY_FLQ'])

            C_FLQres = ChanceNode(name='C_FLQres', cost=0,
                                  future_nodes=[CC_FLQres, TF_FLQres, DEATH_FLQres],
                                  probs=[prob_cost_daly_sampled['ProbCC_FLQres'],
                                         prob_cost_daly_sampled['ProbTF_FLQres'],
                                         prob_cost_daly_sampled['ProbD_FLQres']],
                                  daly=prob_cost_daly_sampled['DALY_FLQ'])

            C_DLM = ChanceNode(name='C_DLM', cost=prob_cost_daly_sampled['Cost_DLM'],
                               future_nodes=[CC_DLM, TF_DLM, DEATH_DLM],
                               probs=[prob_cost_daly_sampled['ProbCC_DLM'],
                                      prob_cost_daly_sampled['ProbTF_DLM'],
                                      prob_cost_daly_sampled['ProbD_DLM']], daly=prob_cost_daly_sampled['DALY_DLM'])

            # Decision Node
            C_FLQ = ChanceNode(name='C_FLQ', cost=prob_cost_daly_sampled['Cost_FLQ'], daly=0,
                                   future_nodes=[C_FLQsus, C_FLQres],
                                   probs=[1-prediction, prediction])

            D = DecisionNode(name='D', cost=0, daly=0, future_nodes=[C_FLQ, C_DLM])

            FLQres_expected_cost_sample.append(C_FLQres.get_expected_cost())
            FLQres_expected_DALY_sample.append(C_FLQres.get_expected_daly())
            FLQsus_expected_cost_sample.append(C_FLQsus.get_expected_cost())
            FLQsus_expected_DALY_sample.append(C_FLQsus.get_expected_daly())
            FLQ_expected_cost_sample.append(D.get_expected_cost()['C_FLQ'])
            FLQ_expected_DALY_sample.append(D.get_expected_daly()['C_FLQ'])
            DLM_expected_cost_sample.append(D.get_expected_cost()['C_DLM'])
            DLM_expected_DALY_sample.append(D.get_expected_daly()['C_DLM'])

        FLQres_expected_cost_avg = statistics.mean(FLQres_expected_cost_sample)
        FLQres_expected_DALY_avg = statistics.mean(FLQres_expected_DALY_sample)
        FLQsus_expected_cost_avg = statistics.mean(FLQsus_expected_cost_sample)
        FLQsus_expected_DALY_avg = statistics.mean(FLQsus_expected_DALY_sample)
        FLQ_expected_cost_avg = statistics.mean(FLQ_expected_cost_sample)
        FLQ_expected_DALY_avg = statistics.mean(FLQ_expected_DALY_sample)
        DLM_expected_cost_avg = statistics.mean(DLM_expected_cost_sample)
        DLM_expected_DALY_avg = statistics.mean(DLM_expected_DALY_sample)

        FLQ_LNMB = wtp * FLQ_expected_DALY_avg + FLQ_expected_cost_avg
        DLM_LNMB = wtp * DLM_expected_DALY_avg + DLM_expected_cost_avg

        if FLQ_LNMB > DLM_LNMB:
            Opt_Treat = 'DLM'
        elif FLQ_LNMB <= DLM_LNMB:
            Opt_Treat = 'FLQ'
        else:
            Opt_Treat = float('nan')

        return {
            'Opt_Treat': Opt_Treat,
            'FLQres_expected_cost_sample_avg': FLQres_expected_cost_avg,
            'FLQres_expected_DALY_sample_avg': FLQres_expected_DALY_avg,
            'FLQsus_expected_cost_sample_avg': FLQsus_expected_cost_avg,
            'FLQsus_expected_DALY_sample_avg': FLQsus_expected_DALY_avg,
            'FLQ_expected_cost_sample_avg': FLQ_expected_cost_avg,
            'FLQ_expected_DALY_sample_avg': FLQ_expected_DALY_avg,
            'DLM_expected_cost_sample_avg': DLM_expected_cost_avg,
            'DLM_expected_DALY_sample_avg': DLM_expected_DALY_avg,
            'FLQ_LNMB': FLQ_LNMB,
            'DLM_LNMB': DLM_LNMB
        }

    def optimal_treat_pm(self, pt, prediction, t):

        if prediction > t:
            Opt_Treat = 'DLM'
        elif prediction <= t:
            Opt_Treat = 'FLQ'
        else:
            Opt_Treat = float('nan')

        return {
            'Opt_Treat': Opt_Treat,
            'FLQres_expected_cost_sample_avg': float('nan'),
            'FLQres_expected_DALY_sample_avg': float('nan'),
            'FLQsus_expected_cost_sample_avg': float('nan'),
            'FLQsus_expected_DALY_sample_avg': float('nan'),
            'FLQ_expected_cost_sample_avg': float('nan'),
            'FLQ_expected_DALY_sample_avg': float('nan'),
            'DLM_expected_cost_sample_avg': float('nan'),
            'DLM_expected_DALY_sample_avg': float('nan'),
            'FLQ_LNMB': float('nan'),
            'DLM_LNMB': float('nan')
        }

    def optimal_treat_dt_sample(self, pt, wtp):

        FLQres_expected_cost_sample = []
        FLQres_expected_DALY_sample = []
        FLQsus_expected_cost_sample = []
        FLQsus_expected_DALY_sample = []
        FLQ_expected_cost_sample = []
        FLQ_expected_DALY_sample = []
        DLM_expected_cost_sample = []
        DLM_expected_DALY_sample = []

        for j in range(1, self.par_samplesize + 1):
            prob_cost_daly_sampled = self.par_sampler.prob_cost_daly_input_table(self.prob_sampled_par,
                                                                                 self.cost_sampled_par,
                                                                                 self.dalyweight_sampled_par,
                                                                                 self.dalylength_sampled_par,
                                                                                 self.sideeffectdaly_sampled_par,
                                                                                 self.sideeffectfreq_sampled_par,
                                                                                 self.sideeffectlength_sampled_par,j)
            diseaseprev_sampled_input = self.par_sampler.diseaseprev_input(self.diseaseprev_sampled, j)
            DALY_Death = self.DALY_individual_Moldova[pt]


            # Terminal Nodes
            Cure_FLQsus = TerminalNode(name='Cure_FLQsus', cost=prob_cost_daly_sampled['Cost_Cure_FLQsus'],
                                       daly=prob_cost_daly_sampled['DALY_Cure_FLQsus'])
            Recurrence_FLQsus = TerminalNode(name='Recurrence_FLQsus',
                                             cost=prob_cost_daly_sampled['Cost_Recurrence_FLQsus'],
                                             daly=prob_cost_daly_sampled['DALY_Recurrence_FLQsus']+ prob_cost_daly_sampled['DALY_DLM'])
            TF_FLQsus = TerminalNode(name='TF_FLQsus', cost=prob_cost_daly_sampled['Cost_TF_FLQsus'],
                                     daly=prob_cost_daly_sampled['DALY_TF_FLQsus']+ prob_cost_daly_sampled['DALY_DLM'])
            Cure_FLQres = TerminalNode(name='Cure_FLQres', cost=prob_cost_daly_sampled['Cost_Cure_FLQres'],
                                       daly=prob_cost_daly_sampled['DALY_Cure_FLQres'])
            Recurrence_FLQres = TerminalNode(name='Recurrence_FLQres',
                                             cost=prob_cost_daly_sampled['Cost_Recurrence_FLQres'],
                                             daly=prob_cost_daly_sampled['DALY_Recurrence_FLQres']+ prob_cost_daly_sampled['DALY_DLM'])
            TF_FLQres = TerminalNode(name='TF_FLQres', cost=prob_cost_daly_sampled['Cost_TF_FLQres'],
                                     daly=prob_cost_daly_sampled['DALY_TF_FLQres']+ prob_cost_daly_sampled['DALY_DLM'])
            Cure_DLM = TerminalNode(name='Cure_DLM', cost=prob_cost_daly_sampled['Cost_Cure_DLM'],
                                    daly=prob_cost_daly_sampled['DALY_Cure_DLM'])
            Recurrence_DLM = TerminalNode(name='Recurrence_DLM',
                                          cost=prob_cost_daly_sampled['Cost_Recurrence_DLM'],
                                          daly=prob_cost_daly_sampled['DALY_Recurrence_DLM']+ prob_cost_daly_sampled['DALY_DLM'])
            TF_DLM = TerminalNode(name='TF_DLM', cost=prob_cost_daly_sampled['Cost_TF_DLM'],
                                  daly=prob_cost_daly_sampled['DALY_TF_DLM']+ prob_cost_daly_sampled['DALY_DLM'])

            DEATH_FLQsus = TerminalNode(name='D_FLQsus', cost=prob_cost_daly_sampled['Cost_D_FLQsus'], daly=DALY_Death)
            DEATH_FLQres = TerminalNode(name='D_FLQres', cost=prob_cost_daly_sampled['Cost_D_FLQres'], daly=DALY_Death)
            DEATH_DLM = TerminalNode(name='D_DLM', cost=prob_cost_daly_sampled['Cost_D_DLM'], daly=DALY_Death)

            # Chance Nodes
            CC_FLQsus = ChanceNode(name='CC_FLQsus', cost=0,
                                   daly=0,
                                   future_nodes=[Cure_FLQsus, Recurrence_FLQsus],
                                   probs=[prob_cost_daly_sampled['ProbCure_CCFLQsus'],
                                          prob_cost_daly_sampled['ProbRecurrence_CCFLQsus']])

            CC_FLQres = ChanceNode(name='CC_FLQres', cost=0,
                                   daly=0,
                                   future_nodes=[Cure_FLQres, Recurrence_FLQres],
                                   probs=[prob_cost_daly_sampled['ProbCure_CCFLQres'],
                                          prob_cost_daly_sampled['ProbRecurrence_CCFLQres']])

            CC_DLM = ChanceNode(name='CC_DLM', cost=0,
                                daly=0,
                                future_nodes=[Cure_DLM, Recurrence_DLM],
                                probs=[prob_cost_daly_sampled['ProbCure_CCDLM'],
                                       prob_cost_daly_sampled['ProbRecurrence_CCDLM']])

            C_FLQsus = ChanceNode(name='C_FLQsus', cost=0,
                                  future_nodes=[CC_FLQsus, TF_FLQsus, DEATH_FLQsus],
                                  probs=[prob_cost_daly_sampled['ProbCC_FLQsus'],
                                         prob_cost_daly_sampled['ProbTF_FLQsus'],
                                         prob_cost_daly_sampled['ProbD_FLQsus']],
                                  daly=prob_cost_daly_sampled['DALY_FLQ'])

            C_FLQres = ChanceNode(name='C_FLQres', cost=0,
                                  future_nodes=[CC_FLQres, TF_FLQres, DEATH_FLQres],
                                  probs=[prob_cost_daly_sampled['ProbCC_FLQres'],
                                         prob_cost_daly_sampled['ProbTF_FLQres'],
                                         prob_cost_daly_sampled['ProbD_FLQres']],
                                  daly=prob_cost_daly_sampled['DALY_FLQ'])


            C_DLM = ChanceNode(name='C_DLM', cost=prob_cost_daly_sampled['Cost_DLM'],
                               future_nodes=[CC_DLM, TF_DLM, DEATH_DLM],
                               probs=[prob_cost_daly_sampled['ProbCC_DLM'],
                                      prob_cost_daly_sampled['ProbTF_DLM'],
                                      prob_cost_daly_sampled['ProbD_DLM']], daly=prob_cost_daly_sampled['DALY_DLM'])


            # Decision Node
            C_FLQ = ChanceNode(name='C_FLQ', cost=prob_cost_daly_sampled['Cost_FLQ'], daly=0,
                               future_nodes=[C_FLQsus, C_FLQres],
                               probs=[1 - diseaseprev_sampled_input, diseaseprev_sampled_input])

            D = DecisionNode(name='D', cost=0, daly=0, future_nodes=[C_FLQ, C_DLM])

            FLQres_expected_cost_sample.append(C_FLQres.get_expected_cost())
            FLQres_expected_DALY_sample.append(C_FLQres.get_expected_daly())
            FLQsus_expected_cost_sample.append(C_FLQsus.get_expected_cost())
            FLQsus_expected_DALY_sample.append(C_FLQsus.get_expected_daly())
            FLQ_expected_cost_sample.append(D.get_expected_cost()['C_FLQ'])
            FLQ_expected_DALY_sample.append(D.get_expected_daly()['C_FLQ'])
            DLM_expected_cost_sample.append(D.get_expected_cost()['C_DLM'])
            DLM_expected_DALY_sample.append(D.get_expected_daly()['C_DLM'])

        FLQres_expected_cost_avg = statistics.mean(FLQres_expected_cost_sample)
        FLQres_expected_DALY_avg = statistics.mean(FLQres_expected_DALY_sample)
        FLQsus_expected_cost_avg = statistics.mean(FLQsus_expected_cost_sample)
        FLQsus_expected_DALY_avg = statistics.mean(FLQsus_expected_DALY_sample)
        FLQ_expected_cost_avg = statistics.mean(FLQ_expected_cost_sample)
        FLQ_expected_DALY_avg = statistics.mean(FLQ_expected_DALY_sample)
        DLM_expected_cost_avg = statistics.mean(DLM_expected_cost_sample)
        DLM_expected_DALY_avg = statistics.mean(DLM_expected_DALY_sample)

        FLQ_LNMB = wtp * FLQ_expected_DALY_avg + FLQ_expected_cost_avg
        DLM_LNMB = wtp * DLM_expected_DALY_avg + DLM_expected_cost_avg

        Opt_Treat = 'DLM' if FLQ_LNMB > DLM_LNMB else 'FLQ'

        return {
            'Opt_Treat': Opt_Treat,
            'FLQres_expected_cost_sample_avg': FLQres_expected_cost_avg,
            'FLQres_expected_DALY_sample_avg': FLQres_expected_DALY_avg,
            'FLQsus_expected_cost_sample_avg': FLQsus_expected_cost_avg,
            'FLQsus_expected_DALY_sample_avg': FLQsus_expected_DALY_avg,
            'FLQ_expected_cost_sample_avg': FLQ_expected_cost_avg,
            'FLQ_expected_DALY_sample_avg': FLQ_expected_DALY_avg,
            'DLM_expected_cost_sample_avg': DLM_expected_cost_avg,
            'DLM_expected_DALY_sample_avg': DLM_expected_DALY_avg,
            'FLQ_LNMB': FLQ_LNMB,
            'DLM_LNMB': DLM_LNMB
        }

    def dr_tb_pmdt_s_opt(self, allthresholds, DALY_individual_Moldova, preliminary_daly_costs, correction="None",
                         sample_disease_prev="N"):
        start_time = time.time()
        NMB_DALY_Cost_SdTreat_PMDT_eachpt = []  # Results container

        if (correction == "OptCorr_Adj"):
            # Call the function
            df_results_main = self.pm_performance.evaluate_pm_thresholds(allthresholds, "main",
                                                                         bootstrapsample="None")

            # Set the percentage for replacement (e.g., 10%)
            minclass_perc = 0.05

            # Dictionary to store results for each bootstrap sample
            bootstrap_results = {}
            origidata_results = {}

            for i in range(1, self.par_samplesize + 1):
                # Evaluate thresholds for the current bootstrap sample
                df_results_bootstrap = self.pm_performance.evaluate_pm_thresholds(allthresholds, "bootstrap",
                                                                                  bootstrapsample=i)
                df_results_origidata = self.pm_performance.evaluate_pm_thresholds(allthresholds, "origdata",
                                                                                  bootstrapsample=i)
                # Update the DataFrame using the replacement function
                df_results_bootstrap_updated = self.pm_performance.replace_rows_with_min_classes(df_results_bootstrap,
                                                                                                 minclass_perc)
                df_results_origidata_updated = self.pm_performance.replace_rows_with_min_classes(df_results_origidata,
                                                                                                 minclass_perc)

                # Store the updated DataFrame in the dictionary
                bootstrap_results[f'Bootstrap_{i}'] = df_results_bootstrap_updated
                origidata_results[f'Bootstrap_{i}'] = df_results_origidata_updated

            bootstrap_results_bythreshold = self.pm_performance.extract_results_by_threshold(bootstrap_results,
                                                                                             allthresholds)
            origidata_results_bythreshold = self.pm_performance.extract_results_by_threshold(origidata_results,
                                                                                             allthresholds)

        for _, row in allthresholds.iterrows():
            threshold = row['threshold']

            start_time_t = time.time()

            if (correction == "OptCorr"):
                evaluate_pm_df_main = self.pm_performance.evaluate_pm(threshold, 'main')
                evaluate_pm_df_boot = self.pm_performance.evaluate_pm(threshold, 'bootstrap')
                evaluate_pm_df_origdata = self.pm_performance.evaluate_pm(threshold, 'origdata')

                decisiontree_prob_df = self.pm_performance.calculate_decisiontree_prob_optcorr(evaluate_pm_df_main,
                                                                                               evaluate_pm_df_boot,
                                                                                               evaluate_pm_df_origdata)
            elif (correction == "OptCorr_Adj"):

                evaluate_pm_df_main = self.pm_performance.extract_row_and_format(df_results_main, threshold)
                evaluate_pm_df_boot = bootstrap_results_bythreshold[f'Threshold_{threshold}']
                evaluate_pm_df_origdata = origidata_results_bythreshold[f'Threshold_{threshold}']

                decisiontree_prob_df = self.pm_performance.calculate_decisiontree_prob_optcorr(evaluate_pm_df_main,
                                                                                               evaluate_pm_df_boot,
                                                                                               evaluate_pm_df_origdata)

            elif (correction == "OptCorr_Beta"):
                evaluate_pm_df_main = self.pm_performance.evaluate_pm(threshold, 'main')
                evaluate_pm_df_boot = self.pm_performance.evaluate_pm(threshold, 'bootstrap')
                evaluate_pm_df_origdata = self.pm_performance.evaluate_pm(threshold, 'origdata')

                decisiontree_prob_df = self.pm_performance.calculate_decisiontree_prob_optcorr_beta(evaluate_pm_df_main,
                                                                                                    evaluate_pm_df_boot,
                                                                                                    evaluate_pm_df_origdata)

            elif (correction == "Method632"):

                evaluate_pm_df_main = self.pm_performance.evaluate_pm(threshold, 'main')
                evaluate_pm_df_oob = self.pm_performance.evaluate_pm(threshold, 'oob_sample')

                # Check if either is None, if so, skip to the next iteration
                if evaluate_pm_df_main is None or evaluate_pm_df_oob is None:
                    continue

                decisiontree_prob_df = self.pm_performance.calculate_decisiontree_prob_632(self.diseaseprev_sampled,
                                                                                           evaluate_pm_df_main,
                                                                                           evaluate_pm_df_oob,
                                                                                           sample_disease_prev)

            elif (correction == "None"):
                pm_evaluation = self.pm_performance.evaluate_pm(threshold, "bootstrap")
                decisiontree_prob_df = self.pm_performance.calculate_decisiontree_prob(self.diseaseprev_sampled,
                                                                                       pm_evaluation,
                                                                                       sample_disease_prev)

            else:
                print('Invalid method specified.\nPlease choose from: None, OptCorr or Method632')

            for i, (DALY_Death, mainpm_prediction, obs) in enumerate(
                    zip(DALY_individual_Moldova, self.pred_data['predicted'], self.pred_data['observed'])):
                optimal_treat = self.optimal_treat_pmdt_sample(i, mainpm_prediction, threshold, self.wtp,
                                                               decisiontree_prob_df)

                FLQ_status = 'FLQ Resistant' if obs == 1 else 'FLQ Susceptible'
                treatment_result = self._prepare_treatment_result(i, threshold, mainpm_prediction, FLQ_status, 'PMDT',
                                                                  optimal_treat,
                                                                  preliminary_daly_costs, self.wtp)

                NMB_DALY_Cost_SdTreat_PMDT_eachpt.append(treatment_result)

            elapsed_time_t = time.time() - start_time_t
            print(f"Threshold {threshold} done in {elapsed_time_t / 60:.2f} minutes.")

        elapsed_time = time.time() - start_time
        print(f"Total running time: {elapsed_time / 60:.2f} minutes.")

        return pd.DataFrame(NMB_DALY_Cost_SdTreat_PMDT_eachpt)

    def dr_tb_pmdt_s(self, allthresholds, DALY_individual_Moldova, preliminary_daly_costs, sample_disease_prev = "N"):
        start_time = time.time()
        NMB_DALY_Cost_SdTreat_PMDT_eachpt = []  # Results container

        for _, row in allthresholds.iterrows():
            threshold = row['threshold']

            start_time_t = time.time()

            pm_evaluation = self.pm_performance.evaluate_pm(threshold, "bootstrap")
            decisiontree_prob_df = self.pm_performance.calculate_decisiontree_prob(self.diseaseprev_sampled,
                                                                                   pm_evaluation,
                                                                                   sample_disease_prev)

            for i, (DALY_Death, mainpm_prediction, obs) in enumerate(
                    zip(DALY_individual_Moldova, self.pred_data['predicted'], self.pred_data['observed'])):
                optimal_treat = self.optimal_treat_pmdt_sample(i, mainpm_prediction, threshold, self.wtp,
                                                               decisiontree_prob_df)

                FLQ_status = 'FLQ Resistant' if obs == 1 else 'FLQ Susceptible'
                treatment_result = self._prepare_treatment_result(i, threshold, mainpm_prediction, FLQ_status, 'PMDT',
                                                                  optimal_treat,
                                                                  preliminary_daly_costs, self.wtp)

                NMB_DALY_Cost_SdTreat_PMDT_eachpt.append(treatment_result)

            elapsed_time_t = time.time() - start_time_t
            print(f"Threshold {threshold} done in {elapsed_time_t / 60:.2f} minutes.")

        elapsed_time = time.time() - start_time
        print(f"Total running time: {elapsed_time / 60:.2f} minutes.")

        return pd.DataFrame(NMB_DALY_Cost_SdTreat_PMDT_eachpt)

    def dr_tb_pmdt_predonly(self,DALY_individual_Moldova, preliminary_daly_costs):
        start_time = time.time()
        NMB_DALY_Cost_SdTreat_PMDT_eachpt = []  # Results container

        threshold = 'None'

        start_time_t = time.time()

        for i, (DALY_Death, mainpm_prediction, obs) in enumerate(
                zip(DALY_individual_Moldova, self.pred_data['predicted'], self.pred_data['observed'])):
            optimal_treat = self.optimal_treat_pmdt_predonly(i, mainpm_prediction, self.wtp)

            FLQ_status = 'FLQ Resistant' if obs == 1 else 'FLQ Susceptible'
            treatment_result = self._prepare_treatment_result(i, threshold, mainpm_prediction, FLQ_status, 'PMDT',
                                                              optimal_treat,
                                                              preliminary_daly_costs, self.wtp)

            NMB_DALY_Cost_SdTreat_PMDT_eachpt.append(treatment_result)

        elapsed_time = time.time() - start_time
        print(f"Total running time: {elapsed_time / 60:.2f} minutes.")

        return pd.DataFrame(NMB_DALY_Cost_SdTreat_PMDT_eachpt)

    def dr_tb_pm_s(self, allthresholds, DALY_individual_Moldova, preliminary_daly_costs):
        start_time = time.time()
        NMB_DALY_Cost_SdTreat_PMDT_eachpt = []  # Results container

        for _, row in allthresholds.iterrows():
            threshold = row['threshold']

            start_time_t = time.time()

            pm_evaluation = self.pm_performance.evaluate_pm(threshold, "bootstrap")


            for i, (DALY_Death, mainpm_prediction, obs) in enumerate(
                    zip(DALY_individual_Moldova, self.pred_data['predicted'], self.pred_data['observed'])):
                optimal_treat = self.optimal_treat_pm(i, mainpm_prediction, threshold)

                FLQ_status = 'FLQ Resistant' if obs == 1 else 'FLQ Susceptible'
                treatment_result = self._prepare_treatment_result(i, threshold, mainpm_prediction, FLQ_status, 'PM',
                                                                  optimal_treat,
                                                                  preliminary_daly_costs, self.wtp)

                NMB_DALY_Cost_SdTreat_PMDT_eachpt.append(treatment_result)

            elapsed_time_t = time.time() - start_time_t
            print(f"Threshold {threshold} done in {elapsed_time_t / 60:.2f} minutes.")

        elapsed_time = time.time() - start_time
        print(f"Total running time: {elapsed_time / 60:.2f} minutes.")

        return pd.DataFrame(NMB_DALY_Cost_SdTreat_PMDT_eachpt)


    def dr_tb_dt_s(self, preliminary_daly_costs, DALY_individual_Moldova):
        start_time = time.time()
        NMB_DALY_Cost_SdTreat_DT_eachpt = []  # Results container

        for i, (DALY_Death, obs) in enumerate(
                zip(DALY_individual_Moldova, self.pred_data['observed'])):
            optimal_treat = self.optimal_treat_dt_sample(i, self.wtp)

            FLQ_status = 'FLQ Resistant' if obs == 1 else 'FLQ Susceptible'
            treatment_result = self._prepare_treatment_result(i, 'None', 'None', FLQ_status, 'DT', optimal_treat,
                                                              preliminary_daly_costs, self.wtp)

            NMB_DALY_Cost_SdTreat_DT_eachpt.append(treatment_result)

        elapsed_time = time.time() - start_time
        print(f"Total running time: {elapsed_time / 60:.2f} minutes.")

        return pd.DataFrame(NMB_DALY_Cost_SdTreat_DT_eachpt)


    def _prepare_treatment_result(self, person_id, threshold, pred, FLQ_status, treatment_type, optimal_treat,
                                  preliminary_daly_costs, wtp):
        if optimal_treat['Opt_Treat'] == 'DLM':
            NMB_SdTreat_DM = preliminary_daly_costs.SdTreat_NMB[person_id] - preliminary_daly_costs.DLM_NMB[person_id]
            NMB_DM = preliminary_daly_costs.DLM_NMB[person_id]
            DALY_SdTreat_DM = preliminary_daly_costs.SdTreat_DALY[person_id] - preliminary_daly_costs.Exp_DLM_DALY[
                person_id]
            DALY_DM = preliminary_daly_costs.Exp_DLM_DALY[person_id]
            Cost_SdTreat_DM = preliminary_daly_costs.SdTreat_cost[person_id] - preliminary_daly_costs.Exp_DLM_cost[
                person_id]
            Cost_DM = preliminary_daly_costs.Exp_DLM_cost[person_id]
        elif optimal_treat['Opt_Treat'] == 'FLQ':
            NMB_SdTreat_DM = preliminary_daly_costs.SdTreat_NMB[person_id] - preliminary_daly_costs.FLQ_NMB[person_id]
            NMB_DM = preliminary_daly_costs.FLQ_NMB[person_id]
            DALY_SdTreat_DM = preliminary_daly_costs.SdTreat_DALY[person_id] - preliminary_daly_costs.Exp_FLQ_DALY[
                person_id]
            DALY_DM = preliminary_daly_costs.Exp_FLQ_DALY[person_id]
            Cost_SdTreat_DM = preliminary_daly_costs.SdTreat_cost[person_id] - preliminary_daly_costs.Exp_FLQ_cost[
                person_id]
            Cost_DM = preliminary_daly_costs.Exp_FLQ_cost[person_id]
        else:
            NMB_SdTreat_DM = float('nan')
            NMB_DM = float('nan')
            DALY_SdTreat_DM =float('nan')
            DALY_DM = float('nan')
            Cost_SdTreat_DM = float('nan')
            Cost_DM = float('nan')

        if pred == 'None':
            PM_classification = 'None'
            PM_prediction = 'None'
        else:
            PM_prediction = pred
            PM_classification = 'None'
            if threshold != 'None':

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
            'DALY_FLQres': optimal_treat['FLQres_expected_DALY_sample_avg'],
            'Cost_FLQres': optimal_treat['FLQres_expected_cost_sample_avg'],
            'DALY_FLQsus': optimal_treat['FLQsus_expected_DALY_sample_avg'],
            'Cost_FLQsus': optimal_treat['FLQsus_expected_cost_sample_avg'],
            'NMB_SdTreat_DM': NMB_SdTreat_DM,
            'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[person_id],
            'NMB_SdTreat_FLQ': wtp * preliminary_daly_costs.Exp_FLQ_SdTreat_DALY[person_id] +
                               preliminary_daly_costs.Exp_FLQ_SdTreat_cost[person_id],
            'NMB_DM': NMB_DM,
            'NMB_DLM': optimal_treat['DLM_LNMB'],
            'NMB_FLQ': optimal_treat['FLQ_LNMB'],
            'DALY_SdTreat_DM': DALY_SdTreat_DM,
            'DALY_SdTreat': preliminary_daly_costs.SdTreat_DALY[person_id],
            'DALY_DM': DALY_DM,
            'Cost_SdTreat_DM': Cost_SdTreat_DM,
            'Cost_SdTreat': preliminary_daly_costs.SdTreat_cost[person_id],
            'Cost_DM': Cost_DM
        }


# if __name__ == '__main__':
#
#     np.random.seed(5)
#
#     # WTP
#     wtp_value = 1 * GDP_moldova
#
#     i = 1
#
#     par_samplesize = 200
#     par_sampler = ParameterSampler(FLQ_Res_prev, prob_data_prior, cost_data_prior, dalyweight_data_prior,
#                                    dalylength_data_prior, sideeffectdaly_data_prior, sideeffectfreq_data_prior,
#                                    sideeffectlength_data_prior, nsamples=par_samplesize)
#     pm_performance = PMPerformance(pred_data, booststrap_pred_data, par_sampler)
#
#     print(f"Parameter sampling starts.")
#     # Sampling from the prior probabilities
#     prob_sampled_par = par_sampler.sample_prob_parameters()
#     # Sampling from the prior costs
#     cost_sampled_par = par_sampler.sample_cost_parameters()
#     # Sampling from the prior daly weights
#     dalyweight_sampled_par = par_sampler.sample_dalyweight_parameters()
#     # Sampling from the prior daly length
#     dalylength_sampled_par = par_sampler.sample_dalylength_parameters()
#     # Sampling from the prior disease prevalence
#     diseaseprev_sampled_par = par_sampler.sample_disease_prevalence()
#     # Sampling from the prior daly weights
#     sideeffectdaly_sampled_par = par_sampler.sample_sideeffectdaly_parameters()
#     # Sampling from the prior daly length
#     sideeffectfreq_sampled_par = par_sampler.sample_sideeffectfreq_parameters()
#     # Sampling from the prior disease prevalence
#     sideeffectlength_sampled_par = par_sampler.sample_sideeffectlength_parameters()
#
#     # Generate the sequence from 0 to 1 with a step of 0.0025
#     threshold_values = np.arange(0, 1.00, 0.25)
#
#     # Create the DataFrame
#     allthresholds = pd.DataFrame({'threshold': threshold_values})
#
#     drtb_instance = DRTuberculosisDT(par_sampler, DALY_individual_Moldova, pm_performance, pred_data, diseaseprev_sampled_par, prob_sampled_par, cost_sampled_par, dalyweight_sampled_par, dalylength_sampled_par, sideeffectdaly_sampled_par, sideeffectfreq_sampled_par, sideeffectlength_sampled_par, par_samplesize, wtp_value)
#
#     ############ Preliminary Costs and DALY Calculation ############
#     # Calculated expected costs and DALYs for each treatment depending on FLQ susceptibility
#     preliminary_daly_costs = calculate_pre_daly_cost_s(par_sampler, pred_data, DALY_individual_Moldova, diseaseprev_sampled_par, prob_sampled_par, cost_sampled_par,
#                                            dalyweight_sampled_par, dalylength_sampled_par,
#                                            sideeffectdaly_sampled_par,
#                                            sideeffectfreq_sampled_par,
#                                            sideeffectlength_sampled_par,
#                                            wtp_value, par_samplesize)
#
#
#     ############ End Preliminary Costs and ############
#
#     PMDT_sampled = drtb_instance.dr_tb_dt_s(preliminary_daly_costs, DALY_individual_Moldova)
#
#     print("Column names individually:")
#     for col in PMDT_sampled.columns:
#         print(col)
#
#     # # Export test file
#     # file_path_PMDT_sampled = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Tests/Test PM bootstraping/' + f'test_output.xlsx'
#     # # Save the DataFrame to an Excel file
#     # PMDT_sampled.to_excel(
#     #     file_path_PMDT_sampled,
#     #     index=False)
