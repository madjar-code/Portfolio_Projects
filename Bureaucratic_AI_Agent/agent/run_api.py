import json
import logging
import pathlib
import tempfile
from uuid import uuid4

from fastapi import FastAPI, File, Form, UploadFile

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
)

app = FastAPI(title="Agent /run endpoint")
logger = logging.getLogger(__name__)

_EXT_TO_FORMAT: dict[str, str] = {
    ".pdf": "PDF",
    ".docx": "DOCX",
    ".jpg": "JPG",
    ".jpeg": "JPG",
    ".png": "PNG",
}


@app.post("/run")
async def run(
    procedure: str = Form(...),
    form_data: str = Form("{}"),
    document: UploadFile | None = File(None),
):
    from models import DocumentMetadata, TaskMessage
    from core.handler import handle_task

    tmp_path: str | None = None
    doc_meta: DocumentMetadata | None = None

    if document and document.filename:
        content = await document.read()
        suffix = pathlib.Path(document.filename).suffix.lower()
        fmt = _EXT_TO_FORMAT.get(suffix, "PDF")

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
            f.write(content)
            tmp_path = f.name

        doc_meta = DocumentMetadata(
            file_name=document.filename,
            file_url=f"file://{tmp_path}",
            file_format=fmt,
            file_size=len(content),
        )
        logger.info("Uploaded: %s → %s (%s)", document.filename, tmp_path, fmt)

    task = TaskMessage(
        application_id=f"run-{uuid4().hex[:8]}",
        procedure=procedure,
        form_data=json.loads(form_data),
        document=doc_meta,
    )

    try:
        report = await handle_task(task)
        return report.model_dump()
    finally:
        if tmp_path:
            pathlib.Path(tmp_path).unlink(missing_ok=True)
