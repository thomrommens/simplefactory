from config import workspaces
from models import IP_ACG, Directory


def describe() -> list[IP_ACG]:
    response = workspaces.describe_ip_groups()
    ip_acgs = []
    for item in response.get("Result"):
        ip_acg = IP_ACG(            
            id=item.get("groupId"),
            name=item.get("groupName"),
            desc=""
        )
    return ip_acgs


def create(ip_acg: IP_ACG, tags: dict) -> str:
    response = workspaces.create_ip_group(
        GroupName=ip_acg.id,
        GroupDesc=ip_acg.desc,
        UserRules=ip_acg.rules,
        Tags=[{"Key": k, "Value": v} for k, v in tags.items()]
    )    
    ip_acg_id = response.get('GroupId')

    return ip_acg_id


def update_rules(ip_acg: IP_ACG):
    response = workspaces.update_rules_of_ip_group(
        GroupId=ip_acg.id,
        UserRules=ip_acg.rules
    )


def associate(ip_acgs: list[IP_ACG], directory: Directory):
    response = workspaces.associate_ip_groups(
        DirectoryId=directory.id,
        GroupIds=ip_acgs.id
    )


def disassociate(ip_acgs: list[IP_ACG], directory: Directory):
    response = workspaces.disassociate_ip_groups(
        DirectoryId=directory.id,
        GroupIds=ip_acgs.id  # TODO: for comprehension
    )


def delete(ip_acg: IP_ACG):
    """
    default: deletes all IP ACGs from directory!
    """
    # check with a describe if any exists
    # TODO: check single/multi delete
    workspaces.delete_ip_group(GroupId=ip_acg.id)
