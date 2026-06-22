import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import UrlInput from "../UrlInput.vue";

vi.mock("vue-i18n", () => ({
  useI18n: () => ({ t: (key: string) => key }),
}));

const ElInput = {
  name: "ElInput",
  template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
  props: ["modelValue", "placeholder", "size", "clearable"],
  emits: ["update:modelValue"],
};

const ElButton = {
  name: "ElButton",
  template: '<button @click="$emit(\'click\')"><slot /></button>',
  props: ["type", "size", "loading"],
  emits: ["click"],
};

const globalStubs = { ElInput, ElButton };

describe("UrlInput", () => {
  it("renders input and button", () => {
    const wrapper = mount(UrlInput, { props: { loading: false }, global: { stubs: globalStubs } });
    expect(wrapper.find("input").exists()).toBe(true);
    expect(wrapper.find("button").exists()).toBe(true);
  });

  it("emits parse with trimmed url on button click", async () => {
    const wrapper = mount(UrlInput, { props: { loading: false }, global: { stubs: globalStubs } });
    const input = wrapper.find("input");
    await input.setValue("  https://youtube.com/watch?v=test  ");
    await wrapper.find("button").trigger("click");
    expect(wrapper.emitted("parse")?.[0]).toEqual(["https://youtube.com/watch?v=test"]);
  });

  it("emits parse on enter key", async () => {
    const wrapper = mount(UrlInput, { props: { loading: false }, global: { stubs: globalStubs } });
    const input = wrapper.find("input");
    await input.setValue("https://youtube.com/watch?v=test");
    await input.trigger("keyup.enter");
    expect(wrapper.emitted("parse")?.[0]).toEqual(["https://youtube.com/watch?v=test"]);
  });

  it("does not emit parse for empty url", async () => {
    const wrapper = mount(UrlInput, { props: { loading: false }, global: { stubs: globalStubs } });
    await wrapper.find("button").trigger("click");
    expect(wrapper.emitted("parse")).toBeUndefined();
  });

  it("does not emit parse for whitespace-only url", async () => {
    const wrapper = mount(UrlInput, { props: { loading: false }, global: { stubs: globalStubs } });
    const input = wrapper.find("input");
    await input.setValue("   ");
    await wrapper.find("button").trigger("click");
    expect(wrapper.emitted("parse")).toBeUndefined();
  });
});
