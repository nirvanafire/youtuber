<template>
  <div>
    <h2>{{ t('download.title') }}</h2>
    <div v-if="downloadStore.tasks.length === 0">
      <el-empty :description="t('download.noDownloads')" />
    </div>
    <DownloadItem
      v-for="task in downloadStore.tasks"
      :key="task.id"
      :task="task"
      @pause="handlePause"
      @resume="handleResume"
      @cancel="handleCancel"
      @remove="handleRemove"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from "vue";
import { useI18n } from "vue-i18n";
import { useDownloadStore } from "@/stores/download";
import { getDownloadQueue, pauseDownload, resumeDownload, cancelDownload } from "@/api/download";
import { useWebSocket } from "@/composables/useWebSocket";
import DownloadItem from "@/components/DownloadItem.vue";

const { t } = useI18n();
const downloadStore = useDownloadStore();
const { connect, disconnect } = useWebSocket();

onMounted(async () => {
  try {
    const tasks = await getDownloadQueue();
    downloadStore.setTasks(tasks);
  } catch {}

  connect((data) => {
    if (data.task_id && data.progress) {
      downloadStore.updateProgress(data.task_id, data.progress);
    }
    if (data.task_id && data.status) {
      downloadStore.updateTask(data.task_id, { status: data.status });
    }
  });
});

onUnmounted(() => {
  disconnect();
});

async function handlePause(id: string) {
  try {
    const task = await pauseDownload(id);
    downloadStore.updateTask(id, task);
  } catch {}
}

async function handleResume(id: string) {
  try {
    const task = await resumeDownload(id);
    downloadStore.updateTask(id, task);
  } catch {}
}

async function handleCancel(id: string) {
  try {
    await cancelDownload(id);
    downloadStore.removeTask(id);
  } catch {}
}

function handleRemove(id: string) {
  downloadStore.removeTask(id);
}
</script>
