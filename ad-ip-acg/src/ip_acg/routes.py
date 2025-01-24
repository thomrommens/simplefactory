import logging

from actions import create, update, delete
from directories import show_current_directories
from exceptions import UnexpectedException
from ip_acgs import show_current_ip_acgs
from interpretation import parse_settings
from validation import validate_work_instruction
from models import Settings, Inventory, AppInput


logger = logging.getLogger("ip_acg_logger")
       

def run_common_route() -> tuple[Settings, Inventory]:
    """
    xx
    """
    directories = show_current_directories()
    ip_acgs = show_current_ip_acgs()
    inventory = Inventory(
        directories=directories,
        ip_acgs=ip_acgs
    ) 

    settings = parse_settings()
    validation_baseline = settings.validation  # TODO validate the validation baseline too?
    work_instruction = validate_work_instruction(settings)
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
        "create": create,
        "update": update,
        "delete": delete
    }
    try:
        action = app_input.cli["action"]
        action_map[action](app_input)
        
    except Exception as e:
        raise UnexpectedException(f"Unexpected error: {e}") 
    