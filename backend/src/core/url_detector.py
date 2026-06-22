import logging
import re
from enum import Enum
from pydantic import BaseModel

logger = logging.getLogger("youtuber.url_detector")


class UrlType(str, Enum):
    VIDEO = "video"
    PLAYLIST = "playlist"
    CHANNEL = "channel"


class UrlDetectionResult(BaseModel):
    type: UrlType
    video_id: str | None = None
    playlist_id: str | None = None
    channel_id: str | None = None
    raw_url: str


_PATTERNS = {
    "video": [
        re.compile(r"(?:youtube\.com/watch\?.*v=|youtu\.be/|youtube\.com/shorts/)([\w-]{11})"),
    ],
    "playlist": [
        re.compile(r"youtube\.com/playlist\?.*list=([\w-]+)"),
    ],
    "playlist_param": [
        re.compile(r"[?&]list=([\w-]+)"),
    ],
    "channel": [
        re.compile(r"youtube\.com/@([\w.-]+)"),
        re.compile(r"youtube\.com/channel/([\w-]+)"),
    ],
}


def detect_url_type(url: str) -> UrlDetectionResult:
    logger.info(f"detect_url_type: raw url={url!r}")
    if not url or not url.strip():
        raise ValueError("URL 不能为空")

    url = url.strip()
    logger.info(f"detect_url_type: trimmed url={url!r}")

    # Check playlist first (may also have video)
    for pattern in _PATTERNS["playlist"]:
        m = pattern.search(url)
        if m:
            playlist_id = m.group(1)
            video_id = None
            for vp in _PATTERNS["video"]:
                vm = vp.search(url)
                if vm:
                    video_id = vm.group(1)
                    break
            if video_id:
                logger.info(f"detect_url_type: matched video+playlist, video_id={video_id}, playlist_id={playlist_id}")
                return UrlDetectionResult(
                    type=UrlType.VIDEO,
                    video_id=video_id,
                    playlist_id=playlist_id,
                    raw_url=url,
                )
            logger.info(f"detect_url_type: matched playlist, playlist_id={playlist_id}")
            return UrlDetectionResult(
                type=UrlType.PLAYLIST,
                playlist_id=playlist_id,
                raw_url=url,
            )

    # Check video
    for pattern in _PATTERNS["video"]:
        m = pattern.search(url)
        if m:
            video_id = m.group(1)
            playlist_id = None
            for pp in _PATTERNS["playlist_param"]:
                pm = pp.search(url)
                if pm:
                    playlist_id = pm.group(1)
                    break
            logger.info(f"detect_url_type: matched video, video_id={video_id}, playlist_id={playlist_id}")
            return UrlDetectionResult(
                type=UrlType.VIDEO,
                video_id=video_id,
                playlist_id=playlist_id,
                raw_url=url,
            )

    # Check channel
    for pattern in _PATTERNS["channel"]:
        m = pattern.search(url)
        if m:
            logger.info(f"detect_url_type: matched channel, channel_id={m.group(1)}")
            return UrlDetectionResult(
                type=UrlType.CHANNEL,
                channel_id=m.group(1),
                raw_url=url,
            )

    logger.warning(f"detect_url_type: no pattern matched for url={url}")
    raise ValueError(f"无法识别的 YouTube URL: {url}")
