"""Selecciona con CV; evalúa test una vez y registra evidencia en MLflow."""

import json
import platform
from importlib.metadata import version

import joblib
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
import xgboost
from mlflow.models import infer_signature
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    cohen_kappa_score,
    f1_score,
    mean_absolute_error,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold

from src.data.dataset import ROOT, config, load_data, split_data, validate
from src.models.candidates import candidates

plt.switch_backend("Agg")


def train(frame=None):
    """Acepta datos ya leídos por Prefect o los obtiene por URL al usarse como CLI."""
    settings = config()
    output = ROOT / "docs/results"
    output.mkdir(parents=True, exist_ok=True)
    frame = load_data() if frame is None else validate(frame)
    x_train, x_test, y_train, y_test = split_data(frame)
    cv = StratifiedKFold(settings["cv_folds"], shuffle=True, random_state=settings["seed"])
    mlflow.set_tracking_uri(f"sqlite:///{(ROOT / 'mlflow.db').as_posix()}")
    mlflow.set_experiment(settings["experiment_name"])
    searches, rows, run_ids = {}, [], {}
    for name, (pipeline, grid) in candidates(settings["seed"]).items():
        print(f"Evaluando {name} con validación cruzada...", flush=True)
        with mlflow.start_run(run_name=name) as run:
            search = GridSearchCV(
                pipeline,
                grid,
                scoring={"f1_macro": "f1_macro", "accuracy": "accuracy"},
                refit="f1_macro",
                cv=cv,
                n_jobs=1,
                error_score="raise",
                return_train_score=True,
            ).fit(x_train, y_train)
            searches[name] = search
            run_ids[name] = run.info.run_id
            index = search.best_index_
            result = search.cv_results_
            row = {
                "model": name,
                "cv_f1_macro": float(result["mean_test_f1_macro"][index]),
                "cv_f1_std": float(result["std_test_f1_macro"][index]),
                "cv_accuracy": float(result["mean_test_accuracy"][index]),
                "train_f1_macro": float(result["mean_train_f1_macro"][index]),
                "best_params": json.dumps(search.best_params_),
            }
            rows.append(row)
            mlflow.log_params(
                {
                    "seed": settings["seed"],
                    "cv_folds": settings["cv_folds"],
                    "test_size": settings["test_size"],
                    "dataset_sha256": settings["dataset_sha256"],
                    **search.best_params_,
                }
            )
            mlflow.log_params(
                {
                    f"estimator_{key}": value
                    for key, value in search.best_estimator_.named_steps["model"]
                    .get_params()
                    .items()
                    if value is None or isinstance(value, (str, int, float, bool))
                }
            )
            mlflow.log_metrics({k: v for k, v in row.items() if isinstance(v, float)})
            mlflow.set_tags({"dataset": "mobile_prices", "selection": "train_cv_only"})
            pd.DataFrame(result).to_csv(output / f"cv_{name}.csv", index=False)
            mlflow.log_artifact(str(output / f"cv_{name}.csv"))
    leaderboard = pd.DataFrame(rows).sort_values("cv_f1_macro", ascending=False)
    leaderboard.to_csv(output / "leaderboard.csv", index=False)
    winner = leaderboard.iloc[0]["model"]
    model = searches[winner].best_estimator_
    # Test no participa en la selección del algoritmo ni de los hiperparámetros.
    prediction = model.predict(x_test)
    report = classification_report(y_test, prediction, output_dict=True, zero_division=0)
    metrics = {
        "test_accuracy": accuracy_score(y_test, prediction),
        "test_f1_macro": f1_score(y_test, prediction, average="macro"),
        "test_ordinal_mae": mean_absolute_error(y_test, prediction),
        "test_quadratic_kappa": cohen_kappa_score(y_test, prediction, weights="quadratic"),
        "test_severe_error_rate": float(np.mean(np.abs(y_test.to_numpy() - prediction) >= 2)),
    }
    passed = bool(
        metrics["test_f1_macro"] >= settings["target_f1_macro"]
        and min(report[str(i)]["recall"] for i in range(4)) >= settings["minimum_class_recall"]
    )
    summary = {
        "winner": winner,
        "selection_rule": "maximum mean 5-fold CV macro F1 on train",
        "train_rows": len(x_train),
        "test_rows": len(x_test),
        "metrics": metrics,
        "acceptance_passed": passed,
        "classification_report": report,
        "best_params": searches[winner].best_params_,
        "dataset_sha256": settings["dataset_sha256"],
        "versions": {
            **{p: version(p) for p in ["scikit-learn", "mlflow", "pandas"]},
            "xgboost": xgboost.__version__,
        },
        "python": platform.python_version(),
    }
    (output / "evaluation.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output / "split_indices.json").write_text(
        json.dumps(
            {
                "train": x_train.index.tolist(),
                "test": x_test.index.tolist(),
            }
        ),
        encoding="utf-8",
    )
    ConfusionMatrixDisplay.from_predictions(y_test, prediction, labels=[0, 1, 2, 3], cmap="Blues")
    plt.title(f"Test reservado — {winner}")
    plt.tight_layout()
    plt.savefig(output / "confusion_matrix.png", dpi=150)
    plt.close()
    (ROOT / "models").mkdir(exist_ok=True)
    joblib.dump(model, ROOT / "models/best_model.joblib")
    with mlflow.start_run(run_id=run_ids[winner]):
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(str(output / "evaluation.json"))
        mlflow.log_artifact(str(output / "confusion_matrix.png"))
        mlflow.log_artifact(str(ROOT / "configs/training.json"))
        info = mlflow.sklearn.log_model(
            sk_model=model,
            name="model",
            signature=infer_signature(x_train, model.predict(x_train)),
        )
        registered = mlflow.register_model(info.model_uri, "mobile-price-classifier")
        client = mlflow.MlflowClient()
        client.set_model_version_tag(
            "mobile-price-classifier",
            registered.version,
            "dataset_sha256",
            settings["dataset_sha256"],
        )
        client.set_model_version_tag(
            "mobile-price-classifier", registered.version, "acceptance_passed", str(passed)
        )
        if passed:
            client.set_registered_model_alias(
                "mobile-price-classifier", "champion", registered.version
            )
    print(leaderboard.to_string(index=False))
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    train()
