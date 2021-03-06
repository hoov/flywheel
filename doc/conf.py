# -*- coding: utf-8 -*-
""" Sphinx conf """
import sys
import os
import sphinx_rtd_theme

# pylint: disable=C0103
docs_basepath = os.path.abspath(os.path.dirname(__file__))

addtl_paths = (
    os.pardir,
)
for path in addtl_paths:
    sys.path.insert(0, os.path.abspath(os.path.join(docs_basepath, path)))

from flywheel_version import git_version_data

extensions = ['sphinx.ext.autodoc', 'numpydoc', 'sphinx.ext.intersphinx',
              'sphinx.ext.linkcode', 'sphinx.ext.autosummary']

master_doc = 'index'
project = u'flywheel'
copyright = u'2013, Steven Arcangeli'

version_data = git_version_data()
version = version_data['tag']
release = version_data['version']

exclude_patterns = ['_build']
pygments_style = 'sphinx'
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
numpydoc_show_class_members = False
intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    'boto': ('http://boto.readthedocs.org/en/latest/', None),
}


def linkcode_resolve(domain, info):
    """ Create source links to github """
    if domain != 'py' or not info['module']:
        return None
    filename = info['module'].replace('.', '/')
    return "https://github.com/mathcamp/flywheel/blob/%s/%s.py" % (version_data['ref'], filename)
