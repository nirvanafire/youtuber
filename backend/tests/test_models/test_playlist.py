from src.models.playlist import PlaylistInfo, PlaylistVideoItem


class TestPlaylistVideoItem:
    def test_create_item(self):
        item = PlaylistVideoItem(
            id="abc123",
            title="Video 1",
            duration=120,
            thumbnail="https://example.com/thumb.jpg",
            url="https://www.youtube.com/watch?v=abc123",
        )
        assert item.id == "abc123"
        assert item.duration == 120

    def test_item_without_duration(self):
        item = PlaylistVideoItem(
            id="abc123",
            title="Live Stream",
            duration=None,
            thumbnail="https://example.com/thumb.jpg",
            url="https://www.youtube.com/watch?v=abc123",
        )
        assert item.duration is None


class TestPlaylistInfo:
    def test_create_playlist(self):
        playlist = PlaylistInfo(
            id="PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
            title="My Playlist",
            uploader="TestUser",
            video_count=3,
            videos=[
                PlaylistVideoItem(
                    id="vid1", title="First", duration=60,
                    thumbnail="https://example.com/1.jpg",
                    url="https://youtube.com/watch?v=vid1",
                ),
                PlaylistVideoItem(
                    id="vid2", title="Second", duration=90,
                    thumbnail="https://example.com/2.jpg",
                    url="https://youtube.com/watch?v=vid2",
                ),
                PlaylistVideoItem(
                    id="vid3", title="Third", duration=120,
                    thumbnail="https://example.com/3.jpg",
                    url="https://youtube.com/watch?v=vid3",
                ),
            ],
            page=1,
            total_pages=1,
        )
        assert playlist.video_count == 3
        assert len(playlist.videos) == 3
        assert playlist.page == 1

    def test_playlist_pagination(self):
        videos = [
            PlaylistVideoItem(
                id=f"vid{i}", title=f"Video {i}", duration=60,
                thumbnail=f"https://example.com/{i}.jpg",
                url=f"https://youtube.com/watch?v=vid{i}",
            )
            for i in range(50)
        ]
        playlist = PlaylistInfo(
            id="PLtest", title="Big Playlist", uploader="TestUser",
            video_count=200, videos=videos, page=1, total_pages=4,
        )
        assert playlist.total_pages == 4
        assert len(playlist.videos) == 50
