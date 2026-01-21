set.seed(42)
library(dplyr)
library(ggplot2)

# Fixed parameters
wtp <- 30000
n_patients <- 540  # fixed number of patients

# Simulation sizes to evaluate
nsim_values <- c(10, 50, 100, 500, 1000, 2000, 5000)

# Fixed patient illness status
p_ill <- 0.19
ill_status <- rbinom(n_patients, 1, p_ill)

p_cure_ill_treat <- 0.85
p_cure_notill <- 0.99

#========= Average NMB by patient

# Store results
results_pt <- data.frame()

for (nsim in nsim_values) {

  mean_nmbs = c()
  
  for(j in 1:n_patients) {
    # Store mean NMBs from each parameter simulation
    
    cost_cure_ill <- rnorm(nsim, mean = 20000, sd = 200)
    cost_death_ill <- rnorm(nsim, mean = 100000, sd = 200)
    cost_cure_notill <- rnorm(nsim, mean = 30000, sd = 200)
    cost_death_notill <- rnorm(nsim, mean = 100000, sd = 200)
    qaly_cure_ill <- rbeta(nsim, 90, 10)
    qaly_cure_notill <- rbeta(nsim, 50, 50)
    
    ill_status_pt = rep(ill_status[j], nsim)
      
    qaly <- ifelse(ill_status_pt == 1, p_cure_ill_treat * qaly_cure_ill , qaly_cure_notill * p_cure_notill)
    cost <- ifelse(ill_status_pt == 1, p_cure_ill_treat * cost_cure_ill + (1-p_cure_ill_treat)*cost_death_ill, 
                     p_cure_notill * cost_cure_notill + (1-p_cure_notill)*cost_death_notill)
      
    nmb <- qaly * wtp - cost
    mean_nmbs[j] <- mean(nmb)
  }
  
  # Calculate mean and t-distribution CI
  mean_nmb <- mean(mean_nmbs)
  se_nmb <- sd(mean_nmbs) / sqrt(n_patients)
  t_crit <- qt(0.975, df = n_patients - 1)
  ci_lower <- mean_nmb - t_crit * se_nmb
  ci_upper <- mean_nmb + t_crit * se_nmb
  
  results_pt <- rbind(results_pt, data.frame(
    nsim = nsim,
    mean_nmb = mean_nmb,
    ci_lower = ci_lower,
    ci_upper = ci_upper
  ))
}

# Plotting the results_pt
ggplot(results_pt, aes(x = nsim, y = mean_nmb)) +
  geom_line(color = "steelblue") +
  geom_point(color = "steelblue") +
  geom_ribbon(aes(ymin = ci_lower, ymax = ci_upper), alpha = 0.2, fill = "steelblue") +
  coord_cartesian(ylim = c(-15000, -14000)) +
  theme_minimal() +
  labs(
    title = "Expected NMB with 95% t-based CI vs. Number of Parameter Simulations",
    x = "Number of Simulations (nsim)",
    y = "Mean Net Monetary Benefit (Treat All Patients)"
  )


#========= Average NMB by simulation

# Store results
results_sim <- data.frame()

for (nsim in nsim_values) {
  
  mean_nmbs = c()

  for(k in 1:nsim) {
      # Store mean NMBs from each parameter simulation
      
    cost_cure_ill <- rnorm(1, mean = 20000, sd = 200)
    cost_death_ill <- rnorm(1, mean = 100000, sd = 200)
    cost_cure_notill <- rnorm(1, mean = 30000, sd = 200)
    cost_death_notill <- rnorm(1, mean = 100000, sd = 200)
    qaly_cure_ill <- rbeta(1, 90, 10)
    qaly_cure_notill <- rbeta(1, 50, 50)
    
    qaly <- ifelse(ill_status == 1, p_cure_ill_treat * qaly_cure_ill , qaly_cure_notill * p_cure_notill)
    cost <- ifelse(ill_status == 1, p_cure_ill_treat * cost_cure_ill + (1-p_cure_ill_treat)*cost_death_ill, 
                   p_cure_notill * cost_cure_notill + (1-p_cure_notill)*cost_death_notill)
    
    nmb <- qaly * wtp - cost
    mean_nmbs[k] <- mean(nmb)
  } 
  # Calculate mean and t-distribution CI
  mean_nmb <- mean(mean_nmbs)
  se_nmb <- sd(mean_nmbs) / sqrt(nsim)
  t_crit <- qt(0.975, df = nsim - 1)
  ci_lower <- mean_nmb - t_crit * se_nmb
  ci_upper <- mean_nmb + t_crit * se_nmb
  
  results_sim <- rbind(results_sim, data.frame(
    nsim = nsim,
    mean_nmb = mean_nmb,
    ci_lower = ci_lower,
    ci_upper = ci_upper
  ))
}



# Plotting the results
ggplot(results_sim, aes(x = nsim, y = mean_nmb)) +
  geom_line(color = "steelblue") +
  geom_point(color = "steelblue") +
  geom_ribbon(aes(ymin = ci_lower, ymax = ci_upper), alpha = 0.2, fill = "steelblue") +
  coord_cartesian(ylim = c(-15000, -14000)) +
  theme_minimal() +
  labs(
    title = "Expected NMB with 95% t-based CI vs. Number of Parameter Simulations",
    x = "Number of Simulations (nsim)",
    y = "Mean Net Monetary Benefit (Treat All Patients)"
  )
