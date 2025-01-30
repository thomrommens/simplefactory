import logging
import re
from collections import Counter
from typing import Optional

from acgenius.config import STD_INSTR_DEBUG, STD_INSTR_SETTINGS
from acgenius.resources.models import Rule, Settings, WorkInstruction
from acgenius.routing.errors import process_error
from acgenius.validation.utils import remove_whitespaces, split_ip_and_prefix

logger = logging.getLogger("acgenius")

MSG_GENERIC = "IP ACG Rule properties validation failed."


def val_ip_linebreaks_absent(rule: Rule) -> Optional[bool]:
    """
    Validate that no linebreaks exist in the IP rule.

    :param rule: Rule object containing IP address to validate
    :raises RuleLinebreakException: If linebreak is found in IP address
    """
    logger.debug(
        f"Validate that there are no linebreaks in IP rule [{rule.ip}]...",
        extra={"depth": 5},
    )

    if "\n" in rule.ip:
        error_code = "RuleLinebreakException"
        error_map = {
            "RuleLinebreakException": {
                "msg": f"Line break found in IP rule [{rule}]. {STD_INSTR_DEBUG}",
                "crash": True,
            }
        }
        process_error(error_map, error_code, MSG_GENERIC)


def val_ip_format_correct(ip: str) -> Optional[bool]:
    """
    Validate that IP address follows IPv4 format.

    :param ip: IP address string to validate
    :raises RuleIPV4FormatInvalidException: If IP address format is invalid
    :note: Regex pattern from https://stackoverflow.com/questions/5284147/
    """
    logger.debug(f"Validate IPv4 format for ip [{ip}]...", extra={"depth": 5})

    pattern = r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$"

    if not re.match(pattern, ip):
        error_code = "RuleIPV4FormatInvalidException"
        error_map = {
            "RuleIPV4FormatInvalidException": {
                "msg": f"IP address [{ip}] does not meet IPv4 standard. "
                f"{STD_INSTR_DEBUG} {STD_INSTR_SETTINGS}",
                "crash": True,
            }
        }
        process_error(error_map, error_code, MSG_GENERIC)


def val_ip_allowed(ip: str, settings: Settings) -> Optional[bool]:
    """
    Validate IP address against list of disallowed IPs from settings.

    :param ip: IP address to validate
    :param settings: Settings object containing validation rules
    :return: True if IP is allowed, False if IP is in disallowed list
    """
    logger.debug(
        f"Validate IP address [{ip}] against disallowed IPs from settings.yaml...",
        extra={"depth": 5},
    )

    invalid_ips = [
        invalid_item.ip for invalid_item in settings.validation.invalid_rules
    ]

    if ip in invalid_ips:
        error_code = "IPAddressInInvalidRange"
        error_map = {
            "IPAddressInInvalidRange": {
                "msg": f"IP address [{ip}] is in invalid range. "
                f"{STD_INSTR_DEBUG} {STD_INSTR_SETTINGS}",
                "crash": True,
            }
        }
        process_error(error_map, error_code, MSG_GENERIC)


def val_prefix_allowed(prefix: int, settings: Settings) -> bool:
    """
    Validate that prefix length is within allowed boundaries.

    :param prefix: Prefix length to validate
    :param settings: Settings object containing validation rules
    :raises RulePrefixInvalidException: If prefix is outside allowed range
    """
    prefix_min = settings.validation.prefix_min
    prefix_default = settings.validation.prefix_default

    logger.debug(f"Validate prefix [{prefix}]...", extra={"depth": 5})
    if not prefix_min <= prefix <= prefix_default:
        error_code = "RulePrefixInvalidException"
        error_map = {
            "RulePrefixInvalidException": {
                "msg": f"Prefix [{prefix}] is invalid. "
                f"{STD_INSTR_DEBUG} {STD_INSTR_SETTINGS}",
                "crash": True,
            }
        }
        process_error(error_map, error_code, MSG_GENERIC)


def val_rule_desc_length(rule: Rule, settings: Settings) -> Optional[bool]:
    """
    Validate that rule description length is within AWS limit.

    :param rule: Rule object containing description to validate
    :param settings: Settings object containing validation rules
    :raises RuleDescriptionLengthException: If description exceeds AWS length limit
    """
    rules_desc_length_max = settings.validation.rules_desc_length_max

    logger.debug(
        f"Validate rule description length for rule [{rule}]...", extra={"depth": 5}
    )
    if len(rule.desc) > rules_desc_length_max:
        error_code = "RuleDescriptionLengthException"
        error_map = {
            "RuleDescriptionLengthException": {
                "msg": f"Rule description is [{len(rule.desc)}] characters, "
                f"so it exceeds the AWS limit of [{rules_desc_length_max}] "
                f"characters. {STD_INSTR_DEBUG} {STD_INSTR_SETTINGS}",
                "crash": True,
            }
        }
        process_error(error_map, error_code, MSG_GENERIC)


def val_rule_unique(rule_list: list) -> Optional[bool]:
    """
    Validate that no duplicate rules exist within an IP ACG.

    :param rule_list: List of rules with updated prefixes (e.g. /32 added)
    :raises IPACGDuplicateRulesException: If duplicate rules are found
    """
    logger.debug(
        "Validate that there are no duplicate rules within the IP ACG...",
        extra={"depth": 4},
    )
    logger.debug(f"Rule list: {rule_list}", extra={"depth": 5})

    duplicates = [k for k, v in Counter(rule_list).items() if v > 1]

    if len(duplicates) > 0:
        error_code = "IPACGDuplicateRulesException"
        error_map = {
            "IPACGDuplicateRulesException": {
                "msg": "Duplicate rule(s) found: "
                f"{duplicates}. Note, this duplication might also occur "
                "due to the app's addition of /32 for a single IP address. "
                f"{STD_INSTR_DEBUG} {STD_INSTR_SETTINGS}",
                "crash": True,
            }
        }
        process_error(error_map, error_code, MSG_GENERIC)


def val_amt_rules_allowed(rule_list: list, settings: Settings) -> Optional[bool]:
    """
    Validate that number of rules is larger than 0 and does not exceed AWS maximum.

    :param rule_list: List of rules to validate
    :param settings: Settings object containing validation rules

    """
    amt_rules_max = settings.validation.rules_amt_max

    logger.debug(
        f"Validate that the maximum number of IP rules is [{amt_rules_max}] or less...",
        extra={"depth": 5},
    )
    amt_rules = len(rule_list)

    error_map = {
        "IPACGMinAmtRulesException": {
            "msg": "The IP ACG in settings.yaml contains "
            f"[{amt_rules}] rules; Please specify at least 1 rule per IP ACG. "
            f"{STD_INSTR_DEBUG} {STD_INSTR_SETTINGS}",
            "crash": True,
        },
        "IPACGMaxAmtRulesException": {
            "msg": "The IP ACG in settings.yaml contains "
            f"[{amt_rules}] rules; more than "
            f"the [{amt_rules_max}] IP rules "
            "AWS allows per IP ACG. "
            f"{STD_INSTR_DEBUG} {STD_INSTR_SETTINGS}",
            "crash": True,
        },
    }

    error_code = ""
    if not amt_rules > 0:
        error_code = "IPACGMinAmtRulesException"
        process_error(error_map, error_code, MSG_GENERIC)
    elif not amt_rules <= amt_rules_max:
        error_code = "IPACGMaxAmtRulesException"
        process_error(error_map, error_code, MSG_GENERIC)


def val_rules(work_instruction: WorkInstruction, settings: Settings) -> WorkInstruction:
    """
    Integrate all Rule validations (Rule level).

    """
    logger.debug("Start: validate IP rules of settings.yaml...", extra={"depth": 2})
    for ip_acg in work_instruction.ip_acgs:
        logger.debug(f"Start: IP ACG [{ip_acg.name}]...", extra={"depth": 3})
        rule_list = []
        for rule in ip_acg.rules:
            logger.debug(
                f"Start: Rule: IP address [{rule.ip}]; description [{rule.desc}]...",
                extra={"depth": 4},
            )
            rule.ip = remove_whitespaces(rule)
            val_ip_linebreaks_absent(rule)

            ip, prefix = split_ip_and_prefix(rule)
            rule_list.append(f"{ip}/{prefix}")

            val_ip_format_correct(ip)
            val_ip_allowed(ip, settings)
            val_prefix_allowed(prefix, settings)
            val_rule_desc_length(rule, settings)

        val_rule_unique(rule_list)
        val_amt_rules_allowed(rule_list, settings)
        logger.debug(f"Finish: IP ACG [{ip_acg.name}]...", extra={"depth": 3})

    logger.debug("Finish: validate IP rules of settings.yaml...", extra={"depth": 2})

    return work_instruction
