import nox
from nox_poetry import session


PYTHON_VERSIONS = ["3.7", "3.8", "3.9", "3.10"]
SPHINX_VERSIONS = ["5.0.2"]
SPHINX_NEEDS_VERSIONS = ["1.0.1", "1.0.2"]


def run_tests(session, sphinx, sphinx_needs):
    session.install(".")
    session.run("pip", "install", f"sphinx=={sphinx}")
    session.run("pip", "install", f"sphinx-needs=={sphinx_needs}")
    session.run("echo", "FINAL PACKAGE LIST", external=True)
    session.run("pip", "freeze")
    session.run("make", "test", external=True)  # runs 'poetry run pytest' which re-uses the active nox environment


@session(python=PYTHON_VERSIONS, reuse_venv=True)
@nox.parametrize("sphinx_needs", SPHINX_NEEDS_VERSIONS)
@nox.parametrize("sphinx", SPHINX_VERSIONS)
def tests(session, sphinx, sphinx_needs):
    run_tests(session, sphinx, sphinx_needs)
