def get_workspace_directories():
    # if value in work_instruction for WorkSpaceDirectory, follow
    # else, get from AWS boto3

    response = workspaces.describe_workspace_directories()

    if response["Directories"]:
        return response
    else:
        raise SomeException()

    # collect raw info
    # logger.debug(Raw info)


def select_workspace_directories():
    # Required? Perhaps do anyway
    pass


def select_workspace_directory_info(workspace_directories):
    workspace_directories = []
    for workspace_directory in workspace_directories["Directories"]:
        workspace_directories.append(
            WorkSpaceDirectory(
                id=workspace_directory["DirectoryId"],
                name=workspace_directory["DirectoryName"],
                type=workspace_directory["DirectoryType"]
            )
        )
    return workspace_directories
