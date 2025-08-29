import os
import glob
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import yt_dlp

# -------------------------
# Config
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# If running on Render with persistent disk, use that path
RENDER_DISK_PATH = "/opt/render/project/src/downloads"
if os.path.isdir(RENDER_DISK_PATH):
    DOWNLOAD_DIR = RENDER_DISK_PATH
else:
    DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")

HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
FFMPEG_DIR = os.path.join(BASE_DIR, "ffmpeg")  # Optional for local ffmpeg binaries

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__)
app.secret_key = "change-me-to-something-secret"

# -------------------------
# Helpers
# -------------------------
def save_history(entry: dict):
    logging.info("Saving history entry")
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:
        data = []
    data.insert(0, entry)  # newest first
    with open(HISTORY_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)

def find_downloaded_file(prepared_path_base):
    """
    prepared_path_base: full path without extension (base)
    find most recent file that matches base.*
    """
    pattern = prepared_path_base + ".*"
    matches = glob.glob(pattern)
    if not matches:
        return None
    return max(matches, key=os.path.getctime)

# -------------------------
# Routes
# -------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/history")
def history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:
        data = []
    return render_template("history.html", history=data)

@app.route("/download", methods=["POST"])
def download():
    url = (request.form.get("url") or "").strip()
    quality = request.form.get("quality") or "720p"
    fmt = request.form.get("format") or "mp4"

    logging.info(f"Download requested: url={url} quality={quality} format={fmt}")

    if not url:
        flash("Please provide a URL.")
        return redirect(url_for("index"))

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outtmpl = os.path.join(DOWNLOAD_DIR, "%(title)s_" + ts + "_%(id)s.%(ext)s")

    # Base yt-dlp options
    ydl_opts = {
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": True,
        "progress_hooks": [],
    }

    # Use ffmpeg folder if present
    if os.path.isdir(FFMPEG_DIR):
        ydl_opts["ffmpeg_location"] = FFMPEG_DIR
        logging.info(f"Using ffmpeg at: {FFMPEG_DIR}")

    # >>> OPTION 3: use cookies from your installed browser
    ydl_opts["cookiesfrombrowser"] = ("chrome",)  # or ("firefox",) if you prefer
    # This tells yt-dlp to grab login/session cookies automatically

    # Format rules
    if fmt == "mp3":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:  # mp4
        if quality == "1080p":
            ydl_opts["format"] = "bestvideo[height<=1080]+bestaudio/best"
        else:
            ydl_opts["format"] = "bestvideo[height<=720]+bestaudio/best"
        ydl_opts["merge_output_format"] = "mp4"

    try:
        logging.info("Starting download via yt-dlp...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            prepared = ydl.prepare_filename(info)
            base_no_ext = os.path.splitext(prepared)[0]
            actual_file = find_downloaded_file(base_no_ext)
            if not actual_file:
                logging.error("Downloaded file not found after yt-dlp ran.")
                return "Download finished but file not found on server.", 500

            logging.info(f"Actual downloaded file: {actual_file}")

            entry = {
                "title": info.get("title") if isinstance(info, dict) else os.path.basename(actual_file),
                "url": url,
                "format": fmt,
                "quality": quality,
                "filename": os.path.basename(actual_file),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_history(entry)

            logging.info("Sending file to client...")
            return send_file(actual_file, as_attachment=True)

    except Exception as e:
        logging.exception("Download failed")
        return f"Error during download: {e}", 500

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    logging.info("Starting Flask app")
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
