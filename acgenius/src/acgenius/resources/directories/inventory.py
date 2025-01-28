from botocore.exceptions import ClientError
import json
import logging
from typing import Optional

from config import EXC_INVALID_PARAM, workspaces
from resources.models import Directory
from resources.utils import create_report
from routing.errors import process_error


logger = logging.getLogger("acgenius")


def get_directories() -> Optional[list[dict]]:
    """
    # if value in work_instruction for Directory, follow
    # else, get from AWS
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/describe_workspace_directories.html
    """
    logger.debug(f"Call [describe_workspace_directories]...", extra={"depth": 2})
    
    try:
        response = workspaces.describe_workspace_directories()
        logger.debug(
            "Response of [describe_workspace_directories]: "
            f"{json.dumps(response, indent=4)}", 
            extra={"depth": 2}
        )
        if response["Directories"]:
            return response["Directories"]

    except ClientError as e:
        msg_generic = "Could not get directories from AWS."
        code = e.response["Error"]["Code"]
        map = {
            "InvalidParameterValuesException": {
                "msg": f"{msg_generic} {EXC_INVALID_PARAM}",
                "crash": True
            }
        }
        process_error(map, code, e)


def sel_directories(directories_inventory: dict) -> list[Directory]:
    """
    There might currently be no IP ACG in a directory.
    Then, for that directory, the key `ipGroupIds`
    is not present in the response.
    """
    logger.debug(
        f"Select relevant directory info from retrieved directories...", 
        extra={"depth": 2}
    )
    
    directories = []

    for directory in directories_inventory:
        directory = Directory(
            id=directory.get("DirectoryId"),
            name=directory.get("DirectoryName"),
            type=directory.get("DirectoryType"),
            state=directory.get("State"),
            ip_acgs=directory.get("ipGroupIds"),
        )
    directories.append(directory)

    return directories


def show_directories() -> list[Directory]:
    """
    Get and display the current directories in AWS WorkSpaces.

    Retrieve directories from AWS, process the response into Directory objects,
    and display them in a formatted table.

    :returns: List of Directory objects containing directory information
    :raises: ClientError: If there is an error calling AWS WorkSpaces API
    """
    logger.info("Current directories (before execution of action):", extra={"depth": 1})  

    directories_inventory = get_directories()
    directories_inventory_sel = sel_directories(directories_inventory)
    
    create_report(subject=directories_inventory_sel, origin="inventory")

    return directories_inventory_sel
