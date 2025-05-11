#!/usr/bin/env python
"""
server.py  –  FastAPI plugin backend for Résumé Builder MVP

Features:
- Serves /.well-known/ai-plugin.json and logo.png
- POST /build → runs resume_build.py → returns resume.pdf
- Overrides OpenAPI 'servers' to your PUBLIC_URL
- Root endpoint to return 200 OK
"""

import subprocess, uuid, tempfile, json
from pathlib import Path

from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi

# ─── CONFIG ─────────────────────────────────────────────────────────────────
PUBLIC_URL = "https://8634-2600-387-f-6c1b-00-6.ngrok-free.app"
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(title="Résumé Builder MVP")

# Serve the manifest & logo under /.well-known
app.mount(
    "/.well-known",
    StaticFiles(directory="plugin_static"),
    name="static"
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/build")
async def build(
    template: UploadFile,             # the .docx template
    placeholders_json: str = Form(...)  # JSON string mapping placeholders
):
    # 1. save the uploaded template
    tmp_tpl = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    tmp_tpl.write(await template.read())
    tmp_tpl.close()

    # 2. save the JSON map
    tmp_json = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    tmp_json.write(placeholders_json.encode("utf-8"))
    tmp_json.close()

    # 3. invoke your CLI
    out_stub = f"/tmp/{uuid.uuid4()}"
    subprocess.check_call([
        "python", "resume_build.py",
        "--template", tmp_tpl.name,
        "--json",     tmp_json.name,
        "--out",      out_stub
    ], timeout=60)

    # 4. return the PDF
    pdf_path = Path(f"{out_stub}.pdf")
    if not pdf_path.exists():
        return JSONResponse(
            {"error": "PDF not found; check conversion step."},
            status_code=500
        )

    return FileResponse(
        str(pdf_path),
        filename="resume.pdf",
        media_type="application/pdf"
    )

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version="1.0.0",
        routes=app.routes,
        description="Resume Builder API"
    )
    schema["servers"] = [{ "url": PUBLIC_URL }]
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi
