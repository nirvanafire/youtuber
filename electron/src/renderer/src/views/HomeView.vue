<template>
  <div>
    <h2>{{ t('home.title') }}</h2>
    <UrlInput :loading="videoStore.loading" @parse="handleParse" />
    <VideoCard v-if="videoStore.currentVideo" :video="videoStore.currentVideo" />
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
import { useI18n } from "vue-i18n";
import { useVideoStore } from "@/stores/video";
import { getVideoInfo } from "@/api/video";
import UrlInput from "@/components/UrlInput.vue";
import VideoCard from "@/components/VideoCard.vue";

const { t } = useI18n();
const videoStore = useVideoStore();

async function handleParse(url: string) {
  videoStore.setLoading(true);
  videoStore.clear();
  try {
    const info = await getVideoInfo(url);
    videoStore.setVideo(info);
  } catch (e: any) {
    videoStore.setError(e.message || "解析失败");
  } finally {
    videoStore.setLoading(false);
  }
}
</script>
