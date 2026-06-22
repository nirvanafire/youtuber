import { describe, it, expect, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useDownloadStore } from "../download";
import type { DownloadTask } from "@/types";

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

describe("downloadStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("starts with empty tasks", () => {
    const store = useDownloadStore();
    expect(store.tasks).toEqual([]);
  });

  it("addTask adds a task", () => {
    const store = useDownloadStore();
    store.addTask(makeTask());
    expect(store.tasks).toHaveLength(1);
    expect(store.tasks[0].id).toBe("task-1");
  });

  it("updateTask merges partial updates", () => {
    const store = useDownloadStore();
    store.addTask(makeTask());
    store.updateTask("task-1", { status: "downloading" });
    expect(store.tasks[0].status).toBe("downloading");
    expect(store.tasks[0].title).toBe("Test Video");
  });

  it("updateTask ignores nonexistent id", () => {
    const store = useDownloadStore();
    store.addTask(makeTask());
    store.updateTask("nonexistent", { status: "completed" });
    expect(store.tasks[0].status).toBe("waiting");
  });

  it("removeTask removes by id", () => {
    const store = useDownloadStore();
    store.addTask(makeTask({ id: "a" }));
    store.addTask(makeTask({ id: "b" }));
    store.removeTask("a");
    expect(store.tasks).toHaveLength(1);
    expect(store.tasks[0].id).toBe("b");
  });

  it("updateProgress updates progress by task id", () => {
    const store = useDownloadStore();
    store.addTask(makeTask());
    const progress = { percent: 50, speed: 1024, downloaded_bytes: 5000, total_bytes: 10000, eta: 5 };
    store.updateProgress("task-1", progress);
    expect(store.tasks[0].progress).toEqual(progress);
  });

  it("setTasks replaces all tasks", () => {
    const store = useDownloadStore();
    store.addTask(makeTask({ id: "old" }));
    store.setTasks([makeTask({ id: "new" })]);
    expect(store.tasks).toHaveLength(1);
    expect(store.tasks[0].id).toBe("new");
  });

  it("waitingTasks filters correctly", () => {
    const store = useDownloadStore();
    store.addTask(makeTask({ id: "1", status: "waiting" }));
    store.addTask(makeTask({ id: "2", status: "downloading" }));
    store.addTask(makeTask({ id: "3", status: "waiting" }));
    expect(store.waitingTasks).toHaveLength(2);
  });

  it("activeTasks filters correctly", () => {
    const store = useDownloadStore();
    store.addTask(makeTask({ id: "1", status: "downloading" }));
    store.addTask(makeTask({ id: "2", status: "waiting" }));
    expect(store.activeTasks).toHaveLength(1);
  });

  it("completedTasks filters correctly", () => {
    const store = useDownloadStore();
    store.addTask(makeTask({ id: "1", status: "completed" }));
    store.addTask(makeTask({ id: "2", status: "failed" }));
    expect(store.completedTasks).toHaveLength(1);
  });
});
