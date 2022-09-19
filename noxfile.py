import nox
from nox_poetry import session

PYTHON_VERSIONS = ["3.8", "3.9.7", "3.10"]
SPHINX_VERSIONS = ["5.0.2"]
TEST_DEPENDENCIES = [
    "pytest",
    "pytest-xdist",
    "pytest_lsp",
    "responses",
    "lxml",
    "pyparsing!=3.0.4",
    "requests-mock",
]


def is_supported(python: str, sphinx: str) -> bool:
    return not (python == "3.6" and sphinx not in ["3.2"])


def run_tests(session, sphinx):
    session.install(".")
    session.install(*TEST_DEPENDENCIES)
    session.run("pip", "install", f"sphinx=={sphinx}", silent=True)
    session.run("pip", "install", "-r", "docs/requirements.txt", silent=True)
    session.run("echo", "TEST FINAL PACKAGE LIST")
    session.run("pip", "freeze")
    session.run("make", "test", external=True)


@session(python=PYTHON_VERSIONS)
@nox.parametrize("sphinx", SPHINX_VERSIONS)
def tests(session, sphinx):
    if is_supported(session.python, sphinx):
        run_tests(session, sphinx)
    else:
        session.skip("unsupported combination")
