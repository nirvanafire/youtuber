import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import DownloadItem from "../DownloadItem.vue";
import type { DownloadTask } from "@/types";

vi.mock("vue-i18n", () => ({
  useI18n: () => ({ t: (key: string) => key }),
}));

const globalStubs = {
  ElCard: { template: '<div class="el-card"><slot /></div>' },
  ElTag: { template: '<span class="el-tag"><slot /></span>', props: ["type", "size"] },
  ElButton: {
    template: '<button class="el-button" @click="$emit(\'click\')"><slot /></button>',
    props: ["size", "type"],
    emits: ["click"],
  },
  ElProgress: { template: '<div class="el-progress"></div>', props: ["percentage", "strokeWidth"] },
};

function makeTask(overrides: Partial<DownloadTask> = {}): DownloadTask {
  return {
    id: "task-1",
    video_id: "vid-1",
    title: "Test Video",
    url: "https://youtube.com/watch?v=test",
    format_id: "22",
    status: "waiting",
    progress: null,
    filepath: null,
    error: null,
    ...overrides,
  };
}

function mountItem(task: DownloadTask) {
  return mount(DownloadItem, { props: { task }, global: { stubs: globalStubs } });
}

describe("DownloadItem", () => {
  it("renders task title", () => {
    const wrapper = mountItem(makeTask());
    expect(wrapper.text()).toContain("Test Video");
  });

  it("shows pause button when downloading", () => {
    const wrapper = mountItem(makeTask({ status: "downloading" }));
    expect(wrapper.text()).toContain("download.pause");
  });

  it("shows resume button when paused", () => {
    const wrapper = mountItem(makeTask({ status: "paused" }));
    expect(wrapper.text()).toContain("download.resume");
  });

  it("shows cancel button when waiting", () => {
    const wrapper = mountItem(makeTask({ status: "waiting" }));
    expect(wrapper.text()).toContain("download.cancel");
  });

  it("shows remove button when completed", () => {
    const wrapper = mountItem(makeTask({ status: "completed" }));
    expect(wrapper.text()).toContain("download.remove");
  });

  it("shows remove button when failed", () => {
    const wrapper = mountItem(makeTask({ status: "failed" }));
    expect(wrapper.text()).toContain("download.remove");
  });

  it("emits pause when pause button clicked", async () => {
    const wrapper = mountItem(makeTask({ status: "downloading" }));
    const buttons = wrapper.findAll("button");
    const pauseBtn = buttons.find((b) => b.text().includes("download.pause"));
    await pauseBtn?.trigger("click");
    expect(wrapper.emitted("pause")?.[0]).toEqual(["task-1"]);
  });

  it("emits cancel when cancel button clicked", async () => {
    const wrapper = mountItem(makeTask({ status: "waiting" }));
    const buttons = wrapper.findAll("button");
    const cancelBtn = buttons.find((b) => b.text().includes("download.cancel"));
    await cancelBtn?.trigger("click");
    expect(wrapper.emitted("cancel")?.[0]).toEqual(["task-1"]);
  });

  it("emits remove when remove button clicked", async () => {
    const wrapper = mountItem(makeTask({ status: "completed" }));
    const buttons = wrapper.findAll("button");
    const removeBtn = buttons.find((b) => b.text().includes("download.remove"));
    await removeBtn?.trigger("click");
    expect(wrapper.emitted("remove")?.[0]).toEqual(["task-1"]);
  });

  it("shows error message when failed", () => {
    const wrapper = mountItem(makeTask({ status: "failed", error: "Network error" }));
    expect(wrapper.text()).toContain("Network error");
  });

  it("shows filepath when completed", () => {
    const wrapper = mountItem(makeTask({ status: "completed", filepath: "/downloads/test.mp4" }));
    expect(wrapper.text()).toContain("/downloads/test.mp4");
  });

  it("shows progress bar when downloading with progress", () => {
    const wrapper = mountItem(
      makeTask({
        status: "downloading",
        progress: { percent: 45.5, speed: 1048576, downloaded_bytes: 5000000, total_bytes: 10000000, eta: 5 },
      }),
    );
    expect(wrapper.find(".el-progress").exists()).toBe(true);
  });
});
