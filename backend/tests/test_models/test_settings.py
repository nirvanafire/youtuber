from src.models.settings import AppSettings


class TestAppSettings:
    def test_default_settings(self):
        settings = AppSettings()
        assert settings.download_dir is not None
        assert settings.default_quality == "best"
        assert settings.proxy is None
        assert settings.max_concurrent_downloads == 3
        assert settings.language == "zh"

    def test_custom_settings(self):
        settings = AppSettings(
            download_dir="/tmp/downloads",
            default_quality="1080p",
            proxy="http://127.0.0.1:7890",
            max_concurrent_downloads=5,
            language="en",
        )
        assert settings.download_dir == "/tmp/downloads"
        assert settings.default_quality == "1080p"
        assert settings.proxy == "http://127.0.0.1:7890"
        assert settings.max_concurrent_downloads == 5
        assert settings.language == "en"

    def test_settings_serialization_roundtrip(self):
        original = AppSettings(
            download_dir="/tmp/test",
            default_quality="720p",
            proxy="socks5://127.0.0.1:1080",
            max_concurrent_downloads=2,
            language="en",
        )
        data = original.model_dump()
        restored = AppSettings(**data)
        assert restored == original

    def test_concurrent_downloads_bounds(self):
        settings = AppSettings(max_concurrent_downloads=1)
        assert settings.max_concurrent_downloads == 1
        settings = AppSettings(max_concurrent_downloads=10)
        assert settings.max_concurrent_downloads == 10
