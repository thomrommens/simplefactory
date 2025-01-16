import click
from config import setup_logger
from dataclasses import dataclass
import logging


class SomeException(Exception):
    # TODO
    pass


@dataclass
class Rule:
    """Rule = IP address, or range of IP addresses"""
    pass


@dataclass
class IP_ACG:
    name: str
    desc: str
    origin: str
    rules: list[Rule]


@dataclass
class Directory:
    id: str
    name: str
    type: str


@dataclass
class WorkInstruction:
    ip_acgs: list[IP_ACG]
    directories: list[Directory]


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
    logger = setup_logger("my_logger", logging.DEBUG)

    click.echo(f"Action selected: {action}")

    logger.info(f"Selected route: [{action}]", extra={'depth': 1})

    # ------------------------------------------------------------------------   
    # COMMON ROUTE (applied for all routes)   
    # ------------------------------------------------------------------------   
    # describe directories/present IP ACGs
    
    
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
        # disassociate
        # delete
        pass

    else:
        raise SomeException("Unexpected error")
      

if __name__ == "__main__":
    main()
