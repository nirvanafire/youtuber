<template>
  <div style="display: flex; gap: 12px">
    <el-input
      v-model="url"
      :placeholder="t('home.urlPlaceholder')"
      size="large"
      clearable
      @keyup.enter="onParse"
    />
    <el-button type="primary" size="large" :loading="loading" @click="onParse">
      {{ loading ? t('home.parsing') : t('home.parse') }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

defineProps<{ loading: boolean }>();
const emit = defineEmits<{ parse: [url: string] }>();

const url = ref("");

function onParse() {
  if (url.value.trim()) {
    emit("parse", url.value.trim());
  }
}
</script>
