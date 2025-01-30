import logging
import sys
from typing import Optional

from botocore.exceptions import ClientError

from acgenius.config import EXC_UNEXPECTED_GENERIC, EXIT_APP

logger = logging.getLogger("acgenius")


def get_error_code(e: Exception) -> str:
    """
    xx
    """
    exception_type = type(e).__name__

    error_code = str(exception_type)
    if exception_type == ClientError:
        error_code = e.response["Error"]["Code"]

    return error_code


def set_app_response(e: Optional[Exception] = None, crash: bool = True) -> None:
    """
    Standard response (preventing full stack trace)
    """
    if e:
        if crash:
            logger.error(f"Full error: {e}", extra={"depth": 1})
            logger.info(f"{EXIT_APP}", extra={"depth": 1})
            sys.exit(1)
        else:
            logger.warning(f"⚠️  Full warning: {e}", extra={"depth": 1})
    else:
        if crash:
            logger.info(f"{EXIT_APP}", extra={"depth": 1})
            sys.exit(1)


def process_error(
    error_map: dict, error_code: str, msg_generic: str, e: Optional[Exception] = None
) -> None:
    """
    e for AWS calls; not for own custom exceptions
    """
    crash = error_map.get(error_code, {}).get("crash", True)
    msg_specific = error_map.get(error_code, {}).get("msg", EXC_UNEXPECTED_GENERIC)
    msg = f"{msg_generic} {msg_specific}"

    logger.info(f"{msg}", extra={"depth": 1})
    set_app_response(e, crash)
