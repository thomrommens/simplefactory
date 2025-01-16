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
def main(action):
    """
    Integrate program.
    :param action: action requested by user on command line.
    """
    logger = setup_logger("ip_acg_logger")

    click.echo(f"Action selected: {action}")

    logger.info(f"Selected route: [{action}]", extra={'depth': 1})

    # ------------------------------------------------------------------------   
    # COMMON ROUTE (applied for all routes)   
    # ------------------------------------------------------------------------   
    ip_acgs = describe()
    
    
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
      

if __name__ == "__main__":
    main()
