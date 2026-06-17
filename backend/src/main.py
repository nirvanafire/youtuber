# backend/src/main.py
import sys
import uvicorn
from fastapi import FastAPI
from src.api.router import api_router
from src.core.progress import ProgressTracker

app = FastAPI(title="Youtuber Backend", version="0.1.0")
app.state.progress_tracker = ProgressTracker()
app.include_router(api_router)


def main():
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()
    print(f"PORT={port}", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    main()
