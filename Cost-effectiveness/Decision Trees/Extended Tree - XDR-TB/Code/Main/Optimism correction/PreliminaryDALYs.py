import pandas as pd
from collections import namedtuple
from DR_TB_Classes import *
from InputData import *
from SampleParameters import *
import statistics
import matplotlib.pyplot as plt
from scipy.stats import norm


def calculate_pre_daly_cost_s(sampler, mainpm_pred_data, DALY_individual_Moldova, diseaseprev_sampled_par,
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

    for i, (DALY_Death, obs) in enumerate(zip(DALY_individual_Moldova, mainpm_pred_data['observed'])):

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
        Person = person,
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

    # Common directory paths
    base_path = '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/'
    hm_output_path = base_path + 'LR/Output/Optimism Corrected/'
    # hm_output_path_method632 = hm_output_path + 'Method 632/'
    cost_effectiveness_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'
    Input_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Input/'
    Output_path = base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/'

    # Read data
    mainpm_pred_data = pd.read_csv(hm_output_path + 'LR_MainPM_PlattCalibration.csv')
    prob_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V9.xlsx',
                                    'Probabilities')
    cost_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V9.xlsx', 'Costs')
    dalyweight_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V9.xlsx',
                                          'DALY Weight')
    dalylength_data_prior = pd.read_excel(cost_effectiveness_path + 'Cost_DALY_Prob_asumptions_V9.xlsx',
                                          'DALY Length')
    par_samplesize = 200
    wtp = GDP_moldova * 3
    FLQ_Res_prev = 1 - 0.812963

    par_sampler = ParameterSampler(FLQ_Res_prev, prob_data_prior, cost_data_prior, dalyweight_data_prior,
                                   dalylength_data_prior, sideeffectdaly_data_prior, sideeffectfreq_data_prior,
                                   sideeffectlength_data_prior, nsamples=par_samplesize)

    # Sampling from the prior probabilities
    prob_sampled_par = par_sampler.sample_prob_parameters()
    # Sampling from the prior costs
    cost_sampled_par = par_sampler.sample_cost_parameters()
    # Sampling from the prior daly weights
    dalyweight_sampled_par = par_sampler.sample_dalyweight_parameters()
    # Sampling from the prior daly length
    dalylength_sampled_par = par_sampler.sample_dalylength_parameters()
    # Sampling from the prior disease prevalence
    diseaseprev_sampled_par = par_sampler.sample_disease_prevalence()
    # Sampling from the prior daly weights
    sideeffectdaly_sampled_par = par_sampler.sample_sideeffectdaly_parameters()
    # Sampling from the prior daly length
    sideeffectfreq_sampled_par = par_sampler.sample_sideeffectfreq_parameters()
    # Sampling from the prior disease prevalence
    sideeffectlength_sampled_par = par_sampler.sample_sideeffectlength_parameters()

    print(prob_sampled_par)

    pre_daly_cost = calculate_pre_daly_cost_s(par_sampler, mainpm_pred_data, DALY_individual_Moldova,
                                              diseaseprev_sampled_par, prob_sampled_par, cost_sampled_par,
                                              dalyweight_sampled_par, dalylength_sampled_par,
                                              sideeffectdaly_sampled_par,
                                              sideeffectfreq_sampled_par,
                                              sideeffectlength_sampled_par,
                                              wtp, par_samplesize)
    print(pre_daly_cost.Exp_FLQ_DALY)

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

    # Daly FLQ
    #
    # pd.DataFrame({"Exp_FLQ_DALY": pre_daly_cost.Exp_FLQ_DALY}).to_excel(base_path + 'Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Tests/Test parameter sampling/' +"DALY_FLQ_10.xlsx", index=False)

    print(pre_daly_cost.SdTreat_NMB[71])
    print(pre_daly_cost.DLM_NMB[71])

    # Convert to dictionary
    data_dict = pre_daly_cost._asdict()

    # List of keys to exclude
    exclude_keys = [
        'SdTreat_cost_res', 'SdTreat_DALY_res', 'SdTreat_NMB_res',
        'SdTreat_cost_sus', 'SdTreat_DALY_sus', 'SdTreat_NMB_sus'
    ]

    # Filter the dictionary
    filtered_dict = {k: v for k, v in data_dict.items() if k not in exclude_keys}

    # Transpose so each key is a column and each value becomes a row
    df = pd.DataFrame.from_dict(filtered_dict, orient='index').transpose()

    print(df)

    # Save to Excel
    df.to_excel(
        '/Users/mraniereneves/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/DR-TB-Modelling/Cost-effectiveness/Decision Trees/Extended Tree - XDR-TB/Output/Main/Daly Cost Analysis/DalyResults_200samples_revision17_07.xlsx',
        index=False)

    # Sample sizes to iterate over
    sample_sizes = list(range(10, 1001, 50))

    # Lists to store results
    means = []
    lower_bounds = []
    upper_bounds = []

    # Set willingness-to-pay threshold
    wtp = GDP_moldova * 3
    FLQ_Res_prev = 1 - 0.812963

    # # Iterate through different parameter sample sizes
    # for par_samplesize in sample_sizes:
    #     # Parameter sampling
    #     par_sampler = ParameterSampler(
    #         FLQ_Res_prev,
    #         prob_data_prior, cost_data_prior, dalyweight_data_prior,
    #         dalylength_data_prior, sideeffectdaly_data_prior,
    #         sideeffectfreq_data_prior, sideeffectlength_data_prior,
    #         nsamples=par_samplesize
    #     )
    #
    #     prob_sampled_par = par_sampler.sample_prob_parameters()
    #     cost_sampled_par = par_sampler.sample_cost_parameters()
    #     dalyweight_sampled_par = par_sampler.sample_dalyweight_parameters()
    #     dalylength_sampled_par = par_sampler.sample_dalylength_parameters()
    #     diseaseprev_sampled_par = par_sampler.sample_disease_prevalence()
    #     sideeffectdaly_sampled_par = par_sampler.sample_sideeffectdaly_parameters()
    #     sideeffectfreq_sampled_par = par_sampler.sample_sideeffectfreq_parameters()
    #     sideeffectlength_sampled_par = par_sampler.sample_sideeffectlength_parameters()
    #
    #     pre_daly_cost = calculate_pre_daly_cost_s(
    #         par_sampler, mainpm_pred_data, DALY_individual_Moldova,
    #         diseaseprev_sampled_par, prob_sampled_par, cost_sampled_par,
    #         dalyweight_sampled_par, dalylength_sampled_par,
    #         sideeffectdaly_sampled_par, sideeffectfreq_sampled_par,
    #         sideeffectlength_sampled_par, wtp, par_samplesize
    #     )
    #
    #     # Extract relevant data
    #     data_dict = pre_daly_cost._asdict()
    #     SdTreat_NMB_values = np.array(data_dict['SdTreat_NMB'])
    #
    #     # Calculate mean and 95% confidence interval
    #     mean_val = np.mean(SdTreat_NMB_values)
    #     std_err = np.std(SdTreat_NMB_values, ddof=1) / np.sqrt(len(SdTreat_NMB_values))
    #     ci_margin = norm.ppf(0.975) * std_err
    #
    #     means.append(mean_val)
    #     lower_bounds.append(mean_val - ci_margin)
    #     upper_bounds.append(mean_val + ci_margin)
    #
    # # Plotting
    # plt.figure(figsize=(10, 6))
    # plt.plot(sample_sizes, means, label='Mean SdTreat_NMB', color='blue')
    # plt.fill_between(sample_sizes, lower_bounds, upper_bounds, color='blue', alpha=0.2, label='95% CI')
    # plt.xlabel('Parameter Sample Size')
    # plt.ylabel('SdTreat_NMB')
    # plt.title('Mean SdTreat_NMB with 95% CI vs Sample Size')
    # plt.legend()
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()
