import csv
from collections import namedtuple
from PreliminaryDALYs import *


############ Function to calculate NMB, DALYs and Costs for the PM + DT ############
def dr_tb_pm_dt(preliminary_daly_costs, sens_spec_PM, pred_data, DALY_individual_Moldova, prob_data, cost_data,
                daly_data, wtp):
    # Make the table variables to be used - Probabilities in the tree
    for index, row in prob_data.iterrows():
        globals()[row['Probability Variable']] = row['Probability Value']

    # Make the table variables to be used - Costs in the tree
    for index, row in cost_data.iterrows():
        globals()[row['Cost Variable']] = row['Cost Value']

    # Make the table variables to be used - DALYs in the tree
    for index, row in daly_data.iterrows():
        globals()[row['DALY Variable']] = row['DALY Value']

    # Auxiliary function that calculates NMB, Cost and DALYs by FLQ susceptibility
    def nmb_daly_cost_flq_res_sus_pmdt_fun(preliminary_daly_costs, key_suffix, treatment_type, i):
        """ Calculate NMB, DALYs and Costs for a patient depending on the treatment type and FLQ resistance status
        :return: no explicit return
        """
        if key_suffix == 'FLQ_Res':
            NMB_SdTreat_PMDT_FLQ_Res.append(
                preliminary_daly_costs.SdTreat_NMB[i] - getattr(preliminary_daly_costs, f"{treatment_type}_NMB")[i])
            NMB_SdTreat_FLQ_Res.append(preliminary_daly_costs.SdTreat_NMB[i])
            NMB_PMDT_FLQ_Res.append(getattr(preliminary_daly_costs, f"{treatment_type}_NMB")[i])
            DALY_SdTreat_PMDT_FLQ_Res.append(
                preliminary_daly_costs.SdTreat_DALY[i] - getattr(preliminary_daly_costs, f"Exp_{treatment_type}_DALY")[
                    i])
            DALY_SdTreat_FLQ_Res.append(preliminary_daly_costs.SdTreat_DALY[i])
            DALY_PMDT_FLQ_Res.append(getattr(preliminary_daly_costs, f"Exp_{treatment_type}_DALY")[i])
            Cost_SdTreat_PMDT_FLQ_Res.append(
                preliminary_daly_costs.SdTreat_cost[i] - getattr(preliminary_daly_costs, f"Exp_{treatment_type}_cost")[
                    i])
            Cost_SdTreat_FLQ_Res.append(preliminary_daly_costs.SdTreat_cost[i])
            Cost_PMDT_FLQ_Res.append(getattr(preliminary_daly_costs, f"Exp_{treatment_type}_cost")[i])
        if key_suffix == 'FLQ_Sus':
            NMB_SdTreat_PMDT_FLQ_Sus.append(
                preliminary_daly_costs.SdTreat_NMB[i] - getattr(preliminary_daly_costs, f"{treatment_type}_NMB")[i])
            NMB_SdTreat_FLQ_Sus.append(preliminary_daly_costs.SdTreat_NMB[i])
            NMB_PMDT_FLQ_Sus.append(getattr(preliminary_daly_costs, f"{treatment_type}_NMB")[i])
            DALY_SdTreat_PMDT_FLQ_Sus.append(
                preliminary_daly_costs.SdTreat_DALY[i] - getattr(preliminary_daly_costs, f"Exp_{treatment_type}_DALY")[
                    i])
            DALY_SdTreat_FLQ_Sus.append(preliminary_daly_costs.SdTreat_DALY[i])
            DALY_PMDT_FLQ_Sus.append(getattr(preliminary_daly_costs, f"Exp_{treatment_type}_DALY")[i])
            Cost_SdTreat_PMDT_FLQ_Sus.append(
                preliminary_daly_costs.SdTreat_cost[i] - getattr(preliminary_daly_costs, f"Exp_{treatment_type}_cost")[
                    i])
            Cost_SdTreat_FLQ_Sus.append(preliminary_daly_costs.SdTreat_cost[i])
            Cost_PMDT_FLQ_Sus.append(getattr(preliminary_daly_costs, f"Exp_{treatment_type}_cost")[i])

    # Initiating the vectors that store output
    NMB_DALY_Cost_SdTreat_PMDT_eachpt = []  # Change in NMB, DALYs and Cost when the optimal treatment (PM + DT) is used in comparison to the standard treatment and separately
    NMB_DALY_Cost_FLQ_DLM_class_avg = []  # Change in NMB, DALYs and Cost of FLQ and DLM depending on the prediction model classification
    NMB_DALY_Cost_FLQ_Res_Sus_avg = []  # Change in NMB, DALYs and Cost depending on FLQ susceptibility

    # Terminal nodes
    CC_FLQsus = TerminalNode(name='CC_FLQsus', cost=Cost_CC_FLQsus, daly=DALY_CC_FLQsus)
    TF_FLQsus = TerminalNode(name='TF_FLQsus', cost=Cost_TF_FLQsus, daly=DALY_TF_FLQsus)
    CC_FLQres = TerminalNode(name='CC_FLQres', cost=Cost_CC_FLQres, daly=DALY_CC_FLQres)
    TF_FLQres = TerminalNode(name='TF_FLQres', cost=Cost_TF_FLQres, daly=DALY_TF_FLQres)
    CC_DLM = TerminalNode(name='CC_DLM', cost=Cost_CC_DLM, daly=DALY_CC_DLM)
    TF_DLM = TerminalNode(name='TF_DLM', cost=Cost_TF_DLM, daly=DALY_TF_DLM)

    with open(sens_spec_PM, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            P_S_R = float(row['P_S_R'])
            P_R_R = float(row['P_R_R'])
            P_S_S = float(row['P_S_S'])
            P_R_S = float(row['P_R_S'])
            t = float(row['threshold'])
            positive = float(row['positive'])
            negative = float(row['negative'])

            # Supporting vectors to calculate Cost and DALYS for DLM And FLQ depending on classification
            DALY_DLM_positiveclass = []
            Cost_DLM_positiveclass = []
            DALY_FLQ_positiveclass = []
            Cost_FLQ_positiveclass = []
            DALY_DLM_negativeclass = []
            Cost_DLM_negativeclass = []
            DALY_FLQ_negativeclass = []
            Cost_FLQ_negativeclass = []

            # NMB, Cost and DALYs by FLQ susceptibility
            NMB_SdTreat_PMDT_FLQ_Res = []
            NMB_SdTreat_FLQ_Res = []
            NMB_PMDT_FLQ_Res = []
            DALY_SdTreat_PMDT_FLQ_Res = []
            DALY_SdTreat_FLQ_Res = []
            DALY_PMDT_FLQ_Res = []
            Cost_SdTreat_PMDT_FLQ_Res = []
            Cost_SdTreat_FLQ_Res = []
            Cost_PMDT_FLQ_Res = []
            NMB_SdTreat_PMDT_FLQ_Sus = []
            NMB_SdTreat_FLQ_Sus = []
            NMB_PMDT_FLQ_Sus = []
            DALY_SdTreat_PMDT_FLQ_Sus = []
            DALY_SdTreat_FLQ_Sus = []
            DALY_PMDT_FLQ_Sus = []
            Cost_SdTreat_PMDT_FLQ_Sus = []
            Cost_SdTreat_FLQ_Sus = []
            Cost_PMDT_FLQ_Sus = []

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

                    # NMB, DALYs and Costs of DLM for patients classified FLQ resistant
                    DALY_DLM_positiveclass.append(D_p.get_expected_daly()['C_DLM'])
                    Cost_DLM_positiveclass.append(D_p.get_expected_cost()['C_DLM'])
                    DALY_FLQ_positiveclass.append(D_p.get_expected_daly()['C_FLQ_p'])
                    Cost_FLQ_positiveclass.append(D_p.get_expected_cost()['C_FLQ_p'])

                    # Select Optimal Treatment
                    if Opt_Treat_p == 'C_DLM':

                        # NMB, DALYs and Costs for each patient
                        NMB_DALY_Cost_SdTreat_PMDT_eachpt.append(
                            {'threshold': t,
                             'Person': i,
                             'FLQ_Status': FLQ_status,
                             'Prediction_Model_Classification': 'FLQ Resistant',
                             'DALY_DLM': D_p.get_expected_daly()['C_DLM'],
                             'Cost_DLM': D_p.get_expected_cost()['C_DLM'],
                             'DALY_FLQ': D_p.get_expected_daly()['C_FLQ_p'],
                             'Cost_FLQ': D_p.get_expected_cost()['C_FLQ_p'],
                             'NMB_SdTreat_PMDT': preliminary_daly_costs.SdTreat_NMB[i] - preliminary_daly_costs.DLM_NMB[
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

                        # NMB, Cost and DALYs by FLQ susceptibility
                        if obs == 1:
                            nmb_daly_cost_flq_res_sus_pmdt_fun(preliminary_daly_costs, 'FLQ_Res', 'DLM', i)
                        else:
                            nmb_daly_cost_flq_res_sus_pmdt_fun(preliminary_daly_costs, 'FLQ_Sus', 'DLM', i)


                    else:

                        # NMB, DALYs and Costs for each patient
                        NMB_DALY_Cost_SdTreat_PMDT_eachpt.append(
                            {'threshold': t,
                             'Person': i,
                             'FLQ_Status': FLQ_status,
                             'Prediction_Model_Classification': 'FLQ Resistant',
                             'DALY_DLM': D_p.get_expected_daly()['C_DLM'],
                             'Cost_DLM': D_p.get_expected_cost()['C_DLM'],
                             'DALY_FLQ': D_p.get_expected_daly()['C_FLQ_p'],
                             'Cost_FLQ': D_p.get_expected_cost()['C_FLQ_p'],
                             'NMB_SdTreat_PMDT': preliminary_daly_costs.SdTreat_NMB[i] - preliminary_daly_costs.FLQ_NMB[
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

                        # NMB, Cost and DALYs by FLQ susceptibility
                        if obs == 1:
                            nmb_daly_cost_flq_res_sus_pmdt_fun(preliminary_daly_costs, 'FLQ_Res', 'FLQ', i)
                        else:
                            nmb_daly_cost_flq_res_sus_pmdt_fun(preliminary_daly_costs, 'FLQ_Sus', 'FLQ', i)

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

                    # NMB, DALYs and Costs of DLM for patients classified FLQ resistant
                    DALY_DLM_negativeclass.append(D_n.get_expected_daly()['C_DLM'])
                    Cost_DLM_negativeclass.append(D_n.get_expected_cost()['C_DLM'])
                    DALY_FLQ_negativeclass.append(D_n.get_expected_daly()['C_FLQ_n'])
                    Cost_FLQ_negativeclass.append(D_n.get_expected_cost()['C_FLQ_n'])

                    # Optimal Treatment
                    Opt_Treat_n = DT_n.get_optimal_decision()[0]

                    # Select Optimal Treatment
                    if Opt_Treat_n == 'C_DLM':

                        # NMB, DALYs and Costs for each patient
                        NMB_DALY_Cost_SdTreat_PMDT_eachpt.append(
                            {'threshold': t,
                             'Person': i,
                             'FLQ_Status': FLQ_status,
                             'Prediction_Model_Classification': 'FLQ Susceptible',
                             'DALY_DLM': D_n.get_expected_daly()['C_DLM'],
                             'Cost_DLM': D_n.get_expected_cost()['C_DLM'],
                             'DALY_FLQ': D_n.get_expected_daly()['C_FLQ_n'],
                             'Cost_FLQ': D_n.get_expected_cost()['C_FLQ_n'],
                             'NMB_SdTreat_PMDT': preliminary_daly_costs.SdTreat_NMB[i] - preliminary_daly_costs.DLM_NMB[
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

                        # NMB, Cost and DALYs by FLQ susceptibility
                        if obs == 1:
                            nmb_daly_cost_flq_res_sus_pmdt_fun(preliminary_daly_costs, 'FLQ_Res', 'DLM', i)
                        else:
                            nmb_daly_cost_flq_res_sus_pmdt_fun(preliminary_daly_costs, 'FLQ_Sus', 'DLM', i)

                    else:

                        # NMB, DALYs and Costs for each patient
                        NMB_DALY_Cost_SdTreat_PMDT_eachpt.append(
                            {'threshold': t,
                             'Person': i,
                             'FLQ_Status': FLQ_status,
                             'Prediction_Model_Classification': 'FLQ Susceptible',
                             'DALY_DLM': D_n.get_expected_daly()['C_DLM'],
                             'Cost_DLM': D_n.get_expected_cost()['C_DLM'],
                             'DALY_FLQ': D_n.get_expected_daly()['C_FLQ_n'],
                             'Cost_FLQ': D_n.get_expected_cost()['C_FLQ_n'],
                             'NMB_SdTreat_PMDT': preliminary_daly_costs.SdTreat_NMB[i] - preliminary_daly_costs.FLQ_NMB[
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

                        # NMB, Cost and DALYs by FLQ susceptibility
                        if obs == 1:
                            nmb_daly_cost_flq_res_sus_pmdt_fun(preliminary_daly_costs, 'FLQ_Res', 'FLQ', i)
                        else:
                            nmb_daly_cost_flq_res_sus_pmdt_fun(preliminary_daly_costs, 'FLQ_Sus', 'FLQ', i)

                        ### End Negative DT ###

            # NMB, Cost and DALYS for DLM And FLQ depending on classification
            NMB_DALY_Cost_FLQ_DLM_class_avg.append(
                {'threshold': t,
                 'DALY_DLM_positiveclass': sum(DALY_DLM_positiveclass) / (positive * 540),
                 'Cost_DLM_positiveclass': sum(Cost_DLM_positiveclass) / (positive * 540),
                 'NMB_DLM_positiveclass': wtp * sum(DALY_DLM_positiveclass) / (positive * 540) + sum(
                     Cost_DLM_positiveclass) / (positive * 540),
                 'DALY_FLQ_positiveclass': sum(DALY_FLQ_positiveclass) / (positive * 540),
                 'Cost_FLQ_positiveclass': sum(Cost_FLQ_positiveclass) / (positive * 540),
                 'NMB_FLQ_positiveclass': wtp * sum(DALY_FLQ_positiveclass) / (positive * 540) + sum(
                     Cost_FLQ_positiveclass) / (positive * 540),
                 'DALY_DLM_negativeclass': sum(DALY_DLM_negativeclass) / (negative * 540),
                 'Cost_DLM_negativeclass': sum(Cost_DLM_negativeclass) / (negative * 540),
                 'NMB_DLM_negativeclass': wtp * sum(DALY_DLM_negativeclass) / (negative * 540) + sum(
                     Cost_DLM_negativeclass) / (negative * 540),
                 'DALY_FLQ_negativeclass': sum(DALY_FLQ_negativeclass) / (negative * 540),
                 'Cost_FLQ_negativeclass': sum(Cost_FLQ_negativeclass) / (negative * 540),
                 'NMB_FLQ_negativeclass': wtp * sum(DALY_FLQ_negativeclass) / (negative * 540) + sum(
                     Cost_FLQ_negativeclass) / (negative * 540)
                 }
            )

            # NMB, Cost and DALYs by FLQ susceptibility
            NMB_DALY_Cost_FLQ_Res_Sus_avg.append(
                {'threshold': t,
                 "NMB_SdTreat_PMDT_FLQ_Res": sum(
                     NMB_SdTreat_PMDT_FLQ_Res) / (FLQ_Res_prev * 540),
                 "NMB_SdTreat_FLQ_Res": sum(NMB_SdTreat_FLQ_Res) / (FLQ_Res_prev * 540),
                 "NMB_PMDT_FLQ_Res": sum(NMB_PMDT_FLQ_Res) / (FLQ_Res_prev * 540),
                 "DALY_SdTreat_PMDT_FLQ_Res": sum(DALY_SdTreat_PMDT_FLQ_Res) / (FLQ_Res_prev * 540),
                 "DALY_SdTreat_FLQ_Res": sum(DALY_SdTreat_FLQ_Res) / (FLQ_Res_prev * 540),
                 "DALY_PMDT_FLQ_Res": sum(DALY_PMDT_FLQ_Res) / (FLQ_Res_prev * 540),
                 "Cost_SdTreat_PMDT_FLQ_Res": sum(Cost_SdTreat_PMDT_FLQ_Res) / (FLQ_Res_prev * 540),
                 "Cost_SdTreat_FLQ_Res": sum(Cost_SdTreat_FLQ_Res) / (FLQ_Res_prev * 540),
                 "Cost_PMDT_FLQ_Res": sum(Cost_PMDT_FLQ_Res) / (FLQ_Res_prev * 540),
                 "NMB_SdTreat_PMDT_FLQ_Sus": sum(NMB_SdTreat_PMDT_FLQ_Sus) / ((
                                                                                      1 - FLQ_Res_prev) * 540),
                 "NMB_SdTreat_FLQ_Sus": sum(NMB_SdTreat_FLQ_Sus) / ((
                                                                            1 - FLQ_Res_prev) * 540),
                 "NMB_PMDT_FLQ_Sus": sum(NMB_PMDT_FLQ_Sus) / ((
                                                                      1 - FLQ_Res_prev) * 540),
                 "DALY_SdTreat_PMDT_FLQ_Sus": sum(DALY_SdTreat_PMDT_FLQ_Sus) / ((
                                                                                        1 - FLQ_Res_prev) * 540),
                 "DALY_SdTreat_FLQ_Sus": sum(DALY_SdTreat_FLQ_Sus) / ((
                                                                              1 - FLQ_Res_prev) * 540),
                 "DALY_PMDT_FLQ_Sus": sum(DALY_PMDT_FLQ_Sus) / ((
                                                                        1 - FLQ_Res_prev) * 540),
                 "Cost_SdTreat_PMDT_FLQ_Sus": sum(Cost_SdTreat_PMDT_FLQ_Sus) / ((
                                                                                        1 - FLQ_Res_prev) * 540),
                 "Cost_SdTreat_FLQ_Sus": sum(Cost_SdTreat_FLQ_Sus) / ((
                                                                              1 - FLQ_Res_prev) * 540),
                 "Cost_PMDT_FLQ_Sus": sum(Cost_PMDT_FLQ_Sus) / ((
                                                                        1 - FLQ_Res_prev) * 540)
                 }
            )

    # Define the named tuple with fields that will hold dictionaries
    dr_tb_tree_output_t = namedtuple('dr_tb_tree_output',
                                     ['NMB_DALY_Cost_SdTreat_PMDT_eachpt', 'NMB_DALY_Cost_FLQ_DLM_class_avg',
                                      'NMB_DALY_Cost_FLQ_Res_Sus_avg'])

    # Create an instance of the named tuple
    dr_tb_tree_output = dr_tb_tree_output_t(NMB_DALY_Cost_SdTreat_PMDT_eachpt=NMB_DALY_Cost_SdTreat_PMDT_eachpt,
                                            NMB_DALY_Cost_FLQ_DLM_class_avg=NMB_DALY_Cost_FLQ_DLM_class_avg,
                                            NMB_DALY_Cost_FLQ_Res_Sus_avg=NMB_DALY_Cost_FLQ_Res_Sus_avg)

    return dr_tb_tree_output


############ Function to calculate NMB, DALYs and Costs for the PM + DT - SIMPLIFIED ############
def dr_tb_pm_dt_s(preliminary_daly_costs, sens_spec_PM, pred_data, DALY_individual_Moldova, prob_data, cost_data,
                  daly_data, wtp):
    # Make the table variables to be used - Probabilities in the tree
    for index, row in prob_data.iterrows():
        globals()[row['Probability Variable']] = row['Probability Value']

    # Make the table variables to be used - Costs in the tree
    for index, row in cost_data.iterrows():
        globals()[row['Cost Variable']] = row['Cost Value']

    # Make the table variables to be used - DALYs in the tree
    for index, row in daly_data.iterrows():
        globals()[row['DALY Variable']] = row['DALY Value']

    # Initiating the vectors that store output
    NMB_DALY_Cost_SdTreat_PMDT_eachpt = []  # Change in NMB, DALYs and Cost when the optimal treatment (PM + DT) is used in comparison to the standard treatment and separately

    # Terminal nodes
    CC_FLQsus = TerminalNode(name='CC_FLQsus', cost=Cost_CC_FLQsus, daly=DALY_CC_FLQsus)
    TF_FLQsus = TerminalNode(name='TF_FLQsus', cost=Cost_TF_FLQsus, daly=DALY_TF_FLQsus)
    CC_FLQres = TerminalNode(name='CC_FLQres', cost=Cost_CC_FLQres, daly=DALY_CC_FLQres)
    TF_FLQres = TerminalNode(name='TF_FLQres', cost=Cost_TF_FLQres, daly=DALY_TF_FLQres)
    CC_DLM = TerminalNode(name='CC_DLM', cost=Cost_CC_DLM, daly=DALY_CC_DLM)
    TF_DLM = TerminalNode(name='TF_DLM', cost=Cost_TF_DLM, daly=DALY_TF_DLM)

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
                             'Person': i,
                             'FLQ_Status': FLQ_status,
                             'Prediction_Model_Classification': 'FLQ Resistant',
                             'DALY_DLM': D_p.get_expected_daly()['C_DLM'],
                             'Cost_DLM': D_p.get_expected_cost()['C_DLM'],
                             'DALY_FLQ': D_p.get_expected_daly()['C_FLQ_p'],
                             'Cost_FLQ': D_p.get_expected_cost()['C_FLQ_p'],
                             'NMB_SdTreat_PMDT': preliminary_daly_costs.SdTreat_NMB[i] - preliminary_daly_costs.DLM_NMB[
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
                             'Person': i,
                             'FLQ_Status': FLQ_status,
                             'Prediction_Model_Classification': 'FLQ Resistant',
                             'DALY_DLM': D_p.get_expected_daly()['C_DLM'],
                             'Cost_DLM': D_p.get_expected_cost()['C_DLM'],
                             'DALY_FLQ': D_p.get_expected_daly()['C_FLQ_p'],
                             'Cost_FLQ': D_p.get_expected_cost()['C_FLQ_p'],
                             'NMB_SdTreat_PMDT': preliminary_daly_costs.SdTreat_NMB[i] - preliminary_daly_costs.FLQ_NMB[
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
                             'Person': i,
                             'FLQ_Status': FLQ_status,
                             'Prediction_Model_Classification': 'FLQ Susceptible',
                             'DALY_DLM': D_n.get_expected_daly()['C_DLM'],
                             'Cost_DLM': D_n.get_expected_cost()['C_DLM'],
                             'DALY_FLQ': D_n.get_expected_daly()['C_FLQ_n'],
                             'Cost_FLQ': D_n.get_expected_cost()['C_FLQ_n'],
                             'NMB_SdTreat_PMDT': preliminary_daly_costs.SdTreat_NMB[i] - preliminary_daly_costs.DLM_NMB[
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
                             'Person': i,
                             'FLQ_Status': FLQ_status,
                             'Prediction_Model_Classification': 'FLQ Susceptible',
                             'DALY_DLM': D_n.get_expected_daly()['C_DLM'],
                             'Cost_DLM': D_n.get_expected_cost()['C_DLM'],
                             'DALY_FLQ': D_n.get_expected_daly()['C_FLQ_n'],
                             'Cost_FLQ': D_n.get_expected_cost()['C_FLQ_n'],
                             'NMB_SdTreat_PMDT': preliminary_daly_costs.SdTreat_NMB[i] - preliminary_daly_costs.FLQ_NMB[
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

    return NMB_DALY_Cost_SdTreat_PMDT_eachpt


############ Function to calculate NMB, DALYs and Costs for the PM alone ############
def dr_tb_pm(preliminary_daly_costs, sens_spec_PM, pred_data):
    # Auxiliary function that calculates NMB, Cost and DALYs by FLQ susceptibility
    def nmb_daly_cost_flq_res_sus_pm_fun(preliminary_daly_costs, key_suffix, treatment_type, i):
        """ Calculate NMB, DALYs and Costs for a patient depending on the treatment type and FLQ resistance status
        :return: no explicit return
        """
        if key_suffix == 'FLQ_Res':
            NMB_SdTreat_PM_FLQ_Res.append(
                preliminary_daly_costs.SdTreat_NMB[i] - getattr(preliminary_daly_costs, f"{treatment_type}_NMB")[i])
            NMB_SdTreat_FLQ_Res.append(preliminary_daly_costs.SdTreat_NMB[i])
            NMB_PM_FLQ_Res.append(getattr(preliminary_daly_costs, f"{treatment_type}_NMB")[i])
            DALY_SdTreat_PM_FLQ_Res.append(
                preliminary_daly_costs.SdTreat_DALY[i] - getattr(preliminary_daly_costs, f"Exp_{treatment_type}_DALY")[
                    i])
            DALY_SdTreat_FLQ_Res.append(preliminary_daly_costs.SdTreat_DALY[i])
            DALY_PM_FLQ_Res.append(getattr(preliminary_daly_costs, f"Exp_{treatment_type}_DALY")[i])
            Cost_SdTreat_PM_FLQ_Res.append(
                preliminary_daly_costs.SdTreat_cost[i] - getattr(preliminary_daly_costs, f"Exp_{treatment_type}_cost")[
                    i])
            Cost_SdTreat_FLQ_Res.append(preliminary_daly_costs.SdTreat_cost[i])
            Cost_PM_FLQ_Res.append(getattr(preliminary_daly_costs, f"Exp_{treatment_type}_cost")[i])
        if key_suffix == 'FLQ_Sus':
            NMB_SdTreat_PM_FLQ_Sus.append(
                preliminary_daly_costs.SdTreat_NMB[i] - getattr(preliminary_daly_costs, f"{treatment_type}_NMB")[i])
            NMB_SdTreat_FLQ_Sus.append(preliminary_daly_costs.SdTreat_NMB[i])
            NMB_PM_FLQ_Sus.append(getattr(preliminary_daly_costs, f"{treatment_type}_NMB")[i])
            DALY_SdTreat_PM_FLQ_Sus.append(
                preliminary_daly_costs.SdTreat_DALY[i] - getattr(preliminary_daly_costs, f"Exp_{treatment_type}_DALY")[
                    i])
            DALY_SdTreat_FLQ_Sus.append(preliminary_daly_costs.SdTreat_DALY[i])
            DALY_PM_FLQ_Sus.append(getattr(preliminary_daly_costs, f"Exp_{treatment_type}_DALY")[i])
            Cost_SdTreat_PM_FLQ_Sus.append(
                preliminary_daly_costs.SdTreat_cost[i] - getattr(preliminary_daly_costs, f"Exp_{treatment_type}_cost")[
                    i])
            Cost_SdTreat_FLQ_Sus.append(preliminary_daly_costs.SdTreat_cost[i])
            Cost_PM_FLQ_Sus.append(getattr(preliminary_daly_costs, f"Exp_{treatment_type}_cost")[i])

    # Initiating the vectors that store output
    NMB_DALY_Cost_SdTreat_PM_eachpt = []  # Change in NMB, DALYs and Cost when the optimal treatment (PM + DT) is used in comparison to the standard treatment and separately
    NMB_DALY_Cost_FLQ_Res_Sus_PM_avg = []  # Change in NMB, DALYs and Cost depending on FLQ susceptibility

    with open(sens_spec_PM, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            t = float(row['threshold'])
            positive = float(row['positive'])
            negative = float(row['negative'])

            # NMB, Cost and DALYs by FLQ susceptibility
            NMB_SdTreat_PM_FLQ_Res = []
            NMB_SdTreat_FLQ_Res = []
            NMB_PM_FLQ_Res = []
            DALY_SdTreat_PM_FLQ_Res = []
            DALY_SdTreat_FLQ_Res = []
            DALY_PM_FLQ_Res = []
            Cost_SdTreat_PM_FLQ_Res = []
            Cost_SdTreat_FLQ_Res = []
            Cost_PM_FLQ_Res = []
            NMB_SdTreat_PM_FLQ_Sus = []
            NMB_SdTreat_FLQ_Sus = []
            NMB_PM_FLQ_Sus = []
            DALY_SdTreat_PM_FLQ_Sus = []
            DALY_SdTreat_FLQ_Sus = []
            DALY_PM_FLQ_Sus = []
            Cost_SdTreat_PM_FLQ_Sus = []
            Cost_SdTreat_FLQ_Sus = []
            Cost_PM_FLQ_Sus = []

            for i, (pred, obs) in enumerate(
                    zip(pred_data['pred'], pred_data['obs'])):

                # NMB, Cost and DALYs by FLQ susceptibility
                if obs == 1:
                    FLQ_status = 'FLQ Resistant'
                else:
                    FLQ_status = 'FLQ Susceptible'

                if pred > t:

                    # NMB, DALYs and Costs for each patient
                    NMB_DALY_Cost_SdTreat_PM_eachpt.append(
                        {'threshold': t,
                         'Person': i,
                         'FLQ_Status': FLQ_status,
                         'Prediction_Model_Classification': 'FLQ Resistant',
                         'NMB_SdTreat_PM': preliminary_daly_costs.SdTreat_NMB[i] - preliminary_daly_costs.DLM_NMB[
                             i],
                         'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[i],
                         'NMB_PM': preliminary_daly_costs.DLM_NMB[i],
                         'DALY_SdTreat_PM': preliminary_daly_costs.SdTreat_DALY[i] -
                                            preliminary_daly_costs.Exp_DLM_DALY[i],
                         'DALY_SdTreat': preliminary_daly_costs.SdTreat_DALY[i],
                         'DALY_PM': preliminary_daly_costs.Exp_DLM_DALY[i],
                         'Cost_SdTreat_PM': preliminary_daly_costs.SdTreat_cost[i] -
                                            preliminary_daly_costs.Exp_DLM_cost[i],
                         'Cost_SdTreat': preliminary_daly_costs.SdTreat_cost[i],
                         'Cost_PM': preliminary_daly_costs.Exp_DLM_cost[i]
                         }
                    )

                    # NMB, Cost and DALYs by FLQ susceptibility
                    if obs == 1:
                        nmb_daly_cost_flq_res_sus_pm_fun(preliminary_daly_costs, 'FLQ_Res', 'DLM', i)
                    else:
                        nmb_daly_cost_flq_res_sus_pm_fun(preliminary_daly_costs, 'FLQ_Sus', 'DLM', i)

                else:

                    # NMB, DALYs and Costs for each patient
                    NMB_DALY_Cost_SdTreat_PM_eachpt.append(
                        {'threshold': t,
                         'Person': i,
                         'FLQ_Status': FLQ_status,
                         'Prediction_Model_Classification': 'FLQ Susceptible',
                         'NMB_SdTreat_PM': preliminary_daly_costs.SdTreat_NMB[i] - preliminary_daly_costs.FLQ_NMB[
                             i],
                         'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[i],
                         'NMB_PM': preliminary_daly_costs.FLQ_NMB[i],
                         'DALY_SdTreat_PM': preliminary_daly_costs.SdTreat_DALY[i] -
                                            preliminary_daly_costs.Exp_FLQ_DALY[i],
                         'DALY_SdTreat': preliminary_daly_costs.SdTreat_DALY[i],
                         'DALY_PM': preliminary_daly_costs.Exp_FLQ_DALY[i],
                         'Cost_SdTreat_PM': preliminary_daly_costs.SdTreat_cost[i] -
                                            preliminary_daly_costs.Exp_FLQ_cost[i],
                         'Cost_SdTreat': preliminary_daly_costs.SdTreat_cost[i],
                         'Cost_PM': preliminary_daly_costs.Exp_FLQ_cost[i]
                         }
                    )

                    # NMB, Cost and DALYs by FLQ susceptibility
                    if obs == 1:
                        nmb_daly_cost_flq_res_sus_pm_fun(preliminary_daly_costs, 'FLQ_Res', 'FLQ', i)
                    else:
                        nmb_daly_cost_flq_res_sus_pm_fun(preliminary_daly_costs, 'FLQ_Sus', 'FLQ', i)

            # NMB, Cost and DALYs by FLQ susceptibility
            NMB_DALY_Cost_FLQ_Res_Sus_PM_avg.append(
                {'threshold': t,
                 "NMB_SdTreat_PM_FLQ_Res": sum(
                     NMB_SdTreat_PM_FLQ_Res) / (FLQ_Res_prev * 540),
                 "NMB_SdTreat_FLQ_Res": sum(NMB_SdTreat_FLQ_Res) / (FLQ_Res_prev * 540),
                 "NMB_PM_FLQ_Res": sum(NMB_PM_FLQ_Res) / (FLQ_Res_prev * 540),
                 "DALY_SdTreat_PM_FLQ_Res": sum(DALY_SdTreat_PM_FLQ_Res) / (FLQ_Res_prev * 540),
                 "DALY_SdTreat_FLQ_Res": sum(DALY_SdTreat_FLQ_Res) / (FLQ_Res_prev * 540),
                 "DALY_PM_FLQ_Res": sum(DALY_PM_FLQ_Res) / (FLQ_Res_prev * 540),
                 "Cost_SdTreat_PM_FLQ_Res": sum(Cost_SdTreat_PM_FLQ_Res) / (FLQ_Res_prev * 540),
                 "Cost_SdTreat_FLQ_Res": sum(Cost_SdTreat_FLQ_Res) / (FLQ_Res_prev * 540),
                 "Cost_PM_FLQ_Res": sum(Cost_PM_FLQ_Res) / (FLQ_Res_prev * 540),
                 "NMB_SdTreat_PM_FLQ_Sus": sum(NMB_SdTreat_PM_FLQ_Sus) / (
                         1 - FLQ_Res_prev),
                 "NMB_SdTreat_FLQ_Sus": sum(NMB_SdTreat_FLQ_Sus) / ((
                                                                            1 - FLQ_Res_prev) * 540),
                 "NMB_PM_FLQ_Sus": sum(NMB_PM_FLQ_Sus) / ((
                                                                  1 - FLQ_Res_prev) * 540),
                 "DALY_SdTreat_PM_FLQ_Sus": sum(DALY_SdTreat_PM_FLQ_Sus) / ((
                                                                                    1 - FLQ_Res_prev) * 540),
                 "DALY_SdTreat_FLQ_Sus": sum(DALY_SdTreat_FLQ_Sus) / ((
                                                                              1 - FLQ_Res_prev) * 540),
                 "DALY_PM_FLQ_Sus": sum(DALY_PM_FLQ_Sus) / ((
                                                                    1 - FLQ_Res_prev) * 540),
                 "Cost_SdTreat_PM_FLQ_Sus": sum(Cost_SdTreat_PM_FLQ_Sus) / ((
                                                                                    1 - FLQ_Res_prev) * 540),
                 "Cost_SdTreat_FLQ_Sus": sum(Cost_SdTreat_FLQ_Sus) / ((
                                                                              1 - FLQ_Res_prev) * 540),
                 "Cost_PM_FLQ_Sus": sum(Cost_PM_FLQ_Sus) / ((
                                                                    1 - FLQ_Res_prev) * 540)
                 }
            )

    # Define the named tuple with fields that will hold dictionaries
    dr_tb_pm_output_t = namedtuple('dr_tb_pm_output',
                                   ['NMB_DALY_Cost_SdTreat_PM_eachpt',
                                    'NMB_DALY_Cost_FLQ_Res_Sus_PM_avg'])

    # Create an instance of the named tuple
    dr_tb_pm_output = dr_tb_pm_output_t(NMB_DALY_Cost_SdTreat_PM_eachpt=NMB_DALY_Cost_SdTreat_PM_eachpt,
                                        NMB_DALY_Cost_FLQ_Res_Sus_PM_avg=NMB_DALY_Cost_FLQ_Res_Sus_PM_avg)

    return dr_tb_pm_output


############ Function to calculate NMB, DALYs and Costs for the PM alone - SIMPLIFIED############
def dr_tb_pm_s(preliminary_daly_costs, sens_spec_PM, pred_data):
    # Initiating the vectors that store output
    NMB_DALY_Cost_SdTreat_PM_eachpt = []  # Change in NMB, DALYs and Cost when the optimal treatment (PM + DT) is used in comparison to the standard treatment and separately

    with open(sens_spec_PM, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            t = float(row['threshold'])

            for i, (pred, obs) in enumerate(
                    zip(pred_data['pred'], pred_data['obs'])):

                # NMB, Cost and DALYs by FLQ susceptibility
                if obs == 1:
                    FLQ_status = 'FLQ Resistant'
                else:
                    FLQ_status = 'FLQ Susceptible'

                if pred > t:

                    # NMB, DALYs and Costs for each patient
                    NMB_DALY_Cost_SdTreat_PM_eachpt.append(
                        {'threshold': t,
                         'Person': i,
                         'FLQ_Status': FLQ_status,
                         'Prediction_Model_Classification': 'FLQ Resistant',
                         'NMB_SdTreat_PM': preliminary_daly_costs.SdTreat_NMB[i] - preliminary_daly_costs.DLM_NMB[
                             i],
                         'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[i],
                         'NMB_PM': preliminary_daly_costs.DLM_NMB[i],
                         'DALY_SdTreat_PM': preliminary_daly_costs.SdTreat_DALY[i] -
                                            preliminary_daly_costs.Exp_DLM_DALY[i],
                         'DALY_SdTreat': preliminary_daly_costs.SdTreat_DALY[i],
                         'DALY_PM': preliminary_daly_costs.Exp_DLM_DALY[i],
                         'Cost_SdTreat_PM': preliminary_daly_costs.SdTreat_cost[i] -
                                            preliminary_daly_costs.Exp_DLM_cost[i],
                         'Cost_SdTreat': preliminary_daly_costs.SdTreat_cost[i],
                         'Cost_PM': preliminary_daly_costs.Exp_DLM_cost[i]
                         }
                    )

                else:

                    # NMB, DALYs and Costs for each patient
                    NMB_DALY_Cost_SdTreat_PM_eachpt.append(
                        {'threshold': t,
                         'Person': i,
                         'FLQ_Status': FLQ_status,
                         'Prediction_Model_Classification': 'FLQ Susceptible',
                         'NMB_SdTreat_PM': preliminary_daly_costs.SdTreat_NMB[i] - preliminary_daly_costs.FLQ_NMB[
                             i],
                         'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[i],
                         'NMB_PM': preliminary_daly_costs.FLQ_NMB[i],
                         'DALY_SdTreat_PM': preliminary_daly_costs.SdTreat_DALY[i] -
                                            preliminary_daly_costs.Exp_FLQ_DALY[i],
                         'DALY_SdTreat': preliminary_daly_costs.SdTreat_DALY[i],
                         'DALY_PM': preliminary_daly_costs.Exp_FLQ_DALY[i],
                         'Cost_SdTreat_PM': preliminary_daly_costs.SdTreat_cost[i] -
                                            preliminary_daly_costs.Exp_FLQ_cost[i],
                         'Cost_SdTreat': preliminary_daly_costs.SdTreat_cost[i],
                         'Cost_PM': preliminary_daly_costs.Exp_FLQ_cost[i]
                         }
                    )

    return NMB_DALY_Cost_SdTreat_PM_eachpt


############ Function to calculate NMB, DALYs and Costs for the DT alone ############
def dr_tb_dt(preliminary_daly_costs, pred_data, DALY_individual_Moldova, prob_data, cost_data, daly_data, wtp):
    # Make the table variables to be used - Probabilities in the tree
    for index, row in prob_data.iterrows():
        globals()[row['Probability Variable']] = row['Probability Value']

    # Make the table variables to be used - Costs in the tree
    for index, row in cost_data.iterrows():
        globals()[row['Cost Variable']] = row['Cost Value']

    # Make the table variables to be used - DALYs in the tree
    for index, row in daly_data.iterrows():
        globals()[row['DALY Variable']] = row['DALY Value']

    # Auxiliary function that calculates NMB, Cost and DALYs by FLQ susceptibility
    def nmb_daly_cost_flq_res_sus_dt_fun(preliminary_daly_costs, key_suffix, treatment_type, i):
        """ Calculate NMB, DALYs and Costs for a patient depending on the treatment type and FLQ resistance status
        :return: no explicit return
        """
        if key_suffix == 'FLQ_Res':
            NMB_SdTreat_DT_FLQ_Res.append(
                preliminary_daly_costs.SdTreat_NMB[i] - getattr(preliminary_daly_costs, f"{treatment_type}_NMB")[i])
            NMB_SdTreat_FLQ_Res.append(preliminary_daly_costs.SdTreat_NMB[i])
            NMB_DT_FLQ_Res.append(getattr(preliminary_daly_costs, f"{treatment_type}_NMB")[i])
            DALY_SdTreat_DT_FLQ_Res.append(
                preliminary_daly_costs.SdTreat_DALY[i] - getattr(preliminary_daly_costs, f"Exp_{treatment_type}_DALY")[
                    i])
            DALY_SdTreat_FLQ_Res.append(preliminary_daly_costs.SdTreat_DALY[i])
            DALY_DT_FLQ_Res.append(getattr(preliminary_daly_costs, f"Exp_{treatment_type}_DALY")[i])
            Cost_SdTreat_DT_FLQ_Res.append(
                preliminary_daly_costs.SdTreat_cost[i] - getattr(preliminary_daly_costs, f"Exp_{treatment_type}_cost")[
                    i])
            Cost_SdTreat_FLQ_Res.append(preliminary_daly_costs.SdTreat_cost[i])
            Cost_DT_FLQ_Res.append(getattr(preliminary_daly_costs, f"Exp_{treatment_type}_cost")[i])
        if key_suffix == 'FLQ_Sus':
            NMB_SdTreat_DT_FLQ_Sus.append(
                preliminary_daly_costs.SdTreat_NMB[i] - getattr(preliminary_daly_costs, f"{treatment_type}_NMB")[i])
            NMB_SdTreat_FLQ_Sus.append(preliminary_daly_costs.SdTreat_NMB[i])
            NMB_DT_FLQ_Sus.append(getattr(preliminary_daly_costs, f"{treatment_type}_NMB")[i])
            DALY_SdTreat_DT_FLQ_Sus.append(
                preliminary_daly_costs.SdTreat_DALY[i] - getattr(preliminary_daly_costs, f"Exp_{treatment_type}_DALY")[
                    i])
            DALY_SdTreat_FLQ_Sus.append(preliminary_daly_costs.SdTreat_DALY[i])
            DALY_DT_FLQ_Sus.append(getattr(preliminary_daly_costs, f"Exp_{treatment_type}_DALY")[i])
            Cost_SdTreat_DT_FLQ_Sus.append(
                preliminary_daly_costs.SdTreat_cost[i] - getattr(preliminary_daly_costs, f"Exp_{treatment_type}_cost")[
                    i])
            Cost_SdTreat_FLQ_Sus.append(preliminary_daly_costs.SdTreat_cost[i])
            Cost_DT_FLQ_Sus.append(getattr(preliminary_daly_costs, f"Exp_{treatment_type}_cost")[i])

    # Initiating the vectors that store output
    NMB_DALY_Cost_SdTreat_DT_eachpt = []  # Change in NMB, DALYs and Cost when the optimal treatment (PM + DT) is used in comparison to the standard treatment and separately
    NMB_DALY_Cost_FLQ_Res_Sus_DT_avg = []  # Change in NMB, DALYs and Cost depending on FLQ susceptibility

    # Terminal nodes
    CC_FLQsus = TerminalNode(name='CC_FLQsus', cost=Cost_CC_FLQsus, daly=DALY_CC_FLQsus)
    TF_FLQsus = TerminalNode(name='TF_FLQsus', cost=Cost_TF_FLQsus, daly=DALY_TF_FLQsus)
    CC_FLQres = TerminalNode(name='CC_FLQres', cost=Cost_CC_FLQres, daly=DALY_CC_FLQres)
    TF_FLQres = TerminalNode(name='TF_FLQres', cost=Cost_TF_FLQres, daly=DALY_TF_FLQres)
    CC_DLM = TerminalNode(name='CC_DLM', cost=Cost_CC_DLM, daly=DALY_CC_DLM)
    TF_DLM = TerminalNode(name='TF_DLM', cost=Cost_TF_DLM, daly=DALY_TF_DLM)

    # NMB, Cost and DALYs by FLQ susceptibility
    NMB_SdTreat_DT_FLQ_Res = []
    NMB_SdTreat_FLQ_Res = []
    NMB_DT_FLQ_Res = []
    DALY_SdTreat_DT_FLQ_Res = []
    DALY_SdTreat_FLQ_Res = []
    DALY_DT_FLQ_Res = []
    Cost_SdTreat_DT_FLQ_Res = []
    Cost_SdTreat_FLQ_Res = []
    Cost_DT_FLQ_Res = []
    NMB_SdTreat_DT_FLQ_Sus = []
    NMB_SdTreat_FLQ_Sus = []
    NMB_DT_FLQ_Sus = []
    DALY_SdTreat_DT_FLQ_Sus = []
    DALY_SdTreat_FLQ_Sus = []
    DALY_DT_FLQ_Sus = []
    Cost_SdTreat_DT_FLQ_Sus = []
    Cost_SdTreat_FLQ_Sus = []
    Cost_DT_FLQ_Sus = []

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

        # Chance Node
        C_FLQ_p = ChanceNode(name='C_FLQ_p', cost=Cost_FLQ, daly=DALY_FLQ,
                             future_nodes=[C_FLQsus, C_FLQres], probs=[(1 - FLQ_Res_prev), FLQ_Res_prev])
        # Decision Node
        D_p = DecisionNode(name='D_p', cost=0, daly=0, future_nodes=[C_FLQ_p, C_DLM])

        # Decision Tree
        DT_p = DecisionTree(name='DT_p', decision_nodes=D_p, willingness_to_pay=wtp)

        # Optimal Treatment
        Opt_Treat_p = DT_p.get_optimal_decision()[0]

        # NMB, Cost and DALYs by FLQ susceptibility
        if obs == 1:
            FLQ_status = 'FLQ Resistant'
        else:
            FLQ_status = 'FLQ Susceptible'

        # Select Optimal Treatment
        if Opt_Treat_p == 'C_DLM':

            # NMB, DALYs and Costs for each patient
            NMB_DALY_Cost_SdTreat_DT_eachpt.append(
                {'Person': i,
                 'FLQ_Status': FLQ_status,
                 'NMB_SdTreat_DT': preliminary_daly_costs.SdTreat_NMB[i] - preliminary_daly_costs.DLM_NMB[
                     i],
                 'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[i],
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

            # NMB, Cost and DALYs by FLQ susceptibility
            if obs == 1:
                nmb_daly_cost_flq_res_sus_dt_fun(preliminary_daly_costs, 'FLQ_Res', 'DLM', i)
            else:
                nmb_daly_cost_flq_res_sus_dt_fun(preliminary_daly_costs, 'FLQ_Sus', 'DLM', i)

        else:

            # NMB, DALYs and Costs for each patient
            NMB_DALY_Cost_SdTreat_DT_eachpt.append(
                {'Person': i,
                 'FLQ_Status': FLQ_status,
                 'NMB_SdTreat_DT': preliminary_daly_costs.SdTreat_NMB[i] - preliminary_daly_costs.FLQ_NMB[
                     i],
                 'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[i],
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

            # NMB, Cost and DALYs by FLQ susceptibility
            if obs == 1:
                nmb_daly_cost_flq_res_sus_dt_fun(preliminary_daly_costs, 'FLQ_Res', 'FLQ', i)
            else:
                nmb_daly_cost_flq_res_sus_dt_fun(preliminary_daly_costs, 'FLQ_Sus', 'FLQ', i)

    # NMB, Cost and DALYs by FLQ susceptibility
    NMB_DALY_Cost_FLQ_Res_Sus_DT_avg.append(
        {"NMB_SdTreat_DT_FLQ_Res": sum(
            NMB_SdTreat_DT_FLQ_Res) / (FLQ_Res_prev * 540),
         "NMB_SdTreat_FLQ_Res": sum(NMB_SdTreat_FLQ_Res) / (FLQ_Res_prev * 540),
         "NMB_DT_FLQ_Res": sum(NMB_DT_FLQ_Res) / (FLQ_Res_prev * 540),
         "DALY_SdTreat_DT_FLQ_Res": sum(DALY_SdTreat_DT_FLQ_Res) / (FLQ_Res_prev * 540),
         "DALY_SdTreat_FLQ_Res": sum(DALY_SdTreat_FLQ_Res) / (FLQ_Res_prev * 540),
         "DALY_DT_FLQ_Res": sum(DALY_DT_FLQ_Res) / (FLQ_Res_prev * 540),
         "Cost_SdTreat_DT_FLQ_Res": sum(Cost_SdTreat_DT_FLQ_Res) / (FLQ_Res_prev * 540),
         "Cost_SdTreat_FLQ_Res": sum(Cost_SdTreat_FLQ_Res) / (FLQ_Res_prev * 540),
         "Cost_DT_FLQ_Res": sum(Cost_DT_FLQ_Res) / (FLQ_Res_prev * 540),
         "NMB_SdTreat_DT_FLQ_Sus": sum(NMB_SdTreat_DT_FLQ_Sus) / ((
                                                                          1 - FLQ_Res_prev) * 540),
         "NMB_SdTreat_FLQ_Sus": sum(NMB_SdTreat_FLQ_Sus) / ((
                                                                    1 - FLQ_Res_prev) * 540),
         "NMB_DT_FLQ_Sus": sum(NMB_DT_FLQ_Sus) / ((
                                                          1 - FLQ_Res_prev) * 540),
         "DALY_SdTreat_DT_FLQ_Sus": sum(DALY_SdTreat_DT_FLQ_Sus) / ((
                                                                            1 - FLQ_Res_prev) * 540),
         "DALY_SdTreat_FLQ_Sus": sum(DALY_SdTreat_FLQ_Sus) / ((
                                                                      1 - FLQ_Res_prev) * 540),
         "DALY_DT_FLQ_Sus": sum(DALY_DT_FLQ_Sus) / ((
                                                            1 - FLQ_Res_prev) * 540),
         "Cost_SdTreat_DT_FLQ_Sus": sum(Cost_SdTreat_DT_FLQ_Sus) / ((
                                                                            1 - FLQ_Res_prev) * 540),
         "Cost_SdTreat_FLQ_Sus": sum(Cost_SdTreat_FLQ_Sus) / ((
                                                                      1 - FLQ_Res_prev) * 540),
         "Cost_DT_FLQ_Sus": sum(Cost_DT_FLQ_Sus) / ((
                                                            1 - FLQ_Res_prev) * 540)
         }
    )

    # Define the named tuple with fields that will hold dictionaries
    dr_tb_dt_output_t = namedtuple('dr_tb_tree_output',
                                   ['NMB_DALY_Cost_SdTreat_DT_eachpt', 'NMB_DALY_Cost_FLQ_Res_Sus_DT_avg'])

    # Create an instance of the named tuple
    dr_tb_dt_output = dr_tb_dt_output_t(NMB_DALY_Cost_SdTreat_DT_eachpt=NMB_DALY_Cost_SdTreat_DT_eachpt,
                                        NMB_DALY_Cost_FLQ_Res_Sus_DT_avg=NMB_DALY_Cost_FLQ_Res_Sus_DT_avg)

    return dr_tb_dt_output


############ Function to calculate NMB, DALYs and Costs for the DT alone - SIMPLIFIED############
def dr_tb_dt_s(preliminary_daly_costs, pred_data, DALY_individual_Moldova, prob_data, cost_data, daly_data, wtp):
    # Make the table variables to be used - Probabilities in the tree
    for index, row in prob_data.iterrows():
        globals()[row['Probability Variable']] = row['Probability Value']

    # Make the table variables to be used - Costs in the tree
    for index, row in cost_data.iterrows():
        globals()[row['Cost Variable']] = row['Cost Value']

    # Make the table variables to be used - DALYs in the tree
    for index, row in daly_data.iterrows():
        globals()[row['DALY Variable']] = row['DALY Value']

    # Initiating the vectors that store output
    NMB_DALY_Cost_SdTreat_DT_eachpt = []  # Change in NMB, DALYs and Cost when the optimal treatment (PM + DT) is used in comparison to the standard treatment and separately

    # Terminal nodes
    CC_FLQsus = TerminalNode(name='CC_FLQsus', cost=Cost_CC_FLQsus, daly=DALY_CC_FLQsus)
    TF_FLQsus = TerminalNode(name='TF_FLQsus', cost=Cost_TF_FLQsus, daly=DALY_TF_FLQsus)
    CC_FLQres = TerminalNode(name='CC_FLQres', cost=Cost_CC_FLQres, daly=DALY_CC_FLQres)
    TF_FLQres = TerminalNode(name='TF_FLQres', cost=Cost_TF_FLQres, daly=DALY_TF_FLQres)
    CC_DLM = TerminalNode(name='CC_DLM', cost=Cost_CC_DLM, daly=DALY_CC_DLM)
    TF_DLM = TerminalNode(name='TF_DLM', cost=Cost_TF_DLM, daly=DALY_TF_DLM)

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

        # Chance Node
        C_FLQ_p = ChanceNode(name='C_FLQ_p', cost=Cost_FLQ, daly=DALY_FLQ,
                             future_nodes=[C_FLQsus, C_FLQres], probs=[(1 - FLQ_Res_prev), FLQ_Res_prev])
        # Decision Node
        D_p = DecisionNode(name='D_p', cost=0, daly=0, future_nodes=[C_FLQ_p, C_DLM])

        # Decision Tree
        DT_p = DecisionTree(name='DT_p', decision_nodes=D_p, willingness_to_pay=wtp)

        # Optimal Treatment
        Opt_Treat_p = DT_p.get_optimal_decision()[0]

        # NMB, Cost and DALYs by FLQ susceptibility
        if obs == 1:
            FLQ_status = 'FLQ Resistant'
        else:
            FLQ_status = 'FLQ Susceptible'

        # Select Optimal Treatment
        if Opt_Treat_p == 'C_DLM':

            # NMB, DALYs and Costs for each patient
            NMB_DALY_Cost_SdTreat_DT_eachpt.append(
                {'Person': i,
                 'FLQ_Status': FLQ_status,
                 'NMB_SdTreat_DT': preliminary_daly_costs.SdTreat_NMB[i] - preliminary_daly_costs.DLM_NMB[
                     i],
                 'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[i],
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
                 'NMB_SdTreat_DT': preliminary_daly_costs.SdTreat_NMB[i] - preliminary_daly_costs.FLQ_NMB[
                     i],
                 'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[i],
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

    return NMB_DALY_Cost_SdTreat_DT_eachpt


if __name__ == "__main__":
    wtp = GDP_moldova
    ############ Preliminary Costs and DALY Calculation ############
    # Calculated expected costs and DALYs for ach treatment depending on FLQ susceptibility
    preliminary_daly_costs = calculate_pre_daly_cost(pred_data, DALY_individual_Moldova, prob_data, cost_data_prior,
                                                     daly_data_prior, wtp)
    ############ End Preliminary Costs and ############

    test = dr_tb_pm_dt(preliminary_daly_costs, sens_spec_PM, pred_data, DALY_individual_Moldova, wtp)

    # # testing if dictionary is being attached properly
    # print(test.NMB_DALY_Cost_SdTreat_PMDT_eachpt)
    #
    # # Testing if it is converted to a data frame=
    # print(pd.DataFrame(test.NMB_DALY_Cost_FLQ_DLM_class_avg))

    # for k in range(5):
    #     exec(f'cat_{k} = dr_tb_tree(preliminary_daly_costs, sens_spec_PM, pred_data, DALY_individual_Moldova, wtp)')
    #
    # print(cat_0)
    # print(cat_1)