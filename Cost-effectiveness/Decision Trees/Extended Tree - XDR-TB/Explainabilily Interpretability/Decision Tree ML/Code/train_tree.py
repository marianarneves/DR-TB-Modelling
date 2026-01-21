# === modeling/train_tree.py ===
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier
import numpy as np

def tune_tree_depth(X, y, random_state, max_treedepth = 'None'):
    """
    Tunes the maximum depth (max_depth) of a decision tree using cross-validation.

    Pre-pruning in decision trees can be done by limiting the depth of the tree.
    A shallower tree is less complex (less risk of overfitting) but might underfit,
    while a deeper tree captures more patterns (risk of overfitting).

    This function:
    1. Defines a grid of candidate depths (1 to 10).
    2. Uses GridSearchCV with k-fold cross-validation to evaluate
       accuracy at each depth.
    3. Selects the depth that yields the best mean cross-validation accuracy.
    4. Plots mean CV accuracy against depth, to visualize how model
       performance changes with increasing complexity.

    Parameters
    ----------
    X : pd.DataFrame or np.ndarray
        Feature matrix.
    y : pd.Series or np.ndarray
        Target vector.
    random_state : int
        Seed for reproducibility.

    Returns
    -------
    best_depth : int
        The max_depth value that gave the highest cross-validation accuracy.
    """

    # Step 1: candidate depths to test
    param_grid = {'max_depth': list(range(1, max_treedepth))}

    # Step 2: cross-validation search
    grid_search = GridSearchCV(
        DecisionTreeClassifier(random_state=random_state),
        param_grid,
        cv=10,
        scoring='accuracy'
    )
    grid_search.fit(X, y)

    # Step 3: best-performing depth
    best_depth = grid_search.best_params_['max_depth']

    # Step 4: collect mean CV scores for each depth
    results = grid_search.cv_results_
    depths = param_grid['max_depth']
    mean_scores_by_depth = {
        params['max_depth']: results['mean_test_score'][i]
        for i, params in enumerate(results['params'])
    }
    mean_scores_ordered = [mean_scores_by_depth[d] for d in depths]

    # Step 5: plot depth vs CV accuracy
    # plt.figure(figsize=(8, 5))
    # plot_depths = [d if d is not None else 11 for d in depths]
    # plt.plot(plot_depths, mean_scores_ordered, marker='o')
    # plt.title('CV Accuracy vs. Tree Depth')
    # plt.xlabel('max_depth')
    # plt.ylabel('Mean CV Accuracy')
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()

    return {"max_depth": best_depth}


from sklearn.tree import _tree

def prune_redundant_nodes(decision_tree):
    tree = decision_tree.tree_

    def prune(node):
        # if it's not a leaf
        if tree.children_left[node] != _tree.TREE_LEAF:
            left = tree.children_left[node]
            right = tree.children_right[node]

            # prune recursively
            prune(left)
            prune(right)

            # if both children are leaves and predict the same class
            if (
                    tree.children_left[left] == _tree.TREE_LEAF and
                    tree.children_left[right] == _tree.TREE_LEAF and
                    tree.value[left].argmax() == tree.value[right].argmax()
            ):
                # make this node a leaf
                tree.children_left[node] = _tree.TREE_LEAF
                tree.children_right[node] = _tree.TREE_LEAF
                tree.feature[node] = _tree.TREE_UNDEFINED

    prune(0)


def tune_tree_pruning(X, y, random_state):
    """
    Tunes the complexity parameter (ccp_alpha) of a decision tree using cross-validation.

    Post-pruning in scikit-learn is done using minimal cost-complexity pruning.
    The tree is first grown to its full depth, and then nodes are pruned away
    if the improvement in impurity is smaller than a penalty controlled by ccp_alpha.

    Steps:
    1. Fit an initial tree to get the effective alphas.
    2. Use GridSearchCV to cross-validate accuracy for each alpha.
    3. Select the alpha with highest mean CV accuracy.
    4. Plot CV accuracy vs alpha for visualization.

    Returns
    -------
    dict
        {'ccp_alpha': best_alpha}, ready to unpack into train_final_tree.
    """

    # Check if y has more than one class
    unique_classes = np.unique(y)
    if len(unique_classes) == 1:
        print(f"Only one class ({unique_classes[0]}) in y. Skipping pruning.")
        return {"ccp_alpha": 0.0}  # no pruning possible

    # Step 1: get candidate alphas
    clf = DecisionTreeClassifier(random_state=random_state)
    path = clf.cost_complexity_pruning_path(X, y)
    ccp_alphas = path.ccp_alphas

    if len(ccp_alphas) > 1:
        ccp_alphas = path.ccp_alphas[:-1]  # drop largest alpha (prunes everything)

    # Step 2: cross-validation grid search
    param_grid = {"ccp_alpha": ccp_alphas}
    grid_search = GridSearchCV(
        DecisionTreeClassifier(random_state=random_state),
        param_grid,
        cv=10,
        scoring="accuracy"
    )
    grid_search.fit(X, y)

    # Step 3: best alpha
    best_alpha = grid_search.best_params_["ccp_alpha"]

    print("Best alpha:", best_alpha)

    # Step 4: plot mean CV accuracy vs alpha
    mean_scores = grid_search.cv_results_['mean_test_score']
    # plt.figure(figsize=(8,5))
    # plt.plot(ccp_alphas, mean_scores, marker='o', drawstyle='steps-post')
    # plt.xlabel('ccp_alpha (pruning strength)')
    # plt.ylabel('Mean CV Accuracy')
    # plt.title('CV Accuracy vs ccp_alpha')
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()

    return {"ccp_alpha": best_alpha}



# === Function 3: Train final tree ===
def train_final_tree(X, y, random_state, **tree_params):
    """
    Train a Decision Tree with tuned parameters.

    Parameters
    ----------
    X : DataFrame
        Feature matrix.
    y : Series or array-like
        Target vector.
    random_state : int
        Random seed for reproducibility.
    **tree_params : dict
        Tuned parameters from tune_tree_depth or tune_tree_pruning.

    Returns
    -------
    DecisionTreeClassifier
        Trained decision tree model.
    """
    clf = DecisionTreeClassifier(random_state=random_state, **tree_params)
    clf.fit(X, y)
    return clf

