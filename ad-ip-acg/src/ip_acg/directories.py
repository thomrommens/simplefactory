from dataclasses import asdict
import json
import logging
import pandas as pd
from tabulate import tabulate

from config import workspaces
from exceptions import DirectoryNoneFoundException
from models import Directory


logger = logging.getLogger("ip_acg_logger")


def get_directories():
    """
    # if value in work_instruction for Directory, follow
    # else, get from AWS
    """
    response = workspaces.describe_workspace_directories()

    logger.debug(
        f"Describe_workspace_directories - response: {response}", 
        extra={"depth": 1}
    )

    if response["Directories"]:
        return response["Directories"]
    else:
        raise DirectoryNoneFoundException(
            "No Workspace directories found. "
            "Make sure to have at least 1 directory available with which "
            "an IP ACG can be associated."
        )


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


def report_directories(directories: list[Directory]):
    """
    xx
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
    xx
    """
    logger.info("Current directories (before execution of action):", extra={"depth": 1})  # TODO make logs more dynamic with actions in them

    directories_received = get_directories()
    directories = sel_directories(directories_received)
    directories_as_dict = [asdict(directory) for directory in directories]
    
    logger.debug(
        f"Directories found in AWS:\n{json.dumps(directories_as_dict, indent=4)}", 
        extra={"depth": 1}
    )
    
    report_directories(directories)

    return directories
