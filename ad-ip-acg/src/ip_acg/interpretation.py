from dataclasses import asdict
import json
import logging
import yaml

from config import SETTINGS_FILE_PATH
from models import (
    IP_ACG, 
    Directory, 
    Rule, 
    Settings, 
    Validation, 
    WorkInstruction
)

logger = logging.getLogger("ip_acg_logger")


def get_settings():
    """
    xx
    """
    with open(SETTINGS_FILE_PATH, "r") as settings_file:
        settings = yaml.safe_load(settings_file)

    return settings


def get_validation_baseline(settings: dict) -> Validation:
    """
    xx
    """
    return Validation(
        invalid_rules=[
            Rule(ip=ip_invalid, desc=desc_invalid)
            for rule in settings["user_input_validation"]["ip_address"]["invalid"]
            for ip_invalid, desc_invalid in rule.items()
        ],
        prefix_default=settings["user_input_validation"]["ip_address"]["prefix"]["default"],
        prefix_min=settings["user_input_validation"]["ip_address"]["prefix"]["min"]
    )


def get_work_instruction(settings: dict):
    """
    xx
    """

    return WorkInstruction(
        directories=[
            Directory(id=directory["id"], name=directory["name"])
            for directory in settings["directories"]
        ],
        ip_acgs=[
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
        work_instruction = work_instruction
    )  
