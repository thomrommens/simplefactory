import pandas as pd
from tabulate import tabulate

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

# ---

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
