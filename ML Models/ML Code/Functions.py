import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve, auc
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_selection import RFE
from sklearn.inspection import permutation_importance


def optimism_corrected_auc(mode, model, X, y, n, alpha, random_state, nselectedfeatures = "", selected_features=""):
    if mode == "Feature Selection":

        num_bootstrap_samples = n
        bootstrap_performances = []
        bootstrap_selectedfeatures = []

        for i in range(num_bootstrap_samples):
            bootstrap_indices = np.random.choice(len(X), len(X), replace=True)
            y_bootstrap = y.iloc[bootstrap_indices]
            X_bootstrap = X.iloc[bootstrap_indices]

            model.fit(X_bootstrap, y_bootstrap)

            # Compute permutation importance
            perm_importance = permutation_importance(model, X, y, n_repeats=10, random_state=random_state)
            sorted_feature_indices = np.argsort(perm_importance.importances_mean)[::-1]
            num_selected_features = nselectedfeatures
            selected_features = X.columns[sorted_feature_indices[:num_selected_features]]

            # Append the selected features for this iteration to the list
            bootstrap_selectedfeatures.append(selected_features)

            model.fit(X_bootstrap[selected_features], y_bootstrap)
            y_pred_bootstrap = model.predict(X_bootstrap[selected_features])
            bootstrap_performance = roc_auc_score(y_bootstrap, y_pred_bootstrap)

            y_pred_orig = model.predict(X[selected_features])
            orig_performance = roc_auc_score(y, y_pred_orig)

            optimism = bootstrap_performance - orig_performance
            bootstrap_performances.append(optimism)

        return bootstrap_performances, bootstrap_selectedfeatures

    if mode == "Final Evaluation":

        model.fit(X[selected_features], y)
        y_pred_full = model.predict(X[selected_features])
        roc_auc_fulldata = roc_auc_score(y, y_pred_full)

        num_bootstrap_samples = n
        bootstrap_performances = []

        for i in range(num_bootstrap_samples):
            bootstrap_indices = np.random.choice(len(X), len(X), replace=True)
            y_bootstrap = y.iloc[bootstrap_indices]
            X_bootstrap = X.iloc[bootstrap_indices][selected_features]

            model.fit(X_bootstrap, y_bootstrap)
            y_pred_bootstrap = model.predict(X_bootstrap)
            bootstrap_performance = roc_auc_score(y_bootstrap, y_pred_bootstrap)

            y_pred_orig = model.predict(X[selected_features])
            orig_performance = roc_auc_score(y, y_pred_orig)

            optimism = bootstrap_performance - orig_performance
            bootstrap_performances.append(optimism)

        average_optimism = np.mean(bootstrap_performances)
        p_corrected = roc_auc_fulldata - average_optimism
        percentiles = np.percentile(bootstrap_performances, [alpha / 2 * 100, (1 - alpha / 2) * 100])
        ci_low = roc_auc_fulldata - percentiles[1]
        ci_high = roc_auc_fulldata - percentiles[0]
        return p_corrected, ci_low, ci_high


def AUC_performance(model, X_test, y_test):
    # Evaluate the model on the test set
    y_pred_probs_test = model.predict_proba(X_test)[:, 1]

    # Compute ROC curve and ROC area for the test set
    fpr, tpr, _ = roc_curve(y_test, y_pred_probs_test)
    roc_auc_test = auc(fpr, tpr)

    return (roc_auc_test, fpr, tpr)


def cross_validate(model, X, y, n_splits, random_state):
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    fpr_cv = []
    tpr_cv = []
    roc_auc_cv = []

    for train, test in cv.split(X, y):
        model.fit(X.iloc[train], y.iloc[train])
        y_true_fold = y.iloc[test]
        y_pred_probs_fold = model.predict_proba(X.iloc[test])[:, 1]
        fpr_cv_loop, tpr_cv_loop, _ = roc_curve(y_true_fold, y_pred_probs_fold)
        roc_auc_cv_loop = auc(fpr_cv_loop, tpr_cv_loop)

        fpr_cv.append(fpr_cv_loop)
        tpr_cv.append(tpr_cv_loop)
        roc_auc_cv.append(roc_auc_cv_loop)

    return fpr_cv, tpr_cv, roc_auc_cv


def select_features(model, X, y, n_repeats, random_state, method, num_selected_features):
    if method == 'PI':
        perm_importance = permutation_importance(model, X, y, n_repeats=n_repeats, random_state=random_state)
        sorted_feature_indices_perm = np.argsort(perm_importance.importances_mean)[::-1]
        selected_features = X.columns[sorted_feature_indices_perm[:num_selected_features]]
        return selected_features
    if method == 'RFE':
        rfe = RFE(model, n_features_to_select=num_selected_features)
        X_rfe = rfe.fit_transform(X, y)
        return X.columns[rfe.support_]


def importantfeaturesstats(bootstrap_selectedfeatures):
    # Flatten the list of lists
    all_features = [feature for sublist in bootstrap_selectedfeatures for feature in sublist]

    # Count the occurrences of each feature
    feature_counts = {feature: all_features.count(feature) for feature in set(all_features)}

    # Calculate the percentage of occurrence for each feature
    total_samples = len(bootstrap_selectedfeatures)
    percentages = {feature: (count / total_samples) * 100 for feature, count in feature_counts.items()}

    # Sort the features by their frequency
    sorted_features = sorted(percentages.items(), key=lambda x: x[1], reverse=True)

    # Extract features and their corresponding percentages
    features = [f[0] for f in sorted_features]
    percentages = [f[1] for f in sorted_features]

    return features, percentages