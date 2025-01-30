import logging
from typing import Counter

from acgenius.config import STD_INSTR_DEBUG, STD_INSTR_SETTINGS
from acgenius.resources.models import IP_ACG, Inventory, Settings, WorkInstruction
from acgenius.routing.errors import process_error

logger = logging.getLogger("acgenius")

MSG_GENERIC = "IP ACG properties validation failed."


def val_amt_groups_per_directory_allowed(
    ip_acg_name_list: list, settings: Settings
) -> None:
    """
    Validate that the number of IP ACGs per directory
    does not exceed the maximum number of groups per directory allowed.
    """
    amt_groups_per_directory_max = settings.validation.groups_per_directory_amt_max

    logger.debug(
        "Validate that the maximum number "
        f"of groups per directory is [{amt_groups_per_directory_max}] or less...",
        extra={"depth": 4},
    )

    amt_groups = len(ip_acg_name_list)

    if not amt_groups <= amt_groups_per_directory_max:
        error_code = "IPACGMaxAmtGroupsPerDirectoryException"
        error_map = {
            "IPACGMaxAmtGroupsPerDirectoryException": {
                "msg": f"You specified [{amt_groups}] groups; "
                f"more than the [{amt_groups_per_directory_max}] AWS allows. "
                f"{STD_INSTR_SETTINGS}",
                "crash": True,
            }
        }
        process_error(error_map, error_code, MSG_GENERIC)


def val_ip_acg_name_length_allowed(ip_acg: IP_ACG, settings: Settings) -> None:
    """
    Validate that IP ACG name is not longer than the AWS imposed limit.
    """
    logger.debug(
        f"Validate that IP ACG name [{ip_acg.name}] "
        f"is not longer than [{settings.validation.ip_acg_name_length_max}] "
        "characters...",
        extra={"depth": 4},
    )
    group_name_length_max = settings.validation.ip_acg_name_length_max

    if not ip_acg.name:
        error_code = "IPACGNAmeNoneException"
        error_map = {
            "IPACGNAmeNoneException": {
                "msg": "One IP ACG group in settings.yaml "
                "seems to have no name. "
                f"{STD_INSTR_DEBUG} {STD_INSTR_SETTINGS}",
                "crash": True,
            }
        }
        process_error(error_map, error_code, MSG_GENERIC)

    len_ip_acg_name = len(str(ip_acg.name))

    if not len_ip_acg_name <= group_name_length_max:
        error_code = "IPACGNameLengthException"
        error_map = {
            "IPACGNameLengthException": {
                "msg": "The IP ACG group name contains "
                f"[{len_ip_acg_name}] characters; "
                f"more than the [{group_name_length_max}] characters AWS allows. "
                f"{STD_INSTR_DEBUG} {STD_INSTR_SETTINGS}",
                "crash": True,
            }
        }
        process_error(error_map, error_code, MSG_GENERIC)


def val_ip_acg_name_unique(ip_acg_name_list: list) -> None:
    """
    Validate that the IP ACG name is unique in the list of all IP ACGs.
    """
    logger.debug(
        "Validate that the IP ACG name is not a duplicate...", extra={"depth": 4}
    )
    logger.debug(f"IP ACG name list: {ip_acg_name_list}", extra={"depth": 5})

    duplicates = [k for k, v in Counter(ip_acg_name_list).items() if v > 1]

    if len(duplicates) > 0:
        error_code = "IPACGNameDuplicateException"
        error_map = {
            "IPACGNameDuplicateException": {
                "msg": "Duplicate IP ACG name found: "
                f"{duplicates}. {STD_INSTR_DEBUG} {STD_INSTR_SETTINGS}",
                "crash": True,
            }
        }
        process_error(error_map, error_code, MSG_GENERIC)


def val_ip_acg_description_length_allowed(ip_acg: IP_ACG, settings: Settings) -> None:
    """
    Validate if IP ACG description has a value and is not longer than allowed
    description length.
    """
    desc_length_max = settings.validation.rules_desc_length_max

    logger.debug(
        "Validate that the IP ACG description "
        f"is not longer than [{desc_length_max}] characters...",
        extra={"depth": 4},
    )
    if not ip_acg.desc:
        error_code = "IPACGDescriptionNoneException"
        error_map = {
            "IPACGDescriptionNoneException": {
                "msg": "IP ACG group [{ip_acg.name}] "
                "seems to have no description. "
                f"{STD_INSTR_DEBUG} {STD_INSTR_SETTINGS}",
                "crash": True,
            }
        }
        process_error(error_map, error_code, MSG_GENERIC)

    len_ip_acg_desc = len(ip_acg.desc)

    if not len_ip_acg_desc <= desc_length_max:
        error_code = "IPACGDescriptionLengthException"
        error_map = {
            "IPACGDescriptionLengthException": {
                "msg": "The description "
                f"of IP ACG [{ip_acg.name}] contains "
                f"[{len_ip_acg_desc}] characters; "
                f"more than the [{desc_length_max}] characters AWS allows. "
                f"{STD_INSTR_DEBUG} {STD_INSTR_SETTINGS}",
                "crash": True,
            }
        }
        process_error(error_map, error_code, MSG_GENERIC)


def val_ip_acgs(
    work_instruction: WorkInstruction, settings: Settings
) -> WorkInstruction:
    """
    Integrate all IP ACG validations (IP ACG level).
    """
    logger.debug(
        "Start: validate IP ACG properties of settings.yaml...", extra={"depth": 2}
    )

    ip_acg_name_list = []
    for ip_acg in work_instruction.ip_acgs:
        logger.debug(f"Start: IP ACG [{ip_acg.name}]...", extra={"depth": 3})
        ip_acg_name_list.append(ip_acg.name)
        val_amt_groups_per_directory_allowed(ip_acg_name_list, settings)
        val_ip_acg_name_unique(ip_acg_name_list)
        val_ip_acg_name_length_allowed(ip_acg, settings)
        val_ip_acg_description_length_allowed(ip_acg, settings)

    logger.debug("Finish: validate IP rules of settings.yaml...", extra={"depth": 2})

    return work_instruction


def val_ip_acgs_match_inventory(matches: int, inventory: Inventory) -> bool:
    """
    Validate if all IP ACGs from the inventory could be matched by name,
    with all IP ACGs from the actual situation in AWS.
    """
    logger.debug(
        "Validate if all IP ACGs from the inventory could be matched by name",
        extra={"depth": 1},
    )
    logger.debug(f"Matches: [{matches}]...", extra={"depth": 1})
    logger.debug(
        f"Inventory [ip_acgs] length: [{len(inventory.ip_acgs)}]...", extra={"depth": 1}
    )
    if not matches == len(inventory.ip_acgs):
        error_code = "IPACGIdMatchException"
        error_map = {
            "IPACGIdMatchException": {
                "msg": "Could not match "
                "all current IP ACGs from AWS with IP ACGs specified "
                "in settings.yaml. Please make sure your settings.yaml is "
                "in sync with the actual situation in AWS.",
                "crash": True,
            }
        }
        process_error(error_map, error_code, MSG_GENERIC)
