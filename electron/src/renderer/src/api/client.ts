import axios from "axios";

let _port: number | null = null;
let _portPromise: Promise<number | null> | null = null;

export function setBackendPort(port: number) {
  _port = port;
}

export function getBackendPort(): number {
  if (!_port) throw new Error("Backend port not set");
  return _port;
}

const client = axios.create({
  timeout: 30000,
});

client.interceptors.request.use(async (config) => {
  if (!_port) {
    // Fallback: fetch port directly from main process if event was missed
    if (!_portPromise && window.electronAPI) {
      _portPromise = window.electronAPI.getBackendPort();
    }
    if (_portPromise) {
      const port = await _portPromise;
      if (port) _port = port;
    }
  }
  if (_port) {
    config.baseURL = `http://127.0.0.1:${_port}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail || error.message || "Unknown error";
    return Promise.reject(new Error(message));
  }
);

export function initApiClient() {
  if (window.electronAPI) {
    window.electronAPI.onBackendReady((port: number) => {
      setBackendPort(port);
    });
  }
}

export default client;
