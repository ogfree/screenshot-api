from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
import subprocess
import uuid
import os

API_KEY = "lol-its-secret-no-hCk1nG"
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Screenshot API is live"}

@app.get("/screenshot")
def screenshot(
    key: str = Query(None),
    url: str = Query(...),
    width: int = Query(1280),
    height: int = Query(720),
    format: str = Query("png"),         # png, jpeg, html
    vt: int = Query(3000)               # virtual time budget in ms
):
    # 🔐 API key check
    if key != API_KEY:
        return JSONResponse({"error": "Unauthorized: invalid API key"}, status_code=401)

    if format not in ["png", "jpeg", "html"]:
        return JSONResponse({"error": "Unsupported format"}, status_code=400)

    output_ext = "png" if format in ["png", "jpeg"] else "html"
    filename = f"/tmp/{uuid.uuid4().hex}.{output_ext}"

    chrome_cmd = [
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        f"--window-size={width},{height}",
        f"--virtual-time-budget={vt}",
        "--run-all-compositor-stages-before-draw"
    ]

    if format == "html":
        chrome_cmd.append("--dump-dom")
    else:
        chrome_cmd.append(f"--screenshot={filename}")

    chrome_cmd.append(url)

    try:
        result = subprocess.run(chrome_cmd, check=True, capture_output=True, text=True, timeout=30)
    except subprocess.CalledProcessError as e:
        return JSONResponse({"error": "Chrome failed", "details": e.stderr}, status_code=500)
    except subprocess.TimeoutExpired:
        return JSONResponse({"error": "Timed out rendering"}, status_code=504)

    if format == "html":
        return HTMLResponse(content=result.stdout, status_code=200)

    media_type = "image/png" if format == "png" else "image/jpeg"
    return FileResponse(filename, media_type=media_type)
