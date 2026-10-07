"""Build English first, then Spanish into /es without removing the English site."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for config in ("mkdocs.yml", "mkdocs.es.yml"):
    subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict", "-f", config], cwd=ROOT, check=True)
