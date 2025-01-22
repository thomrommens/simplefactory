import logging

from directories import show_current_directories
from interpretation import parse_settings
from ip_acgs import show_current_ip_acgs
from exceptions import (
    IPACGNoneSpecifiedForDeleteException, 
    UnexpectedException
)
from validation import validate_work_instruction

from ip_acgs import (
    associate_ip_acg, 
    create_ip_acg, 
    delete_ip_acg, 
    disassociate_ip_acg, 
    report_ip_acgs, 
    update_rules
)
from models import Inventory, Settings

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


def run_selected_route(
        cli_input: dict, 
        settings: Settings, 
        inventory: Inventory
    ) -> None:
    """
    xx
    """
    cli = cli_input
    work_instruction = settings.work_instruction

    if cli["action"] == "create":

        logger.info(
            "These IP ACGs "
            f"{'would' if cli['dryrun']  else 'will'} be created:",  # TODO: abstract away
            extra={"depth": 1}
        )
        report_ip_acgs(work_instruction.ip_acgs)

        if not cli["dryrun"] :
            tags = work_instruction.tags

            ip_acgs_created = []
            for ip_acg in work_instruction.ip_acgs:
                ip_acg_created = create_ip_acg(ip_acg, tags)
                
                if ip_acg_created:
                    ip_acgs_created.append(ip_acg_created)      

                    for directory in work_instruction.directories:
                        associate_ip_acg(ip_acgs_created, directory)

    elif cli["action"] == "update":

        logger.info(
            "Rules of these IP ACGs "
            f"{'would' if cli['dryrun'] else 'will'} be updated:", 
            extra={"depth": 1}
        )
        report_ip_acgs(work_instruction.ip_acgs)

        if not cli["dryrun"]:

            for ip_acg in inventory.ip_acgs:
                update_rules(ip_acg)

    elif cli["action"] == "delete":

        if cli["delete_list"]:
            logger.info(
                "These IP ACGs "
                f"{'would' if cli['dryrun'] else 'will'} "
                f"be deleted: {cli['delete_list']}", 
                extra={"depth": 1}
            )
        else:
            raise IPACGNoneSpecifiedForDeleteException(
                    "You requested to delete IP ACGs, but you have not specified "
                    "any IP ACG id (e.g., wsipg-abc12d34e) to delete. " 
                    "Please do so, when calling the app from the command line. "
                    "See README for further instructions."
            )

        if not cli["dryrun"]:
                for directory in work_instruction.directories:
                    disassociate_ip_acg(cli["delete_list"])
                for ip_acg_id in cli["delete_list"]:
                    delete_ip_acg(ip_acg_id)

    else:
        raise UnexpectedException("Unexpected error")
