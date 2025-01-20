import pandas as pd
from tabulate import tabulate

from config import workspaces
from exceptions import SomeException
from models import Directory


def get_directories():
    """
    # if value in work_instruction for Directory, follow
    # else, get from AWS
    """
    response = workspaces.describe_workspace_directories()
    # print(f"describe_workspace_directories - response: {response}")

    if response["Directories"]:
        return response["Directories"]
    else:
        raise SomeException()


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
            # TODO "ipGroupIds" not showing in response
            # workspace_directory_name=directory_received.get("WorkspaceDirectoryName"),
            # workspace_directory_desc=directory_received.get("WorkspaceDirectoryDescription"),
            # workspace_type=directory_received.get("WorkspaceType"),
            # error_message=directory_received.get("ErrorMessage"),
            # TODO: definitively remove
        )
    directories.append(directory)

    return directories


def report_directory_info():

    # response = workspaces.describe_workspace_directories()  # TODO dedup
    response = {
        "Directories": [
            {
                "DirectoryId": "string",
                "Alias": "string",
                "DirectoryName": "string",
                "RegistrationCode": "string",
                "SubnetIds": [
                    "string"
                ],
                "DnsIpAddresses": [
                    "string"
                ],
                "CustomerUserName": "string",
                "IamRoleId": "string",
                "DirectoryType": "SIMPLE_AD",
                "WorkspaceSecurityGroupId": "string",
                "State": "REGISTERED",
                "WorkspaceCreationProperties": {
                    "EnableWorkDocs": True,
                    "EnableInternetAccess": True,
                    "DefaultOu": "string",
                    "CustomSecurityGroupId": "string",
                    "UserEnabledAsLocalAdministrator": True,
                    "EnableMaintenanceMode": True,
                    "InstanceIamRoleArn": "string"
                },
                "ipGroupIds": [
                    "string"
                ],
                "WorkspaceAccessProperties": {
                    "DeviceTypeWindows": "ALLOW",
                    "DeviceTypeOsx": "ALLOW",
                    "DeviceTypeWeb": "ALLOW",
                    "DeviceTypeIos": "ALLOW",
                    "DeviceTypeAndroid": "ALLOW",
                    "DeviceTypeChromeOs": "ALLOW",
                    "DeviceTypeZeroClient": "ALLOW",
                    "DeviceTypeLinux": "ALLOW"
                },
                "Tenancy": "DEDICATED",
                "SelfservicePermissions": {
                    "RestartWorkspace": "ENABLED",
                    "IncreaseVolumeSize": "ENABLED",
                    "ChangeComputeType": "ENABLED",
                    "SwitchRunningMode": "ENABLED",
                    "RebuildWorkspace": "ENABLED"
                },
                "SamlProperties": {
                    "Status": "DISABLED",
                    "UserAccessUrl": "string",
                    "RelayStateParameterName": "string"
                },
                "CertificateBasedAuthProperties": {
                    "Status": "DISABLED",
                    "CertificateAuthorityArn": "string"
                },
                "MicrosoftEntraConfig": {
                    "TenantId": "string",
                    "ApplicationConfigSecretArn": "string"
                },
                "WorkspaceDirectoryName": "string",
                "WorkspaceDirectoryDescription": "string",
                "UserIdentityType": "CUSTOMER_MANAGED",
                "WorkspaceType": "PERSONAL",
                "IDCConfig": {
                    "InstanceArn": "string",
                    "ApplicationArn": "string"
                },
                "ActiveDirectoryConfig": {
                    "DomainName": "string",
                    "ServiceAccountSecretArn": "string"
                },
                "StreamingProperties": {
                    "StreamingExperiencePreferredProtocol": "TCP",
                    "UserSettings": [
                        {
                            "Action": "CLIPBOARD_COPY_FROM_LOCAL_DEVICE",
                            "Permission": "ENABLED",
                            "MaximumLength": 123
                        }
                    ],
                    "StorageConnectors": [
                        {
                            "ConnectorType": "HOME_FOLDER",
                            "Status": "ENABLED"
                        }
                    ],
                    "GlobalAccelerator": {
                        "Mode": "ENABLED_AUTO",
                        "PreferredProtocol": "TCP"
                    }
                },
                "ErrorMessage": "string"
            }
        ],
        "NextToken": "string"
    }

    data = []
    for directory in response["Directories"]:
        row = {
            "DirectoryId": directory.get("DirectoryId"),
            "Alias": directory.get("Alias"),
            "DirectoryName": directory.get("DirectoryName"),
            "SubnetIds": directory.get("SubnetIds"),
            "DirectoryType": directory.get("DirectoryType"),
            "State": directory.get("State"),
            "ipGroupIds": directory.get("ipGroupIds"),
            "WorkspaceDirectoryName": directory.get("WorkspaceDirectoryName"),
            "WorkspaceDirectoryDescription": directory.get("WorkspaceDirectoryDescription"),
            "WorkspaceType": directory.get("WorkspaceType"),
            "ErrorMessage": directory.get("ErrorMessage")
        }
        data.append(row)

    df = pd.DataFrame(data)
    print(tabulate(df, headers="keys", tablefmt="psql"))
