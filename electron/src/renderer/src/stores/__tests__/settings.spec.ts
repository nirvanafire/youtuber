import { describe, it, expect, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useSettingsStore } from "../settings";
import type { AppSettings } from "@/types";

describe("settingsStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("starts with default settings", () => {
    const store = useSettingsStore();
    expect(store.settings.default_quality).toBe("best");
    expect(store.settings.max_concurrent_downloads).toBe(3);
    expect(store.settings.language).toBe("zh");
  });

  it("setSettings replaces all settings", () => {
    const store = useSettingsStore();
    const custom: AppSettings = {
      download_dir: "/downloads",
      default_quality: "720p",
      proxy: "http://proxy:8080",
      max_concurrent_downloads: 5,
      language: "en",
    };
    store.setSettings(custom);
    expect(store.settings).toEqual(custom);
  });

  it("updateSettings merges partial settings", () => {
    const store = useSettingsStore();
    store.updateSettings({ language: "en", default_quality: "1080p" });
    expect(store.settings.language).toBe("en");
    expect(store.settings.default_quality).toBe("1080p");
    expect(store.settings.max_concurrent_downloads).toBe(3);
  });
});
