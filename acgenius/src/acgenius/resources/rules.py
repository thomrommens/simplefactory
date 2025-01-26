from botocore.exceptions import ClientError
import logging
import json

from config import workspaces, IPACGCreateException
from resources.models import IP_ACG


logger = logging.getLogger("ip_acg_logger")



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


def update_rules(ip_acg: IP_ACG) -> None:
    """
    xx
    """
    rules_formatted = format_rules(ip_acg)

    try:
        response = workspaces.update_rules_of_ip_group(
            GroupId=ip_acg.id,
            UserRules=rules_formatted
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]
        
        if error_code == "AccessDeniedException":
            error_msg = "Access denied when attempting to update IP group rules"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
            
        elif error_code == "InvalidParameterValueException":
            error_msg = "Invalid parameter provided when updating IP group rules"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
            
        elif error_code == "ResourceNotFoundException":
            error_msg = "Resource not found when updating IP group rules"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
            
        else:
            error_msg = f"AWS error when updating IP group rules: {error_code} - {error_message}"
            logger.error(error_msg, extra={"depth": 1})
            raise IPACGCreateException(error_msg)
        
    logger.debug(
        f"update_rules_of_ip_group - response: {json.dumps(response, indent=4)}", 
        extra={"depth": 1}
    )
    logger.info(
        f"Rules for IP ACG [{ip_acg.name}] and id [{ip_acg.id}] updated.",  # TODO: display tabulated with different markup?
        extra={"depth": 1}
    )
