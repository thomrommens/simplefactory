from collections import Counter
import logging
import re

from config import STD_INSTRUCTION
from exceptions import (
    IPACGAmtRulesException, 
    IPACGDescriptionLengthException, 
    IPACGDuplicateRulesException,
    IPACGNameDuplicateException, 
    IPACGNameLengthException, 
    RulePrefixInvalidException, 
    RuleIPV4FormatInvalidException, 
    RuleLinebreakException
)
from models import IP_ACG, Rule, Settings, WorkInstruction

logger = logging.getLogger("ip_acg_logger")

# TODO: consistent naming of validations: right direction

# ****************************************************************************
# Validate RULE level
# ****************************************************************************

def split_ip_and_prefix(rule: Rule) -> tuple[str, int]:
    """
    Split
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
    xx
    """

    logger.debug(f"Remove whitespaces if any...", extra={"depth": 5})
    return rule.ip.replace(" ", "")


def val_linebreaks_absent(rule) -> bool:
    """
    xx
    """
    logger.debug(f"Validate if no linebreaks...", extra={"depth": 5})
    if "\n" in rule.ip:
        raise RuleLinebreakException("Line break found in IP rule [{rule}].")
    

def val_ipv4_format(ip: str) -> bool:
    """
    Ref regex pattern: https://stackoverflow.com/questions/5284147/validating-ipv4-addresses-with-regexp?page=1&tab=scoredesc#tab-top
    Checks for population?
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
        # TODO: check if populated included?


def val_not_invalid(ip: str) -> bool:
    """
    Test against set of IP addresses that do not make sense
    """
    # TODO: other function name
    # TODO: write validation
    # TODO: also validate these settings themselves, for IPv4 format?
    pass


def val_prefix(prefix) -> bool:
    """
    xx
    """
    logger.debug(
        f"Validate prefix [{prefix}]...", 
        extra={"depth": 5}
    )
    if not 27 <= prefix <= 32:  # TODO replace with dynamic values
        raise RulePrefixInvalidException(
            f"Prefix [{prefix}] is invalid. {STD_INSTRUCTION}"
        )
    
# TODO: validate limit of rule description length?

def val_no_dup_rules(rule_list: list) -> None:
    """
    Validate no duplicate rules in rule list per IP ACG.

    :param rule_list: list with updated rules (i.e., added /32 at default)
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
    

def val_amt_rules(rule_list: list) -> None:
    """
    Validate if not larger than max number of IP rules.
    """
    logger.debug(
        f"Validate that the maximum number of IP rules is 10 or less...", # TODO dynamic
        extra={"depth": 5}
    ) 
    amt_rules = len(rule_list)
    if not amt_rules <= 10:
        raise IPACGAmtRulesException(
            f"The IP ACG contains [{amt_rules}] rules; "
            "more than the [10] IP rules AWS allows per IP ACG."   # TODO dynamic
            f"{STD_INSTRUCTION}"
        ) 

# ----------------------------------------------------------------------------

def val_rules(work_instruction: WorkInstruction) -> WorkInstruction:
    """
    xx
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

            val_linebreaks_absent(rule)

            ip, _ = split_ip_and_prefix(rule)
            _, prefix = split_ip_and_prefix(rule)
            
            rule_list.append(f"{ip}/{prefix}")

            val_ipv4_format(ip)
            val_not_invalid(ip)
            val_prefix(prefix)
            
        val_no_dup_rules(rule_list)
        val_amt_rules(rule_list)
        logger.debug(
            f"Finish: IP ACG [{ip_acg.name}]...", 
            extra={"depth": 3}
        )

    logger.debug(
        f"Finish: validate IP rules of settings.yaml...", 
        extra={"depth": 2}
        )
    return work_instruction
  
# ****************************************************************************
# Validate IP ACG level
# ****************************************************************************

def val_group_name(ip_acg: IP_ACG) -> None:
    """
    Validate if IP ACG name not longer than name length.
    """
    logger.debug(
        "Validate that the IP ACG name length "
        "is not longer than 50 characters...",
        extra={"depth": 4}
    ) # TODO dynamic
    len_group_name = len(ip_acg.name)
    if not len_group_name <= 50:
        raise IPACGNameLengthException(
            "The IP ACG group name contains "
            f"[{len_group_name}] characters; "
            "more than the [50] characters AWS allows. "   # TODO dynamic
            f"{STD_INSTRUCTION}",
        ) 


def val_no_dup_ip_acg_name(group_name_list: list) -> None:  # TODO: generalize dup check - ip acg name vs. rule?
    """
    xx
    """
    logger.debug(
        f"Validate that the IP ACG name is not a duplicate...", 
        extra={"depth": 4}
    )
    logger.debug(f"Group name list: {group_name_list}", extra={"depth": 5})

    duplicates = [k for k, v in Counter(group_name_list).items() if v > 1]
        
    if len(duplicates) > 0:        
        raise IPACGNameDuplicateException(
            f"Duplicate group name found: {duplicates}. "
            f"{STD_INSTRUCTION}"
        )
    

def val_group_description(ip_acg: IP_ACG) -> None:
    """
    Validate if IP ACG description not longer than description length.
    """
    logger.debug(
        "Validate that the IP ACG description "
        "is not longer than 255 characters...",
        extra={"depth": 4}
    ) # TODO check + include in settings.json + dynamic
    len_group_desc = len(ip_acg.desc)
    if not len(ip_acg.desc) <= 255:
        raise IPACGDescriptionLengthException(
            "The IP ACG group description contains "
            f"[{len_group_desc}] characters; "
            "more than the [255] characters AWS allows. "   # TODO dynamic
            f"{STD_INSTRUCTION}"
        ) 

# ----------------------------------------------------------------------------

def val_ip_acgs(work_instruction: WorkInstruction) -> WorkInstruction:
    """
    xx
    """
    logger.debug(
        "Start: validate IP ACG properties of settings.yaml...",
        extra={"depth": 2}
        )
    
    for ip_acg in work_instruction.ip_acgs: 
        group_name_list = []
        logger.debug(
            f"Start: IP ACG [{ip_acg.name}]...",
            extra={"depth": 3}
        )   
        group_name_list.append(ip_acg.name)
        val_no_dup_ip_acg_name(group_name_list)     
        val_group_name(ip_acg)
        val_group_description(ip_acg)

    logger.debug(
        f"Finish: validate IP rules of settings.yaml...", 
        extra={"depth": 2}
        )

    return work_instruction
    

# ****************************************************************************

def val_work_instruction(settings: Settings) -> WorkInstruction:
    """
    xx
    """
    logger.debug(
        "Start: validate settings.yaml...",
        extra={"depth": 1}
    )    
    work_instruction_rules_validated = val_rules(settings.work_instruction)
    work_instruction_ip_acgs_validated = val_ip_acgs(work_instruction_rules_validated)
    
    logger.debug(
        "Finish: validate settings.yaml.",
        extra={"depth": 1}
    )
    return work_instruction_ip_acgs_validated
