"""Verificación real y aislada de Prefect; ejecutar como módulo desde la raíz."""

import json
import os
import time

from src.data.dataset import ROOT


def main():
    os.environ["PREFECT_HOME"] = str(ROOT / "logs/prefect-verification")
    os.environ["PREFECT_MEMO_STORE_PATH"] = str(ROOT / "logs/prefect-verification/memo_store.toml")
    os.environ["PREFECT_SERVER_ANALYTICS_ENABLED"] = "false"
    os.environ.pop("PREFECT_API_KEY", None)
    os.environ.pop("PREFECT_API_URL", None)
    from prefect.client.orchestration import get_client
    from prefect.schedules import Cron
    from prefect.testing.utilities import prefect_test_harness

    from src.pipeline.workflow import training_pipeline

    settings = json.loads((ROOT / "configs/pipeline.json").read_text(encoding="utf-8"))
    with prefect_test_harness(server_startup_timeout=90):
        state = training_pipeline(return_state=True)
        assert state.is_completed(), state
        result = state.result()
        deployment = training_pipeline.to_deployment(
            name="verificacion-programacion",
            schedules=[Cron(settings["cron"], timezone=settings["timezone"])],
            paused=True,
            parameters={"validate_only": False},
            concurrency_limit=1,
        )
        deployment_id = deployment.apply()
        with get_client(sync_client=True) as client:
            registered = client.read_deployment(deployment_id)
            schedule = registered.schedules[0].schedule
            assert registered.paused
            assert schedule.cron == settings["cron"]
            assert schedule.timezone == settings["timezone"]
            # Los eventos de tareas se escriben de forma asíncrona en la API.
            for _ in range(10):
                tasks = client.read_task_runs(limit=20)
                if len(tasks) >= 4 and all(t.state.is_completed() for t in tasks):
                    break
                time.sleep(0.5)
            assert len(tasks) >= 4 and all(t.state.is_completed() for t in tasks)
        csv_files = list((ROOT / "data").rglob("*.csv"))
        assert not csv_files
        evidence = {
            "flow_state": state.name,
            "tasks": [{"name": t.name.rsplit("-", 1)[0], "state": t.state.name} for t in tasks],
            "schedule": {
                "cron": schedule.cron,
                "timezone": schedule.timezone,
                "verification_paused": True,
            },
            "csv_files_in_data": len(csv_files),
            "result": result,
        }
        (ROOT / "docs/results/pipeline_verification.json").write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(json.dumps(evidence, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
