# TODO:         - import order

# TODO: - update docstrings
# TODO: update README.md

import click

from acgenius.config import HR, setup_logger, click_help
from acgenius.routing.routes import run_common_route, run_selected_route
from acgenius.resources.models import AppInput


@click.command()
@click.argument(
    "action", 
    type=click.Choice(
        ["status", "create", "update", "delete"], 
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
def main(action: str, ip_acg_ids_to_delete: tuple, dryrun: bool, debug: bool) -> None:
    """
    Integrate app.
    :param action: action requested by user on command line.
    """
    logger = setup_logger("acgenius", debug)

    logger.info(HR)
    logger.info("START APP: ACGENIUS...")
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
    logger.info("FINISH APP: ACGENIUS.")
    logger.info(HR) 
    

if __name__ == "__main__":
    main()
