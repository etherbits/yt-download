from pytube import YouTube
from functools import partial
import sys
import os
import subprocess
import threading
import json
import uuid

def progress_handler(data, stream, chunk, bytes_remaining):
    data["status"] = "downloading"
    data["progress"] = (stream.filesize - bytes_remaining) / stream.filesize
    print(json.dumps(data), flush=True)

def download(output_path, video_url):   
    
    data = {
        "status": "none",
        "progress": 0,
        "title": "none",
        "thumbnail_url": ""
    }
    yt = None
    
    try:
        yt = YouTube(video_url, on_progress_callback=partial(progress_handler, data))
    
    except:    
        data["status"] = "error"
        print(json.dumps(data), flush=True)
        sys.exit(f"yt-download error: {sys.exc_info()[0]}")

    data["status"] = "starting"
    data["title"] = yt.title
    data["thumbnail_url"] = yt.thumbnail_url
    print(json.dumps(data), flush=True)
    
    file_id = uuid.uuid4()

    parsed_title = (
        yt.title.replace("/", "█")
        .replace("\\", "█")
        .replace(":", "█")
        .replace("*", "█")
        .replace("?", "█")
        .replace('"', "█")
        .replace("<", "█")
        .replace(">", "█")
        .replace("|", "█")
    )

    audio_stream = yt.streams.get_audio_only("webm")
    audio_filename = f'{file_id}.webm'
    audio_stream.download(filename=audio_filename)
    
    data["status"] = "processing"
    print(json.dumps(data), flush=True)
    subprocess.run(
        [
            "ffmpeg",
            "-nostats",
            "-loglevel",
            "0",
            "-i",
            audio_filename,
            "-vn",
            "-c:a",
            "copy",
            "-y",
            f"{output_path}{parsed_title}.opus",
        ]
    )
    data["status"] = "complete"
    print(json.dumps(data), flush=True)

    os.remove(audio_filename)
    
def main():
    if len(sys.argv) < 3 or type(sys.argv[1]) != str or type(sys.argv[2]) != str:
        sys.exit("Usage: yt-download [path] [url]")
    
    download(sys.argv[1], sys.argv[2])
    
main()