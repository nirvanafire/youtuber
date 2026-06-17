import axios from "axios";

let _port: number | null = null;

export function setBackendPort(port: number) {
  _port = port;
}

export function getBackendPort(): number {
  if (!_port) throw new Error("Backend port not set");
  return _port;
}

const client = axios.create({
  baseURL: `http://127.0.0.1:${_port}`,
  timeout: 30000,
});

client.interceptors.request.use((config) => {
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

export default client;
