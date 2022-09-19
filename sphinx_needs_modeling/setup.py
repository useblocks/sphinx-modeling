import os
from typing import Any, Dict

from docutils import nodes
from pkg_resources import parse_version
import sphinx
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx_needs.api import add_dynamic_function, add_extra_option, add_need_type
from sphinx_needs_modeling.logging import get_logger
from sphinx_needs_modeling.modeling.defaults import NEEDS_MODELING_REMOVE_BACKLINKS, NEEDS_MODELING_REMOVE_FIELDS
from sphinx_needs_modeling.modeling.main import check_model


sphinx_version = sphinx.__version__

VERSION = "0.1.0"


def setup(app: Sphinx) -> Dict[str, Any]:
    """
    Setup the extension.
    """
    log = get_logger(__name__)
    log.info("Setting up sphinx-needs-modeling extension")

    # configurations
    app.add_config_value("needs_modeling_pydantic_models", [], "html", types=[str])
    app.add_config_value(
        "needs_modeling_remove_fields",
        NEEDS_MODELING_REMOVE_FIELDS,
        "html",
        types=[list],
    )
    app.add_config_value(
        "needs_modeling_remove_backlinks",
        NEEDS_MODELING_REMOVE_BACKLINKS,
        "html",
        types=[bool],
    )

    # events
    # app.connect("env-updated", dummy_func)
    app.connect("env-before-read-docs", prepare_env)
    app.connect("env-before-read-docs", dummy_func)
    app.connect("config-inited", sphinx_needs_generate_config)
    app.connect("doctree-resolved", process_models, 1000)

    return {
        "version": VERSION,  # identifies the version of our extension
        "parallel_read_safe": True,  # support parallel modes
        "parallel_write_safe": True,
    }


def prepare_env(app: Sphinx, env: BuildEnvironment, _docname: str) -> None:
    """Prepares the sphinx environment to store sphinx-needs-modeling internal data."""
    if not hasattr(env, "needs_modeling_workflow"):
        # Used to store workflow status information for already executed tasks.
        # Some tasks like backlink_creation need be performed only once.
        # But most sphinx-events get called several times (for each single document
        # file), which would also execute our code several times...
        env.needs_modeling_workflow = {
            "models_checked": False,
        }


def process_models(app: Sphinx, doctree: nodes.document, fromdocname: str) -> None:
    env = app.builder.env
    check_model(env)


def dummy_func(app: Sphinx, env: BuildEnvironment, docnames) -> None:
    if not docnames:
        check_model(env)
    log = get_logger(__name__)
    log.info("env-updated was called")


def sphinx_needs_generate_config(app, *args):
    """
    Derive configurations need_types, need_extra_options and need_extra_links from user models.

    Some thought must go into this, as mentioned configuration parameters feature more information
    such as plantuml colors, incoming/outgoing link names and more.
    Those could be put as a private field into the model class.
    Also a custom field type will be needed to clearly define a needs link field as there
    are other list like need attributes such as sections.
    """

    # Extra options
    # For details read
    # https://sphinx-needs.readthedocs.io/en/latest/api.html#sphinx_needs.api.configuration.add_extra_option
    # add_extra_option(app, "file")

    # Extra dynamic functions
    # For details about usage read
    # https://sphinx-needs.readthedocs.io/en/latest/api.html#sphinx_needs.api.configuration.add_dynamic_function
    # add_dynamic_function(app, dummy_func)

    # Extra need types
    # For details about usage read
    # https://sphinx-needs.readthedocs.io/en/latest/api.html#sphinx_needs.api.configuration.add_need_type
    # add_need_type(app, directive="foobar", title="foobar", prefix="FOO_")
