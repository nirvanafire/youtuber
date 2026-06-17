from pydantic import BaseModel


class FormatInfo(BaseModel):
    format_id: str
    ext: str
    resolution: str
    fps: int | None
    vcodec: str
    acodec: str
    filesize: int | None
    format_note: str
    is_video_only: bool
    is_audio_only: bool


class SubtitleInfo(BaseModel):
    language: str
    language_name: str
    ext: str
    is_auto_generated: bool


class VideoInfo(BaseModel):
    id: str
    title: str
    duration: int
    uploader: str
    thumbnail: str
    webpage_url: str
    formats: list[FormatInfo]
    subtitles: list[SubtitleInfo]
