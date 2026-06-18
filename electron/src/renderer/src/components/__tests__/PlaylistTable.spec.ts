import { describe, it, expect, vi } from "vitest";
import { mount, config } from "@vue/test-utils";
import PlaylistTable from "../PlaylistTable.vue";
import type { PlaylistInfo } from "@/types";

vi.mock("vue-i18n", () => ({
  useI18n: () => ({ t: (key: string) => key }),
}));

// Ensure stubs render their default slot content
config.global.renderStubDefaultSlot = true;

const globalStubs = {
  ElTable: {
    template: '<div class="el-table"><slot /></div>',
    props: ["data", "stripe"],
    methods: {
      clearSelection() {},
      toggleRowSelection() {},
    },
  },
  ElTableColumn: {
    template: '<div class="el-table-col"><slot v-bind="slotData" /></div>',
    props: ["prop", "label", "width", "type"],
    data() {
      return { slotData: { row: {}, column: {}, $index: 0 } };
    },
  },
  ElButton: {
    template: '<button class="el-button" @click="$emit(\'click\')"><slot /></button>',
    props: ["size", "type", "disabled"],
    emits: ["click"],
  },
  ElInput: {
    template: '<input class="el-input" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
    props: ["modelValue", "placeholder", "clearable", "size"],
    emits: ["update:modelValue"],
  },
  ElPagination: {
    template: '<div class="el-pagination"></div>',
    props: ["currentPage", "pageSize", "total", "layout"],
    emits: ["current-change"],
  },
};

const mockPlaylist: PlaylistInfo = {
  id: "PLtest",
  title: "Test Playlist",
  uploader: "TestUser",
  video_count: 3,
  videos: [
    { id: "v1", title: "First Video", duration: 120, thumbnail: "", url: "" },
    { id: "v2", title: "Second Video", duration: 240, thumbnail: "", url: "" },
    { id: "v3", title: "Another Topic", duration: 180, thumbnail: "", url: "" },
  ],
  page: 1,
  total_pages: 1,
};

function mountComponent() {
  return mount(PlaylistTable, {
    props: { playlist: mockPlaylist },
    global: { stubs: globalStubs },
  });
}

describe("PlaylistTable", () => {
  it("renders search input", () => {
    const wrapper = mountComponent();
    const input = wrapper.find("input.el-input");
    expect(input.exists()).toBe(true);
  });

  it("filters videos by title", async () => {
    const wrapper = mountComponent();
    await wrapper.setData({ searchText: "First" });
    const filtered = wrapper.vm.filteredVideos;
    expect(filtered.length).toBe(1);
    expect(filtered[0].id).toBe("v1");
  });

  it("shows all videos when search is empty", async () => {
    const wrapper = mountComponent();
    await wrapper.setData({ searchText: "First" });
    expect(wrapper.vm.filteredVideos.length).toBe(1);

    await wrapper.setData({ searchText: "" });
    expect(wrapper.vm.filteredVideos.length).toBe(3);
  });

  it("filters case-insensitively", async () => {
    const wrapper = mountComponent();
    await wrapper.setData({ searchText: "first" });
    const filtered = wrapper.vm.filteredVideos;
    expect(filtered.length).toBe(1);
    expect(filtered[0].id).toBe("v1");
  });

  it("returns empty array for no match", async () => {
    const wrapper = mountComponent();
    await wrapper.setData({ searchText: "nonexistent" });
    expect(wrapper.vm.filteredVideos.length).toBe(0);
  });
});
