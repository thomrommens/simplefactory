import logging
from textwrap import indent
from typing import Union
import pandas as pd
from tabulate import tabulate

from acgenius.resources.ip_acgs.utils import format_rules
from acgenius.resources.models import IP_ACG, Directory

logger = logging.getLogger("acgenius")


def specify_report(item: Union[Directory, IP_ACG]) -> dict:
    """
    Specify report for a given item (in order to add to generic report downstream).

    :param item: Directory or IP_ACG
    :return: dictionary with report specification (addition)
    """
    logger.debug("Set report specs...", extra={"depth": 2})

    if isinstance(item, IP_ACG):
        return {
            "description": item.desc,
        }
    elif isinstance(item, Directory):
        return {
            "ip_acgs_associated": item.ip_acgs,
            "type": item.type,
            "state": item.state,
        }


def create_report(subject: Union[list[Directory], list[IP_ACG]], origin: str) -> None:
    """
    Create a report for a given subject.

    :param subject: list of Directories or IP_ACGs
    :param origin: origin of the report
    """
    logger.debug("Create report...", extra={"depth": 1})

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
        logger.warning("No item found for report.", extra={"depth": 1})
