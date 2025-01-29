from datetime import datetime
from dataclasses import asdict
import json
import logging

from acgenius.validation.ip_acgs import val_ip_acgs_match_inventory
from acgenius.resources.models import IP_ACG, Inventory, WorkInstruction

logger = logging.getLogger("acgenius")


def match_ip_acgs(inventory: Inventory, work_instruction: WorkInstruction) -> WorkInstruction:
    """
    1 - Get the current IP ACGs from the inventory.
    2 - Get the to-be-updated IP ACGs from the work instruction.
    The settings.yaml is not aware of the ids of
    the IP ACGs specified.

    Find the ids of the IP ACGs of 2 by looking them up in 1.
    Update the input WorkInstruction with these ids.
    """
    logger.debug(
        f"Try to match IP ACGs from work instruction "
        f"with IP ACGs from inventory...", 
        extra={"depth": 5}
    )
    logger.debug(
        "Current inventory:\n"
        f"{json.dumps(asdict(work_instruction), indent=4)}", 
        extra={"depth": 1}
    )
    logger.debug(
        "Current work instruction:\n"
        f"{json.dumps(asdict(work_instruction), indent=4)}", 
        extra={"depth": 1}
    )

    matches = 0
    for work_instruction_ip_acg in work_instruction.ip_acgs:
        for inventory_ip_acg in inventory.ip_acgs:
            if work_instruction_ip_acg.name == inventory_ip_acg.name:
                logger.debug(
                    f"Matching IP ACG names: [{work_instruction_ip_acg.name}] with "
                    f"[{inventory_ip_acg.name}]...",
                    extra={"depth": 2}
                )
                matches += 1
                work_instruction_ip_acg.id = inventory_ip_acg.id

    val_ip_acgs_match_inventory(matches, inventory)
    
    logger.debug(
        "Updated work instruction:\n"
        f"{json.dumps(asdict(work_instruction), indent=4)}", 
        extra={"depth": 1}
    )

    return work_instruction


def format_rules(ip_acg: IP_ACG) -> list[dict]:
    """
    Fit rules in request syntax format.
    Sort rules for user friendliness.
    """
    logger.debug(
        f"Format rules for IP ACG [{ip_acg.name}]...", 
        extra={"depth": 2}
    )
    rules = [
        {"ipRule": rule.ip, "ruleDesc": rule.desc}
        for rule in ip_acg.rules
    ]
    rules_sorted = sorted(
        rules,
        key=lambda rules: rules["ipRule"]
    )
    return rules_sorted


def extend_tags(tags: dict, ip_acg: IP_ACG) -> dict:
    """
    xx
    """
    logger.debug(
        f"Extend tags for IP ACG [{ip_acg.name}]...", 
        extra={"depth": 2}
    )
    timestamp = datetime.now().isoformat()

    tags["IPACGName"] = ip_acg.name    
    tags["Created"] = timestamp

    return tags


def format_tags(tags: dict) -> list[dict]:
    """
    xx
    """
    logger.debug(
        f"Format tags...", 
        extra={"depth": 2}
    )
    return [{"Key": k, "Value": v} for k, v in tags.items()]
