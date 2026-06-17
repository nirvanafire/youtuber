import yt_dlp
from src.models.video import VideoInfo, FormatInfo, SubtitleInfo


class YtdlWrapper:
    def __init__(self, proxy: str | None = None):
        self._proxy = proxy

    def _base_opts(self) -> dict:
        opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        if self._proxy:
            opts["proxy"] = self._proxy
        return opts

    def _classify_format(self, fmt: dict) -> tuple[bool, bool]:
        vcodec = fmt.get("vcodec", "none")
        acodec = fmt.get("acodec", "none")
        is_video_only = vcodec != "none" and acodec == "none"
        is_audio_only = vcodec == "none" and acodec != "none"
        return is_video_only, is_audio_only

    def _parse_formats(self, raw_formats: list[dict] | None) -> list[FormatInfo]:
        if not raw_formats:
            return []
        result = []
        for fmt in raw_formats:
            is_video_only, is_audio_only = self._classify_format(fmt)
            result.append(FormatInfo(
                format_id=fmt.get("format_id", ""),
                ext=fmt.get("ext", ""),
                resolution=fmt.get("resolution", "N/A"),
                fps=fmt.get("fps"),
                vcodec=fmt.get("vcodec", "none"),
                acodec=fmt.get("acodec", "none"),
                filesize=fmt.get("filesize"),
                format_note=fmt.get("format_note", ""),
                is_video_only=is_video_only,
                is_audio_only=is_audio_only,
            ))
        return result

    def _parse_subtitles(self, subs: dict | None, auto_subs: dict | None) -> list[SubtitleInfo]:
        result = []
        if subs:
            for lang, entries in subs.items():
                ext = entries[0]["ext"] if entries else "srt"
                result.append(SubtitleInfo(
                    language=lang,
                    language_name=lang,
                    ext=ext,
                    is_auto_generated=False,
                ))
        if auto_subs:
            for lang, entries in auto_subs.items():
                ext = entries[0]["ext"] if entries else "vtt"
                result.append(SubtitleInfo(
                    language=lang,
                    language_name=lang,
                    ext=ext,
                    is_auto_generated=True,
                ))
        return result

    def extract_info(self, url: str) -> VideoInfo:
        opts = self._base_opts()
        with yt_dlp.YoutubeDL(opts) as ydl:
            raw = ydl.extract_info(url, download=False)

        return VideoInfo(
            id=raw.get("id", ""),
            title=raw.get("title", ""),
            duration=raw.get("duration", 0),
            uploader=raw.get("uploader", ""),
            thumbnail=raw.get("thumbnail", ""),
            webpage_url=raw.get("webpage_url", url),
            formats=self._parse_formats(raw.get("formats")),
            subtitles=self._parse_subtitles(
                raw.get("subtitles"),
                raw.get("automatic_captions"),
            ),
        )
