<template>
  <div style="margin-top: 16px">
    <h3>{{ t('format.title') }}</h3>
    <el-table :data="formats" stripe style="width: 100%" @selection-change="onSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="format_note" :label="t('format.quality')" width="120" />
      <el-table-column prop="resolution" :label="t('format.resolution')" width="140" />
      <el-table-column prop="ext" :label="t('format.ext')" width="80" />
      <el-table-column prop="fps" :label="t('format.fps')" width="80">
        <template #default="{ row }">
          {{ row.fps ? `${row.fps}fps` : '-' }}
        </template>
      </el-table-column>
      <el-table-column :label="t('format.size')" width="120">
        <template #default="{ row }">
          {{ row.filesize ? formatSize(row.filesize) : t('format.unknown') }}
        </template>
      </el-table-column>
      <el-table-column :label="t('format.type')" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.is_video_only" type="warning" size="small">{{ t('format.videoOnly') }}</el-tag>
          <el-tag v-else-if="row.is_audio_only" type="success" size="small">{{ t('format.audioOnly') }}</el-tag>
          <el-tag v-else type="info" size="small">{{ t('format.merged') }}</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import type { FormatInfo } from "@/types";

const { t } = useI18n();

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
