import logging
import sys
from textwrap import indent
from typing import Union
import pandas as pd
from tabulate import tabulate

from resources.ip_acgs.utils import format_rules
from resources.models import Directory, IP_ACG


logger = logging.getLogger("acgenius")


def specify_report(item: Union[Directory, IP_ACG]) -> dict:
    """
    xx
    """
    logger.debug(f"Specify report...", extra={"depth": 2})
    
    if isinstance(item, IP_ACG):
        return {
            "description": item.desc,
        }
    elif isinstance(item, Directory):
        return {
            "ip_acgs_associated": item.ip_acgs,
            "type": item.type,
            "state": item.state
        }


def create_report(
        subject: Union[list[Directory], list[IP_ACG]],
        origin: str
    ) -> None:
    """
    Report a ...
    Rules is nested within IP_ACG, so no separate argument.
    """
    logger.debug(f"Create report...", extra={"depth": 1})

    data = []
    fmt = "psql" if origin == "work_instruction" else "fancy_grid"

    if subject:

        i = 0
        for item in subject:
            i += 1
            row = {"id": item.id, "name": item.name}
            row.update(specify_report(item))
            data.append(row)

            df = pd.DataFrame(data)
            icon = "□" if isinstance(item, Directory) else "■"
            df.index = [f"{icon} {i}"]
            subject_table = f"{tabulate(df, headers='keys', tablefmt=fmt)}"

            if isinstance(item, IP_ACG):
                
                rules_formatted = format_rules(item)
                rules_table = [["rule", "description"]]

                for item in rules_formatted:
                    rules_table.append([item["ipRule"], item["ruleDesc"]])

                rules_table = tabulate(rules_table, headers="firstrow", tablefmt=fmt)
                print(subject_table)
                print("\____")
                print(indent(rules_table, " " * 6))
                print("\n")
                data = []

            else:
                print(f"\n{subject_table}\n")

    else:
        logger.warning(f"No item found for report.", extra={"depth": 1})


def exit_app() -> None:
    """
    Gently exit app (preventing full stack trace)
    """
    logger.info(
        f"Exiting app.",                
        extra={"depth": 1}
    )
    sys.exit(1)