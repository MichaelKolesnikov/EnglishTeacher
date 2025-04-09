# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath("../../src"))

project = 'BICA project'
copyright = '2025, Anatolii Dolgikh'
author = 'Anatolii Dolgikh'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",      # Генерация документации из docstrings
    "sphinx.ext.napoleon",     # Поддержка Google и NumPy-style docstrings
    "sphinx.ext.viewcode",     # Ссылки на исходный код
    "sphinx_autodoc_typehints",
]

templates_path = ['_templates']
exclude_patterns = ["../../src/test_server.py"]

language = 'ru'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
