import os
import sys

sys.path.insert(0, os.path.abspath("../.."))
project = "Project Management Dashboard"
copyright = "2024, Your Organization"
author = "Your Organization"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx_rtd_theme",
]
templates_path = ["_templates"]
exclude_patterns = []
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_title = "Project Management Dashboard"
html_logo = "_static/logo.png"
html_favicon = "_static/favicon.ico"
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}
