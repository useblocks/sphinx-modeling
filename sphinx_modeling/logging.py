"""Provide the Sphinx logger."""
from sphinx.util import logging
from sphinx.util.logging import SphinxLoggerAdapter


def get_logger(name: str) -> SphinxLoggerAdapter:
    """Return a named Sphinx logger."""
    return logging.getLogger(name)
