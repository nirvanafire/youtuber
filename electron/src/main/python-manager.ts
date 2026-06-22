import { spawn, execFile, ChildProcess } from "child_process";
import path from "path";
import log from "./logger";

const PYTHON_COMMANDS = ["python3", "python", "py"];
const MIN_PYTHON_VERSION = [3, 10];
const MAX_RESTARTS = 3;
const HEALTH_CHECK_INTERVAL = 500;
const HEALTH_CHECK_TIMEOUT = 30000;

export interface PythonManagerState {
  port: number | null;
  pythonPath: string;
  isEmbedded: boolean;
  process: ChildProcess | null;
  ready: boolean;
}

export class PythonManager {
  private state: PythonManagerState = {
    port: null,
    pythonPath: "",
    isEmbedded: false,
    process: null,
    ready: false,
  };
  private restartCount = 0;
  private onReadyCallbacks: ((port: number) => void)[] = [];
  private onErrorCallbacks: ((error: string) => void)[] = [];

  onReady(callback: (port: number) => void) {
    this.onReadyCallbacks.push(callback);
  }

  onError(callback: (error: string) => void) {
    this.onErrorCallbacks.push(callback);
  }

  getState(): PythonManagerState {
    return { ...this.state };
  }

  async detectPython(): Promise<string | null> {
    for (const cmd of PYTHON_COMMANDS) {
      try {
        const version = await this.getPythonVersion(cmd);
        if (version && this.isVersionValid(version)) {
          return cmd;
        }
      } catch {}
    }
    return null;
  }

  private getPythonVersion(cmd: string): Promise<string | null> {
    return new Promise((resolve) => {
      execFile(cmd, ["--version"], { timeout: 5000 }, (err, stdout) => {
        if (err) {
          resolve(null);
          return;
        }
        const match = stdout.match(/Python (\d+\.\d+\.\d+)/);
        resolve(match ? match[1] : null);
      });
    });
  }

  private isVersionValid(version: string): boolean {
    const parts = version.split(".").map(Number);
    return (
      parts[0] > MIN_PYTHON_VERSION[0] ||
      (parts[0] === MIN_PYTHON_VERSION[0] && parts[1] >= MIN_PYTHON_VERSION[1])
    );
  }

  async start(): Promise<void> {
    const pythonCmd = await this.detectPython();
    if (!pythonCmd) {
      const embeddedPath = this.getEmbeddedPythonPath();
      if (embeddedPath) {
        this.state.pythonPath = embeddedPath;
        this.state.isEmbedded = true;
      } else {
        for (const cb of this.onErrorCallbacks) cb("未找到 Python 3.10+ 环境");
        return;
      }
    } else {
      this.state.pythonPath = pythonCmd;
      this.state.isEmbedded = false;
    }

    await this.spawnBackend();
  }

  private getEmbeddedPythonPath(): string | null {
    const isProd = !process.env.NODE_ENV || process.env.NODE_ENV === "production";
    if (!isProd) return null;

    const resourcesPath = process.resourcesPath;
    const platform = process.platform;
    if (platform === "win32") {
      return path.join(resourcesPath, "backend", "python", "python.exe");
    }
    return path.join(resourcesPath, "backend", "python", "bin", "python3");
  }

  private async spawnBackend(): Promise<void> {
    const backendScript = this.getBackendScriptPath();
    const isProd = !process.env.NODE_ENV || process.env.NODE_ENV === "production";
    const cwd = isProd
      ? path.join(process.resourcesPath, "backend")
      : path.join(__dirname, "../../../backend");

    return new Promise((resolve, reject) => {
      const proc = spawn(this.state.pythonPath, [backendScript], {
        stdio: ["pipe", "pipe", "pipe"],
        env: { ...process.env, PYTHONPATH: cwd },
        cwd,
      });

      this.state.process = proc;
      let portFound = false;
      let outputBuffer = "";

      proc.stdout?.on("data", (data: Buffer) => {
        outputBuffer += data.toString();
        const lines = outputBuffer.split("\n");
        outputBuffer = lines.pop() || "";

        for (const line of lines) {
          const portMatch = line.match(/PORT=(\d+)/);
          if (portMatch) {
            this.state.port = parseInt(portMatch[1], 10);
            portFound = true;
            this.waitForHealthCheck().then(() => {
              this.state.ready = true;
              this.restartCount = 0;
              (async () => {
                for (const cb of this.onReadyCallbacks) await cb(this.state.port!);
                resolve();
              })();
            });
          }
        }
      });

      proc.stderr?.on("data", (data: Buffer) => {
        log.error(`[Python stderr] ${data.toString()}`);
      });

      proc.on("error", (err) => {
        for (const cb of this.onErrorCallbacks) cb(`Python 进程启动失败: ${err.message}`);
        reject(err);
      });

      proc.on("exit", (code) => {
        this.state.ready = false;
        this.state.process = null;
        if (!portFound) {
          for (const cb of this.onErrorCallbacks) cb(`Python 进程退出，代码: ${code}`);
          reject(new Error(`Python exited with code ${code}`));
        } else if (this.restartCount < MAX_RESTARTS) {
          this.restartCount++;
          log.warn(`Python backend crashed, restarting (${this.restartCount}/${MAX_RESTARTS})...`);
          this.spawnBackend();
        } else {
          for (const cb of this.onErrorCallbacks) cb("Python 后端多次崩溃，已停止重启");
        }
      });
    });
  }

  private getBackendScriptPath(): string {
    const isProd = !process.env.NODE_ENV || process.env.NODE_ENV === "production";
    if (isProd) {
      return path.join(process.resourcesPath, "backend", "main.py");
    }
    return path.join(__dirname, "../../../backend/src/main.py");
  }

  private async waitForHealthCheck(): Promise<void> {
    const start = Date.now();
    return new Promise((resolve, reject) => {
      const check = async () => {
        try {
          const response = await fetch(`http://127.0.0.1:${this.state.port}/health`);
          if (response.ok) {
            resolve();
            return;
          }
        } catch {}
        if (Date.now() - start > HEALTH_CHECK_TIMEOUT) {
          reject(new Error("Health check timeout"));
          return;
        }
        setTimeout(check, HEALTH_CHECK_INTERVAL);
      };
      check();
    });
  }

  async stop(): Promise<void> {
    if (this.state.process) {
      this.state.process.kill("SIGTERM");
      await new Promise<void>((resolve) => {
        const timeout = setTimeout(() => {
          this.state.process?.kill("SIGKILL");
          resolve();
        }, 5000);
        this.state.process?.on("exit", () => {
          clearTimeout(timeout);
          resolve();
        });
      });
      this.state.process = null;
      this.state.ready = false;
      this.state.port = null;
    }
  }
}
