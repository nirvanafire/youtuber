import http from "http";
import { WebSocket, WebSocketServer } from "ws";

export class ApiProxy {
  private httpServer: http.Server | null = null;
  private wss: WebSocketServer | null = null;
  private targetPort: number = 0;

  start(listenPort: number, targetPort: number): void {
    this.targetPort = targetPort;

    this.httpServer = http.createServer((req, res) => {
      const options = {
        hostname: "127.0.0.1",
        port: targetPort,
        path: req.url,
        method: req.method,
        headers: req.headers,
      };

      const proxyReq = http.request(options, (proxyRes) => {
        res.writeHead(proxyRes.statusCode || 500, proxyRes.headers);
        proxyRes.pipe(res);
      });

      proxyReq.on("error", (err) => {
        console.error("Proxy error:", err.message);
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
        console.error("Backend WS error:", err.message);
        clientWs.close();
      });
    });

    this.httpServer.listen(listenPort, "127.0.0.1");
  }

  stop(): void {
    this.wss?.close();
    this.httpServer?.close();
    this.httpServer = null;
    this.wss = null;
  }
}
