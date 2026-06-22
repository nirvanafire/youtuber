import log from "electron-log";

log.transports.file.resolvePathFn = () => {
  const { app } = require("electron");
  const path = require("path");
  return path.join(app.getPath("exe"), "..", "logs", "main.log");
};

log.transports.file.maxSize = 10 * 1024 * 1024; // 10MB
log.transports.console.level = "debug";
log.transports.file.level = "info";

export default log;
