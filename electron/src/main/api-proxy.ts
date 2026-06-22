import http from "http";
import { WebSocket, WebSocketServer } from "ws";
import log from "./logger";

export class ApiProxy {
  private httpServer: http.Server | null = null;
  private wss: WebSocketServer | null = null;
  private targetPort: number = 0;

  start(listenPort: number, targetPort: number): Promise<void> {
    this.targetPort = targetPort;

    this.httpServer = http.createServer((req, res) => {
      log.info(`[Proxy] ${req.method} ${req.url} -> 127.0.0.1:${targetPort}`);

      // Handle preflight
      if (req.method === "OPTIONS") {
        res.writeHead(204, {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, Authorization",
        });
        res.end();
        return;
      }

      const options = {
        hostname: "127.0.0.1",
        port: targetPort,
        path: req.url,
        method: req.method,
        headers: req.headers,
      };

      const proxyReq = http.request(options, (proxyRes) => {
        log.info(`[Proxy] ${req.method} ${req.url} <- ${proxyRes.statusCode}`);
        const headers = {
          ...proxyRes.headers,
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, Authorization",
        };
        res.writeHead(proxyRes.statusCode || 500, headers);
        proxyRes.pipe(res);
      });

      proxyReq.on("error", (err) => {
        log.error(`[Proxy] ${req.method} ${req.url} ERROR: ${err.message}`);
        res.writeHead(502);
        res.end("Bad Gateway");
      });

      req.pipe(proxyReq);
    });

    this.wss = new WebSocketServer({ server: this.httpServer });
    this.wss.on("connection", (clientWs, req) => {
      const targetWs = new WebSocket(`ws://127.0.0.1:${targetPort}/ws`);

      targetWs.on("open", () => {
        clientWs.on("message", (data) => {
          if (targetWs.readyState === WebSocket.OPEN) {
            targetWs.send(data);
          }
        });
      });

      targetWs.on("message", (data) => {
        if (clientWs.readyState === WebSocket.OPEN) {
          clientWs.send(data);
        }
      });

      clientWs.on("close", () => {
        targetWs.close();
      });

      targetWs.on("close", () => {
        clientWs.close();
      });

      targetWs.on("error", (err) => {
        log.error("Backend WS error:", err.message);
        clientWs.close();
      });
    });

    return new Promise<void>((resolve, reject) => {
      this.httpServer!.once("listening", () => {
        log.info(`API proxy listening on 127.0.0.1:${listenPort} -> 127.0.0.1:${targetPort}`);
        resolve();
      });
      this.httpServer!.once("error", (err) => {
        log.error("Proxy listen error:", err.message);
        reject(err);
      });
      this.httpServer!.listen(listenPort, "127.0.0.1");
    });
  }

  stop(): void {
    this.wss?.close();
    this.httpServer?.close();
    this.httpServer = null;
    this.wss = null;
  }
}
