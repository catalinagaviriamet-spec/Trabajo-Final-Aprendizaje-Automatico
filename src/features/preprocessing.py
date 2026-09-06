"""El escalador queda dentro del pipeline para evitar fuga de información."""

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def model_pipeline(estimator, scale=False):
    steps = []
    if scale:
        steps.append(("scale", StandardScaler()))
    steps.append(("model", estimator))
    return Pipeline(steps)
