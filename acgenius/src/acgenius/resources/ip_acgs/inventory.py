import json
import logging
from typing import Optional

from botocore.exceptions import ClientError

from acgenius.config import (
    EXC_ACCESS_DENIED,
    EXC_INVALID_PARAM,
    STD_INSTR_README,
    workspaces,
)
from acgenius.resources.models import IP_ACG, Rule
from acgenius.resources.utils import create_report
from acgenius.routing.errors import get_error_code, process_error

logger = logging.getLogger("acgenius")


def get_ip_acgs() -> list[IP_ACG]:
    """
    Retrieve IP Access Control Groups from AWS Workspaces.
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/workspaces/client/describe_ip_groups.html

    :return: List of IP_ACG objects containing the IP ACGs found in AWS
    """
    logger.debug("Call [describe_ip_groups]...", extra={"depth": 2})

    try:
        response = workspaces.describe_ip_groups()

        logger.debug(
            f"Response of [describe_ip_groups]: {json.dumps(response, indent=4)}",
            extra={"depth": 2},
        )
        if response.get("Result"):
            return response["Result"]

        logger.info("No IP ACGs found in AWS.", extra={"depth": 2})

    except (ClientError, Exception) as e:
        msg_generic = "Could not get IP ACGs from AWS."
        error_map = {
            "InvalidParameterValuesException": {
                "msg": EXC_INVALID_PARAM,
                "crash": True,
            },
            "AccessDeniedException": {
                "msg": f"{EXC_ACCESS_DENIED} {STD_INSTR_README}",
                "crash": True,
            },
        }
        error_code = get_error_code(e)
        process_error(error_map, error_code, msg_generic, e)


def sel_ip_acgs(ip_acgs_inventory: Optional[list[IP_ACG]]) -> list[IP_ACG]:
    """
    Select relevant IP ACG info from retrieved IP ACGs, and sort by name.

    """
    logger.debug(
        "Select relevant IP ACG info from retrieved IP ACGs, and sort by name...",
        extra={"depth": 2},
    )

    ip_acgs_sel = []

    unsorted_ip_acgs = [
        IP_ACG(
            id=ip_acg.get("groupId"),
            name=ip_acg.get("groupName"),
            desc=ip_acg.get("groupDesc"),
            rules=[
                Rule(ip=rule.get("ipRule"), desc=rule.get("ruleDesc"))
                for rule in ip_acg.get("userRules", {})
            ],
        )
        for ip_acg in ip_acgs_inventory
    ]
    ip_acgs_sel.extend(sorted(unsorted_ip_acgs, key=lambda x: x.name))

    return ip_acgs_sel


def show_ip_acgs() -> Optional[list[IP_ACG]]:
    """
    Get and display the current IP ACGs in AWS WorkSpaces.

    """
    logger.info("Current IP ACGs (before execution of action):", extra={"depth": 1})

    ip_acgs_received = get_ip_acgs()

    if ip_acgs_received:
        ip_acgs = sel_ip_acgs(ip_acgs_received)
        create_report(subject=ip_acgs, origin="inventory")

        return ip_acgs
