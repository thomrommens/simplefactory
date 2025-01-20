import yaml

from config import SETTINGS_FILE_PATH
from models import IP_ACG, Directory, Rule, Validation, WorkInstruction


def get_settings():

    with open(SETTINGS_FILE_PATH, "r") as settings_file:
        settings = yaml.safe_load(settings_file)

    # TODO: parse to separate dataclass?

    return settings


def get_validation_baseline(settings: dict) -> Validation:

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

    return WorkInstruction(
        directories=[
            Directory(id=id, name=name)
            for directory in settings["directories"]
            for id, name in directory.items()
        ],
        ip_acgs=[
            IP_ACG(
                name=ip_acg["name"],
                desc=ip_acg["desc"],
                rules=[
                    Rule(ip=ip, desc=desc)
                    for ip_acg in settings["ip_acgs"]
                    for rule in ip_acg["rules"]
                    for ip, desc in rule.items()
                ],
                origin=ip_acg["origin"],
            )
            for ip_acg in settings["ip_acgs"]

        ],
        tags=settings["tags"]
    )
