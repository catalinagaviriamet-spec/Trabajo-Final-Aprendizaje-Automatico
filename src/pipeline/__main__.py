"""CLI reproducible: run, check o serve. No requiere cuenta Prefect Cloud."""

import argparse
import json
import os
import subprocess
import sys

from src.data.dataset import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["run", "check", "serve", "server"], nargs="?", default="run"
    )
    parser.add_argument("--api-url", help="API de un servidor Prefect local ya iniciado.")
    args = parser.parse_args()
    os.environ["PREFECT_HOME"] = str(ROOT / "logs/prefect")
    os.environ["PREFECT_MEMO_STORE_PATH"] = str(ROOT / "logs/prefect/memo_store.toml")
    os.environ["PREFECT_SERVER_ANALYTICS_ENABLED"] = "false"
    os.environ["PREFECT_RESULTS_PERSIST_BY_DEFAULT"] = "false"
    # Esta CLI usa servidor local o efímero y no hereda una conexión Cloud de otro proyecto.
    os.environ.pop("PREFECT_API_KEY", None)
    api_url = args.api_url or ("http://127.0.0.1:4200/api" if args.command == "serve" else None)
    if api_url:
        os.environ["PREFECT_API_URL"] = api_url
    else:
        os.environ.pop("PREFECT_API_URL", None)
    if args.command == "server":
        subprocess.run(
            [
                sys.executable,
                "-m",
                "prefect",
                "server",
                "start",
                "--host",
                "127.0.0.1",
                "--port",
                "4200",
            ],
            check=True,
        )
        return

    from src.pipeline.workflow import training_pipeline

    if args.command == "serve":
        from prefect.schedules import Cron

        settings = json.loads((ROOT / "configs/pipeline.json").read_text(encoding="utf-8"))
        training_pipeline.serve(
            name=settings["deployment_name"],
            schedules=[Cron(settings["cron"], timezone=settings["timezone"])],
            parameters={"validate_only": False},
            limit=1,
            pause_on_shutdown=True,
        )
    else:
        training_pipeline(validate_only=args.command == "check")


if __name__ == "__main__":
    main()
