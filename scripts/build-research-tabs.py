"""Refresh NRL tabs and factual content without recreating the removed labs page."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parent
runpy.run_path(str(root/'build-nrl-structure.py'))
runpy.run_path(str(root/'build-breadcrumbs.py'))
