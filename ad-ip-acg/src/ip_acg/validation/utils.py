import logging
from models import Rule

logger = logging.getLogger("ip_acg_logger")


def split_ip_and_prefix(rule: Rule) -> tuple[str, int]:
    """
    Split IP address and prefix.
    """

    fwd_slash = rule.ip.find("/")

    if fwd_slash != -1:
        ip = rule.ip[:fwd_slash]
        prefix = int(rule.ip[fwd_slash+1:])

    else:
        ip = rule.ip
        prefix = 32  # TODO replace with dynamic value

    return ip, prefix


def remove_whitespaces(rule: Rule) -> Rule:
    """
    Remove whitespaces from IP address.
    """
    logger.debug(f"Remove whitespaces if any...", extra={"depth": 5})
    return rule.ip.replace(" ", "")
