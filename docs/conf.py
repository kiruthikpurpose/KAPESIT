import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'KAPESIT'
copyright = '2024, KAPESIT Team'
author = 'KAPESIT Team'
version = '1.0.0'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.mathjax',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'qiskit': ('https://qiskit.org/documentation/', None),
}

autodoc_member_order = 'bysource'
add_module_names = False 