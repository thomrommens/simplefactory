import boto3
import logging


CONFIG_FILE = ""

workspaces = boto3.client("workspaces", region_name="eu-west-1")


class DepthFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        pipes = '|' * getattr(record, 'depth', 0)
        record.msg = f'{pipes} {record.msg}'
        return super().format(record)

def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)

    formatter = DepthFormatter(
        '[%(asctime)s] [%(levelname)s] - %(message)s', "%Y-%m-%d %H:%M:%S"
    )
    ch.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(ch)

    return logger


class NoTargetDirectoryFoundException(Exception):
    pass


class RuleSetEmptyException(Exception):
    pass


class RuleSetTooManyEntriesException(Exception):
    pass


class IpAcgNameTooLongException(Exception):
    pass




# main logic
## validators
## workflow components


# workflow


def main():

    # Log
    logger = setup_logger('my_logger', logging.DEBUG)
    logger.debug('This is level 0 log', extra={'depth': 0})
    logger.info('This is level 1 log', extra={'depth': 1})


    # Workflow
    # - Get user defined arguments from click 
    #   - https://click.palletsprojects.com/en/stable/
    #   - specified route (if not recognized, raise error from click)

    # - If/else for route create/modify/delete

    # CREATE
    # - get input: workspace dirs specified?
    #   - yes: use these
    #   - no: get dirs


    # TODO if modify route, apply tag ModifiedBy
    # TODO add dryrun (describe)?
    # TODO: consistent naming 'rule' vs ip address


    pass


if __name__ == "__main__":
    main()