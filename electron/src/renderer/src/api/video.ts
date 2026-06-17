import client from "./client";
import type { VideoInfo } from "@/types";

export async function getVideoInfo(url: string): Promise<VideoInfo> {
  const { data } = await client.post("/api/v1/video/info", { url });
  return data;
}
