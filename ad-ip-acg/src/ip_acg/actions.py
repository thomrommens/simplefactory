import logging

from exceptions import IPACGNoneSpecifiedForDeleteException
from ip_acgs import (
    associate_ip_acg, 
    create_ip_acg, 
    delete_ip_acg, 
    disassociate_ip_acg, 
    report_ip_acgs, 
    update_rules,
    match_ip_acgs
)

logger = logging.getLogger("ip_acg_logger")


def create(app_input):
    """
    xx
    """
    cli = app_input.cli
    work_instruction = app_input.settings.work_instruction

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


def update(app_input):
    """
    xx
    """
    cli = app_input.cli
    work_instruction = app_input.settings.work_instruction
    inventory = app_input.inventory

    logger.info(
        "Rules of these IP ACGs "
        f"{'would' if cli['dryrun'] else 'will'} be updated:", 
        extra={"depth": 1}
            )
    match_ip_acgs(inventory, work_instruction)

    report_ip_acgs(work_instruction.ip_acgs)

    if not cli["dryrun"]:

        for ip_acg in work_instruction.ip_acgs:
            update_rules(ip_acg)


def delete(app_input):
    """
    xx
    """
    cli = app_input.cli
    work_instruction = app_input.settings.work_instruction

    print("DELETE LIST:", cli["delete_list"])

    if cli["delete_list"]:
        logger.info(
            "These IP ACGs "
            f"{'would' if cli['dryrun'] else 'will'} "
            f"be deleted: {cli['delete_list']}", 
            extra={"depth": 1}
        )
        if not cli["dryrun"]:
            delete_list=cli["delete_list"]
            for directory in work_instruction.directories:
                disassociate_ip_acg(
                    delete_list=delete_list,
                    directory=directory
                )
                for ip_acg_id in delete_list:
                    delete_ip_acg(ip_acg_id)

        # TODO: test deleting multiple items

    else:
        raise IPACGNoneSpecifiedForDeleteException(
            "You requested to delete IP ACGs, but you have not specified "
            "any IP ACG id (e.g., wsipg-abc12d34e) to delete. " 
            "Please do so, when calling the app from the command line, "
            "use option '--delete_list'. "
            "See README for further instructions."
        )

    