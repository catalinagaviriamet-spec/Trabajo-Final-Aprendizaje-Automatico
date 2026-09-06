"""Búsqueda pequeña y explícita: 12 configuraciones, 5 folds por configuración."""

from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from xgboost import XGBClassifier

from src.features.preprocessing import model_pipeline


def candidates(seed=42):
    return {
        "dummy": (model_pipeline(DummyClassifier(strategy="most_frequent")), {}),
        "logistic_regression": (
            model_pipeline(LogisticRegression(max_iter=3000, random_state=seed), scale=True),
            {"model__C": [0.1, 1, 10]},
        ),
        "svm": (
            model_pipeline(SVC(kernel="rbf", random_state=seed), scale=True),
            {"model__C": [1, 10], "model__gamma": ["scale"]},
        ),
        "random_forest": (
            model_pipeline(RandomForestClassifier(n_estimators=200, random_state=seed, n_jobs=1)),
            {"model__max_depth": [None, 12], "model__min_samples_leaf": [1]},
        ),
        "xgboost": (
            model_pipeline(
                XGBClassifier(
                    objective="multi:softprob",
                    num_class=4,
                    eval_metric="mlogloss",
                    tree_method="hist",
                    n_estimators=200,
                    random_state=seed,
                    n_jobs=1,
                )
            ),
            {"model__max_depth": [3, 5], "model__learning_rate": [0.05, 0.1]},
        ),
    }
