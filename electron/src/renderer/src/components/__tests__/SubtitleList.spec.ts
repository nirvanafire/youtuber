import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import SubtitleList from "../SubtitleList.vue";
import type { SubtitleInfo } from "@/types";

vi.mock("vue-i18n", () => ({
  useI18n: () => ({ t: (key: string) => key }),
}));

const mockSubtitles: SubtitleInfo[] = [
  { language: "en", language_name: "English", ext: "srt", is_auto_generated: false },
  { language: "zh-Hans", language_name: "Chinese (Simplified)", ext: "srt", is_auto_generated: true },
  { language: "ja", language_name: "Japanese", ext: "vtt", is_auto_generated: true },
];

function mountComponent(props = {}) {
  return mount(SubtitleList, {
    props: {
      subtitles: mockSubtitles,
      ...props,
    },
    global: {
      plugins: [createPinia(), ElementPlus],
    },
  });
}

describe("SubtitleList", () => {
  it("renders search input", () => {
    const wrapper = mountComponent();
    const input = wrapper.find("input");
    expect(input.exists()).toBe(true);
  });

  it("filters subtitles by language_name", async () => {
    const wrapper = mountComponent();
    const input = wrapper.find("input");
    await input.setValue("English");
    await input.trigger("input");
    expect(wrapper.text()).toContain("English");
    expect(wrapper.text()).not.toContain("Japanese");
  });

  it("shows all subtitles when search is empty", async () => {
    const wrapper = mountComponent();
    const input = wrapper.find("input");
    await input.setValue("English");
    await input.setValue("");
    await input.trigger("input");
    expect(wrapper.text()).toContain("English");
    expect(wrapper.text()).toContain("Japanese");
  });
});
