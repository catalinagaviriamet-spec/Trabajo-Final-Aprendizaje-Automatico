from copy import deepcopy

from src.models.gate import accepted


def test_gate_requires_overall_and_every_class():
    settings = {"target_f1_macro": 0.90, "minimum_class_recall": 0.85}
    report = {"macro avg": {"f1-score": 0.97}, **{str(i): {"recall": 0.95} for i in range(4)}}
    assert accepted(report, settings)
    bad_class = deepcopy(report)
    bad_class["2"]["recall"] = 0.60
    assert not accepted(bad_class, settings)
    bad_overall = deepcopy(report)
    bad_overall["macro avg"]["f1-score"] = 0.50
    assert not accepted(bad_overall, settings)
