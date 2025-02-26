import os
import sys

sys.path.insert(0, os.path.abspath(".."))
project = "Project Management Dashboard"
copyright = "2024, Dashboard Team"
author = "Dashboard Team"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.viewcode",
]
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
