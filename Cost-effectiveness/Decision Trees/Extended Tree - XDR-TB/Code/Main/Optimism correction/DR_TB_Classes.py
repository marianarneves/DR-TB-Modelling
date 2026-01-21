class Node:
    """ base (parent) class for nodes """
    def __init__(self, name, cost, daly):
        """
        :param name: name of this node
        :param cost: cost of visiting this node
        :param daly: daly incurred by visiting this node
        """

        self.name = name
        self.cost = cost
        self.daly = daly

    def get_expected_cost(self):
        """ abstract method to be overridden in derived classes
        :returns expected cost of this node """

    def get_expected_daly(self):
        """ abstract method to be overridden in derived classes
        :returns expected daly of this node """


class ChanceNode(Node):

    def __init__(self, name, cost, daly, future_nodes, probs):
        """
        :param name: name of this node
        :param cost: cost of visiting this node
        :param daly: daly incurred by visiting this node
        :param future_nodes: (list) future nodes connected to this node
        :param probs: (list) probability of future nodes
        """

        Node.__init__(self, name, cost, daly)
        self.futureNodes = future_nodes
        self.probs = probs

    def get_expected_cost(self):
        """
        :return: expected cost of this chance node
        E[cost] = (cost of visiting this node)
                  + sum_{i}(probability of future node i)*(E[cost of future node i])
        """

        num_outcomes = len(self.probs)  # number of outcomes
        exp_cost = self.cost  # initialize with the cost of this node

        # go over possible outcomes
        for i in range(num_outcomes):
            exp_cost += self.probs[i] * self.futureNodes[i].get_expected_cost()

        return exp_cost

    def get_expected_daly(self):
        """
        :return: expected daly incurred by visiting this chance node
        E[daly] = (daly incurred by visiting this node)
                  + sum_{i}(probability of future node i)*(E[daly incurred by future node i])
        """

        num_outcomes = len(self.probs)  # number of outcomes
        exp_daly = self.daly  # initialize with the cost of this node

        # go over possible outcomes
        for i in range(num_outcomes):
            exp_daly += self.probs[i] * self.futureNodes[i].get_expected_daly()

        return exp_daly


class TerminalNode(Node):

    def __init__(self, name, cost, daly):
        """
        :param name: name of this node
        :param cost: cost of visiting this node
        """

        Node.__init__(self, name, cost, daly)

    def get_expected_cost(self):
        """
        :return: cost of this visiting this terminal node
        """
        return self.cost

    def get_expected_daly(self):
        """
        :return: daly incurred by visiting this terminal node
        """
        return self.daly


class DecisionNode(Node):

    def __init__(self, name, cost, daly, future_nodes):
        """
        :param name: name of this node
        :param cost: cost of visiting this node
        :param daly: daly incurred by visiting this node
        :param future_nodes: (list) future nodes connected to this node
        (assumes that future nodes can only be chance or terminal nodes)
        """

        Node.__init__(self, name, cost, daly)
        self.futureNode = future_nodes

    def get_expected_cost(self):
        """ returns the expected costs of future nodes
        :return: a dictionary of expected costs of future nodes with node names as dictionary keys
        """

        # a dictionary to store the expected cost of future nodes
        exp_costs = dict()
        # go over all future nodes
        for node in self.futureNode:
            # add the expected cost of this future node to the dictionary
            exp_costs[node.name] = self.cost + node.get_expected_cost()

        return exp_costs

    def get_expected_daly(self):
        """ returns the expected daly incurred by visiting future nodes
        :return: a dictionary of expected dalys incurred by visiting future nodes with node names as dictionary keys
        """

        # a dictionary to store the expected cost of future nodes
        exp_daly = dict()
        # go over all future nodes
        for node in self.futureNode:
            # add the expected cost of this future node to the dictionary
            exp_daly[node.name] = self.daly + node.get_expected_daly()

        return exp_daly


class DecisionTree():

    def __init__(self, name, decision_nodes, willingness_to_pay):
        """
        :param name: name of the tree
        :param decision_nodes: (list) decision nodes connected to this node
        (assumes that future nodes can only be chance or terminal nodes)
        :param willingness_to_pay: the assumed willingness to pay threshold
        """

        self.name = name
        self.decisionNode = decision_nodes
        self.wtp = willingness_to_pay


    def get_expected_nmb(self):
        """ returns the expected Net Monetary Benefit of future nodes
        :return: a dictionary of expected costs of future nodes with node names as dictionary keys
        """

        # a dictionary to store the expected cost of future nodes
        exp_nmb_loss = dict()
        # go over all future nodes
        for node in self.decisionNode.futureNode:
            # add the expected cost of this future node to the dictionary
            exp_nmb_loss[node.name] = self.wtp * node.get_expected_daly() + node.get_expected_cost()

        return exp_nmb_loss

    def get_optimal_decision(self):
        """ returns the node with the minimum expected NMB loss
        :return: a tuple with the name of the node with minimum expected NMB loss and the loss value
        """
        exp_nmb_loss = self.get_expected_nmb()
        min_node = min(exp_nmb_loss, key=exp_nmb_loss.get)
        return min_node, exp_nmb_loss[min_node]


if __name__ == "__main__":
    #test
    a = TerminalNode(name = "a", cost = 10, daly = 0.5)
    b = TerminalNode(name = "b", cost = 20, daly = 0.1)
    c = TerminalNode(name = "c", cost = 5, daly = 0.5)
    d = TerminalNode(name = "d", cost = 30, daly = 0.5)

    e = ChanceNode(name = "e", cost = 0, daly = 0, future_nodes = [a, b], probs = [0.1, 0.9])
    f = ChanceNode(name = "f", cost = 0, daly = 0, future_nodes = [c, d], probs = [0.4, 0.6])

    g = DecisionNode(name = "g", cost = 0, daly = 0, future_nodes = [e, f])


    h = DecisionTree(name = "h", decision_nodes = g, willingness_to_pay =2)

    print(g.get_expected_cost()['e'])
    print(g.get_expected_daly()['e'])
    print(g.get_expected_cost()['f'])
    print(g.get_expected_daly()['f'])

    print(h.get_expected_nmb()['e'])
    print(h.get_expected_nmb()['f'])

    print(h.get_optimal_decision())

