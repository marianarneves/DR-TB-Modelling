import numpy as np
import pandas as pd
from scipy.stats import beta, norm, t
import matplotlib.pyplot as plt
import seaborn as sns

# Set seed for reproducibility
np.random.seed(42)

# Fixed parameters
wtp = 30000
n_patients = 540
nsim_values = [10, 50, 100, 500, 1000, 2000, 5000]

# Fixed patient illness status
p_ill = 0.19
ill_status = np.random.binomial(1, p_ill, size=n_patients)

p_cure_ill_treat = 0.85
p_cure_notill = 0.99

# ========= Average NMB by patient
results_pt = []

for nsim in nsim_values:
    mean_nmbs = []

    for j in range(n_patients):
        cost_cure_ill = norm.rvs(loc=20000, scale=200, size=nsim)
        cost_death_ill = norm.rvs(loc=100000, scale=200, size=nsim)
        cost_cure_notill = norm.rvs(loc=30000, scale=200, size=nsim)
        cost_death_notill = norm.rvs(loc=100000, scale=200, size=nsim)
        qaly_cure_ill = beta.rvs(a=90, b=10, size=nsim)
        qaly_cure_notill = beta.rvs(a=50, b=50, size=nsim)

        ill_status_pt = np.repeat(ill_status[j], nsim)

        qaly = np.where(
            ill_status_pt == 1,
            p_cure_ill_treat * qaly_cure_ill,
            p_cure_notill * qaly_cure_notill
        )
        cost = np.where(
            ill_status_pt == 1,
            p_cure_ill_treat * cost_cure_ill + (1 - p_cure_ill_treat) * cost_death_ill,
            p_cure_notill * cost_cure_notill + (1 - p_cure_notill) * cost_death_notill
        )

        nmb = qaly * wtp - cost
        mean_nmbs.append(np.mean(nmb))

    mean_nmb = np.mean(mean_nmbs)
    se_nmb = np.std(mean_nmbs, ddof=1) / np.sqrt(n_patients)
    t_crit = t.ppf(0.975, df=n_patients - 1)
    ci_lower = mean_nmb - t_crit * se_nmb
    ci_upper = mean_nmb + t_crit * se_nmb

    results_pt.append({
        "nsim": nsim,
        "mean_nmb": mean_nmb,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper
    })

df_pt = pd.DataFrame(results_pt)

# Plot
sns.set(style="whitegrid")
plt.figure(figsize=(10, 6))
plt.plot(df_pt["nsim"], df_pt["mean_nmb"], marker='o', color='steelblue')
plt.fill_between(df_pt["nsim"], df_pt["ci_lower"], df_pt["ci_upper"], color='steelblue', alpha=0.2)
plt.ylim(-15000, -14000)
plt.title("Expected NMB by patient with 95% CI vs. Number of Parameter Simulations (Per Patient)")
plt.xlabel("Number of Simulations (nsim)")
plt.ylabel("Mean Net Monetary Benefit (Treat All Patients)")
plt.show()

# ========= Average NMB by simulation
results_sim = []

for nsim in nsim_values:
    mean_nmbs = []

    for k in range(nsim):
        cost_cure_ill = norm.rvs(loc=20000, scale=200)
        cost_death_ill = norm.rvs(loc=100000, scale=200)
        cost_cure_notill = norm.rvs(loc=30000, scale=200)
        cost_death_notill = norm.rvs(loc=100000, scale=200)
        qaly_cure_ill = beta.rvs(a=90, b=10)
        qaly_cure_notill = beta.rvs(a=50, b=50)

        qaly = np.where(
            ill_status == 1,
            p_cure_ill_treat * qaly_cure_ill,
            p_cure_notill * qaly_cure_notill
        )
        cost = np.where(
            ill_status == 1,
            p_cure_ill_treat * cost_cure_ill + (1 - p_cure_ill_treat) * cost_death_ill,
            p_cure_notill * cost_cure_notill + (1 - p_cure_notill) * cost_death_notill
        )

        nmb = qaly * wtp - cost
        mean_nmbs.append(np.mean(nmb))

    mean_nmb = np.mean(mean_nmbs)
    se_nmb = np.std(mean_nmbs, ddof=1) / np.sqrt(nsim)
    t_crit = t.ppf(0.975, df=nsim - 1)
    ci_lower = mean_nmb - t_crit * se_nmb
    ci_upper = mean_nmb + t_crit * se_nmb

    results_sim.append({
        "nsim": nsim,
        "mean_nmb": mean_nmb,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper
    })

df_sim = pd.DataFrame(results_sim)

# Plot
plt.figure(figsize=(10, 6))
plt.plot(df_sim["nsim"], df_sim["mean_nmb"], marker='o', color='steelblue')
plt.fill_between(df_sim["nsim"], df_sim["ci_lower"], df_sim["ci_upper"], color='steelblue', alpha=0.2)
plt.ylim(-15000, -14000)
plt.title("Expected NMB by simulation with 95% CI vs. Number of Parameter Simulations (Per Simulation)")
plt.xlabel("Number of Simulations (nsim)")
plt.ylabel("Mean Net Monetary Benefit (Treat All Patients)")
plt.show()
