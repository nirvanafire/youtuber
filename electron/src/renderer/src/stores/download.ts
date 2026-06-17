import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { DownloadTask } from "@/types";

export const useDownloadStore = defineStore("download", () => {
  const tasks = ref<DownloadTask[]>([]);

  const waitingTasks = computed(() => tasks.value.filter((t) => t.status === "waiting"));
  const activeTasks = computed(() => tasks.value.filter((t) => t.status === "downloading"));
  const completedTasks = computed(() => tasks.value.filter((t) => t.status === "completed"));

  function addTask(task: DownloadTask) {
    tasks.value.push(task);
  }

  function updateTask(taskId: string, updates: Partial<DownloadTask>) {
    const idx = tasks.value.findIndex((t) => t.id === taskId);
    if (idx !== -1) {
      tasks.value[idx] = { ...tasks.value[idx], ...updates };
    }
  }

  function removeTask(taskId: string) {
    tasks.value = tasks.value.filter((t) => t.id !== taskId);
  }

  function updateProgress(taskId: string, progress: DownloadTask["progress"]) {
    const idx = tasks.value.findIndex((t) => t.id === taskId);
    if (idx !== -1) {
      tasks.value[idx].progress = progress;
    }
  }

  function setTasks(newTasks: DownloadTask[]) {
    tasks.value = newTasks;
  }

  return {
    tasks,
    waitingTasks,
    activeTasks,
    completedTasks,
    addTask,
    updateTask,
    removeTask,
    updateProgress,
    setTasks,
  };
});
