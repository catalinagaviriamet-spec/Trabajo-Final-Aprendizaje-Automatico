from unittest.mock import Mock
from urllib.error import HTTPError, URLError

import pytest

from src.pipeline.workflow import (
    prepare_dataset,
    read_dataset,
    retry_network_error,
    train_model,
    training_pipeline,
    validate_dataset,
)


@pytest.mark.parametrize(
    "error,expected",
    [
        (URLError("offline"), True),
        (TimeoutError(), True),
        (ValueError("Checksum incorrecto"), False),
        (HTTPError("url", 404, "not found", None, None), False),
        (HTTPError("url", 503, "unavailable", None, None), True),
    ],
)
def test_only_transient_errors_are_retried(error, expected):
    state = Mock()
    state.result.side_effect = error
    assert retry_network_error(None, None, state) is expected


def test_dataset_results_are_never_persisted():
    for step in (read_dataset, validate_dataset, train_model, prepare_dataset, training_pipeline):
        assert step.persist_result is False


def test_validation_failure_prevents_training(monkeypatch):
    from src.pipeline import workflow

    monkeypatch.setattr(
        workflow, "prepare_dataset", Mock(side_effect=ValueError("Contrato inválido"))
    )
    trainer = Mock()
    monkeypatch.setattr(workflow, "train_model", trainer)
    with pytest.raises(ValueError, match="Contrato inválido"):
        workflow.training_pipeline.fn()
    trainer.assert_not_called()


def test_training_task_passes_the_same_in_memory_frame(monkeypatch):
    from src.pipeline import workflow

    frame = object()
    trainer = Mock(return_value={"winner": "example"})
    monkeypatch.setattr(workflow, "train", trainer)
    assert train_model.fn(frame) == {"winner": "example"}
    trainer.assert_called_once_with(frame=frame)
