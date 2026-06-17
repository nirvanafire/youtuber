from src.models.video import VideoInfo, FormatInfo, SubtitleInfo


class TestFormatInfo:
    def test_create_format_with_all_fields(self):
        fmt = FormatInfo(
            format_id="137",
            ext="mp4",
            resolution="1920x1080",
            fps=30,
            vcodec="avc1",
            acodec="none",
            filesize=50_000_000,
            format_note="1080p",
            is_video_only=True,
            is_audio_only=False,
        )
        assert fmt.format_id == "137"
        assert fmt.resolution == "1920x1080"
        assert fmt.is_video_only is True
        assert fmt.is_audio_only is False

    def test_format_without_filesize(self):
        fmt = FormatInfo(
            format_id="22",
            ext="mp4",
            resolution="1280x720",
            fps=30,
            vcodec="avc1",
            acodec="mp4a",
            filesize=None,
            format_note="720p",
            is_video_only=False,
            is_audio_only=False,
        )
        assert fmt.filesize is None

    def test_audio_only_format(self):
        fmt = FormatInfo(
            format_id="140",
            ext="m4a",
            resolution="audio only",
            fps=None,
            vcodec="none",
            acodec="mp4a",
            filesize=5_000_000,
            format_note="audio",
            is_video_only=False,
            is_audio_only=True,
        )
        assert fmt.is_audio_only is True
        assert fmt.is_video_only is False


class TestSubtitleInfo:
    def test_manual_subtitle(self):
        sub = SubtitleInfo(
            language="en",
            language_name="English",
            ext="srt",
            is_auto_generated=False,
        )
        assert sub.is_auto_generated is False

    def test_auto_subtitle(self):
        sub = SubtitleInfo(
            language="zh-Hans",
            language_name="Chinese (Simplified)",
            ext="vtt",
            is_auto_generated=True,
        )
        assert sub.is_auto_generated is True


class TestVideoInfo:
    def test_create_video_info(self):
        video = VideoInfo(
            id="dQw4w9WgXcQ",
            title="Never Gonna Give You Up",
            duration=212,
            uploader="Rick Astley",
            thumbnail="https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            webpage_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            formats=[
                FormatInfo(
                    format_id="22",
                    ext="mp4",
                    resolution="1280x720",
                    fps=30,
                    vcodec="avc1",
                    acodec="mp4a",
                    filesize=20_000_000,
                    format_note="720p",
                    is_video_only=False,
                    is_audio_only=False,
                )
            ],
            subtitles=[
                SubtitleInfo(
                    language="en",
                    language_name="English",
                    ext="srt",
                    is_auto_generated=False,
                )
            ],
        )
        assert video.id == "dQw4w9WgXcQ"
        assert video.title == "Never Gonna Give You Up"
        assert video.duration == 212
        assert len(video.formats) == 1
        assert len(video.subtitles) == 1

    def test_video_info_serializes_to_dict(self):
        video = VideoInfo(
            id="test",
            title="Test",
            duration=60,
            uploader="TestUser",
            thumbnail="https://example.com/thumb.jpg",
            webpage_url="https://youtube.com/watch?v=test",
            formats=[],
            subtitles=[],
        )
        d = video.model_dump()
        assert d["id"] == "test"
        assert d["formats"] == []
        assert d["subtitles"] == []
