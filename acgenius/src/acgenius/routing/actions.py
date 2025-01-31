import logging

from acgenius.config import STD_INSTR_README
from acgenius.resources.ip_acgs.utils import match_ip_acgs
from acgenius.resources.ip_acgs.work_instruction import (
    associate_ip_acg,
    create_ip_acg,
    delete_ip_acg,
    disassociate_ip_acg,
    update_rules,
)
from acgenius.resources.models import AppInput
from acgenius.resources.utils import create_report
from acgenius.routing.errors import process_error
from acgenius.validation.directories import val_directories_specified

logger = logging.getLogger("acgenius")


def status(app_input: AppInput) -> None:
    """
    Display status of current situation for IP ACGs.

    :param app_input: all input required for the action
    (not required here, but required for the function signature)
    """
    logger.info("✅ Completed display of status.", extra={"depth": 1})


def create(app_input: AppInput) -> None:
    """
    Create new IP ACGs.

    :param app_input: all input required for the action
    """
    logger.debug("Action: create IP ACGs...", extra={"depth": 1})

    cli = app_input.cli
    work_instruction = app_input.settings.work_instruction
    inventory = app_input.inventory

    create_report(subject=work_instruction.ip_acgs, origin="work_instruction")

    if not cli["dryrun"]:
        tags = work_instruction.tags

        if val_directories_specified(work_instruction):
            directories = work_instruction.directories
        else:
            directories = inventory.directories

        ip_acgs_created = []
        for ip_acg in work_instruction.ip_acgs:
            ip_acg_created = create_ip_acg(ip_acg, tags)

            if ip_acg_created:
                ip_acgs_created.append(ip_acg_created)

                for directory in directories:
                    associate_ip_acg(ip_acgs_created, directory)

    logger.info(
        f"✅ Completed action: create IP ACGs{' (dryrun)' if cli['dryrun'] else ''}.",
        extra={"depth": 1},
    )


def update(app_input: AppInput) -> None:
    """
    Update rules of existing IP ACGs.

    :param app_input: all input required for the action
    """
    logger.debug("Action: update IP ACGs...", extra={"depth": 1})

    cli = app_input.cli
    work_instruction = app_input.settings.work_instruction
    inventory = app_input.inventory

    if inventory.ip_acgs:
        match_ip_acgs(inventory, work_instruction)
        create_report(subject=work_instruction.ip_acgs, origin="work_instruction")

        if not cli["dryrun"]:
            for ip_acg in work_instruction.ip_acgs:
                update_rules(ip_acg)

    else:
        msg_generic = "Could not update IP ACGs."
        error_code = "IPACGNoneFoundException"
        error_map = {
            "IPACGNoneFoundException": {
                "msg": "No IP ACGs found in inventory. "
                "Please make sure you have at least one IP ACG in AWS, "
                "in order to update. "
                f"Run the 'create' action to create an IP ACG. {STD_INSTR_README}",
                "crash": True,
            }
        }
        process_error(error_map, error_code, msg_generic)

    logger.info(
        f"✅ Completed action: update IP ACGs{' (dryrun)' if cli['dryrun'] else ''}.",
        extra={"depth": 1},
    )


def delete(app_input: AppInput) -> None:
    """
    Delete specified IP ACGs.
    This 'delete' route operates independently of 'settings.yaml'.

    :param app_input: all input required for the action
    """
    cli = app_input.cli
    inventory = app_input.inventory

    logger.info(f"{cli['ip_acg_ids_to_delete']}", extra={"depth": 1})
    logger.debug("Action: delete IP ACGs...", extra={"depth": 1})

    if cli["ip_acg_ids_to_delete"]:
        if not cli["dryrun"]:
            ip_acg_ids_to_delete = cli["ip_acg_ids_to_delete"]

            for ip_acg_id in ip_acg_ids_to_delete:
                for directory in inventory.directories:
                    disassociate_ip_acg(
                        ip_acg_ids_to_delete=[ip_acg_id], directory=directory
                    )
                    delete_ip_acg(ip_acg_id)

    else:
        msg_generic = "Could not delete IP ACGs."
        error_code = "IPACGNoneSpecifiedForDeleteException"
        error_map = {
            "IPACGNoneSpecifiedForDeleteException": {
                "msg": "You specified the 'delete' action, "
                "but you have not properly specified which "
                "IP ACG id(s) to delete. "
                f"Please specify at least one IP ACG to delete. "
                f"{STD_INSTR_README}",
                "crash": True,
            }
        }
        process_error(error_map, error_code, msg_generic)

    logger.info(
        f"✅ Completed action: delete IP ACGs{' (dryrun)' if cli['dryrun'] else ''}.",
        extra={"depth": 1},
    )
