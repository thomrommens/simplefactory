from botocore.exceptions import ClientError
import json
import logging
import pandas as pd
from tabulate import tabulate
from typing import Optional

from config import DirectoryNoneFoundException, workspaces
from resources.models import Directory


logger = logging.getLogger("ip_acg_logger")


def get_directories() -> Optional[list[dict]]:
    """
    # if value in work_instruction for Directory, follow
    # else, get from AWS
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/describe_workspace_directories.html
    """
    try:
        response = workspaces.describe_workspace_directories()

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        
        if error_code == "InvalidParameterValuesException":
            error_msg = "Invalid parameter provided when describing directories"
            logger.error(error_msg, extra={"depth": 1})
            raise DirectoryNoneFoundException(error_msg)
            
        else:
            error_msg = "AWS error when describing directories: "
            f"{error_code} - {error_message}"
            logger.error(error_msg, extra={"depth": 1})
            raise DirectoryNoneFoundException(error_msg)

    logger.debug(
        f"describe_workspace_directories - response: {json.dumps(response, indent=4)}", 
        extra={"depth": 1}
    )

    if response["Directories"]:
        return response["Directories"]


def sel_directories(directories_received: dict) -> list[Directory]:
    """
    There might currently be no IP ACG in a directory.
    Then, for that directory, the key `ipGroupIds`
    is not present in the response.
    """
    directories = []

    for directory_received in directories_received:
        directory = Directory(
            id=directory_received.get("DirectoryId"),
            name=directory_received.get("DirectoryName"),
            type=directory_received.get("DirectoryType"),
            state=directory_received.get("State"),
            ip_acgs=directory_received.get("ipGroupIds"),
        )
    directories.append(directory)

    return directories

def report_directories(directories: list[Directory]) -> None:
    """
    Display a formatted table of directory information.

    :param directories: List of Directory objects containing directory details
    :raises None
    """
    data = []
    if directories: 
        for directory in directories:
            row = {
                "id": directory.id,
                "name": directory.name,
                "ip_acgs_associated": directory.ip_acgs,
                "type": directory.type,
                "state": directory.state
            }
            data.append(row)
        df = pd.DataFrame(data)
        df.index += 1
        print(f"{tabulate(df, headers='keys', tablefmt='psql')}\n")
    else:
        print("(No directories found)")


def show_current_directories() -> list[Directory]:
    """
    Get and display the current directories in AWS WorkSpaces.

    Retrieve directories from AWS, process the response into Directory objects,
    and display them in a formatted table.

    :returns: List of Directory objects containing directory information
    :raises: ClientError: If there is an error calling AWS WorkSpaces API
    """
    logger.info("Current directories (before execution of action):", extra={"depth": 1})  
    # TODO make logs more dynamic with actions in them

    directories_received = get_directories()
    directories = sel_directories(directories_received)
    
    report_directories(directories)

    return directories
