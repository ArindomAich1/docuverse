import logging
import sys
from logging.handlers import RotatingFileHandler


LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(log_level: str = "INFO", log_to_file: bool = False) -> None:
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    # ── Console handler (always on) ───────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    handlers: list[logging.Handler] = [console_handler]

    if log_to_file:
        file_handler = RotatingFileHandler(
            filename="logs/app.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # ── Root logger ───────────────────────────────────────────────────────
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        force=True
    )

    # ── Re-attach handler to uvicorn loggers explicitly ───────────────────
    # force=True strips uvicorn's handlers — we must re-add ours manually
    for uvicorn_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(uvicorn_logger_name)
        uvicorn_logger.handlers = [console_handler]   # ← re-attach
        uvicorn_logger.setLevel(logging.INFO)
        uvicorn_logger.propagate = False              # ← prevent double printing