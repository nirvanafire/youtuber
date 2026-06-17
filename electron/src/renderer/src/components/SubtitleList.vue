<template>
  <div v-if="subtitles.length > 0" style="margin-top: 16px">
    <h3>{{ t('subtitle.title') }}</h3>
    <el-checkbox-group v-model="selectedLanguages">
      <div v-for="sub in subtitles" :key="sub.language" style="margin-bottom: 8px">
        <el-checkbox :value="sub.language" :label="sub.language">
          {{ sub.language_name }}
          <el-tag v-if="sub.is_auto_generated" size="small" type="info">{{ t('subtitle.auto') }}</el-tag>
          <el-tag v-else size="small">{{ t('subtitle.manual') }}</el-tag>
          ({{ sub.ext }})
        </el-checkbox>
      </div>
    </el-checkbox-group>
    <el-button
      v-if="selectedLanguages.length > 0"
      type="primary"
      size="small"
      style="margin-top: 8px"
      @click="onDownload"
    >
      {{ t('subtitle.downloadSelected') }}
    </el-button>
  </div>
  <el-empty v-else :description="t('subtitle.empty')" />
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import type { SubtitleInfo } from "@/types";

const { t } = useI18n();

defineProps<{ subtitles: SubtitleInfo[] }>();
const emit = defineEmits<{ download: [languages: string[]] }>();

const selectedLanguages = ref<string[]>([]);

function onDownload() {
  emit("download", selectedLanguages.value);
}
</script>
