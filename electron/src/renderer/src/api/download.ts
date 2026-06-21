import client from "./client";
import type { DownloadTask } from "@/types";

export async function startDownload(
  url: string,
  videoId: string,
  title: string,
  formatId: string
): Promise<DownloadTask> {
  console.log("[startDownload] requesting:", { url, video_id: videoId, title, format_id: formatId });
  const { data } = await client.post("/api/v1/download", {
    url,
    video_id: videoId,
    title,
    format_id: formatId,
  });
  console.log("[startDownload] response:", data);
  return data;
}

export async function startSubtitleDownload(
  url: string,
  videoId: string,
  title: string,
  language: string,
  ext: string
): Promise<DownloadTask> {
  const { data } = await client.post("/api/v1/download/subtitle", {
    url,
    video_id: videoId,
    title,
    language,
    ext,
  });
  return data;
}

export async function getDownloadQueue(): Promise<DownloadTask[]> {
  const { data } = await client.get("/api/v1/download/queue");
  return data;
}

export async function pauseDownload(taskId: string): Promise<DownloadTask> {
  const { data } = await client.post(`/api/v1/download/${taskId}/pause`);
  return data;
}

export async function resumeDownload(taskId: string): Promise<DownloadTask> {
  const { data } = await client.post(`/api/v1/download/${taskId}/resume`);
  return data;
}

export async function cancelDownload(taskId: string): Promise<DownloadTask> {
  const { data } = await client.post(`/api/v1/download/${taskId}/cancel`);
  return data;
}
