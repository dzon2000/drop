from __future__ import annotations

import json
import os
import secrets
import shutil
import time
from pathlib import Path
from urllib.parse import quote

from flask import Flask, after_this_request, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename


EXPIRATIONS = {
    "download": None,
    "5m": 5 * 60,
    "30m": 30 * 60,
    "2h": 2 * 60 * 60,
    "forever": 0,
}
WORDS = (
    ("amber", "brisk", "calm", "clever", "gentle", "quick", "quiet", "sunny"),
    ("badger", "falcon", "maple", "otter", "panda", "robin", "tiger", "willow"),
    ("cloud", "comet", "forest", "harbor", "meadow", "river", "stone", "valley"),
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("DROP_MAX_BYTES", 2 * 1024 * 1024 * 1024))
DATA_DIR = Path(os.getenv("DROP_DATA", "data"))
PUBLIC_URL = os.getenv("DROP_PUBLIC_URL", "").rstrip("/")

def make_slug() -> str:
    return "-".join(secrets.choice(group) for group in WORDS)


def store_upload(upload, expiration: str) -> str:
    filename = secure_filename(upload.filename or "") or "download"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    while True:
        slug = make_slug()
        directory = DATA_DIR / slug
        try:
            directory.mkdir()
            break
        except FileExistsError:
            continue
    upload.save(directory / filename)
    metadata = {
        "filename": filename,
        "expires_at": None if expiration in ("download", "forever") else time.time() + EXPIRATIONS[expiration],
        "delete_after_download": expiration == "download",
    }
    (directory / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    return slug


def find_file(slug: str) -> tuple[Path, dict] | None:
    if not slug or "/" in slug or "\\" in slug:
        return None
    directory = DATA_DIR / slug
    metadata_path = directory / "metadata.json"
    if not metadata_path.is_file():
        return None
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata["expires_at"] is not None and time.time() >= metadata["expires_at"]:
        shutil.rmtree(directory, ignore_errors=True)
        return None
    return directory / metadata["filename"], metadata


def link_for(slug: str) -> str:
    base = PUBLIC_URL or request.host_url.rstrip("/")
    return f"{base}/d/{quote(slug)}"


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/upload")
def upload():
    file = request.files.get("file")
    expiration = request.form.get("expiration", "download")
    if file is None or not file.filename:
        return "A file is required", 400
    if expiration not in EXPIRATIONS:
        return "Invalid expiration", 400
    slug = store_upload(file, expiration)
    url = link_for(slug)
    if request.accept_mimetypes.best == "application/json":
        return jsonify(url=url)
    return render_template("uploaded.html", url=url)


@app.get("/d/<slug>")
def download(slug: str):
    found = find_file(slug)
    if found is None:
        return "File not found or expired", 404
    path, metadata = found
    if not path.is_file():
        return "File not found or expired", 404
    if metadata["delete_after_download"]:
        directory = path.parent

        @after_this_request
        def remove_file(response):
            shutil.rmtree(directory, ignore_errors=True)
            return response

    return send_file(path, as_attachment=True, download_name=metadata["filename"])


@app.errorhandler(413)
def too_large(_error):
    return "File is too large", 413


if __name__ == "__main__":
    app.run(host=os.getenv("DROP_HOST", "0.0.0.0"), port=int(os.getenv("DROP_PORT", "8080")))
