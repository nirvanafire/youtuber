from pydantic import BaseModel


class PlaylistVideoItem(BaseModel):
    id: str
    title: str
    duration: int | None
    thumbnail: str
    url: str


class PlaylistInfo(BaseModel):
    id: str
    title: str
    uploader: str
    video_count: int
    videos: list[PlaylistVideoItem]
    page: int
    total_pages: int
