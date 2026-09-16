import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score


PREDICTIVE_MODEL_BASKET = {
    "Logistic Regression": {
        "class": LogisticRegression,
        "params": {"max_iter": 1000, "class_weight": "balanced", "random_state": 42},
        "description": "Interpretable probability model for estimating each customer's churn risk."
    },
    "Random Forest Classifier": {
        "class": RandomForestClassifier,
        "params": {"n_estimators": 100, "max_depth": 15, "random_state": 42},
        "description": "Robust tree ensemble that captures non-linear churn drivers and interactions."
    },
    "Gradient Boosting Classifier": {
        "class": GradientBoostingClassifier,
        "params": {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 5, "random_state": 42},
        "description": "Sequential boosting model optimized for ranking customers by churn probability."
    },
    "Extra Trees Classifier": {
        "class": ExtraTreesClassifier,
        "params": {"n_estimators": 100, "max_depth": 15, "random_state": 42},
        "description": "Highly randomized tree ensemble for a diverse churn-risk benchmark."
    }
}


def calculate_metrics(y_true, y_pred, y_proba=None) -> dict:
    if y_proba is None:
        y_proba = y_pred
    auc = roc_auc_score(y_true, y_proba) if len(np.unique(y_true)) == 2 else 0.0
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(auc)
    }
