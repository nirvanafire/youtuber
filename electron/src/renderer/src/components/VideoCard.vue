<template>
  <el-card v-if="video" style="margin-top: 16px">
    <div style="display: flex; gap: 16px">
      <img
        :src="video.thumbnail"
        :alt="video.title"
        style="width: 320px; height: 180px; object-fit: cover; border-radius: 8px"
      />
      <div>
        <h3 style="margin: 0 0 8px 0">{{ video.title }}</h3>
        <p style="color: #909399; margin: 0 0 4px 0">
          {{ video.uploader }} · {{ formatDuration(video.duration) }}
        </p>
        <p style="color: #909399; margin: 0; font-size: 12px">
          {{ video.formats.length }} 个格式 · {{ video.subtitles.length }} 个字幕
        </p>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { VideoInfo } from "@/types";

defineProps<{ video: VideoInfo }>();

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}
</script>
