import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

import localstorage.client

# configuration
from models.audio import AudioBook
from models.tonie import Tonie
from toniecloud.client import TonieCloud

logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
logger = logging.getLogger(__name__)

DEBUG = False

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

creative_tonies = None
audio_books_models = None
audio_books = None

def audiobooks():
    audiobooks = localstorage.client.audiobooks(Path(os.environ.get("TONIE_AUDIO_MATCH_MEDIA_PATH")))
    logger.debug("Discovered audiobook paths: %s", audiobooks)
    for album in audiobooks:
        audiobook = AudioBook.from_path(album)
        if audiobook:
            yield audiobook

def refreshAudioBooks():
    global audio_books_models
    global audio_books
    audio_books_models = list(audiobooks())
    audio_books = [
        {
            "id": album.id,
            "artist": album.artist,
            "title": album.album,
            "disc": album.album_no,
            "cover_uri": str(album.cover_relative) if album.cover else None,
        }
        for album in audio_books_models
    ]
    
def refreshTonies():
    global creative_tonies
    tonie_cloud_api = TonieCloud(os.environ.get("TONIE_AUDIO_MATCH_USER"), os.environ.get("TONIE_AUDIO_MATCH_PASS"))
    creative_tonies = tonie_cloud_api.creativetonies()

refreshAudioBooks()
refreshTonies()

@app.route("/refresh", methods=["GET"])
def refreshApp():
    refreshTonies()
    refreshAudioBooks()
    return jsonify("OK!")


@app.route("/audiobooks", methods=["GET"])
def all_audiobooks():
    return jsonify({"status": "success", "audiobooks": audio_books,})


@app.route("/creativetonies", methods=["GET"])
def all_creativetonies():
    return jsonify({"status": "success", "creativetonies": creative_tonies,})


@dataclass
class Upload:
    tonie: Tonie
    audiobook: AudioBook

    @classmethod
    def from_ids(cls, tonie: str, audiobook: str) -> "Upload":
        return cls(
            next(filter(lambda t: t.id == tonie, creative_tonies), None),
            next(filter(lambda a: a.id == audiobook, audio_books_models), None),
        )


@app.route("/upload", methods=["POST"])
def upload_album_to_tonie():
    body = request.json
    upload = Upload.from_ids(tonie=body["tonie_id"], audiobook=body["audiobook_id"])
    logger.debug(f"Created upload object: {upload}")
    tonie_cloud_api = TonieCloud(os.environ.get("TONIE_AUDIO_MATCH_USER"), os.environ.get("TONIE_AUDIO_MATCH_PASS"))
    status = tonie_cloud_api.put_album_on_tonie(upload.audiobook, upload.tonie)
    return jsonify({"status": "success" if status else "failure", "upload_id": str(upload)}), 201

@app.route("/getLogo", methods=["GET"])
def getLogo():
    audiobook = request.args.get('audiobook_id')
    upload = Upload.from_ids("", audiobook=request.args.get('audiobook_id'))
    return send_file(upload.audiobook.cover, download_name='logo.jpg')

if __name__ == "__main__":
    app.run(host="0.0.0.0")
