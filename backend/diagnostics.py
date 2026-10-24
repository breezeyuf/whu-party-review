"""Operational diagnostics without request bodies, credentials or exception values."""
from __future__ import annotations

import json
import logging
import traceback
from contextvars import ContextVar
from pathlib import Path

request_id: ContextVar[str | None] = ContextVar("request_id", default=None)
logger = logging.getLogger("party_review")


def configure_logging() -> None:
    # Respect the desktop's existing file handler and the host's logging setup.
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger.setLevel(logging.INFO)


def event(name: str, *, level=logging.INFO, **context) -> None:
    payload = {"event": name, **context}
    if request_id.get():
        payload["request_id"] = request_id.get()
    logger.log(level, json.dumps(payload, ensure_ascii=False))


def log_exception(name: str, exc: BaseException, **context) -> None:
    # SQL errors and model/client exceptions can embed passwords, document text
    # or bound parameters. Keep type + call sites, never str(exc) or locals.
    frames = traceback.extract_tb(exc.__traceback__)
    event(name, level=logging.ERROR, exception_type=type(exc).__name__,
          frames=[{"file": Path(frame.filename).name, "line": frame.lineno,
                   "function": frame.name} for frame in frames[-40:]], **context)
