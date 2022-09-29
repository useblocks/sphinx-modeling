"""Pytest conftest module containing common test configuration and fixtures."""
import shutil

import pytest
from sphinx.testing.path import path


pytest_plugins = "sphinx.testing.fixtures"


def copy_srcdir_to_tmpdir(srcdir, tmp):
    srcdir = path(__file__).parent.abspath() / srcdir
    tmproot = tmp / path(srcdir).basename()
    shutil.copytree(srcdir, tmproot)
    return tmproot


@pytest.fixture(scope="function")
def test_app(make_app, tmp_path, request):
    builder_params = request.param

    # copy plantuml.jar to current test temdir
    plantuml_jar_file = path(__file__).parent.abspath() / "doc_test/utils"
    shutil.copytree(plantuml_jar_file, tmp_path / "utils")

    # copy test srcdir to test temporary directory sphinx_test_tempdir
    src_dir = builder_params.get("src_dir", None)
    srcdir_in_tmp = copy_srcdir_to_tmpdir(src_dir, tmp_path)
    sphinx_srcdir = path(str(srcdir_in_tmp))  # convert to Sphinx path so Sphinx finds all needed methods

    # return sphinx.testing fixture make_app and new srcdir which in sphinx_test_tempdir
    app = make_app(
        buildername=builder_params.get("buildername", "html"),
        srcdir=sphinx_srcdir,
        freshenv=builder_params.get("freshenv", None),
        confoverrides=builder_params.get("confoverrides", None),
        status=builder_params.get("status", None),
        warning=builder_params.get("warning", None),
        tags=builder_params.get("tags", None),
        docutilsconf=builder_params.get("docutilsconf", None),
        parallel=builder_params.get("parallel", 0),
    )

    yield app
