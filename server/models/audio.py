import os
import imghdr
import logging
from dataclasses import dataclass
from hashlib import sha512
from io import BytesIO
from pathlib import Path
from typing import List, ClassVar, Optional

from tinytag import TinyTag

from localstorage.client import audiofiles, metadata

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AudioTrack:
    album: str
    title: str
    track: int
    file: Path


@dataclass(frozen=True)
class AudioBook:
    covers: ClassVar[Path] = Path(os.environ.get("TONIE_AUDIO_MATCH_MEDIA_PATH"))
    id: str
    album: str
    album_no: int
    artist: str
    cover: Optional[Path]
    tracks: List[AudioTrack]

    @property
    def cover_relative(self) -> Optional[Path]:
        if not self.cover:
            return

        return self.cover.relative_to(self.covers)

    @classmethod
    def from_path(cls, album: Path) -> Optional["AudioBook"]:
        tracks_files = audiofiles(album)
        if not tracks_files:
            logger.error("Album without tracks or no tracks with expected extension: %s", album)
            return None

        tracks: List[AudioTrack] = []

        for file in tracks_files:
            tags = metadata(file)
            tracks.append(AudioTrack(album=tags.album, title=tags.title, track=tags.track, file=file))

        if not len({track.album for track in tracks}) == 1:
            print("WARNING De-normalized album title.")

        tags_first = metadata(tracks[0].file)
        
        album_id = cls.path_hash(album)
        if os.path.exists(album.joinpath("logo.jpg")):
            cover_path = album.joinpath("logo.jpg")
        else:
            cover_path = ""

        return cls(
            id=album_id,
            album=tracks[0].album,
            album_no=tags_first.disc,
            artist=tags_first.artist,
            cover=cover_path,
            tracks=tracks,
        )

    @staticmethod
    def path_hash(path: Path) -> str:
        return sha512(str(path).encode("utf-8")).hexdigest()
