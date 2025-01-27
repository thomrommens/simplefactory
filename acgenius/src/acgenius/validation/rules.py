from collections import Counter
import logging
import re
from typing import Optional

from config import (
    IPACGAmtRulesException,
    IPACGDuplicateRulesException,
    RuleDescriptionLengthException,
    RuleIPV4FormatInvalidException,
    RuleLinebreakException,
    RulePrefixInvalidException,
    STD_INSTRUCTION
)

from resources.models import Rule, Settings, WorkInstruction
from .utils import remove_whitespaces, split_ip_and_prefix

logger = logging.getLogger("acgenius")


def val_ip_linebreaks_absent(rule) -> Optional[bool]:
    """
    Validate that no linebreaks exist in the IP rule.

    :param rule: Rule object containing IP address to validate
    :raises RuleLinebreakException: If linebreak is found in IP address
    """
    logger.debug(f"Validate if no linebreaks...", extra={"depth": 5})
    if "\n" in rule.ip:
        raise RuleLinebreakException(f"Line break found in IP rule [{rule.ip}].")
    

def val_ip_format_correct(ip: str) -> Optional[bool]:
    """
    Validate that IP address follows correct IPv4 format using regex pattern.

    :param ip: IP address string to validate
    :raises RuleIPV4FormatInvalidException: If IP address format is invalid
    :note: Regex pattern from https://stackoverflow.com/questions/5284147/
    """       
    logger.debug(
        f"Validate IPv4 format for ip [{ip}]...", 
        extra={"depth": 5}
    )
    
    pattern = r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$"

    if not re.match(pattern, ip):
        raise RuleIPV4FormatInvalidException(
            f"IP address is invalid. {STD_INSTRUCTION}"
        )


def val_ip_allowed(ip: str, settings: Settings) -> Optional[bool]:
    """
    Validate IP address against list of disallowed IPs from settings.

    :param ip: IP address to validate
    :param settings: Settings object containing validation rules
    :return: True if IP is allowed, False if IP is in disallowed list
    """
    invalid_ips = [
        rule.ip
        for rule 
        in settings.validation.invalid_rules
    ]    
    return ip not in invalid_ips


def val_prefix_allowed(prefix: int, settings: Settings) -> bool:
    """
    Validate that prefix length is within allowed boundaries.

    :param prefix: Prefix length to validate
    :param settings: Settings object containing validation rules
    :raises RulePrefixInvalidException: If prefix is outside allowed range
    """
    prefix_min = settings.validation.prefix_min
    prefix_default = settings.validation.prefix_default
    
    logger.debug(
        f"Validate prefix [{prefix}]...", 
        extra={"depth": 5}
    )
    if not prefix_min <= prefix <= prefix_default:
        raise RulePrefixInvalidException(
            f"Prefix [{prefix}] is invalid. {STD_INSTRUCTION}"
        )
    

def val_rule_desc_length(rule: Rule, settings: Settings) -> Optional[bool]:
    """
    Validate that rule description length is within AWS limit.

    :param rule: Rule object containing description to validate
    :param settings: Settings object containing validation rules
    :raises RuleDescriptionLengthException: If description exceeds AWS length limit
    """
    rules_desc_length_max = settings.validation.rules_desc_length_max
    
    logger.debug(
        f"Validate rule description length for rule [{rule}]...",
        extra={"depth": 5}
    )
    if len(rule.desc) > rules_desc_length_max:
        raise RuleDescriptionLengthException(
            f"Rule description exceeds AWS limit of [{rules_desc_length_max}] characters. "
            f"{STD_INSTRUCTION}"
        )


def val_rule_unique(rule_list: list) -> Optional[bool]:
    """
    Validate that no duplicate rules exist within an IP ACG.

    :param rule_list: List of rules with updated prefixes (e.g. /32 added)
    :raises IPACGDuplicateRulesException: If duplicate rules are found
    """
    logger.debug(
        f"Validate that there are no duplicate rules within the IP ACG...", 
        extra={"depth": 4}
    )
    logger.debug(f"Rule list: {rule_list}", extra={"depth": 5})

    duplicates = [k for k, v in Counter(rule_list).items() if v > 1]
        
    if len(duplicates) > 0:        
        raise IPACGDuplicateRulesException(
            f"Duplicate rule(s) found: {duplicates}. "
            "Note, this might also been due to the app's addition "
            "of /32 for a single IP address. "
            f"{STD_INSTRUCTION}"
        )
    

def val_amt_rules_allowed(rule_list: list, settings: Settings) -> Optional[bool]:
    """
    Validate that number of rules does not exceed AWS maximum.

    :param rule_list: List of rules to validate
    :param settings: Settings object containing validation rules
    :raises IPACGAmtRulesException: If number of rules exceeds AWS maximum
    """
    amt_rules_max = settings.validation.rules_amt_max

    logger.debug(
        f"Validate that the maximum number of IP rules is {amt_rules_max} or less...", 
        extra={"depth": 5}
    ) 
    amt_rules = len(rule_list)
    if not amt_rules <= amt_rules_max:
        raise IPACGAmtRulesException(
            f"The IP ACG contains [{amt_rules}] rules; "
            f"more than the [{amt_rules_max}] IP rules AWS allows per IP ACG."
            f"{STD_INSTRUCTION}"
        ) 
    

def val_rules(work_instruction: WorkInstruction, settings: Settings) -> WorkInstruction:
    """
    Validate all IP rules in the work instruction against AWS requirements.

    :param work_instruction: Work instruction containing IP ACGs and rules to validate
    :param settings: Settings object containing validation rules
    :return: Validated work instruction
    :raises: Various exceptions for rule validation failures
    """
    logger.debug(
        f"Start: validate IP rules of settings.yaml...", 
        extra={"depth": 2}
    )
    for ip_acg in work_instruction.ip_acgs:      
        logger.debug(
            f"Start: IP ACG [{ip_acg.name}]...", 
            extra={"depth": 3}
        )        
        rule_list = []
        for rule in ip_acg.rules: 
            logger.debug(
                f"Start: Rule: IP address [{rule.ip}]; description [{rule.desc}]...", 
                extra={"depth": 4}
            )       
            
            rule.ip = remove_whitespaces(rule)

            val_ip_linebreaks_absent(rule)

            ip, _ = split_ip_and_prefix(rule)
            _, prefix = split_ip_and_prefix(rule)
            
            rule_list.append(f"{ip}/{prefix}")

            val_ip_format_correct(ip)
            val_ip_allowed(ip, settings)
            val_prefix_allowed(prefix, settings)
            
        val_rule_unique(rule_list)
        val_amt_rules_allowed(rule_list, settings)
        logger.debug(
            f"Finish: IP ACG [{ip_acg.name}]...", 
            extra={"depth": 3}
        )

    logger.debug(
        f"Finish: validate IP rules of settings.yaml...", 
        extra={"depth": 2}
        )
    return work_instruction
