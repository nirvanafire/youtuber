import math
import pytest
from unittest.mock import MagicMock, patch
from src.core.ytdl_wrapper import YtdlWrapper
from src.models.video import VideoInfo
from src.models.playlist import PlaylistInfo


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


class TestYtdlWrapperExtractPlaylist:
    @pytest.fixture
    def wrapper(self):
        return YtdlWrapper()

    @pytest.fixture
    def mock_playlist_info(self):
        return {
            "id": "PLtest123",
            "title": "My Playlist",
            "uploader": "TestUser",
            "entries": [
                {
                    "id": "vid1",
                    "title": "First Video",
                    "duration": 60,
                    "thumbnail": "https://example.com/1.jpg",
                    "webpage_url": "https://youtube.com/watch?v=vid1",
                },
                {
                    "id": "vid2",
                    "title": "Second Video",
                    "duration": 90,
                    "thumbnail": "https://example.com/2.jpg",
                    "webpage_url": "https://youtube.com/watch?v=vid2",
                },
            ],
        }

    def test_extract_playlist(self, wrapper, mock_playlist_info):
        with patch("src.core.ytdl_wrapper.yt_dlp.YoutubeDL") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = mock_playlist_info
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            info = wrapper.extract_playlist(
                "https://www.youtube.com/playlist?list=PLtest123",
                page=1,
                page_size=50,
            )

        assert isinstance(info, PlaylistInfo)
        assert info.id == "PLtest123"
        assert info.title == "My Playlist"
        assert info.video_count == 2
        assert len(info.videos) == 2
        assert info.page == 1

    def test_extract_playlist_pagination(self, wrapper):
        entries = [
            {"id": f"vid{i}", "title": f"V{i}", "duration": 60,
             "thumbnail": f"https://example.com/{i}.jpg",
             "webpage_url": f"https://youtube.com/watch?v=vid{i}"}
            for i in range(100)
        ]
        raw = {"id": "PLbig", "title": "Big", "uploader": "User", "entries": entries}

        with patch("src.core.ytdl_wrapper.yt_dlp.YoutubeDL") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = raw
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            page1 = wrapper.extract_playlist("https://youtube.com/playlist?list=PLbig", page=1, page_size=50)

        assert page1.total_pages == 2
        assert len(page1.videos) == 50
        assert page1.page == 1


class TestYtdlWrapperSubtitleDownload:
    def test_download_with_subtitle_lang(self):
        wrapper = YtdlWrapper()
        with patch("src.core.ytdl_wrapper.yt_dlp.YoutubeDL") as MockYDL:
            mock_instance = MagicMock()
            MockYDL.return_value.__enter__ = MagicMock(return_value=mock_instance)
            MockYDL.return_value.__exit__ = MagicMock(return_value=False)
            mock_instance.extract_info.return_value = {"title": "test", "ext": "mp4"}
            mock_instance.prepare_filename.return_value = "/tmp/test.mp4"

            wrapper.download(
                url="https://youtube.com/watch?v=test",
                format_id="22",
                output_dir="/tmp",
                subtitle_lang="en",
            )

            # Verify subtitle options were set
            call_opts = MockYDL.call_args[0][0]
            assert call_opts["writesubtitles"] is True
            assert call_opts["subtitleslangs"] == ["en"]

    def test_download_without_subtitle_lang(self):
        wrapper = YtdlWrapper()
        with patch("src.core.ytdl_wrapper.yt_dlp.YoutubeDL") as MockYDL:
            mock_instance = MagicMock()
            MockYDL.return_value.__enter__ = MagicMock(return_value=mock_instance)
            MockYDL.return_value.__exit__ = MagicMock(return_value=False)
            mock_instance.extract_info.return_value = {"title": "test", "ext": "mp4"}
            mock_instance.prepare_filename.return_value = "/tmp/test.mp4"

            wrapper.download(
                url="https://youtube.com/watch?v=test",
                format_id="22",
                output_dir="/tmp",
            )

            call_opts = MockYDL.call_args[0][0]
            assert "writesubtitles" not in call_opts
