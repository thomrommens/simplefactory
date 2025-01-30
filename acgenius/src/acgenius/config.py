import boto3
import logging
import os
from pathlib import Path


SETTINGS_FILE = "settings.yaml"
SETTINGS_FILE_PATH = os.path.join(Path().resolve().parent, SETTINGS_FILE)

STD_INSTR_SETTINGS = "Please revise settings.yaml."
STD_INSTR_README = "See README.md for more info."
STD_INSTR_DEBUG = "Enable app debug mode (--debug) for more detail."

EXC_INVALID_PARAM = (
    "Please check if you have any empty values, or invalid characters "
    "in names, descriptions, or tags."
)
EXC_ACCESS_DENIED = (
    "It seems you do not have all permissions. Please check your IAM role."
)
EXC_RESOURCE_LIMIT = (
    "It seems you have attempted to many calls in a short amount of time. "
    "Please try again later."
)
EXC_RESOURCE_NOT_FOUND = (
    "Could not find IP ACG and/or the directory in AWS. "
    "Double check if they are created, "
    "and if not, do a 'create' run of this app."
)
EXC_RESOURCE_STATE = (
    "The IP ACG and/or the directory in AWS"
    "are in an unexpected state. "
    "Please inspect these resources in the AWS console. "
)
EXC_OPERATION_NOT_SUPPORTED = "The operation is not supported."
EXC_UNEXPECTED_GENERIC = "An unexpected exception occurred."

EXIT_APP = "❌ Cannot continue. Exit app."


HR = "┉" * 88

workspaces = boto3.client("workspaces", region_name="eu-west-1")

click_help = {
    "dryrun": (
        "Enable dryrun mode? "
        "This only shows the plan or inventory, "
        "and does not actually apply anything in AWS."
    ),
    "debug": (
        "Enable debug mode? This will show more detailed information in the logs."
    ),
}


class DepthFormatter(logging.Formatter):
    """
    Format log messages with pipe-based indentation based on depth.

    Extend the standard logging.Formatter to prepend pipe characters (|) to log messages
    based on a 'depth' attribute. The depth determines the level of indentation,
    making log output more hierarchical and readable.

    Format messages as:
        depth=0: message
        depth=1: | message
        depth=2: | | message
        etc.

    Example:
        [2023-01-01 12:00:00] [INFO] Starting process
        [2023-01-01 12:00:01] [INFO] | Processing item 1
        [2023-01-01 12:00:02] [INFO] | | Validating item 1
    """

    def __init__(self, fmt: str = None, datefmt: str = None, style: str = "%") -> None:
        super().__init__(fmt, datefmt, style)

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log message with indentation based on the depth attribute.

        :param record: actual log record
        :return: formatted log message
        """
        pipes = " |" * getattr(record, "depth", 0)
        record.msg = f"{pipes}{' ' if pipes else ''}{record.msg}"
        return super().format(record)


def setup_logger(name: str, debug: bool) -> logging.Logger:
    """
    Set up a logger with the specified name and debug level.

    :param name: Name of the logger to create
    :param debug: Whether to enable debug logging level
    :return: Configured logger instance with appropriate handler and formatter
    """
    logger = logging.getLogger(name)

    level = logging.INFO
    if debug:
        level = logging.DEBUG

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
