import pandas as pd
from collections import namedtuple
import statistics

# Assumes these are available exactly as in your script
from DR_TB_Classes import *
from InputData import *
from SampleParameters import *


class Preliminary_DALY:
    """
    Class for running DALY calculations and decision-tree
    cost-effectiveness analyses for DR-TB.
    """

    def __init__(self, data, le_data):
        self.data = data
        self.le_data = le_data

    # ---------------------------------------------------------
    # 1. DALY COMPUTATION
    # ---------------------------------------------------------

    def classify_age(self, age):
        """
        Classifies the given age into the specified age categories.

        Parameters:
        age (int): The age to classify.

        Returns:
        str: The category that the age falls into.
        """
        if age < 1:
            return "<1 year"
        elif 1 <= age <= 4:
            return "1-4 years"
        elif 5 <= age <= 9:
            return "5-9 years"
        elif 10 <= age <= 14:
            return "10-14 years"
        elif 15 <= age <= 19:
            return "15-19 years"
        elif 20 <= age <= 24:
            return "20-24 years"
        elif 25 <= age <= 29:
            return "25-29 years"
        elif 30 <= age <= 34:
            return "30-34 years"
        elif 35 <= age <= 39:
            return "35-39 years"
        elif 40 <= age <= 44:
            return "40-44 years"
        elif 45 <= age <= 49:
            return "45-49 years"
        elif 50 <= age <= 54:
            return "50-54 years"
        elif 55 <= age <= 59:
            return "55-59 years"
        elif 60 <= age <= 64:
            return "60-64 years"
        elif 65 <= age <= 69:
            return "65-69 years"
        elif 70 <= age <= 74:
            return "70-74 years"
        elif 75 <= age <= 79:
            return "75-79 years"
        elif 80 <= age <= 84:
            return "80-84 years"
        else:
            return "85+ years"

    def filter_dataframe(self, df, sex, ageband, period_value):
        """
        Filters the DataFrame based on provided conditions and retrieves the 'Value' column.

        Parameters:
        df (pd.DataFrame): The input DataFrame to filter.
        dim2_value (str): The value for the Dim2 column.
        dim1_value (str): The value for the Dim1 column.
        period_value (int): The value for the Period column.

        Returns:
        float or None: The value from the 'Value' column that matches the filter conditions, or None if no match is found.
        """
        # Apply the filter based on the provided conditions
        filtered_df = df[(df['Dim2'] == ageband) & (df['Dim1'] == sex) & (df['Period'] == period_value)]

        # Retrieve the 'Value' column for the filtered row
        if not filtered_df.empty:
            return filtered_df['Value'].values[0]
        else:
            return None

    def compute_daly_individual(self):
        """
        Compute DALYs for each individual using classify_age()
        and filter_dataframe().
        """
        daly_list = []

        for idx in range(len(self.data)):
            age_s = self.classify_age(self.data['age'].iloc[idx])
            sex_s = self.data['sex'].iloc[idx]
            daly = self.filter_dataframe(self.le_data, sex_s, age_s, 2019)
            daly_list.append(daly)

        return daly_list

    # ---------------------------------------------------------
    # 2. COST-EFFECTIVENESS: PRE-DALY + COSTS
    # ---------------------------------------------------------
    def calculate_pre_daly_cost_s(self, sampler, pred_data, DALY_individual_Moldova, diseaseprev_sampled_par,
                                  prob_sampled_par, cost_sampled_par, dalyweight_sampled_par,
                                  dalylength_sampled_par, sideeffectdaly_sampled_par,
                                  sideeffectfreq_sampled_par,
                                  sideeffectlength_sampled_par, wtp, par_samplesize):
        """ returns the expected costs of future nodes
        :param pred_data: external data containing the predictions from the predictive model, the true observed values and age of each patient
        :param wtp: willingness to pay
        :return: a named tuple containing expected dalys for each branch of the decision trees
        """
        # Define a namedtuple to store the results
        DalyResults = namedtuple('DalyResults', [
            'Person',
            'Exp_FLQ_DALY',
            'Exp_FLQ_cost',
            'Exp_DLM_DALY',
            'Exp_DLM_cost',
            'Exp_FLQ_SdTreat_DALY',
            'Exp_FLQ_SdTreat_cost',
            'FLQ_NMB',
            'DLM_NMB',
            'SdTreat_cost',
            'SdTreat_DALY',
            'SdTreat_NMB',
            'SdTreat_cost_res',
            'SdTreat_DALY_res',
            'SdTreat_NMB_res',
            'SdTreat_cost_sus',
            'SdTreat_DALY_sus',
            'SdTreat_NMB_sus'
        ])

        # Initialize lists for results
        Exp_FLQ_DALY = []
        Exp_FLQ_cost = []
        Exp_DLM_DALY = []
        Exp_DLM_cost = []
        Exp_FLQ_SdTreat_DALY = []
        Exp_FLQ_SdTreat_cost = []
        SdTreat_cost = []
        SdTreat_DALY = []
        SdTreat_NMB = []
        SdTreat_cost_res = []
        SdTreat_DALY_res = []
        SdTreat_NMB_res = []
        SdTreat_cost_sus = []
        SdTreat_DALY_sus = []
        SdTreat_NMB_sus = []
        FLQ_NMB = []
        DLM_NMB = []
        person = []

        for i, (DALY_Death, obs) in enumerate(zip(DALY_individual_Moldova, pred_data['observed'])):

            Exp_FLQ_DALY_pt = []  # Expected DALYs incurred by FLQ treatment
            Exp_FLQ_cost_pt = []  # Expected cost incurred by DLM treatment
            FLQ_NMB_pt = []  # NMB loss of FLQ treatment
            SdTreat_cost_pt = []  # Expected cost of the standard treatment
            SdTreat_DALY_pt = []  # Expected DALys incurred by the standard treatment
            SdTreat_NMB_pt = []  # NMB loss of the standard treatment
            SdTreat_cost_res_pt = []  # Expected cost of the standard treatment - FLQ resistant patients only
            SdTreat_DALY_res_pt = []  # Expected DALYs of the standard treatment - FLQ resistant patients only
            SdTreat_NMB_res_pt = []  # NMB loss of FLQ treatment - FLQ resistant patients only
            SdTreat_cost_sus_pt = []  # Expected cost of the standard treatment - FLQ susceptible patients only
            SdTreat_DALY_sus_pt = []  # Expected DALYs of the standard treatment - FLQ susceptible patients only
            SdTreat_NMB_sus_pt = []  # NMB loss of FLQ treatment - FLQ susceptible patients only
            Exp_DLM_cost_pt = []  # the cost of DLM does not change
            Exp_DLM_DALY_pt = []  # Expected DALYs incurred by DLM treatment
            DLM_NMB_pt = []  # NMB loss of DLM treatment
            Exp_FLQ_SdTreat_DALY_pt = []
            Exp_FLQ_SdTreat_cost_pt = []

            for j in range(1, par_samplesize + 1):

                # Generate the sampled tables for cost and daly in the appropriate format (2 columns)
                prob_cost_daly_sampled = sampler.prob_cost_daly_input_table(prob_sampled_par,
                                                                            cost_sampled_par,
                                                                            dalyweight_sampled_par,
                                                                            dalylength_sampled_par,
                                                                            sideeffectdaly_sampled_par,
                                                                            sideeffectfreq_sampled_par,
                                                                            sideeffectlength_sampled_par, j)

                diseaseprev_sampled = sampler.diseaseprev_input(diseaseprev_sampled_par, j)

                # Terminal Nodes
                Cure_FLQsus = TerminalNode(name='Cure_FLQsus', cost=prob_cost_daly_sampled['Cost_Cure_FLQsus'],
                                           daly=prob_cost_daly_sampled['DALY_Cure_FLQsus'])
                Recurrence_FLQsus = TerminalNode(name='Recurrence_FLQsus',
                                                 cost=prob_cost_daly_sampled['Cost_Recurrence_FLQsus'],
                                                 daly=prob_cost_daly_sampled['DALY_Recurrence_FLQsus'])
                TF_FLQsus = TerminalNode(name='TF_FLQsus', cost=prob_cost_daly_sampled['Cost_TF_FLQsus'],
                                         daly=prob_cost_daly_sampled['DALY_TF_FLQsus'])
                Cure_FLQres = TerminalNode(name='Cure_FLQres', cost=prob_cost_daly_sampled['Cost_Cure_FLQres'],
                                           daly=prob_cost_daly_sampled['DALY_Cure_FLQres'])
                Recurrence_FLQres = TerminalNode(name='Recurrence_FLQres',
                                                 cost=prob_cost_daly_sampled['Cost_Recurrence_FLQres'],
                                                 daly=prob_cost_daly_sampled['DALY_Recurrence_FLQres'])
                TF_FLQres = TerminalNode(name='TF_FLQres', cost=prob_cost_daly_sampled['Cost_TF_FLQres'],
                                         daly=prob_cost_daly_sampled['DALY_TF_FLQres'])
                Cure_DLM = TerminalNode(name='Cure_DLM', cost=prob_cost_daly_sampled['Cost_Cure_DLM'],
                                        daly=prob_cost_daly_sampled['DALY_Cure_DLM'])
                Recurrence_DLM = TerminalNode(name='Recurrence_DLM',
                                              cost=prob_cost_daly_sampled['Cost_Recurrence_DLM'],
                                              daly=prob_cost_daly_sampled['DALY_Recurrence_DLM'])
                TF_DLM = TerminalNode(name='TF_DLM', cost=prob_cost_daly_sampled['Cost_TF_DLM'],
                                      daly=prob_cost_daly_sampled['DALY_TF_DLM'])

                DEATH_FLQsus = TerminalNode(name='D_FLQsus', cost=prob_cost_daly_sampled['Cost_D_FLQsus'],
                                            daly=DALY_Death)
                DEATH_FLQres = TerminalNode(name='D_FLQres', cost=prob_cost_daly_sampled['Cost_D_FLQres'],
                                            daly=DALY_Death)
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

                C_FLQsus = ChanceNode(name='C_FLQsus', cost=prob_cost_daly_sampled['Cost_FLQ'],
                                      future_nodes=[CC_FLQsus, TF_FLQsus, DEATH_FLQsus],
                                      probs=[prob_cost_daly_sampled['ProbCC_FLQsus'],
                                             prob_cost_daly_sampled['ProbTF_FLQsus'],
                                             prob_cost_daly_sampled['ProbD_FLQsus']],
                                      daly=prob_cost_daly_sampled['DALY_FLQ'])

                C_FLQres = ChanceNode(name='C_FLQres', cost=prob_cost_daly_sampled['Cost_FLQ'],
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
                # Decision nodes and Expected Values
                D_FLQsus = DecisionNode(name='D_FLQsus', cost=0, future_nodes=[C_FLQsus], daly=0)
                Exp_FLQsus_DALY = D_FLQsus.get_expected_daly()['C_FLQsus']
                Exp_FLQsus_cost = D_FLQsus.get_expected_cost()['C_FLQsus']
                D_FLQres = DecisionNode(name='D_FLQres', cost=0, future_nodes=[C_FLQres], daly=0)
                Exp_FLQres_DALY = D_FLQres.get_expected_daly()['C_FLQres']
                Exp_FLQres_cost = D_FLQres.get_expected_cost()['C_FLQres']
                D_DLM = DecisionNode(name='D_DLM', cost=0, future_nodes=[C_DLM], daly=0)
                Exp_D_DLM_DALY = D_DLM.get_expected_daly()['C_DLM']
                Exp_D_DLM_cost = D_DLM.get_expected_cost()['C_DLM']

                # Decision node for the standard treatment
                C_FLQ_SdTreat = ChanceNode(name='C_FLQ_SdTreat', cost=0, daly=0,
                                           future_nodes=[C_FLQsus, C_FLQres],
                                           probs=[(1 - diseaseprev_sampled), diseaseprev_sampled])
                D_FLQ_SdTreat = DecisionNode(name='D_FLQ_SdTreat', cost=0, future_nodes=[C_FLQ_SdTreat], daly=0)
                Exp_FLQ_SdTreat_DALY_pt.append(D_FLQ_SdTreat.get_expected_daly()['C_FLQ_SdTreat'])
                Exp_FLQ_SdTreat_cost_pt.append(D_FLQ_SdTreat.get_expected_cost()['C_FLQ_SdTreat'])

                Exp_DLM_cost_pt.append(Exp_D_DLM_cost)  # the cost of DLM does not change
                Exp_DLM_DALY_pt.append(Exp_D_DLM_DALY)  # Expected DALYs incurred by DLM treatment
                DLM_NMB_pt.append(wtp * Exp_D_DLM_DALY + Exp_D_DLM_cost)  # NMB loss of DLM treatment

                if obs == 1:
                    Exp_FLQ_DALY_pt.append(Exp_FLQres_DALY)  # Expected DALYs incurred by FLQ treatment
                    Exp_FLQ_cost_pt.append(Exp_FLQres_cost)  # Expected cost incurred by DLM treatment
                    FLQ_NMB_pt.append(wtp * Exp_FLQres_DALY + Exp_FLQres_cost)  # NMB loss of FLQ treatment
                    SdTreat_cost_pt.append(Exp_FLQres_cost)  # Expected cost of the standard treatment
                    SdTreat_DALY_pt.append(Exp_FLQres_DALY)  # Expected DALys incurred by the standard treatment
                    SdTreat_NMB_pt.append(wtp * Exp_FLQres_DALY + Exp_FLQres_cost)  # NMB loss of the standard treatment
                    SdTreat_cost_res_pt.append(
                        Exp_FLQres_cost)  # Expected cost of the standard treatment - FLQ resistant patients only
                    SdTreat_DALY_res_pt.append(
                        Exp_FLQres_DALY)  # Expected DALYs of the standard treatment - FLQ resistant patients only
                    SdTreat_NMB_res_pt.append(
                        wtp * Exp_FLQres_DALY + Exp_FLQres_cost)  # NMB loss of FLQ treatment - FLQ resistant patients only
                else:
                    Exp_FLQ_DALY_pt.append(Exp_FLQsus_DALY)  # Expected DALYs incurred by FLQ treatment
                    Exp_FLQ_cost_pt.append(Exp_FLQsus_cost)  # Expected cost incurred by DLM treatment
                    FLQ_NMB_pt.append(wtp * Exp_FLQsus_DALY + Exp_FLQsus_cost)  # NMB loss of FLQ treatment
                    SdTreat_cost_pt.append(Exp_FLQsus_cost)  # Expected cost of the standard treatment
                    SdTreat_DALY_pt.append(Exp_FLQsus_DALY)  # Expected DALys incurred by the standard treatment
                    SdTreat_NMB_pt.append(wtp * Exp_FLQsus_DALY + Exp_FLQsus_cost)  # NMB loss of the standard treatment
                    SdTreat_cost_sus_pt.append(
                        Exp_FLQsus_cost)  # Expected cost of the standard treatment - FLQ susceptible patients only
                    SdTreat_DALY_sus_pt.append(
                        Exp_FLQsus_DALY)  # Expected DALYs of the standard treatment - FLQ susceptible patients only
                    SdTreat_NMB_sus_pt.append(
                        wtp * Exp_FLQsus_DALY + Exp_FLQsus_cost)  # NMB loss of FLQ treatment - FLQ susceptible patients only

            person.append(i + 1)

            print(f"Preliminary DALYs and Costs: Patient {i} complete.")

            Exp_DLM_cost.append(statistics.mean(Exp_DLM_cost_pt))  # the cost of DLM does not change
            Exp_DLM_DALY.append(statistics.mean(Exp_DLM_DALY_pt))  # Expected DALYs incurred by DLM treatment
            DLM_NMB.append(statistics.mean(DLM_NMB_pt))  # NMB loss of DLM treatment
            Exp_FLQ_DALY.append(statistics.mean(Exp_FLQ_DALY_pt))  # Expected DALYs incurred by FLQ treatment
            Exp_FLQ_cost.append(statistics.mean(Exp_FLQ_cost_pt))  # Expected cost incurred by FLQ treatment
            FLQ_NMB.append(statistics.mean(FLQ_NMB_pt))  # NMB loss of FLQ treatment
            SdTreat_cost.append(statistics.mean(SdTreat_cost_pt))  # Expected cost of the standard treatment
            SdTreat_DALY.append(statistics.mean(SdTreat_DALY_pt))  # Expected DALys incurred by the standard treatment
            SdTreat_NMB.append(statistics.mean(SdTreat_NMB_pt))  # NMB loss of the standard treatment
            Exp_FLQ_SdTreat_DALY.append(
                statistics.mean(Exp_FLQ_SdTreat_DALY_pt))  # Expected DALys incurred by the standard treatment
            Exp_FLQ_SdTreat_cost.append(statistics.mean(Exp_FLQ_SdTreat_cost_pt))  # NMB loss of the standard treatment

            if obs == 1:
                SdTreat_cost_res.append(statistics.mean(
                    SdTreat_cost_res_pt))  # Expected cost of the standard treatment - FLQ resistant patients only
                SdTreat_DALY_res.append(
                    statistics.mean(SdTreat_DALY_res_pt))  # NMB loss of FLQ treatment - FLQ resistant patients only
                SdTreat_NMB_res.append(statistics.mean(
                    SdTreat_NMB_res_pt))  # Expected cost of the standard treatment - FLQ resistant patients only
            else:
                SdTreat_cost_sus.append(statistics.mean(
                    SdTreat_cost_sus_pt))  # Expected cost of the standard treatment - FLQ susceptible patients only
                SdTreat_DALY_sus.append(statistics.mean(
                    SdTreat_DALY_sus_pt))  # Expected DALYs of the standard treatment - FLQ susceptible patients only
                SdTreat_NMB_sus.append(
                    statistics.mean(SdTreat_NMB_sus_pt))  # NMB loss of FLQ treatment - FLQ susceptible patients only
            print(len(Exp_FLQ_DALY))

        print(f"Preliminary DALYs and Costs complete.")

        return DalyResults(
            Person=person,
            Exp_FLQ_DALY=Exp_FLQ_DALY,
            Exp_FLQ_cost=Exp_FLQ_cost,
            Exp_DLM_DALY=Exp_DLM_DALY,
            Exp_DLM_cost=Exp_DLM_cost,
            FLQ_NMB=FLQ_NMB,
            DLM_NMB=DLM_NMB,
            Exp_FLQ_SdTreat_DALY=Exp_FLQ_SdTreat_DALY,
            Exp_FLQ_SdTreat_cost=Exp_FLQ_SdTreat_cost,
            SdTreat_cost=SdTreat_cost,
            SdTreat_DALY=SdTreat_DALY,
            SdTreat_NMB=SdTreat_NMB,
            SdTreat_cost_res=SdTreat_cost_res,
            SdTreat_DALY_res=SdTreat_DALY_res,
            SdTreat_NMB_res=SdTreat_NMB_res,
            SdTreat_cost_sus=SdTreat_cost_sus,
            SdTreat_DALY_sus=SdTreat_DALY_sus,
            SdTreat_NMB_sus=SdTreat_NMB_sus
        )


