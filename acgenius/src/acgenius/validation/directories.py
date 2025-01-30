import logging

from acgenius.resources.models import WorkInstruction

logger = logging.getLogger("acgenius")


def val_directories_specified(work_instruction: WorkInstruction) -> bool:
    """
    See if any directory is specified in the work instruction:
    - yes: downstream IP ACGs will be associated with *specified* directories only.
    - no:  downstream IP ACGs will be associated with *all* directories from inventory.

    :param work_instruction: specification of operations to be executed.
    :return: True if any directory is specified, False otherwise
    """
    logger.debug(
        "Validate if any directory specified in settings.yml...", extra={"depth": 1}
    )

    directories_specified = False

    if work_instruction.directories:
        if work_instruction.directories[0].id and work_instruction.directories[0].name:
            directories_specified = True

    logger.debug(
        f"Any directory specified in settings.yml: [{directories_specified}]...",
        extra={"depth": 1},
    )
    return directories_specified
