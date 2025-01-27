from datetime import datetime
from resources.models import Directory, IP_ACG


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


def report_ip_acgs(ip_acgs: list[IP_ACG]):
    """
    xx
    """
    
    if ip_acgs:
        i = 0
        for ip_acg in ip_acgs:
            
            # TODO: abstract
            # IP ACG
            i += 1
            print(f"■ IP ACG {i}")
            row = {
                "id": ip_acg.id,
                "name": ip_acg.name,
                "description": ip_acg.desc,
            }
            data = [(row)]
            df = pd.DataFrame(data)
            df.index += i
            print(f"{tabulate(df, headers='keys', tablefmt='psql')}")

            # RULES          
            print("\\")    
            rules_formatted = format_rules(ip_acg)
            rules_table = [["rule", "description"]] + [[item["ipRule"], item["ruleDesc"]] for item in rules_formatted]

            rules_table_str = tabulate(rules_table, headers="firstrow", tablefmt="psql")
            rules_table_indented = indent(rules_table_str, " " * 2)
            print(rules_table_indented)
            print("\n")
            
    else:
        print("(No IP ACGs found)")


def format_rules(ip_acg: IP_ACG) -> list[dict]:
    """
    Fit rules in request syntax format.
    Sort rules for user friendliness.
    """
    rules = [
        {"ipRule": rule.ip, "ruleDesc": rule.desc}
        for rule in ip_acg.rules
    ]
    rules_sorted = sorted(
        rules,
        key=lambda rules: rules["ipRule"]
    )
    return rules_sorted


def extend_tags(tags: dict, ip_acg: IP_ACG) -> dict:
    """
    xx
    """
    timestamp = datetime.now().isoformat()

    tags["IPACGName"] = ip_acg.name
    tags["Created"] = timestamp
    tags["RulesLastApplied"] = timestamp  #TODO: make sure to update as only tag at update route

    return tags


def format_tags(tags: dict) -> list[dict]:
    """
    xx
    """
    return [{"Key": k, "Value": v} for k, v in tags.items()]