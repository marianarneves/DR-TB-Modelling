# === modeling/train_tree.py ===
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier

def tune_tree_depth(X, y):
    param_grid = {'max_depth': list(range(1, 11)) + [None]}
    grid_search = GridSearchCV(DecisionTreeClassifier(random_state=42), param_grid, cv=10, scoring='accuracy')
    grid_search.fit(X, y)

    best_depth = grid_search.best_params_['max_depth']
    results = grid_search.cv_results_
    depths = param_grid['max_depth']
    mean_scores_by_depth = {params['max_depth']: results['mean_test_score'][i] for i, params in enumerate(results['params'])}
    mean_scores_ordered = [mean_scores_by_depth[d] for d in depths]

    plt.figure(figsize=(8, 5))
    plot_depths = [d if d is not None else 11 for d in depths]
    plt.plot(plot_depths, mean_scores_ordered, marker='o')
    plt.title('CV Accuracy vs. Tree Depth')
    plt.xlabel('max_depth')
    plt.ylabel('Mean CV Accuracy')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return best_depth

def train_final_tree(X, y, max_depth):
    clf = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    clf.fit(X, y)
    return clf

