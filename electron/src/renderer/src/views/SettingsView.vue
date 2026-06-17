<template>
  <div>
    <h2>{{ t('settings.title') }}</h2>
    <el-form label-width="160px" style="max-width: 600px">
      <el-form-item :label="t('settings.downloadDir')">
        <el-input v-model="form.download_dir" />
      </el-form-item>
      <el-form-item :label="t('settings.defaultQuality')">
        <el-select v-model="form.default_quality" style="width: 100%">
          <el-option :label="t('settings.qualityBest')" value="best" />
          <el-option label="1080p" value="1080p" />
          <el-option label="720p" value="720p" />
          <el-option :label="t('settings.audioOnly')" value="audio" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('settings.proxy')">
        <el-input v-model="form.proxy" placeholder="http://127.0.0.1:7890" clearable />
      </el-form-item>
      <el-form-item :label="t('settings.maxConcurrent')">
        <el-input-number v-model="form.max_concurrent_downloads" :min="1" :max="10" />
      </el-form-item>
      <el-form-item :label="t('settings.language')">
        <el-select v-model="form.language" style="width: 100%" @change="onLanguageChange">
          <el-option label="中文" value="zh" />
          <el-option label="English" value="en" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSave">{{ t('settings.save') }}</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { ElMessage } from "element-plus";
import { useSettingsStore } from "@/stores/settings";
import { getSettings, updateSettings } from "@/api/settings";
import type { AppSettings } from "@/types";

const { t, locale } = useI18n();
const settingsStore = useSettingsStore();

const form = ref<AppSettings>({
  download_dir: "",
  default_quality: "best",
  proxy: null,
  max_concurrent_downloads: 3,
  language: "zh",
});

onMounted(async () => {
  try {
    const settings = await getSettings();
    settingsStore.setSettings(settings);
    form.value = { ...settings };
  } catch {}
});

function onLanguageChange(lang: string) {
  locale.value = lang;
}

async function onSave() {
  try {
    const updated = await updateSettings(form.value);
    settingsStore.setSettings(updated);
    locale.value = updated.language;
    ElMessage.success(t('settings.saved'));
  } catch (e: any) {
    ElMessage.error(e.message || t('settings.saveFailed'));
  }
}
</script>
