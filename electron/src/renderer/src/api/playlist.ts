import client from "./client";
import type { PlaylistInfo } from "@/types";

export async function getPlaylistInfo(
  url: string,
  page = 1,
  pageSize = 50
): Promise<PlaylistInfo> {
  const { data } = await client.post("/api/v1/playlist/info", {
    url,
    page,
    page_size: pageSize,
  });
  return data;
}
