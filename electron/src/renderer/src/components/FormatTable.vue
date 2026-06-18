<template>
  <div style="margin-top: 16px">
    <h3>{{ t('format.title') }}</h3>

    <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 12px; flex-wrap: wrap">
      <el-check-tag
        v-for="chip in qualityChips"
        :key="chip.label"
        :checked="activeChips.has(chip.label)"
        @change="toggleChip(chip.label)"
      >
        {{ chip.label }}
      </el-check-tag>
      <el-input
        v-model="searchText"
        :placeholder="t('format.searchPlaceholder')"
        clearable
        style="width: 200px; margin-left: auto"
        size="small"
      />
    </div>

    <el-table :data="filteredFormats" stripe style="width: 100%">
      <el-table-column :label="t('format.quality')" width="120">
        <template #default="{ row }">{{ row.format_note }}</template>
      </el-table-column>
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
      <el-table-column :label="t('format.action')" width="100" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            :loading="downloadingIds.has(row.format_id)"
            @click="onDownload(row)"
          >
            {{ t('format.download') }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import type { FormatInfo } from "@/types";

const { t } = useI18n();

const props = defineProps<{
  formats: FormatInfo[];
}>();

const emit = defineEmits<{
  download: [format: FormatInfo];
}>();

const searchText = ref("");
const activeChips = ref<Set<string>>(new Set());
const downloadingIds = ref<Set<string>>(new Set());

const qualityChips = [
  { label: "4K", min: 2160 },
  { label: "1080p", min: 1080, max: 2160 },
  { label: "720p", min: 720, max: 1080 },
  { label: "480p", min: 0, max: 720 },
  { label: "Audio", audioOnly: true },
];

function toggleChip(label: string) {
  if (activeChips.value.has(label)) {
    activeChips.value.delete(label);
  } else {
    activeChips.value.add(label);
  }
}

function getResolutionHeight(resolution: string): number {
  const match = resolution.match(/x(\d+)$/);
  return match ? parseInt(match[1], 10) : 0;
}

const filteredFormats = computed(() => {
  let result = props.formats;

  if (activeChips.value.size > 0) {
    result = result.filter((fmt) => {
      for (const chip of qualityChips) {
        if (!activeChips.value.has(chip.label)) continue;
        if (chip.audioOnly && fmt.is_audio_only) return true;
        if (!chip.audioOnly && !fmt.is_audio_only) {
          const h = getResolutionHeight(fmt.resolution);
          if (chip.max !== undefined && h >= chip.min && h < chip.max) return true;
          if (chip.max === undefined && h >= chip.min) return true;
        }
      }
      return false;
    });
  }

  if (searchText.value.trim()) {
    const q = searchText.value.toLowerCase();
    result = result.filter(
      (fmt) =>
        fmt.format_note.toLowerCase().includes(q) ||
        fmt.resolution.toLowerCase().includes(q) ||
        fmt.ext.toLowerCase().includes(q)
    );
  }

  return result;
});

function onDownload(format: FormatInfo) {
  downloadingIds.value.add(format.format_id);
  emit("download", format);
  setTimeout(() => downloadingIds.value.delete(format.format_id), 2000);
}

function formatSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} GB`;
}
</script>
