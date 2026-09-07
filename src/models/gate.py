"""Promoción separada del entrenamiento: comprueba el artefacto cargado por alias."""

import json
from datetime import UTC, datetime

import joblib
import mlflow
import mlflow.sklearn
from sklearn.metrics import classification_report

from src.data.dataset import ROOT, config, load_data, split_data


def accepted(report, settings):
    """No basta con que el entrenamiento termine: deben cumplirse todas las metas."""
    return (
        report["macro avg"]["f1-score"] >= settings["target_f1_macro"]
        and min(report[str(i)]["recall"] for i in range(4)) >= settings["minimum_class_recall"]
    )


def main():
    settings = config()
    mlflow.set_tracking_uri(f"sqlite:///{(ROOT / 'mlflow.db').as_posix()}")
    client = mlflow.MlflowClient()
    name = "mobile-price-classifier"
    candidate = client.get_model_version_by_alias(name, "candidate")
    model = mlflow.sklearn.load_model(f"models:/{name}@candidate")
    _, test, _, target = split_data(load_data())
    report = classification_report(target, model.predict(test), output_dict=True, zero_division=0)
    run = client.get_run(candidate.run_id)
    matches = abs(report["macro avg"]["f1-score"] - run.data.metrics["test_f1_macro"]) <= 0.005
    passed = (
        accepted(report, settings)
        and matches
        and candidate.tags.get("dataset_sha256") == settings["dataset_sha256"]
    )
    previous = client.get_registered_model(name).aliases.get("champion")
    decision = {
        "candidate": candidate.version,
        "previous_champion": previous,
        "approved": passed,
        "metric_reproduced": matches,
        "test_f1_macro": report["macro avg"]["f1-score"],
        "checked_at_utc": datetime.now(UTC).isoformat(),
    }
    client.set_model_version_tag(
        name, candidate.version, "validation_status", "approved" if passed else "rejected"
    )
    (ROOT / "logs").mkdir(exist_ok=True)
    (ROOT / "logs/promotion.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")
    if not passed:
        raise SystemExit("Gate rechazado: se conserva el champion anterior.")
    client.set_registered_model_alias(name, "champion", candidate.version)
    # La API local usa esta exportación del artefacto aprobado; no se publica en Git.
    joblib.dump(model, ROOT / "models/best_model.joblib")
    (ROOT / "models/model_metadata.json").write_text(json.dumps(decision), encoding="utf-8")
    print(json.dumps(decision))


if __name__ == "__main__":
    main()
