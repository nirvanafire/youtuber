export interface FormatInfo {
  format_id: string;
  ext: string;
  resolution: string;
  fps: number | null;
  vcodec: string;
  acodec: string;
  filesize: number | null;
  format_note: string;
  is_video_only: boolean;
  is_audio_only: boolean;
}

export interface SubtitleInfo {
  language: string;
  language_name: string;
  ext: string;
  is_auto_generated: boolean;
}

export interface VideoInfo {
  id: string;
  title: string;
  duration: number;
  uploader: string;
  thumbnail: string;
  webpage_url: string;
  formats: FormatInfo[];
  subtitles: SubtitleInfo[];
}

export interface PlaylistVideoItem {
  id: string;
  title: string;
  duration: number | null;
  thumbnail: string;
  url: string;
}

export interface PlaylistInfo {
  id: string;
  title: string;
  uploader: string;
  video_count: number;
  videos: PlaylistVideoItem[];
  page: number;
  total_pages: number;
}

export type DownloadStatus =
  | "waiting"
  | "downloading"
  | "paused"
  | "completed"
  | "failed"
  | "cancelled";

export interface DownloadProgress {
  percent: number;
  speed: number;
  downloaded_bytes: number;
  total_bytes: number | null;
  eta: number | null;
}

export interface DownloadTask {
  id: string;
  video_id: string;
  title: string;
  url: string;
  format_id: string;
  status: DownloadStatus;
  progress: DownloadProgress | null;
  filepath: string | null;
  error: string | null;
}

export interface AppSettings {
  download_dir: string;
  default_quality: string;
  proxy: string | null;
  max_concurrent_downloads: number;
  language: string;
}
