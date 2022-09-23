import nox
from nox_poetry import session

PYTHON_VERSIONS = ["3.7", "3.8", "3.9.7", "3.10"]
SPHINX_VERSIONS = ["5.0.2"]
SPHINX_NEEDS_VERSIONS = ["0.7.9", "1.0.1", "1.0.2"]
TEST_DEPENDENCIES = [
    "pytest",
    "pytest-xdist",
    "pytest_lsp",
]


def run_tests(session, sphinx):
    session.install(".")
    session.install(*TEST_DEPENDENCIES)
    session.run("pip", "install", f"sphinx=={sphinx}", silent=True)
    session.run("pip", "install", "-r", "docs/requirements.txt", silent=True)
    session.run("echo", "TEST FINAL PACKAGE LIST")
    session.run("pip", "freeze")
    session.run("make", "test", external=True)


@session(python=PYTHON_VERSIONS)
@nox.parametrize("sphinx_needs", SPHINX_NEEDS_VERSIONS)
@nox.parametrize("sphinx", SPHINX_VERSIONS)
def tests(session, sphinx, sphinx_needs):
    run_tests(session, sphinx)
