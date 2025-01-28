from botocore.exceptions import ClientError, ParamValidationError

import json
import logging
from typing import Optional

from routing.errors import process_error

from config import (
    EXC_ACCESS_DENIED, 
    EXC_INVALID_PARAM, 
    EXC_OPERATION_NOT_SUPPORTED, 
    EXC_RESOURCE_LIMIT, 
    EXC_RESOURCE_NOT_FOUND, 
    EXC_RESOURCE_STATE, 
    STD_INSTR_README, 
    workspaces
)

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
            f"☑ Created IP ACG [{ip_acg.name}] with id [{ip_acg.id}].",
            extra={"depth": 2}
        )        
        return ip_acg
    
    except ParamValidationError as e:
        msg_generic = f"Could not create IP ACG [{ip_acg.name}] in AWS."
        code = "ParamValidationError"
        map = {
            "ParamValidationError": {
                "msg": f"{msg_generic} {EXC_INVALID_PARAM}",
                "crash": True
            }
        }
        process_error(map, code, e)

    except ClientError as e:
        msg_generic = f"Could not create IP ACG [{ip_acg.name}] in AWS."
        code = e.response["Error"]["Code"]
        map = {
            "InvalidParameterValuesException": {
                "msg": f"{msg_generic} {EXC_INVALID_PARAM}",
                "crash": True
            },
            "ResourceLimitExceededException": {
                "msg": f"{msg_generic} {EXC_RESOURCE_LIMIT}",
                "crash": True
            },
            "ResourceAlreadyExistsException": {
                "msg": f"{msg_generic} It seems the IP ACG already exists. ",
                "crash": False
            },
            "ResourceCreationFailedException": {
                "msg": f"{msg_generic} Something went wrong internally at AWS. "
                    "Please try again later.",
                "crash": True
            },
            "AccessDeniedException": {
                "msg": f"{msg_generic} {EXC_ACCESS_DENIED} {STD_INSTR_README}",
                "crash": True
            }
        }
        process_error(map, code, e)
 

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
        logger.debug(
            f"Response of [associate_ip_acg]: {json.dumps(response, indent=4)}",
            extra={"depth": 2}
        )
        logger.info(
            f"☑ Associated IP ACGs with directory [{directory.id} - {directory.name}].",
            extra={"depth": 2}
        )  

    except ParamValidationError as e:
        msg_generic = f"Could not associate IP ACGs with directory."
        code = "ParamValidationError"
        map = {
            "ParamValidationError": {
                "msg": f"{msg_generic} {EXC_INVALID_PARAM}",
                "crash": True
            }
        }
        process_error(map, code, e)
    
    except ClientError as e:
        msg_generic = (
            f"Could not associate IP ACGs with directory [{directory.id}] in AWS."
        )
        code = e.response["Error"]["Code"]
        map = {
            "InvalidParameterValuesException": {
                "msg": f"{msg_generic} {EXC_INVALID_PARAM}",
                "crash": True
            },
            "ResourceNotFoundException": {
                "msg": f"{msg_generic} {EXC_RESOURCE_NOT_FOUND} {STD_INSTR_README}",
                "crash": True
            },
            "ResourceLimitExceededException": {
                "msg": f"{msg_generic} {EXC_RESOURCE_LIMIT}",
                "crash": True
            },
            "InvalidResourceStateException": {
                "msg": f"{msg_generic} {EXC_RESOURCE_STATE}",
                "crash": True
            },
            "AccessDeniedException": {
                "msg": f"{msg_generic} {EXC_ACCESS_DENIED} {STD_INSTR_README}",
                "crash": True
            },
            "OperationNotSupportedException": {
                "msg": f"{msg_generic} {EXC_OPERATION_NOT_SUPPORTED}",
                "crash": True
            },
        }
        process_error(map, code, e)


def update_rules(ip_acg: IP_ACG) -> None:
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/update_rules_of_ip_group.html
    """
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
        logger.debug(
        f"Response of [update_rules_of_ip_group]: {json.dumps(response, indent=4)}.", 
        extra={"depth": 2}
        )
        logger.info(
            f"☑ Updated rules for IP ACG [{ip_acg.id} - {ip_acg.name}].",
            extra={"depth": 1}
        )

    except ClientError as e:
        msg_generic = (
            f"Could not update rules of IP ACG [{ip_acg.name}] "
            "and id [{ip_acg.id}] in AWS."
        )
        code = e.response["Error"]["Code"]
        map = {
            "InvalidParameterValuesException": {
                "msg": f"{msg_generic} {EXC_INVALID_PARAM}",
                "crash": True
            },
            "ResourceNotFoundException": {
                "msg": f"{msg_generic} Could not find the IP ACG. Are you sure it exists?",
                "crash": True
            },
            "ResourceLimitExceededException": {
                "msg": f"{msg_generic} {EXC_RESOURCE_LIMIT}",
                "crash": True
            },
            "InvalidResourceStateException": {
                "msg": (
                    f"{msg_generic} The IP ACG is in an unexpected state. "
                    "Please inspect it in the AWS console. "
                ),
                "crash": True
            },
            "AccessDeniedException": {
                "msg": f"{msg_generic} {EXC_ACCESS_DENIED} {STD_INSTR_README}",
                "crash": True
            }
        }
        process_error(map, code, e)


def disassociate_ip_acg(ip_acg_ids_to_delete: list, directory: Directory) -> None:
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/disassociate_ip_groups.html
    """
    logger.debug(
        f"Disassociate IP ACGs [{ip_acg_ids_to_delete}] "
        f"from directory [{directory.id} - {directory.name}]...", 
        extra={"depth": 2}
    )
    try:
        response = workspaces.disassociate_ip_groups(
            DirectoryId=directory.id,
            GroupIds=ip_acg_ids_to_delete
        )
        logger.debug(
            "Response of [disassociate_ip_acg]: "
            f"{json.dumps(response, indent=4)}...",
            extra={"depth": 2}
        )
        logger.info(
            f"☑ Disassociated IP ACGs {ip_acg_ids_to_delete} "
            f"from directory [{directory.id} - {directory.name}].",
            extra={"depth": 1}
        )  

    except ClientError as e:
        msg_generic = (
            f"Could not disassociate all IP ACGs "
            f"from directory [{directory.id} - {directory.name}] in AWS."
        )
        code = e.response["Error"]["Code"]
        map = {
            "ValidationException": {  # TODO: check if this error is caught
                "msg": (
                    f"{msg_generic} Are you sure you specified "
                    "a valid IP ACG id? "
                    "And does the IP ACG still exist? "
                    "Please check the status in "
                    f"a status run of the app. {STD_INSTR_README}"
                ),
                "crash": True
            },
            "InvalidParameterValuesException": {
                "msg": f"{msg_generic} {EXC_INVALID_PARAM}",
                "crash": True
            },
            "ResourceNotFoundException": {
                "msg": f"{msg_generic} {EXC_RESOURCE_NOT_FOUND}",
                "crash": True
            },
            "InvalidResourceStateException": {
                "msg": f"{msg_generic} {EXC_RESOURCE_STATE}",
                "crash": True
            },
            "AccessDeniedException": {
                "msg": f"{msg_generic} {EXC_ACCESS_DENIED} {STD_INSTR_README}",
                "crash": True
            },
            "OperationNotSupportedException": {
                "msg": f"{msg_generic} {EXC_OPERATION_NOT_SUPPORTED}",
                "crash": True
            }
        }
        process_error(map, code, e)


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
        logger.info(f"☑ Deleted IP ACG [{ip_acg_id}].", extra={"depth": 1})

    except ClientError as e:
        msg_generic = f"Could not delete IP ACG [{ip_acg_id}] in AWS."
        code = e.response["Error"]["Code"]
        map = {
            "InvalidParameterValuesException": {
                "msg": f"{msg_generic} {EXC_INVALID_PARAM}",
                "crash": True
            },
            "ResourceNotFoundException": {
                "msg": f"{msg_generic} Could not find IP ACG in AWS. "
                    "Double check if it is created, and if not, "
                    f"do a 'create' run of this app. {STD_INSTR_README}",
                "crash": True
            },
            "ResourceAssociatedException": {
                "msg": (
                    f"{msg_generic} The IP ACG is still associated " 
                    "with a directory in AWS. Please retry a 'delete' run first. " 
                    "Otherwise, please inspect in the AWS console."
                ),
                "crash": True
            },
            "AccessDeniedException": {
                "msg": f"{msg_generic} {EXC_ACCESS_DENIED} {STD_INSTR_README}",
                "crash": True
            }
        }
        process_error(map, code, e)
