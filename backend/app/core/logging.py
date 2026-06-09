import sys
import json
from pathlib import Path
from loguru import logger

from app.core.config import settings


def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger.remove()

    log_format = settings.log_format
    log_level = settings.log_level.upper()

    if log_format == "json":
        fmt = lambda r: json.dumps({
            "timestamp": r["time"].isoformat(),
            "level": r["level"].name,
            "module": r["name"],
            "function": r["function"],
            "line": r["line"],
            "message": r["message"],
            "extra": r["extra"],
        })
    else:
        fmt = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} | {message}"

    logger.add(
        sys.stdout,
        format=fmt,
        level=log_level,
        colorize=True,
    )

    logger.add(
        log_dir / "openmailer_{time:YYYY-MM-DD}.log",
        format=fmt,
        level=log_level,
        rotation="1 day",
        retention="30 days",
        compression="gz",
    )

    logger.add(
        log_dir / "errors_{time:YYYY-MM-DD}.log",
        format=fmt,
        level="ERROR",
        rotation="1 day",
        retention="90 days",
        compression="gz",
    )

    logger.info(f"Logging configured: level={log_level}, format={log_format}")
    return logger
