import boto3
import logging

workspaces = boto3.client("workspaces", region_name="eu-west-1")


class DepthFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        pipes = '|' * getattr(record, 'depth', 0)
        record.msg = f'{pipes} {record.msg}'
        return super().format(record)


def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)

    formatter = DepthFormatter(
        '[%(asctime)s] [%(levelname)s] - %(message)s', "%Y-%m-%d %H:%M:%S"
    )
    ch.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(ch)

    return logger
