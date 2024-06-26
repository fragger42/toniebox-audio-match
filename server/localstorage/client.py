import logging
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Set

from tinytag import TinyTag

logger = logging.getLogger(__name__)
AUDIO_EXTENSIONS = [".mp3", ".m4a", ".wma"]


@dataclass
class AudioTag:
    album: str
    artist: str
    title: str
    track: int
    disc: int


def audiobooks(root: Path) -> Set[Path]:
    all_dirs = root.glob("**/")
    all_audiobooks = set()
    for dir in all_dirs:
        if dir.parent in all_audiobooks:
            all_audiobooks.remove(dir.parent)
        all_audiobooks.add(dir)

    return all_audiobooks


def audiofiles(album: Path) -> Set[Path]:
    return {track for track in album.glob("*.*") if track.suffix in AUDIO_EXTENSIONS}


def metadata(file: Path) -> AudioTag:
    tags = TinyTag.get(str(file))
    if(tags.album is None):
        tags.album=PurePosixPath(file).parent.name
    if(tags.track is None):
        tags.track=PurePosixPath(file).stem
    else:
        tags.track=tags.track.rjust(10, '0')
    if(tags.title is None):
        tags.title=PurePosixPath(file).stem
    logger.debug("Fetched metadata for file '%s': %s", file, tags)

    return AudioTag(album=tags.album, artist=tags.albumartist, title=tags.title, track=tags.track, disc=tags.disc)
