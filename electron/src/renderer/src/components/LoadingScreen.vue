<template>
  <div class="loading-screen">
    <div class="loading-content">
      <el-icon :size="48" class="loading-spinner"><Loading /></el-icon>
      <h2 style="margin-top: 16px">{{ message }}</h2>
      <p v-if="subMessage" style="color: #909399">{{ subMessage }}</p>
      <el-button v-if="showRetry" type="primary" style="margin-top: 16px" @click="$emit('retry')">
        重试
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Loading } from "@element-plus/icons-vue";

defineProps<{
  message: string;
  subMessage?: string;
  showRetry?: boolean;
}>();

defineEmits<{ retry: [] }>();
</script>

<style scoped>
.loading-screen {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f5f7fa;
}
.loading-content {
  text-align: center;
}
.loading-spinner {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
