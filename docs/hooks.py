"""Share design assets between the two independently built language sites."""
from pathlib import Path
import shutil


def on_pre_build(config):
    source = Path(__file__).parent / 'assets'
    destination = Path(config['docs_dir']) / 'assets'
    shutil.copytree(source, destination, dirs_exist_ok=True)
