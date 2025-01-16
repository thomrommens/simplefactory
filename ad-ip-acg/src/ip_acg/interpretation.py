CONFIG_FILE = ""


def read_settings():
    # yaml to dict
    # yaml.safe_load(file)
    pass


def read_validation_baseline():
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
