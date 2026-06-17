import { defineStore } from "pinia";
import { ref } from "vue";
import type { VideoInfo, PlaylistInfo } from "@/types";

export const useVideoStore = defineStore("video", () => {
  const currentVideo = ref<VideoInfo | null>(null);
  const currentPlaylist = ref<PlaylistInfo | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  function setVideo(info: VideoInfo) {
    currentVideo.value = info;
    currentPlaylist.value = null;
    error.value = null;
  }

  function setPlaylist(info: PlaylistInfo) {
    currentPlaylist.value = info;
    currentVideo.value = null;
    error.value = null;
  }

  function setLoading(v: boolean) {
    loading.value = v;
  }

  function setError(msg: string | null) {
    error.value = msg;
  }

  function clear() {
    currentVideo.value = null;
    currentPlaylist.value = null;
    error.value = null;
  }

  return {
    currentVideo,
    currentPlaylist,
    loading,
    error,
    setVideo,
    setPlaylist,
    setLoading,
    setError,
    clear,
  };
});
