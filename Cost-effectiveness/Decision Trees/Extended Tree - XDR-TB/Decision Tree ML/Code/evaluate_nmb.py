# === modeling/evaluate_nmb.py ===
def _prepare_treatment_result(pred_df, preliminary_daly_costs, DALY_individual_Moldova, wtp, threshold):
    results = []
    for i, (DALY_Death, pred, obs, pt) in enumerate(zip(DALY_individual_Moldova, pred_df['predicted'], pred_df['observed'], pred_df['Pt_id'])):
        FLQ_status = 'FLQ Resistant' if obs == 1 else 'FLQ Susceptible'
        if pred == 1:
            # BPaLC (DLM)
            NMB_SdTreat_DM = preliminary_daly_costs.SdTreat_NMB[pt-1] - preliminary_daly_costs.DLM_NMB[pt-1]
            NMB_DM = preliminary_daly_costs.DLM_NMB[pt-1]
            DALY_SdTreat_DM = preliminary_daly_costs.SdTreat_DALY[pt-1] - preliminary_daly_costs.Exp_DLM_DALY[pt-1]
            DALY_DM = preliminary_daly_costs.Exp_DLM_DALY[pt-1]
            Cost_SdTreat_DM = preliminary_daly_costs.SdTreat_cost[pt-1] - preliminary_daly_costs.Exp_DLM_cost[pt-1]
            Cost_DM = preliminary_daly_costs.Exp_DLM_cost[pt-1]
            PM_classification = 'FLQ Resistant'
            optimal_treat = 'BPaLC'
        elif pred == 0:
            # BPaLM (FLQ)
            NMB_SdTreat_DM = preliminary_daly_costs.SdTreat_NMB[pt-1] - preliminary_daly_costs.FLQ_NMB[pt-1]
            NMB_DM = preliminary_daly_costs.FLQ_NMB[pt-1]
            DALY_SdTreat_DM = preliminary_daly_costs.SdTreat_DALY[pt-1] - preliminary_daly_costs.Exp_FLQ_DALY[pt-1]
            DALY_DM = preliminary_daly_costs.Exp_FLQ_DALY[pt-1]
            Cost_SdTreat_DM = preliminary_daly_costs.SdTreat_cost[pt-1] - preliminary_daly_costs.Exp_FLQ_cost[pt-1]
            Cost_DM = preliminary_daly_costs.Exp_FLQ_cost[pt-1]
            PM_classification = 'FLQ Susceptible'
            optimal_treat = 'BPaLM'
        else:
            NMB_SdTreat_DM = NMB_DM = DALY_SdTreat_DM = DALY_DM = Cost_SdTreat_DM = Cost_DM = float('nan')
            PM_classification = 'Unknown'
            optimal_treat = 'Unknown'

        result = {
            'Person': pt,
            'Threshold': threshold,
            'PM_classification': PM_classification,
            'FLQ_Status': FLQ_status,
            'Opt_Treat': optimal_treat,
            'NMB_SdTreat_DM': NMB_SdTreat_DM,
            'NMB_SdTreat': preliminary_daly_costs.SdTreat_NMB[pt - 1],
            'NMB_SdTreat_FLQ': wtp * preliminary_daly_costs.Exp_FLQ_SdTreat_DALY[pt - 1] +
                               preliminary_daly_costs.Exp_FLQ_SdTreat_cost[pt - 1],
            'NMB_DM': NMB_DM,
            'DALY_SdTreat_DM': DALY_SdTreat_DM,
            'DALY_SdTreat': preliminary_daly_costs.SdTreat_DALY[pt - 1],
            'DALY_DM': DALY_DM,
            'Cost_SdTreat_DM': Cost_SdTreat_DM,
            'Cost_SdTreat': preliminary_daly_costs.SdTreat_cost[pt - 1],
            'Cost_DM': Cost_DM
        }
        results.append(result)
    return results
