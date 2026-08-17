import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, SGDRegressor
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


PREDICTIVE_MODEL_BASKET = {
    "Random Forest Regressor": {
        "class": RandomForestRegressor,
        "params": {"n_estimators": 100, "max_depth": 15, "random_state": 42},
        "description": "Ensemble of decision trees. Captures non-linear feature interactions with high robustness."
    },
    "Gradient Boosting Regressor": {
        "class": GradientBoostingRegressor,
        "params": {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 5, "random_state": 42},
        "description": "Sequential boosted decision trees. Excellent predictive performance for complex tabular data."
    },
    "HistGradientBoosting Regressor": {
        "class": HistGradientBoostingRegressor,
        "params": {"max_iter": 100, "learning_rate": 0.1, "random_state": 42},
        "description": "Fast histogram-based gradient boosting (similar to LightGBM). Native handling for large datasets."
    },
    "SGD Regressor (Gradient Descent)": {
        "class": SGDRegressor,
        "params": {"max_iter": 1000, "tol": 1e-3, "random_state": 42},
        "description": "Linear model fitted using Stochastic Gradient Descent. Scalable benchmark model."
    },
    "Ridge Regression (L2)": {
        "class": Ridge,
        "params": {"alpha": 1.0},
        "description": "Linear regression with L2 regularization penalty to prevent overfitting."
    },
    "Lasso Regression (L1)": {
        "class": Lasso,
        "params": {"alpha": 1.0, "random_state": 42},
        "description": "Linear regression with L1 regularization penalty for sparse feature selection."
    },
    "Extra Trees Regressor": {
        "class": ExtraTreesRegressor,
        "params": {"n_estimators": 100, "max_depth": 15, "random_state": 42},
        "description": "Extremely randomized trees ensemble for reduced variance."
    },
    "MLP Neural Network": {
        "class": MLPRegressor,
        "params": {"hidden_layer_sizes": (64, 32), "max_iter": 500, "random_state": 42},
        "description": "Multi-Layer Perceptron Neural Network for deep non-linear regression."
    }
}


def calculate_metrics(y_true, y_pred) -> dict:
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return {
        "rmse": float(rmse),
        "mae": float(mae),
        "r2": float(r2),
        "mse": float(mse)
    }
