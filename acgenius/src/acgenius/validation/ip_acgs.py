import logging
from typing import Counter

from config import (
    IPACGDescriptionLengthException,
    IPACGIdMatchException,
    IPACGNameDuplicateException,
    IPACGNameLengthException,
    STD_INSTRUCTION
)
from resources.models import IP_ACG, Inventory, Settings, WorkInstruction


logger = logging.getLogger("acgenius")

# TODO: validate if selected directory exists? -> dir in wi vs dir in inv


def val_ip_acg_name_length_allowed(ip_acg: IP_ACG, settings: Settings) -> None:
    """
    Validate that IP ACG name is not longer than the AWS imposed limit.
    """
    logger.debug(
        f"Validate that IP ACG name [{ip_acg.name}] "
        f"is not longer than [{settings.validation.ip_acg_name_length_max}] "
        f"characters...",
        extra={"depth": 4}
    )
    group_name_length_max = settings.validation.ip_acg_name_length_max

    len_ip_acg_name = len(ip_acg.name)
    if not len_ip_acg_name <= group_name_length_max:
        raise IPACGNameLengthException(
            "The IP ACG group name contains "
            f"[{len_ip_acg_name}] characters; "
            f"more than the [{group_name_length_max}] characters AWS allows. "
            f"{STD_INSTRUCTION}",
        ) 


def val_ip_acg_name_unique(ip_acg_name_list: list) -> None:
    """
    Validate that the IP ACG name is unique in the list of all IP ACGs.
    """
    logger.debug(
        f"Validate that the IP ACG name is not a duplicate...", 
        extra={"depth": 4}
    )
    logger.debug(f"IP ACG name list: {ip_acg_name_list}", extra={"depth": 5})

    duplicates = [k for k, v in Counter(ip_acg_name_list).items() if v > 1]
        
    if len(duplicates) > 0:        
        raise IPACGNameDuplicateException(
            f"Duplicate IP ACG name found: {duplicates}. "
            f"{STD_INSTRUCTION}"
        )
    

def val_ip_acg_description_length_allowed(ip_acg: IP_ACG, settings: Settings) -> None:
    """
    Validate if IP ACG description not longer than description length.
    """
    desc_length_max = settings.validation.rules_desc_length_max

    logger.debug(
        "Validate that the IP ACG description "
        f"is not longer than [{desc_length_max}] characters...",
        extra={"depth": 4}
    )
    len_ip_acg_desc = len(ip_acg.desc)
    if not len_ip_acg_desc <= desc_length_max:
        raise IPACGDescriptionLengthException(
            "The IP ACG group description contains "
            f"[{len_ip_acg_desc}] characters; "
            f"more than the [{desc_length_max}] characters AWS allows. "
            f"{STD_INSTRUCTION}"
        ) 


def val_ip_acgs(work_instruction: WorkInstruction, settings: Settings) -> WorkInstruction:
    """
    xx
    """
    logger.debug(
        "Start: validate IP ACG properties of settings.yaml...",
        extra={"depth": 2}
        )
    
    for ip_acg in work_instruction.ip_acgs: 
        ip_acg_name_list = []
        logger.debug(
            f"Start: IP ACG [{ip_acg.name}]...",
            extra={"depth": 3}
        )   
        ip_acg_name_list.append(ip_acg.name)
        val_ip_acg_name_unique(ip_acg_name_list)     
        val_ip_acg_name_length_allowed(ip_acg, settings)
        val_ip_acg_description_length_allowed(ip_acg, settings)

    logger.debug(
        f"Finish: validate IP rules of settings.yaml...", 
        extra={"depth": 2}
        )

    return work_instruction


def val_ip_acgs_match_inventory(matches: int, inventory: Inventory) -> bool:
    """
    Validate if all IP ACGs from the inventory could be matched by name,
    with all IP ACGs from the actual situation in AWS.
    """
    logger.debug(
        "Validate if all IP ACGs from the inventory could be matched by name", 
        extra={"depth": 1}
    )
    logger.debug(f"Matches: [{matches}]...", extra={"depth": 1})
    logger.debug(
        f"Inventory [ip_acgs] length: [{len(inventory.ip_acgs)}]...", extra={"depth": 1}
    )
    if not matches == len(inventory.ip_acgs):
        raise IPACGIdMatchException(
            "Could not match all current IP ACGs from AWS with IP ACGs specified "
            "in settings.yaml. Are you sure you have the correct IP ACGs specified "
            "in settings.yaml?"
        )
