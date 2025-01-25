# TODO: Now
# TODO: - in work_instruction, also nest IP ACGs underneath directories? Currently None.
# TODO: - try/except for responses
# TODO:     - add default AWS exceptions?
# TODO: - order of functions/split to utils?

# TODO: Intermediate
# TODO: - logs consistent language, debug also
# TODO: - check pipes in log

# TODO: Final
# TODO: - remove prints
# TODO: - consistent with arguments
# TODO: - check docstrings
# TODO: - check typing
# TODO: - Ruff checker

import click

from config import HR, setup_logger
from routes import run_common_route, run_selected_route
from feedback import msg
from models import AppInput

# TODO: cont - enable 
# - python -m main create
# - python -m main update 
# - python -m main delete --list 1234567890, 1234567891
# - python -m main action -debug 
# - python -m main action -dryrun

@click.command()
@click.argument(
    "action",
    type=click.Choice(
        ["create", "update", "delete"],
        case_sensitive=False
    ),
    default="create"
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
    multiple=True,
    default=[],
    help=msg["click_options"]["delete_list"]
)
def main(action: str, dryrun: bool, debug: bool, delete_list: list) -> None:
    """
    Integrate app.
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
