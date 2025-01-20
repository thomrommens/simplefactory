import os
import boto3
import logging
from pathlib import Path

workspaces = boto3.client("workspaces", region_name="eu-west-1")

log_level = logging.INFO

HR = "=" * 88

SETTINGS_FILE = "settings.yaml"
SETTINGS_FILE_PATH = os.path.join(
    Path().resolve(), 
    "ad-ip-acg", 
    SETTINGS_FILE
)


class DepthFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style="%"):
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        pipes = "|" * getattr(record, "depth", 0)
        record.msg = f"{pipes}{' ' if pipes else ''}{record.msg}"
        return super().format(record)


def setup_logger(name, level=log_level):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)

    formatter = DepthFormatter(
        "[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    ch.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(ch)

    return logger
