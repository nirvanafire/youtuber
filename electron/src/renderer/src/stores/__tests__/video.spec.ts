import { describe, it, expect, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useVideoStore } from "../video";
import type { VideoInfo, PlaylistInfo } from "@/types";

const mockVideo: VideoInfo = {
  id: "vid-1",
  title: "Test Video",
  duration: 120,
  uploader: "TestChannel",
  thumbnail: "https://example.com/thumb.jpg",
  webpage_url: "https://youtube.com/watch?v=vid-1",
  formats: [],
  subtitles: [],
};

const mockPlaylist: PlaylistInfo = {
  id: "pl-1",
  title: "Test Playlist",
  uploader: "TestChannel",
  video_count: 5,
  videos: [],
  page: 1,
  total_pages: 1,
};

describe("videoStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("starts with null state", () => {
    const store = useVideoStore();
    expect(store.currentVideo).toBeNull();
    expect(store.currentPlaylist).toBeNull();
    expect(store.loading).toBe(false);
    expect(store.error).toBeNull();
  });

  it("setVideo sets video and clears playlist", () => {
    const store = useVideoStore();
    store.setPlaylist(mockPlaylist);
    store.setVideo(mockVideo);
    expect(store.currentVideo).toEqual(mockVideo);
    expect(store.currentPlaylist).toBeNull();
    expect(store.error).toBeNull();
  });

  it("setPlaylist sets playlist and clears video", () => {
    const store = useVideoStore();
    store.setVideo(mockVideo);
    store.setPlaylist(mockPlaylist);
    expect(store.currentPlaylist).toEqual(mockPlaylist);
    expect(store.currentVideo).toBeNull();
    expect(store.error).toBeNull();
  });

  it("setLoading updates loading state", () => {
    const store = useVideoStore();
    store.setLoading(true);
    expect(store.loading).toBe(true);
  });

  it("setError sets error message", () => {
    const store = useVideoStore();
    store.setError("something went wrong");
    expect(store.error).toBe("something went wrong");
  });

  it("clear resets all state", () => {
    const store = useVideoStore();
    store.setVideo(mockVideo);
    store.setError("error");
    store.clear();
    expect(store.currentVideo).toBeNull();
    expect(store.currentPlaylist).toBeNull();
    expect(store.error).toBeNull();
  });
});
