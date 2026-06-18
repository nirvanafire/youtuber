import logging
import math
import os
from collections.abc import Callable

import yt_dlp
from src.models.video import VideoInfo, FormatInfo, SubtitleInfo
from src.models.playlist import PlaylistInfo, PlaylistVideoItem

logger = logging.getLogger("youtuber.ytdl")


class DownloadInterrupted(Exception):
    pass


class YtdlWrapper:
    def __init__(self, proxy: str | None = None):
        self._proxy = proxy

    def _base_opts(self) -> dict:
        # NOTE: quiet/no_warnings set to False for diagnostics — restore after investigation
        opts = {"quiet": False, "no_warnings": False, "skip_download": True}
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
        logger.info(f"extract_info: url={url}")
        opts = self._base_opts()
        logger.info(f"extract_info: opts={opts}")
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                raw = ydl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"extract_info: yt-dlp DownloadError: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"extract_info: unexpected error: {type(e).__name__}: {e}", exc_info=True)
            raise

        logger.info(f"extract_info: raw keys={list(raw.keys()) if raw else 'None'}")
        logger.info(f"extract_info: id={raw.get('id')}, title={raw.get('title')}, extractor={raw.get('extractor')}")
        fmt_count = len(raw.get("formats") or [])
        sub_count = len(raw.get("subtitles") or {})
        logger.info(f"extract_info: formats={fmt_count}, subtitles={sub_count}")

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

    @staticmethod
    def _normalize_playlist_url(url: str) -> str:
        """Convert watch?v=...&list=... to pure playlist URL for reliable extraction."""
        import re
        m = re.search(r'[?&]list=([\w-]+)', url)
        if m and 'playlist?list=' not in url:
            playlist_id = m.group(1)
            normalized = f"https://www.youtube.com/playlist?list={playlist_id}"
            logger.info(f"_normalize_playlist_url: {url} -> {normalized}")
            return normalized
        return url

    def extract_playlist(self, url: str, page: int = 1, page_size: int = 50) -> PlaylistInfo:
        url = self._normalize_playlist_url(url)
        logger.info(f"extract_playlist: url={url}, page={page}, page_size={page_size}")
        opts = self._base_opts()
        opts["extract_flat"] = True
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                raw = ydl.extract_info(url, download=False)
        except Exception as e:
            logger.error(f"extract_playlist: error: {type(e).__name__}: {e}", exc_info=True)
            raise

        entries = list(raw.get("entries", []))
        total = len(entries)
        total_pages = max(1, math.ceil(total / page_size))
        start = (page - 1) * page_size
        end = start + page_size
        page_entries = entries[start:end]

        videos = [
            PlaylistVideoItem(
                id=e.get("id", ""),
                title=e.get("title", ""),
                duration=e.get("duration"),
                thumbnail=e.get("thumbnail", ""),
                url=e.get("webpage_url", e.get("url", "")),
            )
            for e in page_entries
        ]

        return PlaylistInfo(
            id=raw.get("id", ""),
            title=raw.get("title", ""),
            uploader=raw.get("uploader", ""),
            video_count=total,
            videos=videos,
            page=page,
            total_pages=total_pages,
        )

    def download(
        self,
        url: str,
        format_id: str,
        output_dir: str,
        progress_hook: Callable | None = None,
        should_abort: Callable[[], bool] | None = None,
        subtitle_lang: str | None = None,
    ) -> str:
        logger.info(f"download: url={url}, format_id={format_id}, output_dir={output_dir}, subtitle_lang={subtitle_lang}")
        opts = self._base_opts()
        opts["format"] = format_id
        opts["outtmpl"] = os.path.join(output_dir, "%(title)s.%(ext)s")
        opts.pop("skip_download", None)

        if subtitle_lang:
            opts["writesubtitles"] = True
            opts["subtitleslangs"] = [subtitle_lang]

        hooks = []
        if progress_hook:
            hooks.append(progress_hook)
        if should_abort:
            def abort_hook(d: dict):
                if should_abort():
                    raise DownloadInterrupted("下载被中断")
            hooks.append(abort_hook)
        if hooks:
            opts["progress_hooks"] = hooks

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
        except Exception as e:
            logger.error(f"download: error: {type(e).__name__}: {e}", exc_info=True)
            raise
        logger.info(f"download: completed, filename={filename}")
        return filename
