from dataclasses import asdict
from datetime import datetime
import json
import logging
from textwrap import indent
from typing import Optional
from botocore.exceptions import ClientError
import pandas as pd

from tabulate import tabulate
from config import workspaces
from exceptions import IPACGIdMatchException
from models import IP_ACG, Directory, Inventory, Rule, WorkInstruction

# TODO: format file to logical order of functions


logger = logging.getLogger("ip_acg_logger")


def get_ip_acgs() -> list[IP_ACG]:
    """
    xx
    """
    response = workspaces.describe_ip_groups()
    logger.debug(
        f"describe_ip_groups - response: {json.dumps(response, indent=4)}",
        extra={"depth": 1}
    )

    if response["Result"]:
        return response["Result"]
    else:
        logger.debug(
            f"No IP ACGs found in AWS. Skip describing.",
            extra={"depth": 1}
    )  # TODO: not displayed - inspect specific response at none


def sel_ip_acgs(ip_acgs_received: Optional[dict]) -> list[IP_ACG]:
    """
    xx
    """
    ip_acgs = []

    for ip_acg_received in ip_acgs_received:
        ip_acg = IP_ACG(            
            id=ip_acg_received.get("groupId"),
            name=ip_acg_received.get("groupName"),
            desc=ip_acg_received.get("groupDesc"),
            rules=[
                Rule(
                    ip=rule.get("ipRule"),
                    desc=rule.get("ruleDesc")
                )
                for rule 
                in ip_acg_received.get("userRules")
            ]
        )
        ip_acgs.append(ip_acg)

    return ip_acgs


def report_ip_acgs(ip_acgs: list[IP_ACG]):
    """
    xx
    """
    
    if ip_acgs:
        i = 0
        for ip_acg in ip_acgs:
            
            # TODO: abstract
            # IP ACG
            i += 1
            print(f"■ IP ACG {i}")
            row = {
                "id": ip_acg.id,
                "name": ip_acg.name,
                "description": ip_acg.desc,
            }
            data = [(row)]
            df = pd.DataFrame(data)
            df.index += i
            print(f"{tabulate(df, headers='keys', tablefmt='psql')}")

            # RULES          
            print("\\")    
            rules_formatted = format_rules(ip_acg)
            rules_table = [["rule", "description"]] + [[item["ipRule"], item["ruleDesc"]] for item in rules_formatted]

            rules_table_str = tabulate(rules_table, headers="firstrow", tablefmt="psql")
            rules_table_indented = indent(rules_table_str, " " * 2)
            print(rules_table_indented)
            print("\n")
            
    else:
        print("(No IP ACGs found)")


def show_current_ip_acgs() -> Optional[list[IP_ACG]]:
    """
    xx
    """
    logger.info("Current IP ACGs (before execution of action):", extra={"depth": 1})

    ip_acgs_received = get_ip_acgs()
    if ip_acgs_received:
        ip_acgs = sel_ip_acgs(ip_acgs_received)
        ip_acgs_as_dict = [asdict(ip_acg) for ip_acg in ip_acgs]

        report_ip_acgs(ip_acgs)

        logger.debug(
            f"IP ACGs found in AWS:\n{json.dumps(ip_acgs_as_dict, indent=4)}", 
            extra={"depth": 1}
        )

        return ip_acgs

# ----------------------------------------------------------------------------


def format_rules(ip_acg: IP_ACG):
    """
    Fit rules in request syntax format.
    Sort rules for user friendliness.
    """
    rules = [
        {"ipRule": rule.ip, "ruleDesc": rule.desc}
        for rule in ip_acg.rules
    ]
    rules_sorted = sorted(
        rules,
        key=lambda rules: rules["ipRule"]
    )
    return rules_sorted


def update_tags(tags: dict, ip_acg: IP_ACG):
    """
    Replace placeholders
    """
    timestamp = datetime.now().isoformat()

    tags["IPACGName"] = ip_acg.name
    tags["Created"] = timestamp
    tags["RulesLastApplied"] = timestamp  #TODO: make sure to update as only tag at update route

    return tags


def format_tags(tags: dict):
    """
    xx
    """
    return [{"Key": k, "Value": v} for k, v in tags.items()]


def create_ip_acg(ip_acg: IP_ACG, tags: dict) -> Optional[str]:
    """
    Skip (not error out) at trying to create existing
    :return: updated IP ACG
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/create_ip_group.html
    """
    tags_updated = update_tags(tags, ip_acg)
    tags_formatted = format_tags(tags_updated)

    rules_formatted = format_rules(ip_acg)
    
    try:
        response = workspaces.create_ip_group(
            GroupName=ip_acg.name,
            GroupDesc=ip_acg.desc,
            UserRules=rules_formatted,
            Tags=tags_formatted
        )
        logger.debug(
        f"create_ip_group - response: {json.dumps(response, indent=4)}",
        extra={"depth": 1}
        )

        ip_acg.id = response.get("GroupId")

        logger.info(
            f"Created IP ACG [{ip_acg.name}] with id: [{ip_acg.id}]", 
            extra={"depth": 1}
        )
        
        return ip_acg
    
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceAlreadyExistsException":
            logger.info(
                f"IP ACG [{ip_acg.name}] already exists. Skip creation.", 
                extra={"depth": 1}
            )
        else:
            logger.info(f"Client error: {e}", extra={"depth": 1})


def validate_match_inventory(matches: int, inventory: Inventory) -> bool:
    """
    Validate if all IP ACGs from the inventory could be matched by name,
    with all IP ACGs from the actual situation in AWS.
    """
    if not matches == len(inventory.ip_acgs):
        raise IPACGIdMatchException("xx")


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
                matches =+ 1
                work_instruction_ip_acg.id = inventory_ip_acg.id

    validate_match_inventory(matches, inventory)
    # TODO: specify which IP ACGs could not be matched by name?
    
    logger.debug(
        "Updated work instruction:\n"
        f"{json.dumps(asdict(work_instruction), indent=4)}", 
        extra={"depth": 1}
    )

    return work_instruction


def update_rules(ip_acg: IP_ACG):
    """
    xx
    """
    rules_formatted = format_rules(ip_acg)

    response = workspaces.update_rules_of_ip_group(
        GroupId=ip_acg.id,
        UserRules=rules_formatted
    )
    logger.debug(
        f"update_rules_of_ip_group - response: {json.dumps(response, indent=4)}", 
        extra={"depth": 1}
    )
    logger.info(
        f"Rules for IP ACG [{ip_acg.name}]updated.", extra={"depth": 1}
    )
    

def associate_ip_acg(ip_acgs: list[IP_ACG], directory: Directory):
    """
    xx
    """
    response = workspaces.associate_ip_groups(
        DirectoryId=directory.id,
        GroupIds=[ip_acg.id for ip_acg in ip_acgs]
    )
    logger.debug(
        f"associate_ip_acg - response: {json.dumps(response, indent=4)}",
        extra={"depth": 1}
    )


def disassociate_ip_acg(delete_list: list, directory: Directory):
    """
    xx
    """
    response = workspaces.disassociate_ip_groups(
        DirectoryId=directory.id,
        GroupIds=delete_list
    )
    logger.debug(
        f"disassociate_ip_acg - response: {json.dumps(response, indent=4)}",
        extra={"depth": 1}
    )


def delete_ip_acg(ip_acg_id: str):
    """
    needs disassociate first.
    Unrelated to settings.yaml
    """
    try:
        response = workspaces.delete_ip_group(GroupId=ip_acg_id)

        logger.debug(
            f"delete_ip_acg - response: {json.dumps(response, indent=4)}",
            extra={"depth": 1}
        )
        logger.info(f"Deleted IP ACG [{ip_acg_id}].", extra={"depth": 1})

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logger.info(
                f"IP ACG [{ip_acg_id}] not found. Skip deletion.", 
                extra={"depth": 1}
            )
        else:
            logger.info(f"Client error: {e}", extra={"depth": 1})
