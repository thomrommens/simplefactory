# TODO: directories vs workspace_directories: consistent
# TODO: Ruff checker
# TODO: consistent: rule vs ip rule
# TODO: consistent with arguments
# TODO: logs consistent language, debug also
# TODO: order of functions
# TODO: add default AWS exceptions?
# TODO: integrate main parts with extra layer?
# TODO: abstract routes in main away, to modules
# TODO: abstract messages away to feedback.py
# TODO: order of functions/split to utils?
# TODO: more try/catch approach to be able to skip and continue
# TODO: try/except for responses
# TODO: sort retrieved responses/dataclasses to consistently keep order in showing current vs. to be created
# TODO: in work_instruction, also nest IP ACGs underneath directories? Currently None.
# TODO: check pipes in log
# TODO: consistent 'program' vs. 'app'
# TODO: remove prints

import click

from config import HR, setup_logger
from routes import run_common_route, run_selected_route
from feedback import msg
from models import AppInput


@click.command()
@click.option(
    "--action", 
    type=click.Choice(
        ["create", "update", "delete"], 
        case_sensitive=False
    ), 
    default="create", 
    help=msg["click_options"]["action"]
)
@click.option(
    "--dryrun", 
    type=bool,
    default=True,
    help=msg["click_options"]["dryrun"]
)
@click.option(
    "--debug", 
    type=bool,
    default=False,
    help=msg["click_options"]["debug"]
)
@click.option(
    "--delete_list", 
    multiple=True, # TODO: check type
    default=[],
    help=msg["click_options"]["delete_list"]
)
def main(action: str, dryrun: bool, debug: bool, delete_list: list) -> None:
    """
    Integrate program.
    :param action: action requested by user on command line.
    """
    logger = setup_logger("ip_acg_logger", debug)

    logger.info(HR)
    logger.info(f"START MODULE: AMAZON WORKSPACES IP ACG")
    logger.info(HR)

    logger.info(f"Selected action:      [{action}]", extra={"depth": 1})
    logger.info(f"Dry run mode enabled: [{dryrun}]", extra={"depth": 1})
    logger.info(f"Delete list supplied: [{delete_list}]", extra={"depth": 1})
    logger.info(f"Debug mode enabled:   [{debug}]", extra={"depth": 1})

    settings, inventory = run_common_route()

    app_input = AppInput(
        cli={
            "action": action,
                "dryrun": dryrun, 
                "delete_list": delete_list
        },
        settings=settings,
        inventory=inventory
    )
    
    run_selected_route(app_input)

    logger.info(HR) 
    logger.info(f"FINISH MODULE: AMAZON WORKSPACES IP ACG")
    logger.info(HR) 
    

if __name__ == "__main__":
    main()
