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
            logger.warning(error_msg, extra={"depth": 1})

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
            error_msg = "Invalid parameter provided when associating IP groups."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
                               
        elif error_code == "ResourceNotFoundException":
            error_msg = "Resource not found when associating IP groups."
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
            error_msg = f"AWS error when associating IP groups: {error_code} - {error_message}."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
    logger.debug(
        f"associate_ip_acg - response: {json.dumps(response, indent=4)}",
        extra={"depth": 1}
    )


def update_rules(ip_acg: IP_ACG) -> None:
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/update_rules_of_ip_group.htmlx
    """
    rules_formatted = format_rules(ip_acg)

    try:
        response = workspaces.update_rules_of_ip_group(
            GroupId=ip_acg.id,
            UserRules=rules_formatted
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "InvalidParameterValuesException":
            error_msg = "Invalid parameter provided when updating IP group rules."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "ResourceNotFoundException":
            error_msg = "Resource not found when updating IP group rules."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "ResourceLimitExceededException":
            error_msg = "Limit exceeded when updating IP group."
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
            error_msg = f"AWS error when updating IP group rules: {error_code} - {error_message}."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
    logger.debug(
        f"update_rules_of_ip_group - response: {json.dumps(response, indent=4)}.", 
        extra={"depth": 1}
    )
    logger.info(
        f"Rules for IP ACG [{ip_acg.name}] and id [{ip_acg.id}] updated.",  # TODO: display tabulated with different markup?
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
        # TODO: add log
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
        logger.debug(
            f"delete_ip_acg - response: {json.dumps(response, indent=4)}",
            extra={"depth": 1}
        )
        logger.info(f"Deleted IP ACG [{ip_acg_id}].", extra={"depth": 1})

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "InvalidParameterValuesException":
            error_msg = "Invalid parameter provided when deleting IP group."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "ResourceNotFoundException":
            error_msg = "IP group not found when attempting deletion."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "ResourceAssociatedException":
            error_msg = "IP group is associated with a directory."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
        elif error_code == "AccessDeniedException":
            error_msg = "Access denied when attempting to delete IP group."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
            
        else:
            error_msg = f"AWS error when deleting IP group: {error_code} - {error_message}."
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)

