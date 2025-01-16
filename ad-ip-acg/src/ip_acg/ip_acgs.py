def describe():
    response = workspaces.describe_ip_groups()
    ip_acgs = []
    for item in response.get("Result"):
        ip_acg = IP_ACG(            
            id=item.get("groupId"),
            name=item.get("groupName"),
            desc=""
        )


def create():
    response = workspaces.create_ip_group(
        GroupName=name,
        GroupDesc=desc,
        UserRules=rules,
        Tags=[{"Key": k, "Value": v} for k, v in tags.items()]
    )    
    ip_acg_id = response.get('GroupId')

    return ip_acg_id


def associate():
    response = workspaces.associate_ip_groups(
        DirectoryId=directory.id,
        GroupIds=group_id
    )


def update_rules():
    response = workspaces.update_rules_of_ip_group(
        GroupId=group_id,
        UserRules=rules
    )
    pass


def disassociate():
    response = workspaces.disassociate_ip_groups(
        DirectoryId=directory.id,
        GroupIds=group_ids
    )

def delete():
    # check if any exists
    workspaces.delete_ip_group(GroupId=group_id)
