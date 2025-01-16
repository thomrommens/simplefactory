from config import workspaces
from exceptions import SomeException
from models import Directory


def get_directories():
    # if value in work_instruction for Directory, follow
    # else, get from AWS boto3

    response = workspaces.describe_directories()

    if response["Directories"]:
        return response
    else:
        raise SomeException()

    # collect raw info
    # logger.debug(Raw info)


def select_directories():
    # Required? Perhaps do anyway
    pass


def select_directory_info(directories):
    directories = []
    for directory in directories["Directories"]:
        directories.append(
            Directory(
                id=directory["DirectoryId"],
                name=directory["DirectoryName"],
                type=directory["DirectoryType"]
            )
        )
    return directories
