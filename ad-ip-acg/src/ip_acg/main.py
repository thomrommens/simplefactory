from dataclasses import asdict
import json
import click

from config import HR, setup_logger
from interpretation import (
    get_settings, 
    get_validation_baseline, 
    get_work_instruction
)
from exceptions import SomeException
from directories import get_directories, sel_directories
from ip_acgs import get_ip_acgs, sel_ip_acgs
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
        ["true", "false"], 
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
def main(action, dryrun, debug):
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
    # # Directories
    # directories_received = get_directories()
    # directories = sel_directories(directories_received)
    # directories_as_dict = [asdict(directory) for directory in directories]
    # logger.debug(
    #     f"Directories found in AWS:\n{json.dumps(directories_as_dict, indent=4)}", 
    #     extra={"depth": 1}
    # )

    # # IP ACGs
    # ip_acgs_received = get_ip_acgs()
    # ip_acgs = sel_ip_acgs(ip_acgs_received)
    # ip_acgs_as_dict = [asdict(ip_acg) for ip_acg in ip_acgs]
    # logger.debug(
    #     f"IP ACGs found in AWS:\n{json.dumps(ip_acgs_as_dict, indent=4)}", 
    #     extra={"depth": 1}
    # )   
    
    # Settings retrieval
    settings = get_settings()
    logger.debug(
        f"Settings retrieved from YAML file:\n{json.dumps(settings, indent=4)}", 
        extra={"depth": 1}
    )

    # - validation baseline
    validation_baseline = get_validation_baseline(settings)
    logger.debug(
        f"Validation baseline parsed from YAML file:\n{json.dumps(asdict(validation_baseline), indent=4)}", 
        extra={"depth": 1}
    )   

    # - work instruction
    work_instruction_raw = get_work_instruction(settings)
    logger.debug(
        f"Work instruction parsed from YAML file:\n{json.dumps(asdict(work_instruction_raw), indent=4)}", 
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

     
    # ------------------------------------------------------------------------   
    # SPECIFIC ROUTE
    # ------------------------------------------------------------------------   
        
    if action in ("create, update"):
        # I would do this: ...

        if not dryrun:
            # I do this: ...
            
            # create/overwrite
            if action == "create":
                # create
                # associate
                pass

    elif action in ("delete"):
        if ip_acgs:
            # I would do this: ...

            if not dryrun:
            # I do this: ...
            # disassociate
            # delete()
                pass

    else:
        raise SomeException("Unexpected error")
    
    logger.info(f"FINISH MODULE: AMAZON WORKSPACES IP ACG")
    logger.info(HR)
      

# ============================================================================

if __name__ == "__main__":
    main()


# TODO: directories vs workspace_directories: consistent
# TODO: integrate logger across module
# TODO: Ruff checker
# TODO: remove prints
# TODO: consistent: rule vs ip rule