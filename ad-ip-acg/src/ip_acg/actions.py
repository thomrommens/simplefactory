import logging

from exceptions import IPACGNoneFoundException, IPACGNoneSpecifiedForDeleteException
from ip_acgs import (
    associate_ip_acg, 
    create_ip_acg, 
    delete_ip_acg, 
    disassociate_ip_acg, 
    report_ip_acgs, 
    update_rules,
    match_ip_acgs
)
from models import AppInput

logger = logging.getLogger("ip_acg_logger")


def create(app_input: AppInput) -> None:
    """
    Creates new IP Access Control Groups in AWS based on the work instruction.
    
    If not in dryrun mode:
    - Creates each IP ACG specified in the work instruction
    - Applies the tags from the work instruction
    - Associates the created IP ACGs with specified directories
    
    :param app_input: Contains CLI arguments, settings and inventory data
    :return: None
    :raises: Various AWS exceptions during creation and association
    """
    cli = app_input.cli
    work_instruction = app_input.settings.work_instruction

    logger.info(
        "These IP ACGs "
        f"{'would' if cli['dryrun']  else 'will'} be {cli['action']}d:",
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


def update(app_input: AppInput) -> None:
    """
    Updates existing IP Access Control Groups in AWS with new rules.
    
    If not in dryrun mode:
    - Matches IP ACGs from work instruction to existing ones in AWS
    - Updates the rules for each matched IP ACG
    
    :param app_input: Contains CLI arguments, settings and inventory data
    :return: None
    :raises: IPACGIdMatchException if IP ACGs cannot be matched
    :raises: Various AWS exceptions during update
    """
    cli = app_input.cli
    work_instruction = app_input.settings.work_instruction
    inventory = app_input.inventory

    if inventory.ip_acgs:

        logger.info(
            "These IP ACGs "
            f"{'would' if cli['dryrun']  else 'will'} be {cli['action']}d:", 
            extra={"depth": 1}
        )
        match_ip_acgs(inventory, work_instruction)

        report_ip_acgs(work_instruction.ip_acgs)

        if not cli["dryrun"]:

            for ip_acg in work_instruction.ip_acgs:
                update_rules(ip_acg)

    else:
        raise IPACGNoneFoundException(
            "No IP ACGs found in inventory. Skip update of IP ACG rules. Please make sure you have "
            "at least one IP ACG in AWS to update. Run the 'create' action to create an IP ACG. "
            "See README.md for more information."
        )

def delete(app_input: AppInput) -> None:
    """
    Deletes specified IP Access Control Groups from AWS.
    
    If not in dryrun mode:
    - Disassociates IP ACGs from their directories
    - Deletes each IP ACG specified in the delete list
    
    :param app_input: Contains CLI arguments, settings and inventory data
    :return: None
    :raises: IPACGNoneSpecifiedForDeleteException if no IP ACGs specified for deletion
    :raises: Various AWS exceptions during disassociation and deletion
    """
    cli = app_input.cli
    work_instruction = app_input.settings.work_instruction

    if cli["ip_acg_ids_to_delete"]:
        logger.info(
            "These IP ACGs "
            f"{'would' if cli['dryrun'] else 'will'} be attempted to {cli['action']}: "
            f"{cli['ip_acg_ids_to_delete']}", extra={"depth": 1}
        )
        if not cli["dryrun"]:
            ip_acg_ids_to_delete=cli["ip_acg_ids_to_delete"]
            for directory in work_instruction.directories:
                disassociate_ip_acg(
                    ip_acg_ids_to_delete=ip_acg_ids_to_delete,
                    directory=directory
                )
                for ip_acg_id in ip_acg_ids_to_delete:
                    delete_ip_acg(ip_acg_id)

    else:
        raise IPACGNoneSpecifiedForDeleteException(
            "Selected action is delete, but no IP ACGs specified for deletion."
        )
    