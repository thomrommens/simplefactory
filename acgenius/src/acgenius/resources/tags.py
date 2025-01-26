from datetime import datetime

from resources.models import IP_ACG


def update_tags(tags: dict, ip_acg: IP_ACG) -> dict:
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
