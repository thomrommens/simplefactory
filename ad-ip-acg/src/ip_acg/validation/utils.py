from dataclasses import asdict
import json
import logging
import yaml

from config import SETTINGS_FILE_PATH
from resources.models import (
    IP_ACG, 
    Directory, 
    Rule, 
    Settings, 
    Validation, 
    WorkInstruction
)

logger = logging.getLogger("ip_acg_logger")


def get_settings() -> dict:
    """
    Get settings from settings.yaml.
    """
    with open(SETTINGS_FILE_PATH, "r") as settings_file:
        settings = yaml.safe_load(settings_file)

    return settings


def get_validation_baseline(settings: dict) -> Validation:
    """
    Get validation baseline (settings to validate user input against)from settings.yaml.
    """
    return Validation(
        invalid_rules=[
            Rule(ip=ip_invalid, desc=desc_invalid)
            for rule in settings["user_input_validation"]["ip_address"]["invalid"]
            for ip_invalid, desc_invalid in rule.items()
        ],
        prefix_default=settings["user_input_validation"]["ip_address"]["prefix"]["default"],
        prefix_min=settings["user_input_validation"]["ip_address"]["prefix"]["min"],
        rules_amt_max=settings["user_input_validation"]["ip_acg"]["rules_amt"]["max"],
        rules_desc_length_max=settings["user_input_validation"]["ip_acg"]["rules_desc_length"]["max"],
        ip_acg_name_length_max=settings["user_input_validation"]["ip_acg"]["name_length"]["max"]
    )


def get_work_instruction(settings: dict) -> WorkInstruction:
    """
    Parse retrieved settings to a WorkInstruction object.
    Make sure IP ACGs are sorted by name.
    """
    return WorkInstruction(
        directories=[
            Directory(id=directory["id"], name=directory["name"])
            for directory in settings["directories"]
        ],
        ip_acgs=sorted(
            [
                IP_ACG(
                    name=ip_acg["name"],
                    desc=ip_acg["desc"],
                    rules=[
                        Rule(ip=ip, desc=desc)
                        for rule in ip_acg["rules"]
                        for ip, desc in rule.items()
                    ],
                    origin=ip_acg["origin"],
                )
                for ip_acg in settings["ip_acgs"]
            ],
            key=lambda x: x.name
        ),
        tags=settings["tags"]
    )

def parse_settings() -> Settings:
    """
    xx
    """

    settings = get_settings()
    logger.debug(
        "Settings retrieved from YAML file:\n"
        f"{json.dumps(settings, indent=4)}", 
        extra={"depth": 1}
    )

    validation_baseline = get_validation_baseline(settings)
    logger.debug(
        "Validation baseline parsed from YAML file:\n"
        f"{json.dumps(asdict(validation_baseline), indent=4)}", 
        extra={"depth": 1}
    ) 

    work_instruction = get_work_instruction(settings)
    logger.debug(
        "Work instruction parsed from YAML file:\n"
        f"{json.dumps(asdict(work_instruction), indent=4)}", 
        extra={"depth": 1}
    )

    return Settings(
        validation=validation_baseline,
        work_instruction=work_instruction
    )  


def split_ip_and_prefix(rule: Rule) -> tuple[str, int]:
    """
    Split IP address and prefix.
    """

    fwd_slash = rule.ip.find("/")

    if fwd_slash != -1:
        ip = rule.ip[:fwd_slash]
        prefix = int(rule.ip[fwd_slash+1:])

    else:
        ip = rule.ip
        prefix = 32  # TODO replace with dynamic value

    return ip, prefix


def remove_whitespaces(rule: Rule) -> Rule:
    """
    Remove whitespaces from IP address.
    """
    logger.debug(f"Remove whitespaces if any...", extra={"depth": 5})
    return rule.ip.replace(" ", "")
