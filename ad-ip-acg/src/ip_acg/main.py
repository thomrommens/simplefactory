# TODO: Now
# TODO: - in work_instruction, also nest IP ACGs underneath directories? Currently None.
# TODO: - order of functions

# TODO: Intermediate
# TODO: - logs consistent language, debug also
# TODO: - check pipes in log
# TODO: - nest IP ACGs underneath directories? Currently None.

# TODO: Final
# TODO: - remove prints
# TODO: - check if both logger.error and raise are used
# TODO: - check if logger.debug properly covered
# TODO: - check if logger.debug properly displayed
# TODO: - consistent with arguments
# TODO: - check docstrings
# TODO: - check typing
# TODO: - Ruff checker
# TODO: - run black	
# TODO: - wrap at 88 (black)
# TODO: - check import types
# TODO: - replace xx
# TODO: - test generally in AWS
# TODO: - add deletion marker in tabulate
# TODO: - add specs of to-be-deleted IP ACGs
# TODO: - add status route to only show current state in AWS
# TODO: - consistent groups vs IP ACGs

import click

from config import HR, setup_logger, click_help
from routing.routes import run_common_route, run_selected_route

from resources.models import AppInput


@click.command()
@click.argument(
    "action", 
    type=click.Choice(
        ["create", "update", "delete"], 
        case_sensitive=False
    )
)
@click.argument(
    "ip_acg_ids_to_delete", 
    nargs=-1, 
    required=False,
)
@click.option("--dryrun",is_flag=True, default=False, help=click_help["dryrun"])
@click.option("--debug", is_flag=True, default=False, help=click_help["debug"])
def main(action: str, debug: bool, ip_acg_ids_to_delete: tuple, dryrun: bool) -> None:
    """
    Integrate app.
    :param action: action requested by user on command line.
    """
    logger = setup_logger("ip_acg_logger", debug)

    logger.info(HR)
    logger.info(f"START MODULE: AMAZON WORKSPACES IP ACG")
    logger.info(HR)

    logger.info(f"Selected action:        [{action}]", extra={"depth": 1})
    logger.info(f"Delete list of IP ACGs: [{ip_acg_ids_to_delete}]", extra={"depth": 1})
    logger.info(f"Dry run mode enabled:   [{dryrun}]", extra={"depth": 1})
    logger.info(f"Debug mode enabled:     [{debug}]", extra={"depth": 1})

    settings, inventory = run_common_route()

    app_input = AppInput(
        cli={
            "action": action,
                "dryrun": dryrun, 
                "ip_acg_ids_to_delete": ip_acg_ids_to_delete
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
