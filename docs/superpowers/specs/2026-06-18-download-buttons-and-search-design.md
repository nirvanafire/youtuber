# Download Buttons + Search/Filter Design

## Overview

Wire up the existing (but stubbed) download functionality and add search/filter capabilities to the video info display components.

## Part 1: Download Buttons

### FormatTable — Per-Row Download Button

Add a download button column to each format row. On click:
1. Call `startDownload(url, videoId, title, formatId)` via the API
2. Add the returned task to the download store
3. Show `ElMessage.success` notification
4. The button shows a loading spinner while the request is in-flight

Props added to FormatTable: `videoUrl: string`, `videoId: string`, `videoTitle: string`.
New emit: `download(format: FormatInfo)` — used by HomeView to call the API.

### SubtitleList — Subtitle Download

The current backend download endpoint only accepts `format_id`. Subtitle downloads require different yt-dlp options (`writesubtitles`, `subtitleslangs`).

**Backend changes:**
- Add `DownloadSubtitleRequest` model: `{ url, video_id, title, language, ext }`
- Add `POST /api/v1/download/subtitle` endpoint
- Extend `YtdlWrapper.download()` with optional `subtitle_lang` parameter that sets `writesubtitles=True` and `subtitleslangs=[lang]`
- Subtitle downloads use the same `DownloadManager` queue and progress tracking

**Frontend changes:**
- Add `startSubtitleDownload()` to `api/download.ts`
- HomeView's `onSubtitleDownload(languages)` loops through selected languages, calling `startSubtitleDownload()` for each
- Show success message per subtitle, auto-add tasks to download store

### PlaylistTable — Batch Download

Since playlist extraction uses `extract_flat=True` (no format details), batch download uses `format_id="best"` for all selected videos.

HomeView's `onPlaylistDownload(videos)`:
1. Loop through selected `PlaylistVideoItem[]`
2. Call `startDownload(video.url, video.id, video.title, "best")` for each
3. Add each task to download store
4. Show `ElMessage.success` with count: "已添加 N 个下载任务"

## Part 2: Search/Filter

### FormatTable — Quality Chips + Text Search

**Quality chips** above the table. Clicking a chip toggles filtering. Active chip is highlighted.
- Chips: 4K, 1080p, 720p, 480p, Audio Only
- Filtering logic: parse resolution string (e.g. "1920x1080"), extract height, match:
  - 4K: height >= 2160
  - 1080p: 1080 <= height < 2160
  - 720p: 720 <= height < 1080
  - 480p: height < 720 (and not audio-only)
- Audio Only: filter where `is_audio_only === true`
- Multiple chips can be active (OR logic)

**Text search** input next to chips.
- Filters by: `format_note`, `resolution`, `ext`
- Case-insensitive substring match

Both filters combine with AND logic: row must match active chips AND search text.

### SubtitleList — Text Search

Add search input above the subtitle list.
- Filters by: `language_name`, `language`
- Case-insensitive substring match

### PlaylistTable — Text Search

Add search input above the playlist table.
- Filters by: `title`
- Case-insensitive substring match
- Client-side filtering within current page only

## Files to Modify

| File | Type | Changes |
|------|------|---------|
| `electron/src/renderer/src/components/FormatTable.vue` | Modify | Add download button column, quality chips, text search, new props/emits |
| `electron/src/renderer/src/components/SubtitleList.vue` | Modify | Add text search input, filter logic |
| `electron/src/renderer/src/components/PlaylistTable.vue` | Modify | Add text search input, filter logic |
| `electron/src/renderer/src/views/HomeView.vue` | Modify | Wire up download handlers to call API, add success feedback |
| `electron/src/renderer/src/api/download.ts` | Modify | Add `startSubtitleDownload()` function |
| `electron/src/renderer/src/i18n/zh.ts` | Modify | Add new i18n keys |
| `electron/src/renderer/src/i18n/en.ts` | Modify | Add new i18n keys |
| `backend/src/api/download.py` | Modify | Add subtitle download endpoint |
| `backend/src/core/ytdl_wrapper.py` | Modify | Add subtitle download support |

## UX Flow

### Single Video Download
1. User parses a URL → VideoCard + FormatTable + SubtitleList appear
2. User clicks download button on a format row → task created, success message shown
3. User can click "Downloads" in sidebar to monitor progress

### Subtitle Download
1. User selects subtitle languages via checkboxes
2. Clicks "Download Selected" → one task per language created
3. Success message: "已下载 N 个字幕"

### Playlist Batch Download
1. User parses a playlist URL → PlaylistTable appears
2. User selects videos via checkboxes (or "Select All")
3. Clicks "Download Selected (N)" → N tasks created with "best" quality
4. Success message: "已添加 N 个下载任务"

### Search/Filter
1. Quality chips above FormatTable — click to filter by resolution
2. Text search inputs above each list — type to filter in real-time
3. Filters are client-side, instant, and reset when URL is re-parsed
