import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import FormatTable from "../FormatTable.vue";
import type { FormatInfo } from "@/types";

vi.mock("vue-i18n", () => ({
  useI18n: () => ({ t: (key: string) => key }),
}));

const globalStubs = {
  ElTable: { template: '<div class="el-table"><slot /></div>', props: ["data", "stripe"] },
  ElTableColumn: {
    template: '<div class="el-table-col"><slot :row="{}" /></div>',
    props: ["prop", "label", "width", "fixed", "type"],
  },
  ElTag: { template: '<span class="el-tag"><slot /></span>', props: ["type", "size"] },
  ElButton: {
    template: '<button class="el-button" @click="$emit(\'click\')"><slot /></button>',
    props: ["size", "type", "loading"],
    emits: ["click"],
  },
  ElCheckTag: {
    template: '<span class="el-check-tag" :class="{ checked }" @click="$emit(\'change\')"><slot /></span>',
    props: ["checked"],
    emits: ["change"],
  },
  ElInput: {
    template: '<input class="el-input" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
    props: ["modelValue", "placeholder", "clearable", "size"],
    emits: ["update:modelValue"],
  },
};

const mockFormats: FormatInfo[] = [
  {
    format_id: "22",
    ext: "mp4",
    resolution: "1280x720",
    fps: 30,
    vcodec: "avc1",
    acodec: "mp4a",
    filesize: 10485760,
    format_note: "720p",
    is_video_only: false,
    is_audio_only: false,
  },
  {
    format_id: "140",
    ext: "m4a",
    resolution: "audio only",
    fps: null,
    vcodec: "none",
    acodec: "mp4a",
    filesize: 5242880,
    format_note: "audio",
    is_video_only: false,
    is_audio_only: true,
  },
  {
    format_id: "137",
    ext: "mp4",
    resolution: "1920x1080",
    fps: 30,
    vcodec: "avc1",
    acodec: "none",
    filesize: 52428800,
    format_note: "1080p",
    is_video_only: true,
    is_audio_only: false,
  },
];

function mountComponent(props = {}) {
  return mount(FormatTable, {
    props: {
      formats: mockFormats,
      ...props,
    },
    global: {
      stubs: globalStubs,
    },
  });
}

/** Helper to set activeChips directly on the reactive ref */
function setActiveChips(wrapper: ReturnType<typeof mountComponent>, labels: string[]) {
  (wrapper.vm as any).activeChips = new Set(labels);
}

describe("FormatTable", () => {
  it("renders quality chips", () => {
    const wrapper = mountComponent();
    expect(wrapper.text()).toContain("4K");
    expect(wrapper.text()).toContain("1080p");
    expect(wrapper.text()).toContain("720p");
    expect(wrapper.text()).toContain("480p");
    expect(wrapper.text()).toContain("Audio");
  });

  it("renders search input", () => {
    const wrapper = mountComponent();
    const input = wrapper.find("input.el-input");
    expect(input.exists()).toBe(true);
  });

  it("renders download button text", () => {
    const wrapper = mountComponent();
    // The stub renders the slot text "format.download" as the button label
    expect(wrapper.text()).toContain("format.download");
  });

  it("has all formats initially in filteredFormats", () => {
    const wrapper = mountComponent();
    expect(wrapper.vm.filteredFormats).toEqual(mockFormats);
  });

  it("filters by search text matching format_note", async () => {
    const wrapper = mountComponent();
    await wrapper.setData({ searchText: "720p" });
    const filtered = wrapper.vm.filteredFormats;
    expect(filtered.length).toBe(1);
    expect(filtered[0].format_id).toBe("22");
  });

  it("filters by search text matching ext", async () => {
    const wrapper = mountComponent();
    await wrapper.setData({ searchText: "m4a" });
    const filtered = wrapper.vm.filteredFormats;
    expect(filtered.length).toBe(1);
    expect(filtered[0].format_id).toBe("140");
  });

  it("filters by search text matching resolution", async () => {
    const wrapper = mountComponent();
    await wrapper.setData({ searchText: "1920" });
    const filtered = wrapper.vm.filteredFormats;
    expect(filtered.length).toBe(1);
    expect(filtered[0].format_id).toBe("137");
  });

  it("filters by quality chip for 720p", async () => {
    const wrapper = mountComponent();
    setActiveChips(wrapper, ["720p"]);
    await wrapper.vm.$nextTick();
    const filtered = wrapper.vm.filteredFormats;
    expect(filtered.length).toBe(1);
    expect(filtered[0].format_id).toBe("22");
  });

  it("filters by quality chip for Audio", async () => {
    const wrapper = mountComponent();
    setActiveChips(wrapper, ["Audio"]);
    await wrapper.vm.$nextTick();
    const filtered = wrapper.vm.filteredFormats;
    expect(filtered.length).toBe(1);
    expect(filtered[0].format_id).toBe("140");
  });

  it("filters by quality chip for 1080p", async () => {
    const wrapper = mountComponent();
    setActiveChips(wrapper, ["1080p"]);
    await wrapper.vm.$nextTick();
    const filtered = wrapper.vm.filteredFormats;
    expect(filtered.length).toBe(1);
    expect(filtered[0].format_id).toBe("137");
  });

  it("combines chip and text filters with AND logic", async () => {
    const wrapper = mountComponent();
    // Audio chip + search for "m4a" => should find the audio format
    setActiveChips(wrapper, ["Audio"]);
    await wrapper.setData({ searchText: "m4a" });
    expect(wrapper.vm.filteredFormats.length).toBe(1);
    expect(wrapper.vm.filteredFormats[0].format_id).toBe("140");

    // Audio chip + search for "mp4" => should find nothing (audio is m4a)
    await wrapper.setData({ searchText: "mp4" });
    expect(wrapper.vm.filteredFormats.length).toBe(0);
  });

  it("clears search returns all matching chip results", async () => {
    const wrapper = mountComponent();
    setActiveChips(wrapper, ["Audio"]);
    await wrapper.setData({ searchText: "nonexistent" });
    expect(wrapper.vm.filteredFormats.length).toBe(0);

    await wrapper.setData({ searchText: "" });
    expect(wrapper.vm.filteredFormats.length).toBe(1);
  });
});
