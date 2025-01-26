import logging
from typing import Counter

from config import (
    IPACGDescriptionLengthException,
    IPACGNameDuplicateException,
    IPACGNameLengthException,
    STD_INSTRUCTION
)
from resources.models import IP_ACG, Settings, WorkInstruction


logger = logging.getLogger("ip_acg_logger")


def val_group_name_length_allowed(ip_acg: IP_ACG, settings: Settings) -> None:
    """
    Validate that IP ACG name is not longer than the AWS imposed limit.
    """
    group_name_length_max = settings.validation.ip_acg_name_length_max

    logger.debug(
        "Validate that the IP ACG name length "
        f"is not longer than [{group_name_length_max}] characters...",
        extra={"depth": 4}
    )
    len_group_name = len(ip_acg.name)
    if not len_group_name <= group_name_length_max:
        raise IPACGNameLengthException(
            "The IP ACG group name contains "
            f"[{len_group_name}] characters; "
            f"more than the [{group_name_length_max}] characters AWS allows. "
            f"{STD_INSTRUCTION}",
        ) 


def val_ip_acg_name_unique(group_name_list: list) -> None:
    """
    Validate that the IP ACG name is unique in the list of all IP ACGs.
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
    

def val_group_description_length_allowed(ip_acg: IP_ACG, settings: Settings) -> None:
    """
    Validate if IP ACG description not longer than description length.
    """
    group_desc_length_max = settings.validation.rules_desc_length_max

    logger.debug(
        "Validate that the IP ACG description "
        f"is not longer than [{group_desc_length_max}] characters...",
        extra={"depth": 4}
    )
    len_group_desc = len(ip_acg.desc)
    if not len_group_desc <= group_desc_length_max:
        raise IPACGDescriptionLengthException(
            "The IP ACG group description contains "
            f"[{len_group_desc}] characters; "
            f"more than the [{group_desc_length_max}] characters AWS allows. "
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
        group_name_list = []
        logger.debug(
            f"Start: IP ACG [{ip_acg.name}]...",
            extra={"depth": 3}
        )   
        group_name_list.append(ip_acg.name)
        val_ip_acg_name_unique(group_name_list)     
        val_group_name_length_allowed(ip_acg, settings)
        val_group_description_length_allowed(ip_acg, settings)

    logger.debug(
        f"Finish: validate IP rules of settings.yaml...", 
        extra={"depth": 2}
        )

    return work_instruction
