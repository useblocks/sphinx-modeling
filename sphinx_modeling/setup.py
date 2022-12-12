"""Extension entry point for Sphinx."""
from contextlib import suppress
import os
import pickle
from typing import Any, Dict, List

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.environment import BuildEnvironment
from sphinx_needs.api import add_dynamic_function, add_extra_option, add_need_type

from sphinx_modeling.logging import get_logger
from sphinx_modeling.modeling.defaults import MODELING_REMOVE_BACKLINKS, MODELING_REMOVE_FIELDS, MODELING_RESOLVE_LINKS
from sphinx_modeling.modeling.main import check_model


VERSION = "0.2.0"
MODELING_MSG_FOLDER = ".modeling"
MODELING_MSG_FILE = "messages.pickle"


def setup(app: Sphinx) -> Dict[str, Any]:
    """Setup the extension."""
    log = get_logger(__name__)
    log.info("Setting up sphinx-modeling extension")

    # configurations
    app.add_config_value("modeling_models", {}, "html", types=[Dict[str, Any]])
    app.add_config_value(
        "modeling_remove_fields",
        MODELING_REMOVE_FIELDS,
        "html",
        types=[list],
    )
    app.add_config_value(
        "modeling_remove_backlinks",
        MODELING_REMOVE_BACKLINKS,
        "html",
        types=[bool],
    )
    app.add_config_value(
        "modeling_resolve_links",
        MODELING_RESOLVE_LINKS,
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
    """Emit previous log messages in case no document changed in an incremental build."""
    if not docnames:
        # incremental build detected without a single document changed which means sphinx-needs
        # does not calculate parent_needs, parent_need and backlinks; this happens only
        # when doctree-resolved gets fired; it means modeling cannot correctly validate models;
        # therefore previous messages are logged as those have not changed
        log = get_logger(__name__)
        msg_path = _get_modeling_msg_file_path(app)
        with suppress(FileNotFoundError), open(msg_path, "rb") as fp:
            # if the file does not exist, no messages can be emitted, maybe the file was manually deleted
            messages = pickle.load(fp)
            for msg in messages:
                log.warning(msg)


def _get_modeling_msg_file_path(app: Sphinx) -> str:
    """Return path to the modeling messages pickle file."""
    return os.path.join(app.outdir, MODELING_MSG_FOLDER, MODELING_MSG_FILE)


def sphinx_needs_generate_config(
    app: Sphinx,
    config: Config,  # pylint: disable=unused-argument
) -> None:
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
    add_extra_option(app, "file")

    # Extra dynamic functions
    # For details about usage read
    # https://sphinx-needs.readthedocs.io/en/latest/api.html#sphinx_needs.api.configuration.add_dynamic_function
    add_dynamic_function(app, lambda x: x)

    # Extra need types
    # For details about usage read
    # https://sphinx-needs.readthedocs.io/en/latest/api.html#sphinx_needs.api.configuration.add_need_type
    add_need_type(app, directive="foobar", title="foobar", prefix="FOO_")
