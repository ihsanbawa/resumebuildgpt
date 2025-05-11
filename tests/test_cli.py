import subprocess, tempfile, pathlib, os

def test_cli_build():
    md = pathlib.Path(__file__).parent / "sample.md"
    out = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
    subprocess.check_call(["python", "resume_build.py", "--markdown", md, "--out", out])
    assert os.path.getsize(out) > 100          # at least some bytes
