import logging

from validation.directories import val_directories_specified
from config import STD_INSTRUCTION_README
from routing.errors import process_error
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
        "✅ Completed display of status.",
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
    logger.debug(f"Action: create IP ACGs...", extra={"depth": 1})
    
    cli = app_input.cli
    work_instruction = app_input.settings.work_instruction
    inventory = app_input.inventory

    create_report(subject=work_instruction.ip_acgs, origin="work_instruction")

    if not cli["dryrun"]:
        
        tags = work_instruction.tags
               
        if val_directories_specified(work_instruction):  # TODO: test
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
        f"✅ Completed action: create IP ACGs"
        f"{' (dryrun)' if cli['dryrun'] else ''}.", 
        extra={"depth": 1}
    )


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
    logger.debug(f"Action: update IP ACGs...", extra={"depth": 1})

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
        code = "IPACGNoneFoundException"
        map = {
            "IPACGNoneFoundException": {
                "msg": f"{msg_generic} No IP ACGs found in inventory. "
                    "Please make sure you have at least one IP ACG in AWS, "
                    "in order to update. "
                    f"Run the 'create' action to create an IP ACG. {STD_INSTRUCTION_README}",
                "crash": True
            }
        }        
        process_error(map, code)
       
    logger.info(
        f"✅ Completed action: update IP ACGs"
        f"{' (dryrun)' if cli['dryrun'] else ''}.", 
        extra={"depth": 1}
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
    inventory = app_input.inventory

    logger.info(f"{cli['ip_acg_ids_to_delete']}", extra={"depth": 1})
    logger.debug(f"Action: delete IP ACGs...", extra={"depth": 1})

    if cli["ip_acg_ids_to_delete"]:

        if not cli["dryrun"]:
            ip_acg_ids_to_delete = cli["ip_acg_ids_to_delete"]
            
            for ip_acg_id in ip_acg_ids_to_delete:
                for directory in inventory.directories:
                    disassociate_ip_acg(
                        ip_acg_ids_to_delete=[ip_acg_id],
                        directory=directory
                    )
                    delete_ip_acg(ip_acg_id)

    else:
        msg_generic = "Could not delete IP ACGs."
        code = "IPACGNoneSpecifiedForDeleteException"
        map = {
            "IPACGNoneSpecifiedForDeleteException": {
                "msg": f"{msg_generic} You specified the 'delete' action, "
                    "but you have not properly specified which "
                    "IP ACG id(s) to delete. "
                    f"Please specify at least one IP ACG to delete. "
                    f"{STD_INSTRUCTION_README}",
                "crash": True
            }
        }        
        process_error(map, code)
    
    logger.info(
        f"✅ Completed action: delete IP ACGs"
        f"{' (dryrun)' if cli['dryrun'] else ''}.", 
        extra={"depth": 1}
    )
