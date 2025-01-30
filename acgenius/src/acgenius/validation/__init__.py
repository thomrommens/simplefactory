import logging

from acgenius.resources.models import Settings, WorkInstruction
from acgenius.validation.ip_acgs import val_ip_acgs
from acgenius.validation.rules import val_rules

logger = logging.getLogger("acgenius")


def val_work_instruction(settings: Settings) -> WorkInstruction:
    """
    Validate work instruction: IP ACGs and their rules.
    :param settings: settings from settings.yaml
    """
    logger.debug("Start: validate settings.yaml...", extra={"depth": 1})

    work_instruction_rules_validated = val_rules(settings.work_instruction, settings)
    work_instruction_ip_acgs_validated = val_ip_acgs(
        work_instruction_rules_validated, settings
    )

    logger.debug("Finish: validate settings.yaml.", extra={"depth": 1})
    return work_instruction_ip_acgs_validated
