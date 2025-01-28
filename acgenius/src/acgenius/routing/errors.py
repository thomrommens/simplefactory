import logging
import sys
from typing import Optional

from config import EXIT_APP


logger = logging.getLogger("acgenius")


def process_error(map: dict, code: str, e: Optional[Exception] = None):
    """
    e for AWS calls; not for own custom exceptions
    """
    crash = map.get(code, {}).get("crash", True)
    msg = map.get(code, {}).get("msg", "Unexpected error.")
    
    if e:
        msg = map.get(code, {}).get("msg", "Unexpected AWS error.")

    logger.info(f"{msg}", extra={"depth": 1})
    set_app_response(e, crash)


def set_app_response(e: Optional[Exception] = None, crash: bool = True) -> None:
    """
    Standard response (preventing full stack trace)
    """
    if e:
        if crash:        
            logger.error(f"❌ Full error: {e}", extra={"depth": 1})
            logger.info(f"{EXIT_APP}", extra={"depth": 1})
            sys.exit(1)
        else:
            logger.warning(f"⚠️  Full warning: {e}", extra={"depth": 1})
    else:
        logger.info(f"{EXIT_APP}", extra={"depth": 1})
