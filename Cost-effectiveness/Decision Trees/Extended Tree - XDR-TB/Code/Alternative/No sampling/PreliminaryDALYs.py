import pandas as pd

from DR_TB_Classes import *
from InputData import *
from collections import namedtuple
import statistics


def calculate_pre_daly_cost(pred_data, DALY_individual_Moldova, prob_data, cost_data, daly_data, wtp):
    """ returns the expected costs of future nodes
    :param pred_data: external data containing the predictions from the predictive model, the true observed values and age of each patient
    :param wtp: willingness to pay
    :return: a named tuple containing expected dalys for each branch of the decision trees
    """

    # Make the table variables to be used - Probabilities in the tree
    for index, row in prob_data.iterrows():
        globals()[row['Probability Variable']] = row['Probability Value']

    # Make the table variables to be used - Costs in the tree
    for index, row in cost_data.iterrows():
        globals()[row['Cost Variable']] = row['Cost Value']

    # Make the table variables to be used - DALYs in the tree
    for index, row in daly_data.iterrows():
        globals()[row['DALY Variable']] = row['DALY Value']

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

    # Terminal nodes
    CC_FLQsus = TerminalNode(name='CC_FLQsus', cost=Cost_CC_FLQsus, daly=DALY_CC_FLQsus)
    TF_FLQsus = TerminalNode(name='TF_FLQsus', cost=Cost_TF_FLQsus, daly=DALY_TF_FLQsus)
    CC_FLQres = TerminalNode(name='CC_FLQres', cost=Cost_CC_FLQres, daly=DALY_CC_FLQres)
    TF_FLQres = TerminalNode(name='TF_FLQres', cost=Cost_TF_FLQres, daly=DALY_TF_FLQres)
    CC_DLM = TerminalNode(name='CC_DLM', cost=Cost_CC_DLM, daly=DALY_CC_DLM)
    TF_DLM = TerminalNode(name='TF_DLM', cost=Cost_TF_DLM, daly=DALY_TF_DLM)

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

    i = 0

    for DALY_Death, obs in zip(DALY_individual_Moldova, pred_data['obs']):
        # Terminal Nodes
        DEATH_FLQsus = TerminalNode(name='D_FLQsus', cost=Cost_D_FLQsus, daly=DALY_Death)
        DEATH_FLQres = TerminalNode(name='D_FLQres', cost=Cost_D_FLQres, daly=DALY_Death)
        DEATH_DLM = TerminalNode(name='D_DLM', cost=Cost_D_DLM, daly=DALY_Death)

        # Chance nodes
        C_FLQsus = ChanceNode(name='C_FLQsus', cost=Cost_FLQ,
                                   future_nodes=[CC_FLQsus, TF_FLQsus, DEATH_FLQsus],
                                   probs=[Prob_CC_FLQsus, Prob_TF_FLQsus, Prob_D_FLQsus], daly=DALY_FLQ)
        C_FLQres = ChanceNode(name='C_FLQres', cost=Cost_FLQ,
                                   future_nodes=[CC_FLQres, TF_FLQres, DEATH_FLQres],
                                   probs=[Prob_CC_FLQres, Prob_TF_FLQres, Prob_D_FLQres], daly=DALY_FLQ)
        C_DLM = ChanceNode(name='C_DLM', cost=Cost_DLM,
                                future_nodes=[CC_DLM, TF_DLM, DEATH_DLM],
                                probs=[Prob_CC_DLM, Prob_TF_DLM, Prob_D_DLM], daly=DALY_DLM)

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
        C_FLQ_SdTreat = ChanceNode(name='C_FLQ_SdTreat', cost=Cost_FLQ, daly=0,
                                         future_nodes=[C_FLQsus, C_FLQres], probs=[(1-FLQ_Res_prev), FLQ_Res_prev])
        D_FLQ_SdTreat = DecisionNode(name='D_FLQ_SdTreat', cost=0, future_nodes=[C_FLQ_SdTreat], daly=0)
        Exp_FLQ_SdTreat_DALY.append(D_FLQ_SdTreat.get_expected_daly()['C_FLQ_SdTreat'])
        Exp_FLQ_SdTreat_cost.append(D_FLQ_SdTreat.get_expected_cost()['C_FLQ_SdTreat'])


        Exp_DLM_cost.append(Exp_D_DLM_cost) # the cost of DLM does not change
        Exp_DLM_DALY.append(Exp_D_DLM_DALY)  # Expected DALYs incurred by DLM treatment
        DLM_NMB.append(wtp * Exp_D_DLM_DALY + Exp_D_DLM_cost) # NMB loss of DLM treatment

        if obs == 1:
            Exp_FLQ_DALY.append(Exp_FLQres_DALY) # Expected DALYs incurred by FLQ treatment
            Exp_FLQ_cost.append(Exp_FLQres_cost)  # Expected cost incurred by DLM treatment
            FLQ_NMB.append(wtp * Exp_FLQres_DALY + Exp_FLQres_cost) # NMB loss of FLQ treatment
            SdTreat_cost.append(Exp_FLQres_cost) # Expected cost of the standard treatment
            SdTreat_DALY.append(Exp_FLQres_DALY) # Expected DALys incurred by the standard treatment
            SdTreat_NMB.append(wtp * Exp_FLQres_DALY + Exp_FLQres_cost) # NMB loss of the standard treatment
            SdTreat_cost_res.append(Exp_FLQres_cost) # Expected cost of the standard treatment - FLQ resistant patients only
            SdTreat_DALY_res.append(Exp_FLQres_DALY) # Expected DALYs of the standard treatment - FLQ resistant patients only
            SdTreat_NMB_res.append(wtp * Exp_FLQres_DALY + Exp_FLQres_cost) # NMB loss of FLQ treatment - FLQ resistant patients only
        else:
            Exp_FLQ_DALY.append(Exp_FLQsus_DALY) # Expected DALYs incurred by FLQ treatment
            Exp_FLQ_cost.append(Exp_FLQsus_cost) # Expected cost incurred by DLM treatment
            FLQ_NMB.append(wtp * Exp_FLQsus_DALY + Exp_FLQsus_cost) # NMB loss of FLQ treatment
            SdTreat_cost.append(Exp_FLQsus_cost) # Expected cost of the standard treatment
            SdTreat_DALY.append(Exp_FLQsus_DALY) # Expected DALys incurred by the standard treatment
            SdTreat_NMB.append(wtp * Exp_FLQsus_DALY + Exp_FLQsus_cost) # NMB loss of the standard treatment
            SdTreat_cost_sus.append(Exp_FLQsus_cost) # Expected cost of the standard treatment - FLQ susceptible patients only
            SdTreat_DALY_sus.append(Exp_FLQsus_DALY) # Expected DALYs of the standard treatment - FLQ susceptible patients only
            SdTreat_NMB_sus.append(wtp * Exp_FLQsus_DALY + Exp_FLQsus_cost) # NMB loss of FLQ treatment - FLQ susceptible patients only

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

