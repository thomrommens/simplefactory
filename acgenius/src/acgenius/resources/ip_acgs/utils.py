import json
import logging
from dataclasses import asdict
from datetime import datetime

from acgenius.resources.models import IP_ACG, Inventory, WorkInstruction
from acgenius.validation.ip_acgs import val_ip_acgs_match_inventory

logger = logging.getLogger("acgenius")


def match_ip_acgs(
    inventory: Inventory, work_instruction: WorkInstruction
) -> WorkInstruction:
    """
    Match IP ACGs from work instruction with IP ACGs from inventory.

    1 - Get the current IP ACGs from the inventory.
    2 - Get the to-be-updated IP ACGs from the work instruction.
    The settings.yaml is not aware of the ids of
    the IP ACGs specified.

    Find the ids of the IP ACGs of 2 by looking them up in 1.
    Update the input WorkInstruction.

    :param inventory: Inventory object
    :param work_instruction: WorkInstruction object
    :return: WorkInstruction object with matched IP ACGs
    """
    logger.debug(
        "Try to match IP ACGs from work instruction with IP ACGs from inventory...",
        extra={"depth": 5},
    )
    logger.debug(
        f"Current inventory:\n{json.dumps(asdict(work_instruction), indent=4)}",
        extra={"depth": 1},
    )
    logger.debug(
        f"Current work instruction:\n{json.dumps(asdict(work_instruction), indent=4)}",
        extra={"depth": 1},
    )

    matches = 0
    for work_instruction_ip_acg in work_instruction.ip_acgs:
        for inventory_ip_acg in inventory.ip_acgs:
            if work_instruction_ip_acg.name == inventory_ip_acg.name:
                logger.debug(
                    f"Matching IP ACG names: [{work_instruction_ip_acg.name}] with "
                    f"[{inventory_ip_acg.name}]...",
                    extra={"depth": 2},
                )
                matches += 1
                work_instruction_ip_acg.id = inventory_ip_acg.id

    val_ip_acgs_match_inventory(matches, inventory)

    logger.debug(
        f"Updated work instruction:\n{json.dumps(asdict(work_instruction), indent=4)}",
        extra={"depth": 1},
    )

    return work_instruction


def format_rules(ip_acg: IP_ACG) -> list[dict]:
    """
    Format rules to IP ACG to AWS request syntax format.
    Sort rules for user friendliness.

    :param ip_acg: IP ACG
    :return: List of rules formatted for AWS request syntax
    """
    logger.debug(f"Format rules for IP ACG [{ip_acg.name}]...", extra={"depth": 2})
    rules = [{"ipRule": rule.ip, "ruleDesc": rule.desc} for rule in ip_acg.rules]
    rules_sorted = sorted(rules, key=lambda rules: rules["ipRule"])
    return rules_sorted


def extend_tags(tags: dict, ip_acg: IP_ACG) -> dict:
    """
    Add tags with dynamic values to 'static' tags.

    :param tags: 'static' tags
    :param ip_acg: IP ACG
    :return: 'static' tags extended with dynamic values
    """
    logger.debug(f"Extend tags for IP ACG [{ip_acg.name}]...", extra={"depth": 2})
    timestamp = datetime.now().isoformat()

    tags["IPACGName"] = ip_acg.name
    tags["Created"] = timestamp

    return tags


def format_tags(tags: dict) -> list[dict]:
    """
    Format tags to AWS request syntax format.

    :param tags: input tags
    :return: List of tags formatted for AWS request syntax
    """
    logger.debug("Format tags...", extra={"depth": 2})
    return [{"Key": k, "Value": v} for k, v in tags.items()]
