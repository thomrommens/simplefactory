from dataclasses import dataclass
from config import setup_logger
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
    rule_set: list

@dataclass
class WorkSpaceDirectory:
    id: str
    name: str
    type: str


@dataclass
class WorkInstruction:
    ip_acgs: list[IP_ACG]
    workspace_directories: list[WorkSpaceDirectory]


def main():
    logger = setup_logger('my_logger', logging.DEBUG)
    
    # Get user defined arguments from click 
    # - https://click.palletsprojects.com/en/stable/

    # Validate cmd line arguments
    # route unrecognized; raise error
    
    # Pick route for action = create/update/delete
    # create/update:
    #   - parse yaml
    #   - create/overwrite
    # delete:
    #   - default: deletes all!
    #   - disassociate
    #   - delete
    # check if IP ACG already exists, at any route; switch route accordingly


    # TODO if modify route, apply tag ModifiedBy
    # TODO add dryrun (describe)?
    # TODO: consistent naming 'rule' vs ip address
    # TODO: 'workspace_directory' -> 'directory'
    pass


if __name__ == "__main__":
    main()
