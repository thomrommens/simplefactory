import click
import prettyprinter as pp

from config import HR, setup_logger
from interpretation import get_settings
from exceptions import SomeException
from directories import get_directories, sel_directories
from ip_acgs import get_ip_acgs, sel_ip_acgs


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
    logger = setup_logger("ip_acg_logger")

    logger.info(HR)
    logger.info(f"START MODULE: AMAZON WORKSPACES IP ACG")
    logger.info(f"Selected action:      [{action}]", extra={'depth': 1})
    logger.info(f"Dry run mode enabled: [{dryrun}]", extra={'depth': 1})
    logger.info(f"Debug mode enabled:   [{debug}]", extra={'depth': 1})

    # ------------------------------------------------------------------------   
    # COMMON ROUTE (applied for all routes)   
    # ------------------------------------------------------------------------   
    
    directories_received = get_directories()
    directories = sel_directories(directories_received)
    pp.pprint(directories, width=1)

    ip_acgs_received = get_ip_acgs()
    ip_acgs = sel_ip_acgs(ip_acgs_received)
    pp.pprint(ip_acgs, width=1)

    settings = get_settings()

    # ------------------------------------------------------------------------   
    # SPECIFIC ROUTE
    # ------------------------------------------------------------------------   
        
    if action in ("create, update"):
        # I would do this: ...

        if not dryrun:
            # I do this: ...
            
            # create/overwrite
            if action == "create":
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
      

if __name__ == "__main__":
    main()


# TODO: directories vs workspace_directories: consistent
# TODO: integrate logger across module
# TODO: Ruff checker
# TODO: remove prints