from pytube import YouTube
import sys
import os
import subprocess
import requests
import threading
import json
import uuid

def progress_handler(stream, chunk, bytes_remaining):
    data["status"] = "downloading"
    data["progress"] = (stream.filesize - bytes_remaining) / stream.filesize
    print(json.dumps(data), flush=True)


def download_audio():
    audio_stream.download(filename=audio_name)


def download_thumbnail():
    img_data = requests.get(yt.thumbnail_url).content
    with open(thumbnail_name, "wb") as handler:
        handler.write(img_data)


if len(sys.argv) < 3 or type(sys.argv[1]) != str or type(sys.argv[2]) != str:
    sys.exit("Usage: downer [output_path] [video_url] ")


data = {
    "status": "none",
    "progress": 0,
    "title": "none",
}

output_path = sys.argv[1]
video_url = sys.argv[2]

yt = YouTube(video_url, on_progress_callback=progress_handler)

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
audio_name = f'{file_id}.webm'
thumbnail_name = f'{file_id}.jpg'

t1 = threading.Thread(target=download_audio)
t2 = threading.Thread(target=download_thumbnail)

t1.start()
t2.start()

data["status"] = "starting"
data["title"] = parsed_title
print(json.dumps(data), flush=True)


t1.join()
t2.join()

data["status"] = "processing"
print(json.dumps(data), flush=True)
subprocess.run(
    [
        "ffmpeg",
        "-nostats",
        "-loglevel",
        "0",
        "-i",
        audio_name,
        "-vn",
        "-c:a",
        "copy",
        "-y",
        "-attach",
        f"{file_id}.jpg",
        "-metadata:s:t:0",
        "mimetype=image/jpg",
        "-metadata:s:t:0",
        "filename=cover.jpg",
        f"{output_path}{parsed_title}.mkv",
    ]
)
data["status"] = "complete"
print(json.dumps(data), flush=True)

os.remove(audio_name)
os.remove(thumbnail_name)