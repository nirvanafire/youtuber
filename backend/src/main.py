# backend/src/main.py
import logging
import time
import uvicorn
from fastapi import FastAPI, Request
from src.api.router import api_router
from src.core.progress import ProgressTracker

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger("youtuber")
# Suppress noisy third-party loggers
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

app = FastAPI(title="Youtuber Backend", version="0.1.0")
app.state.progress_tracker = ProgressTracker()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f">>> {request.method} {request.url.path} (client: {request.client})")
    start = time.time()
    try:
        response = await call_next(request)
        elapsed = (time.time() - start) * 1000
        logger.info(f"<<< {request.method} {request.url.path} -> {response.status_code} ({elapsed:.0f}ms)")
        return response
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        logger.error(f"!!! {request.method} {request.url.path} -> EXCEPTION ({elapsed:.0f}ms): {e}")
        raise


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
