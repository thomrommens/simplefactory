from dataclasses import asdict
import json
import click

from config import HR, setup_logger
from exceptions import IPACGNoneSpecifiedForDeleteException, UnexpectedException
from interpretation import (
    get_settings, 
    get_validation_baseline, 
    get_work_instruction
)
from directories import get_directories, sel_directories, show_directories
from ip_acgs import associate_ip_acg, create_ip_acg, delete_ip_acg, disassociate_ip_acg, get_ip_acgs, sel_ip_acgs, show_ip_acgs, update_rules
from validation import validate_work_instruction


@click.command()
@click.option(
    "--action", 
    type=click.Choice(
        ["create", "update", "delete"], 
        case_sensitive=False
    ), 
    default="create", 
    help="Which IP ACG action would you like to do??"
)
@click.option(
    "--dryrun", 
    type=click.Choice(
        ["true", "false"],  # TODO make type bool? https://click.palletsprojects.com/en/stable/options/
        case_sensitive=False
    ), 
    default="true", 
    help=(
        "Enable dryrun mode? "
        "This only shows the plan or inventory, " 
        "and does not actually apply anything in AWS."
    )
)
@click.option(
    "--debug", 
    type=click.Choice(
        ["true", "false"], 
        case_sensitive=False
    ), 
    default="false", 
    help="Enable debug mode?"
)
@click.option(
    "--delete_list", 
    multiple=True, 
    default=[]
    help="Specify ids (e.g., wsipg-abc12d34e) of IP ACGs that should be deleted."
)
def main(action, dryrun, debug, delete_list):
    """
    Integrate program.
    :param action: action requested by user on command line.
    """
    logger = setup_logger("ip_acg_logger", debug)

    logger.info(HR)
    logger.info(f"START MODULE: AMAZON WORKSPACES IP ACG")
    logger.info(f"Selected action:      [{action}]", extra={"depth": 1})
    logger.info(f"Dry run mode enabled: [{dryrun}]", extra={"depth": 1})
    logger.info(f"Debug mode enabled:   [{debug}]", extra={"depth": 1})

    # ------------------------------------------------------------------------   
    # COMMON ROUTE (applied for all routes)   
    # ------------------------------------------------------------------------   
    # Directories
    directories_received = get_directories()
    directories = sel_directories(directories_received)
    directories_as_dict = [asdict(directory) for directory in directories]
    logger.debug(
        f"Directories found in AWS:\n{json.dumps(directories_as_dict, indent=4)}", 
        extra={"depth": 1}
    )

    # IP ACGs
    ip_acgs_received = get_ip_acgs()
    ip_acgs = sel_ip_acgs(ip_acgs_received)
    ip_acgs_as_dict = [asdict(ip_acg) for ip_acg in ip_acgs]
    logger.debug(
        f"IP ACGs found in AWS:\n{json.dumps(ip_acgs_as_dict, indent=4)}", 
        extra={"depth": 1}
    )   
    
    # Settings retrieval
    settings = get_settings()
    logger.debug(
        "Settings retrieved from YAML file:\n"
        f"{json.dumps(settings, indent=4)}", 
        extra={"depth": 1}
    )

    # - validation baseline
    validation_baseline = get_validation_baseline(settings)
    logger.debug(
        "Validation baseline parsed from YAML file:\n"
        f"{json.dumps(asdict(validation_baseline), indent=4)}", 
        extra={"depth": 1}
    )   

    # - work instruction
    work_instruction_raw = get_work_instruction(settings)
    logger.debug(
        "Work instruction parsed from YAML file:\n"
        f"{json.dumps(asdict(work_instruction_raw), indent=4)}", 
        extra={"depth": 1}
    )   

    # Settings validation
    work_instruction = validate_work_instruction(work_instruction_raw)
    logger.debug(
        "Work instruction validated:",
        extra={"depth": 1}
    )
    logger.debug(
        json.dumps(asdict(work_instruction), indent=4))
    
    # Before - status
    logger.info("Current directories (before action):", extra={"depth": 1})
    show_directories(directories)

    logger.info("Current IP ACGs (before action):", extra={"depth": 1})
    show_ip_acgs(ip_acgs)
     
    # ------------------------------------------------------------------------   
    # SPECIFIC ROUTE
    # ------------------------------------------------------------------------   
    # Create a brand new ACG
    if action == "create":

        logger.info(
            "These IP ACGs "
            f"{'would' if dryrun == 'true' else 'will'} "
            f"be created:", 
            extra={"depth": 1}
        )
        show_ip_acgs(work_instruction.ip_acgs)

        if not dryrun:
            tags = work_instruction.tags

            ip_acgs_created = []
            for ip_acg in work_instruction.ip_acgs:
                ip_acg_created = create_ip_acg(ip_acg, tags)
                ip_acgs_created.append(ip_acg_created)      

            for directory in directories:
                associate_ip_acg(ip_acgs_created, directory)

    # Update rules of an existing ACG (keeps associated)
    elif action == "update":

        if not dryrun:

            for ip_acg in work_instruction.ip_acgs:
                update_rules(ip_acg)


    # Delete group (disassociate to-delete-group from directory first)
    elif action == "delete":

        # TODO rephrase delete_list
        if delete_list:
            logger.info(
                "These IP ACGs "
                f"{'would' if dryrun == 'true' else 'will'} "
                f"be deleted: {delete_list}", 
                extra={"depth": 1}
            )
        else:
            raise IPACGNoneSpecifiedForDeleteException(
                    "You requested to delete IP ACGs, but you have not specified "
                    "any IP ACG id (e.g., wsipg-abc12d34e) to delete." 
            )

        if not dryrun:

                for directory in directories:
                    disassociate_ip_acg(delete_list)
                for ip_acg_id in delete_list:
                    delete_ip_acg(ip_acg_id)

    else:
        raise UnexpectedException("Unexpected error")
    
    logger.info(f"FINISH MODULE: AMAZON WORKSPACES IP ACG")
    logger.info(HR)
      

# ============================================================================

if __name__ == "__main__":
    main()


# TODO: directories vs workspace_directories: consistent
# TODO: Ruff checker
# TODO: consistent: rule vs ip rule
# TODO: consistent with arguments
# TODO: logs consistent language, debug also
# TODO: order of functions
# TODO: add default AWS exceptions?
# TODO: integrate main parts with extra layer?