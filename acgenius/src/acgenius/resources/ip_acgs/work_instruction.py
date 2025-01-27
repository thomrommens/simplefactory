from botocore.exceptions import ClientError, ParamValidationError

import json
import logging
from typing import Optional

from config import UnexpectedException, workspaces

from resources.models import (
    Directory,
    IP_ACG
)
from resources.ip_acgs.utils import (
    format_rules,
    format_tags,
    extend_tags
)


logger = logging.getLogger("acgenius")


def create_ip_acg(ip_acg: IP_ACG, tags: dict) -> Optional[str]:
    """
    Skip (not error out) at trying to create existing
    :return: updated IP ACG
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/create_ip_group.html
    """
    logger.debug(
        f"Create IP ACG [{ip_acg.name}]...", 
        extra={"depth": 1}
    )
    tags_extended = extend_tags(tags, ip_acg)
    tags_formatted = format_tags(tags_extended)

    rules_formatted = format_rules(ip_acg)
    
    try:
        response = workspaces.create_ip_group(
            GroupName=ip_acg.name,
            GroupDesc=ip_acg.desc,
            UserRules=rules_formatted,
            Tags=tags_formatted
        )
        logger.debug(
            f"Response of [create_ip_group]: {json.dumps(response, indent=4)}",
            extra={"depth": 2}
        )
        ip_acg.id = response.get("GroupId")
        logger.info(
            f"Created IP ACG [{ip_acg.name}] with id [{ip_acg.id}].",
            extra={"depth": 2}
        )        
        return ip_acg

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        logger.error(
            f"AWS error at [create_ip_group]: {error_code} - {error_message}", 
            extra={"depth": 2}
        )
 

def associate_ip_acg(ip_acgs: list[IP_ACG], directory: Directory) -> None:
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/associate_ip_groups.html
    """
    logger.debug(
        f"Associate IP ACG [{ip_acgs}] to directory [{directory.name}]", 
        extra={"depth": 1}
    )

    try:
        response = workspaces.associate_ip_groups(
            DirectoryId=directory.id,
            GroupIds=[ip_acg.id for ip_acg in ip_acgs]
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        logger.error(
            f"AWS error at [associate_ip_groups]: {error_code} - {error_message}", 
            extra={"depth": 1}
        )  
               
    logger.debug(
        f"Response of [associate_ip_acg]: {json.dumps(response, indent=4)}",
        extra={"depth": 2}
    )


def update_rules(ip_acg: IP_ACG, tags: dict) -> None:
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/update_rules_of_ip_group.htmlx
    """
    tags_extended = extend_tags(tags, ip_acg)
    tags_formatted = format_tags(tags_extended)

    rules_formatted = format_rules(ip_acg)

    logger.debug(
        f"Update rules for IP ACG [{ip_acg.name}]...", 
        extra={"depth": 1}
    )

    try:
        response = workspaces.update_rules_of_ip_group(
            GroupId=ip_acg.id,
            UserRules=rules_formatted
        )
    
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "ValidationException": # TODO: test
            logger.error (
                f"AWS error at [update_rules_of_ip_group]: "
                f"{error_code} - {error_message}. ",
                extra={"depth": 1}
            )
            raise UnexpectedException(
                f"Validation error: {e}. "
                "Are you sure the IP ACGs from settings.yaml "
                "already exist in in AWS?", 
                extra={"depth": 1}
            )
        
    logger.debug(
        f"Response of [update_rules_of_ip_group]: {json.dumps(response, indent=4)}.", 
        extra={"depth": 2}
    )
    logger.info(
        f"Rules for IP ACG with name[{ip_acg.name}] and id [{ip_acg.id}] updated.",
        extra={"depth": 1}
    )


def disassociate_ip_acg(ip_acg_ids_to_delete: list, directory: Directory) -> None:
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/disassociate_ip_groups.html
    """
    logger.debug(
        f"Disassociate IP ACG [{ip_acg_ids_to_delete}] "
        f"from directory [{directory.name}]...", 
        extra={"depth": 2}
    )
    try:
        response = workspaces.disassociate_ip_groups(
            DirectoryId=directory.id,
            GroupIds=ip_acg_ids_to_delete
        )

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "ValidationException":

            logger.error(f"Validation error when calling DeleteIpGroup: {e}", extra={"depth": 1})
            raise UnexpectedException(
                f"Validation error: {e}. "
                "Are you sure you specified an IP ACG id (e.g., 'wsipg-ab1234567')?"
            )
        
        else:
            logger.error(
                f"AWS error at [disassociate_ip_groups]: {error_code} - {error_message}", 
                extra={"depth": 1}
            )

    logger.debug(
        f"Response of [disassociate_ip_acg]: {json.dumps(response, indent=4)}...",
        extra={"depth": 2}
    )


def delete_ip_acg(ip_acg_id: str) -> None:
    """
    needs disassociate first.
    Unrelated to settings.yaml
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/delete_ip_group.html
    """
    logger.debug(
        f"Delete IP ACG [{ip_acg_id}]...", 
        extra={"depth": 1}
    )
    try:
        response = workspaces.delete_ip_group(GroupId=ip_acg_id)
        logger.debug(
            f"Response of [delete_ip_acg]: {json.dumps(response, indent=4)}",
            extra={"depth": 2}
        )
        logger.info(f"Deleted IP ACG [{ip_acg_id}].", extra={"depth": 1})

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "ResourceNotFoundException":
            logger.error(
                f"IP ACG [{ip_acg_id}] not found in AWS. "
                f"Are you sure [{ip_acg_id}] actually exists in AWS?",
                extra={"depth": 1}
            )
        else:
            logger.error(
                "AWS error at [delete_ip_acg]: "
                f"{error_code} - {error_message}", 
                extra={"depth": 1}
            )