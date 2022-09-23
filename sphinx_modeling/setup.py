import os
import pickle
from typing import Any, Dict, List

from docutils import nodes
import sphinx
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.environment import BuildEnvironment
from sphinx_needs.api import add_dynamic_function, add_extra_option, add_need_type
from sphinx_modeling.logging import get_logger
from sphinx_modeling.modeling.defaults import NEEDS_MODELING_REMOVE_BACKLINKS, NEEDS_MODELING_REMOVE_FIELDS
from sphinx_modeling.modeling.main import check_model


sphinx_version = sphinx.__version__

VERSION = "0.1.0"
MODELING_MSG_FOLDER = ".modeling"
MODELING_MSG_FILE = "messages.pickle"


def setup(app: Sphinx) -> Dict[str, Any]:
    """
    Setup the extension.
    """
    log = get_logger(__name__)
    log.info("Setting up sphinx-modeling extension")

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
    # app.connect("config-inited", sphinx_needs_generate_config)  # not yet implemented
    app.connect("env-before-read-docs", prepare_env)
    app.connect("env-before-read-docs", emit_old_messages)
    app.connect("doctree-resolved", process_models, 1000)  # call this after sphinx-needs finished processing

    return {
        "version": VERSION,  # identifies the version of our extension
        "parallel_read_safe": True,  # support parallel modes
        "parallel_write_safe": True,
    }


def prepare_env(app: Sphinx, env: BuildEnvironment, _docname: str) -> None:
    """Prepares the sphinx environment to store sphinx-modeling internal data."""
    # for incremental builds needs_modeling_workflow already exists on env
    if not hasattr(env, "needs_modeling_workflow"):
        # Used to store workflow status information for already executed tasks.
        # Model processing needs to be done only once at the earliest possible time
        # to get early feedback. doctree-resolved is used for that which can be
        # fired multiple times. Therefore the models_checked workflow step is stored
        # on the env.
        env.needs_modeling_workflow = {  # type: ignore
            "models_checked": False,
        }


def process_models(app: Sphinx, doctree: nodes.document, fromdocname: str) -> None:
    """Check the user provided models against all needs."""
    env = app.builder.env
    msg_path = _get_modeling_msg_file_path(app)
    check_model(env, msg_path)


def emit_old_messages(app: Sphinx, env: BuildEnvironment, docnames: List[str]) -> None:
    if not docnames:
        # incremental build detected without a single document changed which means sphinx-needs
        # does not calculate parent_needs, parent_need and backlinks; this happens only
        # when doctree-resolved gets fired; it means modeling cannot correctly validate models;
        # therefore previous messages are logged as those have not changed
        log = get_logger(__name__)
        msg_path = _get_modeling_msg_file_path(app)
        try:
            with open(msg_path, "rb") as fp:
                messages = pickle.load(fp)
                for msg in messages:
                    log.warn(msg)
        except FileNotFoundError as exc:
            # no messages can be emitted, maybe the file was manually deleted
            pass


def _get_modeling_msg_file_path(app: Sphinx) -> str:
    """Return path to the modeling messages pickle file."""
    return os.path.join(app.outdir, MODELING_MSG_FOLDER, MODELING_MSG_FILE)


def sphinx_needs_generate_config(app: Sphinx, config: Config) -> None:
    """
    Derive configurations need_types, need_extra_options and need_extra_links from user models.

    Some thought must go into this, as mentioned configuration parameters feature more information
    such as plantuml colors, incoming/outgoing link names and more.
    Those could be put as a private field into the model class.
    Also a custom field type will be needed to clearly define a needs link field as there
    are other list like need attributes such as sections.
    """
    pass
    # Extra options
    # For details read
    # https://sphinx-needs.readthedocs.io/en/latest/api.html#sphinx_needs.api.configuration.add_extra_option
    add_extra_option(app, "file")

    # Extra dynamic functions
    # For details about usage read
    # https://sphinx-needs.readthedocs.io/en/latest/api.html#sphinx_needs.api.configuration.add_dynamic_function
    add_dynamic_function(app, lambda x: x)

    # Extra need types
    # For details about usage read
    # https://sphinx-needs.readthedocs.io/en/latest/api.html#sphinx_needs.api.configuration.add_need_type
    add_need_type(app, directive="foobar", title="foobar", prefix="FOO_")