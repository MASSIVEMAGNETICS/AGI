"""
Shared logging helpers for Victor.

Note: basicConfig uses force=True which will override existing logging
configuration when this module is imported.
"""
from __future__ import annotations

import logging
import os


def is_verbose() -> bool:
    return os.getenv("VICTOR_VERBOSE_LOG", "0").lower() in ("1", "true", "yes")


VERBOSE_LOGGING = is_verbose()


def configure_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.DEBUG if VERBOSE_LOGGING else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True,
    )
    logger = logging.getLogger(name)
    return logger


def v_log(message: str) -> None:
    if VERBOSE_LOGGING:
        print(f"[verbose] {message}")
