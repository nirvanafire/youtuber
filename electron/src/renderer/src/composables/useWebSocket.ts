import { ref, onUnmounted } from "vue";
import { getBackendPort } from "@/api/client";

export function useWebSocket() {
  const connected = ref(false);
  const ws = ref<WebSocket | null>(null);
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  function connect(onMessage: (data: any) => void) {
    const port = getBackendPort();
    const socket = new WebSocket(`ws://127.0.0.1:${port}/ws`);

    socket.onopen = () => {
      connected.value = true;
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch {}
    };

    socket.onclose = () => {
      connected.value = false;
      reconnectTimer = setTimeout(() => connect(onMessage), 3000);
    };

    socket.onerror = () => {
      socket.close();
    };

    ws.value = socket;
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
    if (ws.value) {
      ws.value.close();
      ws.value = null;
    }
  }

  onUnmounted(disconnect);

  return { connected, connect, disconnect };
}
