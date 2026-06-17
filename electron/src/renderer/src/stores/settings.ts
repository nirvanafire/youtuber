import { defineStore } from "pinia";
import { ref } from "vue";
import type { AppSettings } from "@/types";

export const useSettingsStore = defineStore("settings", () => {
  const settings = ref<AppSettings>({
    download_dir: "",
    default_quality: "best",
    proxy: null,
    max_concurrent_downloads: 3,
    language: "zh",
  });

  function setSettings(newSettings: AppSettings) {
    settings.value = newSettings;
  }

  function updateSettings(partial: Partial<AppSettings>) {
    settings.value = { ...settings.value, ...partial };
  }

  return { settings, setSettings, updateSettings };
});
