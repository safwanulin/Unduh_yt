from flask import Flask, render_template, request, jsonify
import yt_dlp
import os
from datetime import datetime

app = Flask(__name__)
DOWNLOAD_FOLDER = 'static/downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Halaman utama
@app.route("/")
def index():
    return render_template("index.html")

# Pencarian YouTube
@app.route("/search")
def search():
    query = request.args.get("q", "")
    if not query:
        return jsonify([])
    try:
        with yt_dlp.YoutubeDL({
            'quiet': True,
            'default_search': 'ytsearch10',
            'extract_flat': True,
            'skip_download': True
        }) as ydl:
            results = ydl.extract_info(f"ytsearch10:{query}", download=False)
            videos = []
            for v in results['entries']:
                videos.append({
                    "id": v["id"],
                    "title": v["title"],
                    "thumbnail": f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg"
                })
            return jsonify(videos)
    except Exception as e:
        print("Search error:", e)
        return jsonify([])

# Fungsi bantu download video/audio
def download_media(video_id, format_str, ext):
    url = f"https://www.youtube.com/watch?v={video_id}"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{video_id}_{timestamp}.{ext}"
    output_path = os.path.join(DOWNLOAD_FOLDER, filename)

    ydl_opts = {
        'format': format_str,
        'outtmpl': output_path,
        'quiet': True,
        'noplaylist': True,
        'postprocessors': []
    }

    if ext == 'mp3':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            size_bytes = os.path.getsize(output_path)
            size_mb = round(size_bytes / 1024 / 1024, 2)
            return {
                "url": f"/{output_path.replace(os.sep, '/')}",
                "filename": filename,
                "size": f"{size_mb} MB"
            }
    except Exception as e:
        print("Download error:", e)
        return {"error": "Gagal mengunduh."}

# Download video 480p
@app.route("/download_480")
def download_480():
    video_id = request.args.get("id")
    return jsonify(download_media(video_id, "best[height<=480]", "mp4"))

# Download video 720p
@app.route("/download_720")
def download_720():
    video_id = request.args.get("id")
    return jsonify(download_media(video_id, "best[height<=720]", "mp4"))

# Download MP3
@app.route("/download_audio")
def download_audio():
    video_id = request.args.get("id")
    return jsonify(download_media(video_id, "bestaudio", "mp3"))

if __name__ == "__main__":
    app.run(debug=True)
