import yaml

from config import SETTINGS_FILE_PATH


def get_settings():

    with open(SETTINGS_FILE_PATH, "r") as settings_file:
        settings = yaml.safe_load(settings_file)

    return settings


def set_validation_baseline():
    # yaml-dict to dict (select)
    return {
        "ip_address": {
            "invalid": {},
            "prefix": {
                "default": "",
                "min": "",
            }
        },
        "ip_acg_properties": {
            "name_char_length": {
                "max": ""
            },
            "rules_amt": {
                "max": ""
            }
        }
    }


def read_work_instruction():
    # yaml-dict to dataclasses
    # -> work_instruction_raw = WorkInstruction()

    # logger.debug("Received work_instruction:")
    pass
