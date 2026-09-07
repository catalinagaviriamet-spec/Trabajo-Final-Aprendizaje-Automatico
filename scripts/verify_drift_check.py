"""Comprueba códigos de salida reales, no solo que el comando termine."""

import subprocess
import sys

if __name__ == "__main__":
    for scenario, expected in [("control", 0), ("selected", 2)]:
        result = subprocess.run(
            [sys.executable, "-m", "src.monitoring", "--check", scenario], check=False
        )
        if result.returncode != expected:
            raise SystemExit(f"{scenario}: se esperaba {expected}, se obtuvo {result.returncode}")
        print(f"{scenario}: código {expected} verificado")
