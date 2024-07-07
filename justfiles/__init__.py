import asyncio
import atexit
import os
import shutil
import tempfile
import zipfile
from hashlib import sha256
from pathlib import Path

import aiofiles
import aiofiles.os as aos
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from fastapi.staticfiles import StaticFiles

KEEP_ZIP = True
BASE_DIR = os.environ.get("SHARED", "/tmp").rstrip("/")
TEMP_DIR = tempfile.mkdtemp(prefix="hprbwzr", suffix="temp")
STATIC_DIR = os.environ.get("STATIC", "dist")
SHOW_HIDDEN = False
DEFAULT_FILE_PERMISSIONS = 0o644

print(f"Sharing {BASE_DIR}")
try:
    os.mkdir(TEMP_DIR, 0o755)
except FileExistsError:
    pass


def cleanup():
    """Clean up the temporary directory."""
    try:
        shutil.rmtree(TEMP_DIR)
    except Exception:
        pass


atexit.register(cleanup)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "http://localhost",
        "http://files.crava.ch",
        "https://files.crava.ch",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")


@app.get("/")
async def main():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/favicon.ico")
async def favicon():
    return FileResponse(os.path.join(STATIC_DIR, "favicon.ico"))


def get_real_path(path):
    """Get the real path of a file or folder."""
    root = os.path.abspath(os.path.join(BASE_DIR, path.lstrip("/")))
    if not root.startswith(BASE_DIR):
        raise HTTPException(status_code=400, detail="Invalid path")
    return root


@app.get("/files/")
@app.get("/files/{path:path}")
async def list_files(path="./") -> JSONResponse:
    root = get_real_path(path)
    files = []
    folders = []
    for entry in await aos.scandir(root):
        if not SHOW_HIDDEN and entry.name.startswith("."):
            continue
        if entry.is_file():
            files.append(entry.name)
        else:
            folders.append(entry.name)
    folders.sort()
    files.sort()
    return {"files": files, "folders": folders}


@app.post("/upload")
async def upload_file(files: list[UploadFile] = File(...)) -> dict[str, str]:
    """Upload files to the server."""
    for file in files:
        file_location = os.path.join(BASE_DIR, file.filename)
        async with aiofiles.open(file_location, "wb") as f:
            while True:
                content = await file.read(1024**2)  # read file content
                if not content:
                    break
                await f.write(content)  # write content to file
        os.chmod(file_location, DEFAULT_FILE_PERMISSIONS)
    return {"message": "Files uploaded successfully"}


@app.post("/mkdir/{file_name:path}")
def make_directory(file_name: str) -> FileResponse:
    file_path = get_real_path(file_name)
    os.mkdir(file_path)


@app.get("/download-zip/{path:path}")
async def download_zip(path: str, background_tasks: BackgroundTasks) -> FileResponse:
    # compute hash of path
    hashed = sha256(path.encode()).hexdigest()
    zip_filename = f"dir_{hashed}.zip"
    zip_path = os.path.join(TEMP_DIR, zip_filename)

    source_path = get_real_path(path)

    def zip_files():
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for entry in os.scandir(source_path):
                if entry.is_file():
                    zipf.write(entry.path, os.path.relpath(entry.path, BASE_DIR))

    # Run the zipping operation in a separate thread
    await asyncio.to_thread(zip_files)

    if not KEEP_ZIP:
        background_tasks.add_task(clean_up, zip_path)
    return FileResponse(zip_path, filename=zip_filename)


def clean_up(file_path: str):
    """Clean up the generated file."""
    if os.path.exists(file_path):
        os.remove(file_path)


def serve():
    import uvicorn

    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    serve()
