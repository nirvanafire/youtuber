import pytest
from src.core.url_detector import detect_url_type, UrlType


class TestDetectUrlType:
    def test_single_video(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = detect_url_type(url)
        assert result.type == UrlType.VIDEO
        assert result.video_id == "dQw4w9WgXcQ"
        assert result.playlist_id is None

    def test_shorts_url(self):
        url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        result = detect_url_type(url)
        assert result.type == UrlType.VIDEO
        assert result.video_id == "dQw4w9WgXcQ"

    def test_playlist_url(self):
        url = "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        result = detect_url_type(url)
        assert result.type == UrlType.PLAYLIST
        assert result.playlist_id == "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"

    def test_video_with_playlist(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        result = detect_url_type(url)
        assert result.type == UrlType.VIDEO
        assert result.video_id == "dQw4w9WgXcQ"
        assert result.playlist_id == "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"

    def test_channel_at_url(self):
        url = "https://www.youtube.com/@RickAstleyYT"
        result = detect_url_type(url)
        assert result.type == UrlType.CHANNEL

    def test_channel_id_url(self):
        url = "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw"
        result = detect_url_type(url)
        assert result.type == UrlType.CHANNEL

    def test_invalid_url(self):
        with pytest.raises(ValueError, match="无法识别"):
            detect_url_type("https://example.com/not-youtube")

    def test_empty_url(self):
        with pytest.raises(ValueError):
            detect_url_type("")

    def test_youtu_be_short_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = detect_url_type(url)
        assert result.type == UrlType.VIDEO
        assert result.video_id == "dQw4w9WgXcQ"
