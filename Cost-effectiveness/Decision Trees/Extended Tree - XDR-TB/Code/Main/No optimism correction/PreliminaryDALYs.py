import pandas as pd
from collections import namedtuple
from DR_TB_Classes import *
from InputData import *
from SampleParameters import *
import statistics


def calculate_pre_daly_cost_s(sampler, mainpm_pred_data, DALY_individual_Moldova, diseaseprev_sampled_par, prob_data, cost_sampled_par, dalyweight_sampled_par,
                                                      dalylength_sampled_par, wtp, par_samplesize):
    """ returns the expected costs of future nodes
    :param pred_data: external data containing the predictions from the predictive model, the true observed values and age of each patient
    :param wtp: willingness to pay
    :return: a named tuple containing expected dalys for each branch of the decision trees
    """

    # Make the table variables to be used - Probabilities in the tree
    probability_variables = dict(zip(prob_data['Probability Variable'], prob_data['Probability Value']))

    # Define a namedtuple to store the results
    DalyResults = namedtuple('DalyResults', [
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
    FLQ_NMB =[]
    DLM_NMB = []


    for i, (DALY_Death, obs) in enumerate(zip(DALY_individual_Moldova, mainpm_pred_data['observed'])):

        Exp_FLQ_DALY_pt = [] # Expected DALYs incurred by FLQ treatment
        Exp_FLQ_cost_pt = [] # Expected cost incurred by DLM treatment
        FLQ_NMB_pt = [] # NMB loss of FLQ treatment
        SdTreat_cost_pt = [] # Expected cost of the standard treatment
        SdTreat_DALY_pt = [] # Expected DALys incurred by the standard treatment
        SdTreat_NMB_pt = [] # NMB loss of the standard treatment
        SdTreat_cost_res_pt = [] # Expected cost of the standard treatment - FLQ resistant patients only
        SdTreat_DALY_res_pt = [] # Expected DALYs of the standard treatment - FLQ resistant patients only
        SdTreat_NMB_res_pt = []  # NMB loss of FLQ treatment - FLQ resistant patients only
        SdTreat_cost_sus_pt = [] # Expected cost of the standard treatment - FLQ susceptible patients only
        SdTreat_DALY_sus_pt = [] # Expected DALYs of the standard treatment - FLQ susceptible patients only
        SdTreat_NMB_sus_pt = [] # NMB loss of FLQ treatment - FLQ susceptible patients only
        Exp_DLM_cost_pt = []  # the cost of DLM does not change
        Exp_DLM_DALY_pt = []  # Expected DALYs incurred by DLM treatment
        DLM_NMB_pt = []  # NMB loss of DLM treatment

        for j in range(1, par_samplesize + 1):

            # Generate the sampled tables for cost and daly in the appropriate format (2 columns)
            cost_daly_sampled = sampler.cost_daly_input_table(cost_sampled_par, dalyweight_sampled_par,
                                                      dalylength_sampled_par, j)

            diseaseprev_sampled = sampler.diseaseprev_input(diseaseprev_sampled_par,j)

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

            # Terminal Nodes
            DEATH_FLQsus = TerminalNode(name='D_FLQsus', cost=cost_daly_sampled['Cost_D_FLQsus'], daly=DALY_Death)
            DEATH_FLQres = TerminalNode(name='D_FLQres', cost=cost_daly_sampled['Cost_D_FLQres'], daly=DALY_Death)
            DEATH_DLM = TerminalNode(name='D_DLM', cost=cost_daly_sampled['Cost_D_DLM'], daly=DALY_Death)

            # Chance nodes
            C_FLQsus = ChanceNode(name='C_FLQsus', cost=cost_daly_sampled['Cost_FLQ'],
                                  future_nodes=[CC_FLQsus, TF_FLQsus, DEATH_FLQsus],
                                  probs=[probability_variables['Prob_CC_FLQsus'], probability_variables['Prob_TF_FLQsus'], probability_variables['Prob_D_FLQsus']],
                                  daly=cost_daly_sampled['DALY_FLQ'])
            C_FLQres = ChanceNode(name='C_FLQres', cost=cost_daly_sampled['Cost_FLQ'],
                                  future_nodes=[CC_FLQres, TF_FLQres, DEATH_FLQres],
                                  probs=[probability_variables['Prob_CC_FLQres'], probability_variables['Prob_TF_FLQres'], probability_variables['Prob_D_FLQres']],
                                  daly=cost_daly_sampled['DALY_FLQ'])
            C_DLM = ChanceNode(name='C_DLM', cost=cost_daly_sampled['Cost_DLM'],
                               future_nodes=[CC_DLM, TF_DLM, DEATH_DLM],
                               probs=[probability_variables['Prob_CC_DLM'], probability_variables['Prob_TF_DLM'], probability_variables['Prob_D_DLM']], daly=cost_daly_sampled['DALY_DLM'])

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
                                             future_nodes=[C_FLQsus, C_FLQres], probs=[(1-diseaseprev_sampled), diseaseprev_sampled])
            D_FLQ_SdTreat = DecisionNode(name='D_FLQ_SdTreat', cost=0, future_nodes=[C_FLQ_SdTreat], daly=0)
            Exp_FLQ_SdTreat_DALY.append(D_FLQ_SdTreat.get_expected_daly()['C_FLQ_SdTreat'])
            Exp_FLQ_SdTreat_cost.append(D_FLQ_SdTreat.get_expected_cost()['C_FLQ_SdTreat'])

            Exp_DLM_cost_pt.append(Exp_D_DLM_cost) # the cost of DLM does not change
            Exp_DLM_DALY_pt.append(Exp_D_DLM_DALY)  # Expected DALYs incurred by DLM treatment
            DLM_NMB_pt.append(wtp * Exp_D_DLM_DALY + Exp_D_DLM_cost) # NMB loss of DLM treatment

            if obs == 1:
                Exp_FLQ_DALY_pt.append(Exp_FLQres_DALY) # Expected DALYs incurred by FLQ treatment
                Exp_FLQ_cost_pt.append(Exp_FLQres_cost)  # Expected cost incurred by DLM treatment
                FLQ_NMB_pt.append(wtp * Exp_FLQres_DALY + Exp_FLQres_cost) # NMB loss of FLQ treatment
                SdTreat_cost_pt.append(Exp_FLQres_cost) # Expected cost of the standard treatment
                SdTreat_DALY_pt.append(Exp_FLQres_DALY) # Expected DALys incurred by the standard treatment
                SdTreat_NMB_pt.append(wtp * Exp_FLQres_DALY + Exp_FLQres_cost) # NMB loss of the standard treatment
                SdTreat_cost_res_pt.append(Exp_FLQres_cost) # Expected cost of the standard treatment - FLQ resistant patients only
                SdTreat_DALY_res_pt.append(Exp_FLQres_DALY) # Expected DALYs of the standard treatment - FLQ resistant patients only
                SdTreat_NMB_res_pt.append(wtp * Exp_FLQres_DALY + Exp_FLQres_cost) # NMB loss of FLQ treatment - FLQ resistant patients only
            else:
                Exp_FLQ_DALY_pt.append(Exp_FLQsus_DALY) # Expected DALYs incurred by FLQ treatment
                Exp_FLQ_cost_pt.append(Exp_FLQsus_cost) # Expected cost incurred by DLM treatment
                FLQ_NMB_pt.append(wtp * Exp_FLQsus_DALY + Exp_FLQsus_cost) # NMB loss of FLQ treatment
                SdTreat_cost_pt.append(Exp_FLQsus_cost) # Expected cost of the standard treatment
                SdTreat_DALY_pt.append(Exp_FLQsus_DALY) # Expected DALys incurred by the standard treatment
                SdTreat_NMB_pt.append(wtp * Exp_FLQsus_DALY + Exp_FLQsus_cost) # NMB loss of the standard treatment
                SdTreat_cost_sus_pt.append(Exp_FLQsus_cost) # Expected cost of the standard treatment - FLQ susceptible patients only
                SdTreat_DALY_sus_pt.append(Exp_FLQsus_DALY) # Expected DALYs of the standard treatment - FLQ susceptible patients only
                SdTreat_NMB_sus_pt.append(wtp * Exp_FLQsus_DALY + Exp_FLQsus_cost) # NMB loss of FLQ treatment - FLQ susceptible patients only

        print(f"Preliminary DALYs and Costs: Patient {i} complete.")

        Exp_DLM_cost.append(statistics.mean(Exp_DLM_cost_pt))  # the cost of DLM does not change
        Exp_DLM_DALY.append(statistics.mean(Exp_DLM_DALY_pt))  # Expected DALYs incurred by DLM treatment
        DLM_NMB.append(statistics.mean(DLM_NMB_pt))  # NMB loss of DLM treatment
        Exp_FLQ_DALY.append(statistics.mean(Exp_FLQ_DALY_pt))  # Expected DALYs incurred by FLQ treatment
        Exp_FLQ_cost.append(statistics.mean(Exp_FLQ_cost_pt))  # Expected cost incurred by DLM treatment
        FLQ_NMB.append(statistics.mean(FLQ_NMB_pt))  # NMB loss of FLQ treatment
        SdTreat_cost.append(statistics.mean(SdTreat_cost_pt))  # Expected cost of the standard treatment
        SdTreat_DALY.append(statistics.mean(SdTreat_DALY_pt))  # Expected DALys incurred by the standard treatment
        SdTreat_NMB.append(statistics.mean(SdTreat_NMB_pt))  # NMB loss of the standard treatment

        if obs == 1:
            SdTreat_cost_res.append(statistics.mean(SdTreat_cost_res_pt))  # Expected cost of the standard treatment - FLQ resistant patients only
            SdTreat_DALY_res.append(statistics.mean(SdTreat_DALY_res_pt))  # NMB loss of FLQ treatment - FLQ resistant patients only
            SdTreat_NMB_res.append(statistics.mean(SdTreat_NMB_res_pt))  # Expected cost of the standard treatment - FLQ resistant patients only
        else:
            SdTreat_cost_sus.append(statistics.mean(SdTreat_cost_sus_pt))  # Expected cost of the standard treatment - FLQ susceptible patients only
            SdTreat_DALY_sus.append(statistics.mean(SdTreat_DALY_sus_pt))  # Expected DALYs of the standard treatment - FLQ susceptible patients only
            SdTreat_NMB_sus.append(statistics.mean(SdTreat_NMB_sus_pt))  # NMB loss of FLQ treatment - FLQ susceptible patients only
        print(len(Exp_FLQ_DALY))

    print(f"Preliminary DALYs and Costs complete.")

    return DalyResults(
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



if __name__ == "__main__":
    # Usage

    base_path = '/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/'
    cost_effectiveness_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'

    # Read data
    cost_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'Costs')
    dalyweight_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'DALY Weight')
    dalylenght_data = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V3.xlsx', 'DALY Lenght')

    par_samplesize = 100
    wtp = GDP_moldova * 3

    sampler = ParameterSampler(cost_data_prior, dalyweight_data, dalylength_data, nsamples=par_samplesize)

    # Sampling from the prior costs
    cost_sampled_par = sampler.sample_cost_parameters()

    # Sampling from the prior daly weights
    dalyweight_sampled_par =sampler.sample_dalyweight_parameters()
    # Sampling from the prior daly length
    dalylength_sampled_par = sampler.sample_dalylength_parameters()

    pre_daly_cost = calculate_pre_daly_cost_s(pred_data, DALY_individual_Moldova, prob_data, cost_sampled_par, dalyweight_sampled_par,dalylength_sampled_par,
                              wtp, par_samplesize)

    # Convert the dictionary to a pandas DataFrame
    # df_DT_NMB = pd.DataFrame({
    #     "Exp_FLQ_DALY":[statistics.mean(pre_daly_cost.Exp_FLQ_DALY)],
    #     "Exp_FLQ_cost":[statistics.mean(pre_daly_cost.Exp_FLQ_cost)],
    #     "Exp_DLM_DALY":[statistics.mean(pre_daly_cost.Exp_DLM_DALY)],
    #     "Exp_DLM_cost":[statistics.mean(pre_daly_cost.Exp_DLM_cost)],
    #     "FLQ_NMB":[statistics.mean(pre_daly_cost.FLQ_NMB)],
    #     "DLM_NMB":[statistics.mean(pre_daly_cost.DLM_NMB)],
    #     "Exp_FLQ_SdTreat_DALY":[statistics.mean(pre_daly_cost.Exp_FLQ_SdTreat_DALY)],
    #     "Exp_FLQ_SdTreat_cost":[statistics.mean(pre_daly_cost.Exp_FLQ_SdTreat_cost)],
    #     "SdTreat_cost":[statistics.mean(pre_daly_cost.SdTreat_cost)],
    #     "SdTreat_DALY":[statistics.mean(pre_daly_cost.SdTreat_DALY)],
    #     "SdTreat_NMB":[statistics.mean(pre_daly_cost.SdTreat_NMB)],
    #     "SdTreat_cost_res": [statistics.mean(pre_daly_cost.SdTreat_cost_res)],
    #     "SdTreat_DALY_res": [statistics.mean(pre_daly_cost.SdTreat_DALY_res)],
    #     "SdTreat_NMB_res": [statistics.mean(pre_daly_cost.SdTreat_NMB_res)],
    #     "SdTreat_cost_sus": [statistics.mean(pre_daly_cost.SdTreat_cost_sus)],
    #     "SdTreat_DALY_sus": [statistics.mean(pre_daly_cost.SdTreat_DALY_sus)],
    #     "SdTreat_NMB_sus": [statistics.mean(pre_daly_cost.SdTreat_NMB_sus)],
    # })
    # # Save the DataFrame to an Excel file
    # df_DT_NMB.to_excel(base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Tests/Test parameter sampling/' +"preliminary_daly_10.xlsx", index=False)

    #Daly FLQ
    #
    # pd.DataFrame({"Exp_FLQ_DALY": pre_daly_cost.Exp_FLQ_DALY}).to_excel(base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Tests/Test parameter sampling/' +"DALY_FLQ_10.xlsx", index=False)

    print(pre_daly_cost.SdTreat_NMB[71])
    print(pre_daly_cost.DLM_NMB[71])
    print(pre_daly_cost.SdTreat_NMB[71]-pre_daly_cost.DLM_NMB[71])