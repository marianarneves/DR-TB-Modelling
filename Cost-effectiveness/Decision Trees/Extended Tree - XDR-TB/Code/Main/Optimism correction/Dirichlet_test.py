import numpy as np
import matplotlib.pyplot as plt

def plot_dirichlet(alpha, title):
    samples = np.random.dirichlet(alpha, size=1000)
    plt.scatter(samples[:, 0], samples[:, 1], alpha=0.5)
    plt.title(title)
    plt.xlabel("p1")
    plt.ylabel("p2")
    plt.axis("equal")
    plt.show()

# Example alphas for different c values
alpha_small = [0.1, 0.3, 0.6]  # c = 1
alpha_moderate = [0.5, 1.5, 3]  # c = 5
alpha_moderate2 = [1, 3, 6]  # c = 5
alpha_moderate3 = [5,15, 30]  # c = 5
alpha_large = [10, 30, 60]      # c = 100

plot_dirichlet(alpha_small, "Small c (c=1)")
plot_dirichlet(alpha_moderate, "Moderate c (c=5)")
plot_dirichlet(alpha_moderate2, "Moderate c (c=10)")
plot_dirichlet(alpha_moderate3, "Moderate c (c=50)")
plot_dirichlet(alpha_large, "Large c (c=100)")
