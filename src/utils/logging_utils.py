import logging
import os
from pathlib import Path

from src.config import LOG_FORMAT, LOG_DIR


def init_logger(log_file_name: str, logger_name: str) -> logging.Logger:
    os.makedirs(LOG_DIR, exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT)

    handler = logging.FileHandler(Path(LOG_DIR, log_file_name))
    handler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger
