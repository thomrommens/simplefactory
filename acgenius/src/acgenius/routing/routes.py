import logging

from acgenius.resources.directories.inventory import show_directories
from acgenius.resources.ip_acgs.inventory import show_ip_acgs
from acgenius.resources.models import AppInput, Inventory, Settings
from acgenius.routing.actions import create, delete, status, update
from acgenius.routing.errors import get_error_code, process_error
from acgenius.validation import val_work_instruction
from acgenius.validation.utils import parse_settings

logger = logging.getLogger("acgenius")


def run_common_route() -> tuple[Settings, Inventory]:
    """ 
    Run route for all actions.
    Whatever action is picked, inventory and settings are always retrieved.
    """
    logger.debug("Run common route...", extra={"depth": 1})

    directories = show_directories()
    ip_acgs = show_ip_acgs()
    inventory = Inventory(directories=directories, ip_acgs=ip_acgs)

    settings = parse_settings()
    validation_baseline = settings.validation
    work_instruction = val_work_instruction(settings)
    settings = Settings(
        validation=validation_baseline, work_instruction=work_instruction
    )

    return settings, inventory


def run_selected_route(app_input: AppInput) -> None:
    """
    Run selected route.
    """
    logger.debug("Run selected route...", extra={"depth": 1})

    action_map = {
        "status": status,
        "create": create,
        "update": update,
        "delete": delete,
    }
    try:
        action = app_input.cli["action"]

    except Exception as e:
        msg_generic = "Could not run selected route."
        error_map = {}
        error_code = get_error_code(e)
        process_error(error_map, error_code, msg_generic, e)

    cli = app_input.cli

    if not cli["action"] == "status":
        logger.info(
            "These IP ACGs "
            f"{'would' if cli['dryrun'] else 'will'} be attempted to {cli['action']}: ",
            extra={"depth": 1},
        )
    action_map[action](app_input)
