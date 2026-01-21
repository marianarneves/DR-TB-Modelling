import pyAgrum as gum
import pyAgrum.lib.notebook as gnb

# Assuming you already have your dataset loaded as 'data'
# Load the dataset


# Learn both structure and parameters of the Bayesian Network
learner = gum.BNLearner("/Users/mrn29/Library/CloudStorage/OneDrive-YaleUniversity/Yale/TB/Republic of Moldova data/DATA_tb_moldova_NN.csv")  # Replace "data.csv" with the filename of your dataset
bn_learned = learner.learnBN()

# Visualize the learned structure
gnb.showBN(bn_learned)
