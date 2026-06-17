import client from "./client";
import type { AppSettings } from "@/types";

export async function getSettings(): Promise<AppSettings> {
  const { data } = await client.get("/api/v1/settings");
  return data;
}

export async function updateSettings(
  partial: Partial<AppSettings>
): Promise<AppSettings> {
  const { data } = await client.put("/api/v1/settings", partial);
  return data;
}
