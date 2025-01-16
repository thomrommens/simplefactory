import click

from config import setup_logger
from exceptions import SomeException
from ip_acgs import delete, describe


@click.command()
@click.option(
    "--action", 
    type=click.Choice(
        ["dry_run", "create", "update", "delete"], 
        case_sensitive=False
    ), 
    default="dry_run", 
    help="Which action?"
)
@click.option(
    "--debug", 
    type=click.Choice(
        ["false", "true"], 
        case_sensitive=False
    ), 
    default="false", 
    help="Enable debug mode?"
)
def main(action, debug):
    """
    Integrate program.
    :param action: action requested by user on command line.
    """
    logger = setup_logger("ip_acg_logger")
    logger.info(f"{'=' * 70}")
    logger.info(f"START MODULE: AMAZON WORKSPACES IP ACG")

    logger.info(f"Selected action: [{action}]", extra={'depth': 1})
    logger.info(f"Debug mode enabled: [{debug}]", extra={'depth': 1})

    # ------------------------------------------------------------------------   
    # COMMON ROUTE (applied for all routes)   
    # ------------------------------------------------------------------------   
    # ip_acgs = describe()
    
    
    # ------------------------------------------------------------------------   
    # SPECIFIC ROUTE
    # ------------------------------------------------------------------------   
    if action == "dry_run":
        # report on described directories/present IP ACGs
        # do not parse yaml
        pass
        
    elif action in ("create, update"):
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
    logger.info(f"{'=' * 70}")
      

if __name__ == "__main__":
    main()
