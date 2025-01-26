from botocore.exceptions import ClientError
from dataclasses import asdict
import json
import logging
import pandas as pd
from tabulate import tabulate
from textwrap import indent
from typing import Optional

from config import (
    IPACGCreateException, 
    IpAcgDisassociationException,
    workspaces
)
from resources.models import IP_ACG, Directory, Inventory, Rule, WorkInstruction
from resources.rules import format_rules
from resources.tags import update_tags, format_tags
from validation.ip_acgs import val_ip_acgs_match_inventory


logger = logging.getLogger("ip_acg_logger")


def get_inventory_ip_acgs() -> list[IP_ACG]:
    """
    Retrieve IP Access Control Groups from AWS Workspaces.
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/describe_ip_groups.html

    :return: List of IP_ACG objects containing the IP ACGs found in AWS
    """
    try:
        response = workspaces.describe_ip_groups()
        
        logger.debug(
            f"describe_ip_groups - response: {json.dumps(response, indent=4)}", 
            extra={"depth": 1}
        )
        if response["Result"]:
            return response["Result"]
        
        logger.warning("No IP ACGs found in AWS.", extra={"depth": 1})

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "InvalidParameterValuesException":
            error_msg = "Invalid parameter provided when describing IP groups"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "AccessDeniedException":
            error_msg = "Access denied when attempting to describe IP groups"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
            
        else:
            error_msg = f"AWS error when describing IP groups: {error_code} - {error_message}"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)


def sel_inventory_ip_acgs(ip_acgs_inventory: Optional[list[IP_ACG]]) -> list[IP_ACG]:
    """
    Make sure ip_acgs are sorted by name.
    """
    ip_acgs_sel = []

    unsorted_ip_acgs = [
        IP_ACG(            
            id=ip_acg.get("groupId"),
            name=ip_acg.get("groupName"),
            desc=ip_acg.get("groupDesc"),
            rules=[
                Rule(
                    ip=rule.get("ipRule"),
                    desc=rule.get("ruleDesc")
                )
                for rule 
                in ip_acg.get("userRules")
            ]
        )
        for ip_acg in ip_acgs_inventory
    ]
    ip_acgs_sel.extend(sorted(unsorted_ip_acgs, key=lambda x: x.name))

    return ip_acgs_sel


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


def show_inventory_ip_acgs() -> Optional[list[IP_ACG]]:
    """
    Show the current IP Access Control Groups in AWS.

    Retrieve IP ACGs from AWS, process them into internal format, and display a report.
    Log the raw and processed IP ACGs at debug level.

    :returns: List of IP_ACG objects if any exist in AWS, None otherwise
    :raises: Any exceptions from get_ip_acgs() or sel_ip_acgs() are propagated
    """
    # TODO make more generic show_ip_acgs?
    logger.info("Current IP ACGs (before execution of action):", extra={"depth": 1})

    ip_acgs_received = get_inventory_ip_acgs()
    logger.debug(f"ip_acgs_received: {ip_acgs_received}", extra={"depth": 1})

    if ip_acgs_received:
        ip_acgs = sel_inventory_ip_acgs(ip_acgs_received)
        ip_acgs_as_dict = [asdict(ip_acg) for ip_acg in ip_acgs]

        report_ip_acgs(ip_acgs)

        logger.debug(
            f"IP ACGs found in AWS:\n{json.dumps(ip_acgs_as_dict, indent=4)}", 
            extra={"depth": 1}
        )

        return ip_acgs


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
            f"Created IP ACG [{ip_acg.name}] with id [{ip_acg.id}].",  # TODO: add tabulated here too, with other markup?
            extra={"depth": 1}
        )        
        return ip_acg
    
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "InvalidParameterValuesException":
            error_msg = "Invalid parameter provided when creating IP group."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)

        elif error_code == "ResourceLimitExceededException":
            error_msg = "Limit exceeded when creating IP group."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "ResourceAlreadyExistsException":
            error_msg = f"IP group [{ip_acg.name}] already exists. Skip create."
            logger.error(error_msg, extra={"depth": 1})

        elif error_code == "ResourceCreationFailedException":
            error_msg = "Failed to create IP group."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "AccessDeniedException":
            error_msg = "Access denied when attempting to create IP group. Please check your IAM role. See README.md for more information."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
                       
        else:
            error_msg = f"AWS error when creating IP group: {error_code} - {error_message}."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)


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
                logger.debug(
                    f"Matching IP ACG names: {work_instruction_ip_acg.name} with {inventory_ip_acg.name}",
                    extra={"depth": 2}
                )
                matches += 1
                work_instruction_ip_acg.id = inventory_ip_acg.id

    val_ip_acgs_match_inventory(matches, inventory)
    # TODO: specify which IP ACGs could not be matched by name?
    
    logger.debug(
        "Updated work instruction:\n"
        f"{json.dumps(asdict(work_instruction), indent=4)}", 
        extra={"depth": 1}
    )

    return work_instruction
  

def associate_ip_acg(ip_acgs: list[IP_ACG], directory: Directory) -> None:
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/associate_ip_groups.html
    """
    try:
        response = workspaces.associate_ip_groups(
            DirectoryId=directory.id,
            GroupIds=[ip_acg.id for ip_acg in ip_acgs]
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "InvalidParameterValuesException":
            error_msg = "Invalid parameter provided when associating IP groups"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
                               
        elif error_code == "ResourceNotFoundException":
            error_msg = "Resource not found when associating IP groups"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "ResourceLimitExceededException":
            error_msg = "Limit exceeded when associating IP groups"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "InvalidResourceStateException":
            error_msg = "Invalid resource state when associating IP groups"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "AccessDeniedException":
            error_msg = "Access denied when attempting to associate IP groups"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
       
        elif error_code == "OperationNotSupportedException":
            error_msg = "Operation not supported when associating IP groups"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
            
        else:
            error_msg = f"AWS error when associating IP groups: {error_code} - {error_message}"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
    logger.debug(
        f"associate_ip_acg - response: {json.dumps(response, indent=4)}",
        extra={"depth": 1}
    )


def disassociate_ip_acg(ip_acg_ids_to_delete: list, directory: Directory) -> None:
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/disassociate_ip_groups.html
    """
    try:
        response = workspaces.disassociate_ip_groups(
            DirectoryId=directory.id,
            GroupIds=ip_acg_ids_to_delete
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "InvalidParameterValuesException":
            error_msg = "Invalid parameter provided for disassociation."
            logger.error(error_msg, extra={"depth": 1})
            raise IpAcgDisassociationException(error_msg)

        elif error_code == "ResourceNotFoundException":
            error_msg = "IP ACG or Directory not found."
            logger.error(error_msg, extra={"depth": 1})
            raise IpAcgDisassociationException(error_msg)
        
        elif error_code == "InvalidResourceStateException":
            error_msg = "Invalid resource state when associating IP groups"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "AccessDeniedException":
            error_msg = "Access denied when attempting disassociation."
            logger.error(error_msg, extra={"depth": 1})
            raise IpAcgDisassociationException(error_msg)
        
        elif error_code == "OperationNotSupportedException":
            error_msg = "Operation not supported when disassociating IP groups"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        else:
            error_msg = f"AWS error during disassociation: {error_code} - {error_message}"
            logger.error(error_msg, extra={"depth": 1})
            raise IpAcgDisassociationException(error_msg)
        
    logger.debug(
        f"disassociate_ip_acg - response: {json.dumps(response, indent=4)}",
        extra={"depth": 1}
    )


def delete_ip_acg(ip_acg_id: str) -> None:
    """
    needs disassociate first.
    Unrelated to settings.yaml
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/delete_ip_group.html
    """
    try:
        response = workspaces.delete_ip_group(GroupId=ip_acg_id)
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "InvalidParameterValuesException":
            error_msg = "Invalid parameter provided when deleting IP group"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "ResourceNotFoundException":
            error_msg = "IP group not found when attempting deletion"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "ResourceAssociatedException":
            error_msg = "IP group is associated with a directory"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "AccessDeniedException":
            error_msg = "Access denied when attempting to delete IP group"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
            
        else:
            error_msg = f"AWS error when deleting IP group: {error_code} - {error_message}"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)

    logger.debug(
        f"delete_ip_acg - response: {json.dumps(response, indent=4)}",
        extra={"depth": 1}
    )
    logger.info(f"Deleted IP ACG [{ip_acg_id}].", extra={"depth": 1})
