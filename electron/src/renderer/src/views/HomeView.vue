<template>
  <div>
    <h2>{{ t('home.title') }}</h2>
    <UrlInput :loading="videoStore.loading" @parse="handleParse" />
    <VideoCard v-if="videoStore.currentVideo" :video="videoStore.currentVideo" />
    <FormatTable
      v-if="videoStore.currentVideo"
      :formats="videoStore.currentVideo.formats"
      @select="onFormatSelect"
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
import { useVideoStore } from "@/stores/video";
import { getVideoInfo } from "@/api/video";
import { getPlaylistInfo } from "@/api/playlist";
import UrlInput from "@/components/UrlInput.vue";
import VideoCard from "@/components/VideoCard.vue";
import FormatTable from "@/components/FormatTable.vue";
import SubtitleList from "@/components/SubtitleList.vue";
import PlaylistTable from "@/components/PlaylistTable.vue";
import type { FormatInfo, PlaylistVideoItem } from "@/types";

const { t } = useI18n();
const videoStore = useVideoStore();
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

function onFormatSelect(formats: FormatInfo[]) {
  console.log("Selected formats:", formats);
}

function onSubtitleDownload(languages: string[]) {
  console.log("Download subtitles:", languages);
}

function onPlaylistDownload(videos: PlaylistVideoItem[]) {
  console.log("Batch download playlist videos:", videos);
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
