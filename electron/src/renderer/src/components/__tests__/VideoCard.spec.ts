import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import VideoCard from "../VideoCard.vue";
import type { VideoInfo } from "@/types";

vi.mock("vue-i18n", () => ({
  useI18n: () => ({ t: (key: string) => key }),
}));

const globalStubs = {
  ElCard: { template: '<div class="el-card"><slot /></div>' },
};

const mockVideo: VideoInfo = {
  id: "vid-1",
  title: "Test Video Title",
  duration: 185,
  uploader: "TestChannel",
  thumbnail: "https://example.com/thumb.jpg",
  webpage_url: "https://youtube.com/watch?v=vid-1",
  formats: [{ format_id: "22", ext: "mp4", resolution: "720p", fps: 30, vcodec: "avc1", acodec: "mp4a", filesize: 10000000, format_note: "720p", is_video_only: false, is_audio_only: false }],
  subtitles: [{ language: "en", language_name: "en", ext: "srt", is_auto_generated: false }],
};

describe("VideoCard", () => {
  it("renders video title", () => {
    const wrapper = mount(VideoCard, { props: { video: mockVideo }, global: { stubs: globalStubs } });
    expect(wrapper.text()).toContain("Test Video Title");
  });

  it("renders uploader name", () => {
    const wrapper = mount(VideoCard, { props: { video: mockVideo }, global: { stubs: globalStubs } });
    expect(wrapper.text()).toContain("TestChannel");
  });

  it("formats duration as m:ss", () => {
    const wrapper = mount(VideoCard, { props: { video: mockVideo }, global: { stubs: globalStubs } });
    expect(wrapper.text()).toContain("3:05");
  });

  it("renders thumbnail image", () => {
    const wrapper = mount(VideoCard, { props: { video: mockVideo }, global: { stubs: globalStubs } });
    const img = wrapper.find("img");
    expect(img.attributes("src")).toBe("https://example.com/thumb.jpg");
  });

  it("shows format and subtitle counts", () => {
    const wrapper = mount(VideoCard, { props: { video: mockVideo }, global: { stubs: globalStubs } });
    expect(wrapper.text()).toContain("1");
  });
});
