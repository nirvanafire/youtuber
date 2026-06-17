<template>
  <div style="margin-top: 16px">
    <h3>可用格式</h3>
    <el-table :data="formats" stripe style="width: 100%" @selection-change="onSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="format_note" label="清晰度" width="120" />
      <el-table-column prop="resolution" label="分辨率" width="140" />
      <el-table-column prop="ext" label="格式" width="80" />
      <el-table-column prop="fps" label="帧率" width="80">
        <template #default="{ row }">
          {{ row.fps ? `${row.fps}fps` : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="大小" width="120">
        <template #default="{ row }">
          {{ row.filesize ? formatSize(row.filesize) : '未知' }}
        </template>
      </el-table-column>
      <el-table-column label="类型" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.is_video_only" type="warning" size="small">仅视频</el-tag>
          <el-tag v-else-if="row.is_audio_only" type="success" size="small">仅音频</el-tag>
          <el-tag v-else type="info" size="small">合并</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { FormatInfo } from "@/types";

defineProps<{ formats: FormatInfo[] }>();
const emit = defineEmits<{ select: [formats: FormatInfo[]] }>();

const selected = ref<FormatInfo[]>([]);

function onSelectionChange(val: FormatInfo[]) {
  selected.value = val;
  emit("select", val);
}

function formatSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} GB`;
}
</script>
