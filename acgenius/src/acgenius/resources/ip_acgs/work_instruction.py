from botocore.exceptions import ClientError
import json
import logging
from typing import Optional

from config import (
    IPACGCreateException,
    IpAcgDisassociationException,
    workspaces
)
from resources.models import (
    Directory,
    IP_ACG,
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
        extra={"depth": 5}
    )
    tags_updated = extend_tags(tags, ip_acg)
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
            f"Response of [create_ip_group]: {json.dumps(response, indent=4)}",
            extra={"depth": 1}
        )
        ip_acg.id = response.get("GroupId")
        logger.info(
            f"Created IP ACG [{ip_acg.name}] with id [{ip_acg.id}].",
            extra={"depth": 1}
        )        
        return ip_acg
    
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "InvalidParameterValuesException":
            error_msg = "You provided an invalid parameter."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)

        elif error_code == "ResourceLimitExceededException":
            error_msg = "Limit exceeded when creating IP group."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "ResourceAlreadyExistsException":
            error_msg = f"IP group [{ip_acg.name}] already exists. Skip create."
            logger.warning(error_msg, extra={"depth": 1})

        elif error_code == "ResourceCreationFailedException":
            error_msg = "Failed to create IP group."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "AccessDeniedException":
            error_msg = (
                "Access denied when attempting to create IP group. "
                "Please check your IAM role. "
                "See README.md for more information."
            )
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
                       
        else:
            error_msg = (
                f"AWS error when creating IP group: {error_code} - {error_message}."
            )
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
 

def associate_ip_acg(ip_acgs: list[IP_ACG], directory: Directory) -> None:
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/associate_ip_groups.html
    """
    logger.debug(
        f"Associate IP ACG [{ip_acgs}] to directory [{directory.name}]", 
        extra={"depth": 5}
    )
    try:
        response = workspaces.associate_ip_groups(
            DirectoryId=directory.id,
            GroupIds=[ip_acg.id for ip_acg in ip_acgs]
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "InvalidParameterValuesException":
            error_msg = "You provided an invalid parameter."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
                               
        elif error_code == "ResourceNotFoundException":
            error_msg = "Directory or IP ACG not found."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "ResourceLimitExceededException":
            error_msg = "Limit exceeded when associating IP groups."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "InvalidResourceStateException":
            error_msg = "Invalid resource state when associating IP groups."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "AccessDeniedException":
            error_msg = "Access denied when attempting to associate IP groups."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
       
        elif error_code == "OperationNotSupportedException":
            error_msg = "Operation not supported when associating IP groups."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
            
        else:
            error_msg = (
                f"AWS error when associating IP groups to directory "
                f"[{directory.name} - {directory.id}]: "
                f"{error_code} - {error_message}."
            )
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
    logger.debug(
        f"Response of [associate_ip_acg]: {json.dumps(response, indent=4)}",
        extra={"depth": 1}
    )


def update_rules(ip_acg: IP_ACG) -> None:
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/update_rules_of_ip_group.htmlx
    """
    rules_formatted = format_rules(ip_acg)

    logger.debug(
        f"Update rules for IP ACG [{ip_acg.name}]...", 
        extra={"depth": 5}
    )

    try:
        response = workspaces.update_rules_of_ip_group(
            GroupId=ip_acg.id,
            UserRules=rules_formatted
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "InvalidParameterValuesException":
            error_msg = "You provided an invalid parameter."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "ResourceNotFoundException":
            error_msg = f"IP ACG [{ip_acg.name} - {ip_acg.name}] not found."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "ResourceLimitExceededException":
            error_msg = (
                f"Limit exceeded when updating IP group "
                f"[{ip_acg.name} - {ip_acg.name}]."
            )
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "InvalidResourceStateException":
            error_msg = "Invalid resource state when updating IP group rules."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "AccessDeniedException":
            error_msg = "Access denied when attempting to update IP group rules."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        else:
            error_msg = (
                f"AWS error when updating IP group rules: "
                f"{error_code} - {error_message}."
            )
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
    logger.debug(
        f"Response of [update_rules_of_ip_group]: {json.dumps(response, indent=4)}.", 
        extra={"depth": 1}
    )
    logger.info(
        f"Rules for IP ACG [{ip_acg.name}] and id [{ip_acg.id}] updated.",
        extra={"depth": 1}
    )


def disassociate_ip_acg(ip_acg_ids_to_delete: list, directory: Directory) -> None:
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/disassociate_ip_groups.html
    """
    logger.debug(
        f"Disassociate IP ACG [{ip_acg_ids_to_delete}] "
        f"from directory [{directory.name}]...", 
        extra={"depth": 5}
    )
    try:
        response = workspaces.disassociate_ip_groups(
            DirectoryId=directory.id,
            GroupIds=ip_acg_ids_to_delete
        )
        # TODO: add log
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "InvalidParameterValuesException":
            error_msg = "You provided an invalid parameter."
            logger.error(error_msg, extra={"depth": 1})
            raise IpAcgDisassociationException(error_msg)

        elif error_code == "ResourceNotFoundException":
            error_msg = "IP ACG or Directory not found."
            logger.error(error_msg, extra={"depth": 1})
            raise IpAcgDisassociationException(error_msg)
        
        elif error_code == "InvalidResourceStateException":
            error_msg = "Invalid resource state when associating IP groups."
            logger.error(error_msg, extra={"depth": 1})
            raise IpAcgDisassociationException(error_msg)
        
        elif error_code == "AccessDeniedException":
            error_msg = "Access denied when attempting disassociation."
            logger.error(error_msg, extra={"depth": 1})
            raise IpAcgDisassociationException(error_msg)
        
        elif error_code == "OperationNotSupportedException":
            error_msg = "Operation not supported when disassociating IP groups."
            logger.error(error_msg, extra={"depth": 1})
            raise IpAcgDisassociationException(error_msg)
        
        else:
            error_msg = f"AWS error during disassociation: {error_code} - {error_message}."
            logger.error(error_msg, extra={"depth": 1})
            raise IpAcgDisassociationException(error_msg)
        
    logger.debug(
        f"Response of [disassociate_ip_acg]: {json.dumps(response, indent=4)}...",
        extra={"depth": 1}
    )


def delete_ip_acg(ip_acg_id: str) -> None:
    """
    needs disassociate first.
    Unrelated to settings.yaml
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/delete_ip_group.html
    """
    logger.debug(
        f"Delete IP ACG [{ip_acg_id}]...", 
        extra={"depth": 5}
    )
    try:
        response = workspaces.delete_ip_group(GroupId=ip_acg_id)
        logger.debug(
            f"Response of [delete_ip_acg]: {json.dumps(response, indent=4)}",
            extra={"depth": 1}
        )
        logger.info(f"Deleted IP ACG [{ip_acg_id}].", extra={"depth": 1})

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "InvalidParameterValuesException":
            error_msg = f"Invalid parameter provided when deleting IP ACG [{ip_acg_id}]."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "ResourceNotFoundException":
            error_msg = f"IP ACG [{ip_acg_id}] not found when attempting deletion."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "ResourceAssociatedException":
            error_msg = f"IP ACG [{ip_acg_id}] is still associated with a directory."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "AccessDeniedException":
            error_msg = "Access denied when attempting to delete IP ACG [{ip_acg_id}]"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
            
        else:
            error_msg = (
                f"AWS error when deleting IP ACG [{ip_acg_id}]: "
                f"{error_code} - {error_message}."
            )
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
