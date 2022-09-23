"""
Default values for sphinx-modeling parameters.

Can be overriden in conf.py.
"""


MODELING_REMOVE_FIELDS = [
    "docname",
    "external_css",
    "hide",
    "is_modified",
    "layout",
    "style",
    "type_color",
    "type_name",
    "type_prefix",
    "type_style",
]
"""List of keys/fields to remove from a need dictionary before validation."""

MODELING_REMOVE_BACKLINKS = True
"""Flag to remove back-referencing links (e.g. blocks -> blocks_back) before validation."""
