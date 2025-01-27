import logging

from config import UnexpectedException
from acgenius.src.acgenius.resources.directories.inventory import show_inventory_directories
from acgenius.src.acgenius.resources.ip_acgs.inventory import show_inventory_ip_acgs
from resources.models import AppInput, Inventory, Settings
from routing.actions import status, create, delete, update
from validation import val_work_instruction
from validation.utils import parse_settings


logger = logging.getLogger("ip_acg_logger")
       

def run_common_route() -> tuple[Settings, Inventory]:
    """
    """
    directories = show_inventory_directories()
    ip_acgs = show_inventory_ip_acgs()
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
        "status": status,
        "create": create,
        "update": update,
        "delete": delete
    }
    try:
        action = app_input.cli["action"]
        
    except Exception as e:
        raise UnexpectedException(f"Unexpected error: {e}") 
    
    action_map[action](app_input)
    