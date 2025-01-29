import logging
from acgenius.resources.models import WorkInstruction


logger = logging.getLogger("acgenius")


def val_directories_specified(work_instruction: WorkInstruction) -> bool:
    """
    See if any directory is specified in the work instruction.
    If yes, downstream IP ACGs will be associated 
    with that specified directory.
    If not, downstream IP ACGs will be associated 
    with all directories found in the inventory.
    """
    logger.debug(
        f"Validate if any directory specified in settings.yml...", 
        extra={"depth": 1}
    )

    directories_specified = False

    if work_instruction.directories:
        if (
            work_instruction.directories[0].id 
            and work_instruction.directories[0].name
        ):
            directories_specified = True

    logger.debug(
        f"Any directory specified in settings.yml: [{directories_specified}]...", 
        extra={"depth": 1}
    )
    return directories_specified
