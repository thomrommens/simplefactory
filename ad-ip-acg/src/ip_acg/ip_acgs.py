import logging

import pandas as pd
from tabulate import tabulate
from config import workspaces
from exceptions import IPACGNoneFoundException
from models import IP_ACG, Directory, Rule


logger = logging.getLogger("ip_acg_logger")


def get_ip_acgs() -> list[IP_ACG]:
    """
    xx
    """
    response = workspaces.describe_ip_groups()
    logger.debug(
        f"describe_ip_groups - response: {response}", 
        extra={"depth": 1}
    )

    if response["Result"]:
        return response["Result"]
    else:
        raise IPACGNoneFoundException(
            "No Workspace directories found. "
            "Make sure to have at least 1 directory available with which "
            "an IP ACG can be associated."
        )


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


def show_ip_acgs(ip_acgs: list[IP_ACG]):
    
    if ip_acgs:
        i = 0
        for ip_acg in ip_acgs:
            i += 1
            row = {
                "id": ip_acg.id,
                "name": ip_acg.name,
                "description": ip_acg.desc,
            }
            data = [(row)]
            df = pd.DataFrame(data)
            df.index += i
            df = df.rename_axis("IP ACG #", axis="index")
            print(f"{tabulate(df, headers='keys', tablefmt='fancy_grid')}")  # TODO deal with wide strings with rules
            print(f"Rules of [IP ACG #{i} - {ip_acg.name}]:")
            print("-------")
            for rule in ip_acg.rules:
                print(f"- {rule.ip} - {rule.desc}")
            print("-------")
            print("\n")
            # TODO: prettify, also print with tabulate?

            # TODO: plans with tablefmt=psql; realized styles with fancy_grid
    else:
        print("(No IP ACGs found)")



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
