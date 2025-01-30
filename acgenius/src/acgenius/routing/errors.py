import logging
import sys
from typing import Optional

from botocore.exceptions import ClientError

from acgenius.config import EXC_UNEXPECTED_GENERIC, EXIT_APP

logger = logging.getLogger("acgenius")


def get_error_code(e: Exception) -> str:
    """
    Get error code in exception style.

    :param e: Exception
    :return: error code
    """
    exception_type = type(e).__name__

    error_code = str(exception_type)
    if exception_type == ClientError:
        error_code = e.response["Error"]["Code"]

    return error_code


def set_app_response(e: Optional[Exception] = None, crash: bool = True) -> None:
    """
    Formulate response to an error; soft landing instead of displaying hard error.

    :param e: Exception
    :param crash: whether to crash the app
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
    Integrate steps for app to process an error: set up message and take action.

    :param error_map: error map
    :param error_code: error code
    :param msg_generic: generic message applicable to scenario(s)
    :param e: Exception
    """
    crash = error_map.get(error_code, {}).get("crash", True)
    msg_specific = error_map.get(error_code, {}).get("msg", EXC_UNEXPECTED_GENERIC)
    msg = f"{msg_generic} {msg_specific}"

    logger.info(f"{msg}", extra={"depth": 1})
    set_app_response(e, crash)
