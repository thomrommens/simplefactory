import logging

from config import UnexpectedException
from resources.directories.inventory import show_directories
from resources.ip_acgs.inventory import show_ip_acgs
from resources.models import AppInput, Inventory, Settings
from routing import actions
from validation import val_work_instruction
from validation.utils import parse_settings


logger = logging.getLogger("acgenius")
       

def run_common_route() -> tuple[Settings, Inventory]:
    """
    """
    directories = show_directories()
    ip_acgs = show_ip_acgs()
    inventory = Inventory(
        directories=directories,
        ip_acgs=ip_acgs
    ) 

    settings = parse_settings()
    validation_baseline = settings.validation  # TODO validate the validation baseline too?
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
    action_map = {
        "status": actions.status,
        "create": actions.create,
        "update": actions.update,
        "delete": actions.delete
    }
    try:
        action = app_input.cli["action"]
        
    except Exception as e:
        raise UnexpectedException(f"Unexpected error: {e}") 
    
    cli = app_input.cli    
    logger.info(
        "These IP ACGs "
        f"{'would' if cli['dryrun'] else 'will'} be attempted to {cli['action']}:",
        extra={"depth": 1}
    )
    action_map[action](app_input)
