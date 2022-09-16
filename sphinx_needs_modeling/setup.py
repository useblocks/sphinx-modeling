import os

from pkg_resources import parse_version
import sphinx
from sphinx_needs.api import add_dynamic_function, add_extra_option, add_need_type


sphinx_version = sphinx.__version__
if parse_version(sphinx_version) >= parse_version("1.6"):
    from sphinx.util import logging
else:
    import logging

VERSION = "0.1.0"


def setup(app):
    """
    Setup the extension.
    """
    log = logging.getLogger(__name__)
    log.info("Setting up sphinx-needs-modeling extension")

    # configurations
    app.add_config_value("needs_modeling_models", app.confdir, [])

    # events
    app.connect("env-updated", dummy_func)
    app.connect("config-inited", dummy_func)
    app.connect("config-inited", sphinx_needs_update)

    return {
        "version": VERSION,  # identifies the version of our extension
        "parallel_read_safe": True,  # support parallel modes
        "parallel_write_safe": True,
    }


def dummy_func(app, *args):
    logging.getLogger(__name__).info("I was called")


def sphinx_needs_update(app, *args):
    """
    sphinx-needs configuration
    """

    # Extra options
    # For details read
    # https://sphinx-needs.readthedocs.io/en/latest/api.html#sphinx_needs.api.configuration.add_extra_option
    add_extra_option(app, "file")

    # Extra dynamic functions
    # For details about usage read
    # https://sphinx-needs.readthedocs.io/en/latest/api.html#sphinx_needs.api.configuration.add_dynamic_function
    add_dynamic_function(app, dummy_func)

    # Extra need types
    # For details about usage read
    # https://sphinx-needs.readthedocs.io/en/latest/api.html#sphinx_needs.api.configuration.add_need_type
    add_need_type(app, ())
