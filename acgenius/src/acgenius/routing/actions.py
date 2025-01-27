import logging

from config import IPACGNoneFoundException, IPACGNoneSpecifiedForDeleteException
from resources.utils import create_report
from resources.ip_acgs.work_instruction import (
    associate_ip_acg, 
    create_ip_acg, 
    delete_ip_acg, 
    disassociate_ip_acg
)
from resources.ip_acgs.work_instruction import update_rules
from resources.ip_acgs.utils import match_ip_acgs
from resources.models import AppInput


logger = logging.getLogger("acgenius")


def status(app_input: AppInput) -> None:
    """
    Placeholder
    """
    logger.info(
        "Completed display of status.",
        extra={"depth": 1}
    )


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
    logger.debug(f"Action: create IP ACGs...", extra={"depth": 5})
    
    cli = app_input.cli
    work_instruction = app_input.settings.work_instruction
    inventory = app_input.inventory

    create_report(subject=work_instruction.ip_acgs, origin="work_instruction")

    if not cli["dryrun"] :
        tags = work_instruction.tags
        
        # If no directories are specified in the settings.yaml, 
        #  associate the IP ACGs with all directories in the inventory
        #  TODO: test
        if not work_instruction.directories[0].id and not work_instruction.directories[0].name:  # TODO: separate function
            directories = inventory.directories
        else:
            directories = work_instruction.directories

        ip_acgs_created = []
        for ip_acg in work_instruction.ip_acgs:
            ip_acg_created = create_ip_acg(ip_acg, tags)
            
            if ip_acg_created:
                ip_acgs_created.append(ip_acg_created)  
                               
                for directory in directories:
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
    logger.debug(f"Action: update IP ACGs...", extra={"depth": 5})

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
        raise IPACGNoneFoundException(
            "No IP ACGs found in inventory. Skip update of IP ACG rules. " 
            "Please make sure you have at least one IP ACG in AWS to update. "
            "Run the 'create' action to create an IP ACG. "
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
    logger.debug(f"Action: delete IP ACGs...", extra={"depth": 5})

    cli = app_input.cli
    inventory = app_input.inventory

    if cli["ip_acg_ids_to_delete"]:

        if not cli["dryrun"]:
            ip_acg_ids_to_delete = cli["ip_acg_ids_to_delete"]
            
            for ip_acg_id in ip_acg_ids_to_delete:
                for directory in inventory.directories:
                    try:
                        disassociate_ip_acg(
                            ip_acg_ids_to_delete=[ip_acg_id],
                            directory=directory
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to disassociate IP ACG [{ip_acg_id}] "
                            f"from directory [{directory.name} - {directory.id}]: "
                            f"{str(e)}",
                            extra={"depth": 2}
                        )
                delete_ip_acg(ip_acg_id)

    else:
        raise IPACGNoneSpecifiedForDeleteException(
            f"You selected action [{cli['action']}], "
            "but you did not specify any IP ACGs to delete. "
            "Please specify at least one IP ACG to delete. "
            "See README.md for more information."
        )
