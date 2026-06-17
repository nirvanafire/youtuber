import pytest
from unittest.mock import MagicMock, patch
from src.core.ytdl_wrapper import YtdlWrapper
from src.models.video import VideoInfo


class TestYtdlWrapperExtractInfo:
    @pytest.fixture
    def wrapper(self):
        return YtdlWrapper()

    @pytest.fixture
    def mock_ytdl_info(self):
        """Simulated yt-dlp extract_info result."""
        return {
            "id": "dQw4w9WgXcQ",
            "title": "Never Gonna Give You Up",
            "duration": 212,
            "uploader": "Rick Astley",
            "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "webpage_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "formats": [
                {
                    "format_id": "22",
                    "ext": "mp4",
                    "resolution": "1280x720",
                    "fps": 30,
                    "vcodec": "avc1",
                    "acodec": "mp4a",
                    "filesize": 20_000_000,
                    "format_note": "720p",
                },
                {
                    "format_id": "137",
                    "ext": "mp4",
                    "resolution": "1920x1080",
                    "fps": 30,
                    "vcodec": "avc1",
                    "acodec": "none",
                    "filesize": 50_000_000,
                    "format_note": "1080p",
                },
                {
                    "format_id": "140",
                    "ext": "m4a",
                    "resolution": "audio only",
                    "fps": None,
                    "vcodec": "none",
                    "acodec": "mp4a",
                    "filesize": 5_000_000,
                    "format_note": "audio",
                },
            ],
            "subtitles": {
                "en": [
                    {"ext": "srt", "url": "https://example.com/en.srt"},
                ],
            },
            "automatic_captions": {
                "zh-Hans": [
                    {"ext": "vtt", "url": "https://example.com/zh.vtt"},
                ],
            },
        }

    def test_extract_video_info(self, wrapper, mock_ytdl_info):
        with patch("src.core.ytdl_wrapper.yt_dlp.YoutubeDL") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = mock_ytdl_info
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            info = wrapper.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        assert isinstance(info, VideoInfo)
        assert info.id == "dQw4w9WgXcQ"
        assert info.title == "Never Gonna Give You Up"
        assert info.duration == 212
        assert info.uploader == "Rick Astley"

    def test_extract_info_parses_formats(self, wrapper, mock_ytdl_info):
        with patch("src.core.ytdl_wrapper.yt_dlp.YoutubeDL") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = mock_ytdl_info
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            info = wrapper.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        assert len(info.formats) == 3
        video_only = [f for f in info.formats if f.is_video_only]
        audio_only = [f for f in info.formats if f.is_audio_only]
        assert len(video_only) == 1
        assert len(audio_only) == 1
        assert video_only[0].format_id == "137"
        assert audio_only[0].format_id == "140"

    def test_extract_info_parses_subtitles(self, wrapper, mock_ytdl_info):
        with patch("src.core.ytdl_wrapper.yt_dlp.YoutubeDL") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = mock_ytdl_info
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            info = wrapper.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        assert len(info.subtitles) == 2
        manual = [s for s in info.subtitles if not s.is_auto_generated]
        auto = [s for s in info.subtitles if s.is_auto_generated]
        assert len(manual) == 1
        assert manual[0].language == "en"
        assert len(auto) == 1
        assert auto[0].language == "zh-Hans"

    def test_extract_info_no_formats(self, wrapper):
        raw = {
            "id": "test",
            "title": "Test",
            "duration": 60,
            "uploader": "User",
            "thumbnail": "https://example.com/t.jpg",
            "webpage_url": "https://youtube.com/watch?v=test",
            "formats": None,
            "subtitles": {},
            "automatic_captions": {},
        }
        with patch("src.core.ytdl_wrapper.yt_dlp.YoutubeDL") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = raw
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            info = wrapper.extract_info("https://youtube.com/watch?v=test")

        assert info.formats == []
        assert info.subtitles == []

    def test_extract_info_ytdl_error(self, wrapper):
        import yt_dlp

        with patch("src.core.ytdl_wrapper.yt_dlp.YoutubeDL") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.extract_info.side_effect = yt_dlp.utils.DownloadError("Video unavailable")
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            with pytest.raises(Exception, match="Video unavailable"):
                wrapper.extract_info("https://youtube.com/watch?v=private")
