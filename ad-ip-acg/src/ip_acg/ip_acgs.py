from config import workspaces
from exceptions import SomeException
from models import IP_ACG, Directory, Rule


def get_ip_acgs() -> list[IP_ACG]:
    """
    xx
    """
    response = workspaces.describe_ip_groups()
    # print(f"describe_ip_groups - response: {response}")

    if response["Result"]:
        return response["Result"]
    else:
        raise SomeException()


def sel_ip_acgs(ip_acgs_received: dict) -> list[IP_ACG]:
    """
    xx
    """
    ip_acgs = []

    for ip_acg_received in ip_acgs_received:
        ip_acg = IP_ACG(            
            id=ip_acg_received.get("groupId"),
            name=ip_acg_received.get("groupName"),
            desc=ip_acg_received.get("groupDesc"),
            rules=[
                Rule(
                    ip=rule.get("ipRule"),
                    desc=rule.get("ruleDesc")
                )
                for rule 
                in ip_acg_received.get("userRules")
            ]
        )
    ip_acgs.append(ip_acg)

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

    #  target_rule = {
    #     "ipRule": "key",
    #     "ruleDesc": "value__desc_from_rule_in_yaml"
    # }

    # target_rules = []

    # target_rules_sorted = sorted(
    #     target_rules,
    #     key=lambda target_rules: target_rules["ipRule"]
    # )


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
