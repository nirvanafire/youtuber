<template>
  <el-card style="margin-bottom: 12px">
    <div style="display: flex; justify-content: space-between; align-items: center">
      <div style="flex: 1">
        <h4 style="margin: 0 0 4px 0">{{ task.title }}</h4>
        <div style="display: flex; gap: 12px; align-items: center">
          <el-tag :type="statusType" size="small">{{ statusText }}</el-tag>
          <span v-if="task.progress" style="color: #909399; font-size: 12px">
            {{ formatSpeed(task.progress.speed) }} · {{ formatEta(task.progress.eta) }}
          </span>
        </div>
        <el-progress
          v-if="task.status === 'downloading' && task.progress"
          :percentage="Math.round(task.progress.percent)"
          :stroke-width="8"
          style="margin-top: 8px"
        />
        <p v-if="task.error" style="color: #f56c6c; font-size: 12px; margin: 4px 0 0 0">
          {{ task.error }}
        </p>
        <p v-if="task.filepath" style="color: #67c23a; font-size: 12px; margin: 4px 0 0 0">
          {{ task.filepath }}
        </p>
      </div>
      <div style="display: flex; gap: 8px">
        <el-button v-if="task.status === 'downloading'" size="small" @click="$emit('pause', task.id)">
          {{ t('download.pause') }}
        </el-button>
        <el-button v-if="task.status === 'paused'" size="small" type="primary" @click="$emit('resume', task.id)">
          {{ t('download.resume') }}
        </el-button>
        <el-button
          v-if="task.status === 'waiting' || task.status === 'downloading' || task.status === 'paused'"
          size="small"
          type="danger"
          @click="$emit('cancel', task.id)"
        >
          {{ t('download.cancel') }}
        </el-button>
        <el-button
          v-if="task.status === 'completed' || task.status === 'failed' || task.status === 'cancelled'"
          size="small"
          @click="$emit('remove', task.id)"
        >
          {{ t('download.remove') }}
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import type { DownloadTask } from "@/types";

const { t } = useI18n();

const props = defineProps<{ task: DownloadTask }>();
defineEmits<{
  pause: [id: string];
  resume: [id: string];
  cancel: [id: string];
  remove: [id: string];
}>();

const statusType = computed(() => {
  const map: Record<string, string> = {
    waiting: "info",
    downloading: "",
    paused: "warning",
    completed: "success",
    failed: "danger",
    cancelled: "info",
  };
  return map[props.task.status] || "info";
});

const statusText = computed(() => {
  const key = `download.${props.task.status}`;
  return t(key);
});

function formatSpeed(bytesPerSec: number): string {
  if (bytesPerSec < 1024 * 1024) return `${(bytesPerSec / 1024).toFixed(0)} KB/s`;
  return `${(bytesPerSec / 1024 / 1024).toFixed(1)} MB/s`;
}

function formatEta(seconds: number | null): string {
  if (!seconds) return "";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${t('download.eta')} ${m}:${s.toString().padStart(2, "0")}`;
}
</script>
