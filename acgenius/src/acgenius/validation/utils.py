import json
import logging
from dataclasses import asdict

import yaml

from acgenius.config import SETTINGS_FILE_PATH, STD_INSTR_SETTINGS
from acgenius.resources.models import (
    IP_ACG,
    Directory,
    Rule,
    Settings,
    Validation,
    WorkInstruction,
)
from acgenius.routing.errors import get_error_code, process_error

logger = logging.getLogger("acgenius")


def get_settings() -> dict:
    """
    Get settings from settings.yaml.

    :return: settings from settings.yaml
    """
    logger.debug("Get settings from settings.yaml...", extra={"depth": 2})

    try:
        with open(SETTINGS_FILE_PATH, "r") as settings_file:
            settings = yaml.safe_load(settings_file)
        return settings

    except (yaml.parser.ParserError, FileNotFoundError, Exception) as e:
        msg_generic = "Could not load settings.yaml."
        error_map = {
            "SettingsYAMLParserError": {
                "msg": "Is the structure still correct?",
                "crash": True,
            },
            "FileNotFoundError": {
                "msg": (
                    f"Could not find file settings.yaml on path [{SETTINGS_FILE_PATH}]"
                ),
                "crash": True,
            },
        }
        error_code = get_error_code(e)
        process_error(error_map, error_code, msg_generic, e)


def val_settings_main_structure(settings: dict) -> None:
    """
    Validate if expected 'main' keys of settings.yaml have at least an empty value
    in the expected type.

    :param settings: all settings required for the validation
    """
    logger.debug(
        "Validate if expected 'main' keys of settings.yaml "
        "have at least an empty value in the expected type...",
        extra={"depth": 2},
    )
    keys = {
        "ip_acgs": list,
        "tags": dict,
        "directories": list,
        "user_input_validation": dict,
    }

    for k, v in keys.items():
        if not isinstance(settings.get(k), v):
            msg_generic = "Generic structure validation of settings.yaml failed."
            error_code = "SettingsYAMLExpectedKeyException"
            error_map = {
                "SettingsYAMLExpectedKeyException": {
                    "msg": f"Value of key [{k}] is expected to be present, and "
                    f"of type [{v.__name__}], "
                    "but seems to be absent, or of a different type. "
                    f"{STD_INSTR_SETTINGS}",
                    "crash": True,
                }
            }
            process_error(error_map, error_code, msg_generic)


def val_settings_ip_acg_structure(settings: dict) -> None:
    """
    Validate if keys expected in settings["ip_acgs"] of settings.yaml
    are present.

    :param settings: all settings required for the validation
    """
    logger.debug("Validate settings['ip_acgs'] of settings.yaml...", extra={"depth": 2})
    ip_acg_keys = ["name", "desc", "origin", "rules"]
    msg_generic = "Specific IP ACG structure validation of settings.yaml failed."

    if settings["ip_acgs"] == [None]:
        error_code = "SettingsYAMLIPACGNoKeysException"
        error_map = {
            "SettingsYAMLIPACGNoKeysException": {
                "msg": f"{msg_generic} No IP ACGs were found in settings.yaml. "
                "Are you sure you have added at least one IP ACG? "
                f"{STD_INSTR_SETTINGS}",
                "crash": True,
            }
        }
        process_error(error_map, error_code, msg_generic)

    for ip_acg in settings["ip_acgs"]:
        for ip_acg_key in ip_acg_keys:
            if ip_acg_key not in ip_acg.keys():
                error_code = "SettingsYAMLIPACGExpectedKeyException"
                error_map = {
                    "SettingsYAMLIPACGExpectedKeyException": {
                        "msg": f"{msg_generic} Key [{ip_acg_key}] is expected to be "
                        "part of the IP ACGs in settings.yaml, but was not found. "
                        f"{STD_INSTR_SETTINGS}",
                        "crash": True,
                    }
                }
                process_error(error_map, error_code, msg_generic)


def get_validation_baseline(settings: Settings) -> Validation:
    """
    Get validation baseline: settings to validate user input against,
    from settings.yaml.

    :param settings: all settings required for the validation
    :return: Validation object containing validation rules
    """
    logger.debug("Get validation baseline from settings.yaml...", extra={"depth": 2})

    ui = settings["user_input_validation"]

    return Validation(
        invalid_rules=[
            Rule(ip=ip_invalid, desc=desc_invalid)
            for rule in ui["ip_address"]["invalid"]
            for ip_invalid, desc_invalid in rule.items()
        ],
        rules_amt_max=ui["ip_acg"]["rules_amt"]["max"],
        rules_desc_length_max=ui["ip_acg"]["rules_desc_length"]["max"],
        prefix_default=ui["ip_address"]["prefix"]["default"],
        prefix_min=ui["ip_address"]["prefix"]["min"],
        ip_acg_name_length_max=ui["ip_acg"]["name_length"]["max"],
        groups_per_directory_amt_max=ui["ip_acg"]["groups_per_directory_amt"]["max"],
    )


def get_work_instruction(settings: Settings) -> WorkInstruction:
    """
    Parse retrieved settings to a WorkInstruction.
    Make sure IP ACGs are sorted by name.

    :param settings: all settings required for the validation
    :return: WorkInstruction object containing directories and IP ACGs
    """
    logger.debug("Get work instruction from settings...", extra={"depth": 2})

    try:
        work_instruction = WorkInstruction(
            directories=[
                Directory(id=directory.get("id"), name=directory.get("name"))
                for directory in settings["directories"]
            ],
            ip_acgs=sorted(
                [
                    IP_ACG(
                        name=ip_acg.get("name", ""),
                        desc=ip_acg.get("desc", ""),
                        origin=ip_acg.get("origin", ""),
                        rules=[
                            Rule(ip, desc=desc)
                            for rule in (ip_acg.get("rules") or [])
                            if rule is not None
                            for ip, desc in (rule.items() if rule else {})
                        ],
                    )
                    for ip_acg in (settings.get("ip_acgs") or [])
                ],
                key=lambda x: x.name or "",
            ),
            tags=settings["tags"],
        )

        return work_instruction

    except (TypeError, Exception) as e:
        msg_generic = "Could parse settings to work instruction."
        error_map = {
            "TypeError": {
                "msg": (
                    "Please verify if all values in settings.yaml, "
                    "especially the name of the IP ACG, are encapsulated "
                    "with double quotes."
                ),
                "crash": True,
            }
        }
        error_code = get_error_code(e)
        process_error(error_map, error_code, msg_generic, e)


def parse_settings() -> Settings:
    """
    Integrate parsing of settings.

    :return: Settings object containing validation and work instruction
    """
    logger.debug("Parse settings...", extra={"depth": 1})

    settings = get_settings()
    val_settings_main_structure(settings)
    val_settings_ip_acg_structure(settings)

    logger.debug(
        f"Settings retrieved from YAML file:\n{json.dumps(settings, indent=4)}",
        extra={"depth": 2},
    )

    validation_baseline = get_validation_baseline(settings)
    logger.debug(
        "Validation baseline parsed from YAML file:\n"
        f"{json.dumps(asdict(validation_baseline), indent=4)}",
        extra={"depth": 3},
    )

    work_instruction = get_work_instruction(settings)
    logger.debug(
        "Work instruction parsed from YAML file:\n"
        f"{json.dumps(asdict(work_instruction), indent=4)}",
        extra={"depth": 3},
    )

    return Settings(validation=validation_baseline, work_instruction=work_instruction)


def split_ip_and_prefix(rule: Rule, settings: Settings) -> tuple[str, int]:
    """
    Split IP address and prefix.

    :param rule: Rule object containing IP address to split
    :param settings: all settings required for the validation
    :return: Tuple containing IP address and prefix
    """
    logger.debug("Split IP address and prefix...", extra={"depth": 5})

    fwd_slash = rule.ip.find("/")

    if fwd_slash != -1:
        ip = rule.ip[:fwd_slash]
        prefix = int(rule.ip[fwd_slash + 1 :])
        logger.debug(f"Prefix present, using user input: {prefix}", extra={"depth": 6})

    else:
        ip = rule.ip
        prefix = settings.validation.prefix_default
        logger.debug(f"Prefix absent, using default: {prefix}", extra={"depth": 6})

    return ip, prefix


def remove_whitespaces(rule: Rule) -> Rule:

    """
    Remove whitespaces from IP address.

    :param rule: Rule object containing IP address to remove whitespaces from, if any.
    :return: Rule object containing IP address without whitespaces
    """
    logger.debug("Remove whitespaces if any...", extra={"depth": 5})

    return rule.ip.replace(" ", "")
