import logging

from config import STD_INSTR_README
from resources.directories.inventory import show_directories
from resources.ip_acgs.inventory import show_ip_acgs
from resources.models import AppInput, Inventory, Settings
from routing.actions import status, create, update, delete
from routing.errors import process_error
from validation import val_work_instruction
from validation.utils import parse_settings


logger = logging.getLogger("acgenius")
       

def run_common_route() -> tuple[Settings, Inventory]:
    """
    """
    logger.debug(f"Run common route...", extra={"depth": 1})

    directories = show_directories()
    ip_acgs = show_ip_acgs()
    inventory = Inventory(
        directories=directories,
        ip_acgs=ip_acgs
    ) 

    settings = parse_settings()
    validation_baseline = settings.validation
    work_instruction = val_work_instruction(settings)
    settings = Settings(
        validation=validation_baseline, 
        work_instruction=work_instruction
    )

    return settings, inventory


def run_selected_route(app_input: AppInput) -> None:
    """
    xx
    """
    logger.debug(f"Run selected route...", extra={"depth": 1})

    action_map = {
        "status": status,
        "create": create,
        "update": update,
        "delete": delete
    }
    try:
        action = app_input.cli["action"]
        
    except Exception as e:
        msg_generic = f"Could not run selected route."
        code = e.response["Error"]["Code"]
        map = {
            "UnexpectedException": {
                "msg": (
                    f"{msg_generic} Are you sure you specified a valid route? "
                    f"{STD_INSTR_README}"
                ),
                "crash": True
            },
        }
        process_error(map, code, e)
    
    cli = app_input.cli    
    
    if not cli["action"] == "status":
        logger.info(
            "These IP ACGs "
            f"{'would' if cli['dryrun'] else 'will'} be attempted to {cli['action']}: ",
            extra={"depth": 1}
        )
    action_map[action](app_input)
