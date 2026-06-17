<template>
  <LoadingScreen
    v-if="!backendReady"
    :message="loadingMessage"
    :sub-message="loadingError"
    :show-retry="!!loadingError"
    @retry="retryConnection"
  />
  <router-view v-else />
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import LoadingScreen from "./components/LoadingScreen.vue";

const backendReady = ref(false);
const loadingMessage = ref("正在初始化...");
const loadingError = ref<string | undefined>(undefined);

onMounted(() => {
  if (window.electronAPI) {
    window.electronAPI.onBackendReady((port: number) => {
      backendReady.value = true;
    });
    window.electronAPI.onBackendError((error: string) => {
      loadingError.value = error;
      loadingMessage.value = "启动失败";
    });
  } else {
    // Dev mode without Electron
    backendReady.value = true;
  }

  // Timeout
  setTimeout(() => {
    if (!backendReady.value && !loadingError.value) {
      loadingError.value = "启动超时，请检查 Python 环境";
      loadingMessage.value = "启动失败";
    }
  }, 30000);
});

function retryConnection() {
  loadingError.value = undefined;
  loadingMessage.value = "正在重试...";
  window.location.reload();
}
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}
#app {
  height: 100%;
}
</style>
