<template>
  <div style="margin-top: 16px">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px">
      <h3>{{ playlist.title }} ({{ playlist.video_count }} {{ t('playlist.videoCount') }})</h3>
      <div>
        <el-button size="small" @click="toggleAll">
          {{ allSelected ? t('playlist.deselectAll') : t('playlist.selectAll') }}
        </el-button>
        <el-button type="primary" size="small" :disabled="selectedIds.size === 0" @click="onBatchDownload">
          {{ t('playlist.downloadSelected') }} ({{ selectedIds.size }})
        </el-button>
      </div>
    </div>
    <el-table ref="tableRef" :data="playlist.videos" stripe style="width: 100%" @selection-change="onSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column :label="t('playlist.thumbnail')" width="120">
        <template #default="{ row }">
          <img :src="row.thumbnail" :alt="row.title" style="width: 100px; height: 56px; object-fit: cover; border-radius: 4px" />
        </template>
      </el-table-column>
      <el-table-column prop="title" :label="t('playlist.title')" />
      <el-table-column :label="t('playlist.duration')" width="100">
        <template #default="{ row }">
          {{ row.duration ? formatDuration(row.duration) : '-' }}
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-if="playlist.total_pages > 1"
      :current-page="playlist.page"
      :page-size="50"
      :total="playlist.video_count"
      layout="prev, pager, next"
      style="margin-top: 16px; justify-content: center"
      @current-change="onPageChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import type { TableInstance } from "element-plus";
import type { PlaylistInfo, PlaylistVideoItem } from "@/types";

const { t } = useI18n();

const props = defineProps<{ playlist: PlaylistInfo }>();
const emit = defineEmits<{
  download: [videos: PlaylistVideoItem[]];
  pageChange: [page: number];
}>();

const tableRef = ref<TableInstance>();
const selectedItems = ref<PlaylistVideoItem[]>([]);
const selectedIds = computed(() => new Set(selectedItems.value.map((v) => v.id)));
const allSelected = computed(() => selectedIds.value.size === props.playlist.videos.length && props.playlist.videos.length > 0);

function onSelectionChange(items: PlaylistVideoItem[]) {
  selectedItems.value = items;
}

function toggleAll() {
  if (!tableRef.value) return;
  if (allSelected.value) {
    tableRef.value.clearSelection();
  } else {
    props.playlist.videos.forEach((row) => {
      tableRef.value!.toggleRowSelection(row, true);
    });
  }
}

function onBatchDownload() {
  emit("download", selectedItems.value);
}

function onPageChange(page: number) {
  emit("pageChange", page);
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}
</script>
