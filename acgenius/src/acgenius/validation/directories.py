from resources.models import WorkInstruction


def val_directories_specified(work_instruction: WorkInstruction) -> bool:
    """
    See if any directory is specified in the work instruction.
    If yes, downstream IP ACGs will be associated with that specified directory.
    If not, downstream IP ACGs will be associated with all directories found in the inventory.
    """
    return (
        work_instruction.directories[0].id 
        and work_instruction.directories[0].name
    )
