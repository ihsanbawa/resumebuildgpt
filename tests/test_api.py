import subprocess, time, httpx, threading, uvicorn
from server import app

def _run_server():
    uvicorn.run(app, host="127.0.0.1", port=3333, log_level="warning")

def test_build_endpoint(tmp_path):
    # start API in a background thread
    t = threading.Thread(target=_run_server, daemon=True)
    t.start()
    time.sleep(1)  # give uvicorn a moment

    md_path = tmp_path / "x.md"
    md_path.write_text("# Hi", encoding="utf-8")
    with open(md_path, "rb") as fh:
        r = httpx.post("http://127.0.0.1:3333/build", files={"markdown": fh})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert len(r.content) > 200
