from pathlib import Path
import subprocess

import pytest


@pytest.mark.parametrize("test_app", [{"buildername": "html", "src_dir": "doc_test/doc_modeling"}], indirect=True)
def test_doc_build_html(test_app):
    app = test_app
    app.build()
    html = Path(app.outdir, "index.html").read_text(encoding="utf8")
    assert html


@pytest.mark.parametrize(
    "test_app",
    [{"buildername": "html", "src_dir": "doc_test/doc_modeling"}],
    indirect=True,
)
def test_modeling_success(test_app):
    app = test_app

    src_dir = Path(app.srcdir)
    out_dir = src_dir / "_build"

    out = subprocess.run(["sphinx-build", "-M", "html", src_dir, out_dir], capture_output=True)
    assert out.returncode == 0

    assert "Validation was successful!" in out.stdout.decode("utf-8")
