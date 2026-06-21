<template>
  <div>
    <h2>{{ t('home.title') }}</h2>
    <UrlInput :loading="videoStore.loading" @parse="handleParse" />
    <VideoCard v-if="videoStore.currentVideo" :video="videoStore.currentVideo" />
    <FormatTable
      v-if="videoStore.currentVideo"
      :formats="videoStore.currentVideo.formats"
      @download="onFormatDownload"
    />
    <SubtitleList
      v-if="videoStore.currentVideo"
      :subtitles="videoStore.currentVideo.subtitles"
      @download="onSubtitleDownload"
    />
    <PlaylistTable
      v-if="videoStore.currentPlaylist"
      :playlist="videoStore.currentPlaylist"
      @download="onPlaylistDownload"
      @page-change="onPlaylistPageChange"
    />
    <el-alert
      v-if="videoStore.error"
      :title="videoStore.error"
      type="error"
      show-icon
      style="margin-top: 16px"
      closable
      @close="videoStore.setError(null)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { ElMessage } from "element-plus";
import { useVideoStore } from "@/stores/video";
import { useDownloadStore } from "@/stores/download";
import { getVideoInfo } from "@/api/video";
import { getPlaylistInfo } from "@/api/playlist";
import { startDownload, startSubtitleDownload } from "@/api/download";
import UrlInput from "@/components/UrlInput.vue";
import VideoCard from "@/components/VideoCard.vue";
import FormatTable from "@/components/FormatTable.vue";
import SubtitleList from "@/components/SubtitleList.vue";
import PlaylistTable from "@/components/PlaylistTable.vue";
import type { FormatInfo, PlaylistVideoItem } from "@/types";

const { t } = useI18n();
const videoStore = useVideoStore();
const downloadStore = useDownloadStore();
const playlistUrl = ref("");

const playlistUrlPattern = /[?&]list=/;

async function handleParse(url: string) {
  videoStore.setLoading(true);
  videoStore.clear();
  playlistUrl.value = "";
  try {
    if (playlistUrlPattern.test(url)) {
      playlistUrl.value = url;
      const info = await getPlaylistInfo(url);
      videoStore.setPlaylist(info);
    } else {
      const info = await getVideoInfo(url);
      videoStore.setVideo(info);
    }
  } catch (e: any) {
    videoStore.setError(e.message || t('home.parseFailed'));
  } finally {
    videoStore.setLoading(false);
  }
}

async function onFormatDownload(format: FormatInfo) {
  const video = videoStore.currentVideo;
  if (!video) {
    console.warn("[onFormatDownload] no currentVideo, aborting");
    return;
  }
  console.log("[onFormatDownload] starting download:", {
    url: video.webpage_url,
    videoId: video.id,
    title: video.title,
    formatId: format.format_id,
    formatNote: format.format_note,
  });
  try {
    const task = await startDownload(video.webpage_url, video.id, video.title, format.format_id);
    console.log("[onFormatDownload] task created:", task);
    downloadStore.addTask(task);
    ElMessage.success(`${t('download.taskAdded')}: ${video.title} (${format.format_note})`);
  } catch (e: any) {
    console.error("[onFormatDownload] failed:", e);
    ElMessage.error(e.message || t('download.startFailed'));
  }
}

async function onSubtitleDownload(languages: string[]) {
  const video = videoStore.currentVideo;
  if (!video) return;
  let count = 0;
  for (const lang of languages) {
    const sub = video.subtitles.find((s) => s.language === lang);
    if (!sub) continue;
    try {
      const task = await startSubtitleDownload(video.webpage_url, video.id, video.title, lang, sub.ext);
      downloadStore.addTask(task);
      count++;
    } catch (e: any) {
      ElMessage.error(`${sub.language_name}: ${e.message || t('download.startFailed')}`);
    }
  }
  if (count > 0) {
    ElMessage.success(`${t('download.subtitleAdded')}: ${count}`);
  }
}

async function onPlaylistDownload(videos: PlaylistVideoItem[]) {
  let count = 0;
  for (const video of videos) {
    try {
      const task = await startDownload(video.url, video.id, video.title, "best");
      downloadStore.addTask(task);
      count++;
    } catch (e: any) {
      ElMessage.error(`${video.title}: ${e.message || t('download.startFailed')}`);
    }
  }
  if (count > 0) {
    ElMessage.success(`${t('download.playlistAdded')}: ${count}`);
  }
}

async function onPlaylistPageChange(page: number) {
  if (!playlistUrl.value) return;
  videoStore.setLoading(true);
  try {
    const info = await getPlaylistInfo(playlistUrl.value, page);
    videoStore.setPlaylist(info);
  } catch (e: any) {
    videoStore.setError(e.message || t('home.loadPageFailed'));
  } finally {
    videoStore.setLoading(false);
  }
}
</script>
