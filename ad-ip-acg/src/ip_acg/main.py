import click

from config import HR, setup_logger
from exceptions import SomeException
from ip_acgs import delete, describe


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
    directories = {}

    # ip_acgs = describe()
    ip_acgs = {}

    
    
    # ------------------------------------------------------------------------   
    # SPECIFIC ROUTE
    # ------------------------------------------------------------------------   
    if action == "dry_run":
        # report on described directories/present IP ACGs
        # do not parse yaml
        pass
        
    if action in ("create, update"):
        # parse yaml
        # create/overwrite

        if action == "create":
            # associate
            pass

    elif action in ("delete"):
        if ip_acgs:
            # disassociate
            # delete()
            pass

    else:
        raise SomeException("Unexpected error")
    
    logger.info(f"FINISH MODULE: AMAZON WORKSPACES IP ACG")
    logger.info(HR)
      

if __name__ == "__main__":
    main()
