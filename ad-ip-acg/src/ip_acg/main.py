# IMPORTS --------------------------------------------------------------------

from dataclasses import dataclass
import boto3
import logging


# CONSTANTS ------------------------------------------------------------------

CONFIG_FILE = ""
workspaces = boto3.client("workspaces", region_name="eu-west-1")


# MODULE CONFIG --------------------------------------------------------------

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


# EXCEPTION CLASSES ----------------------------------------------------------

class SomeException(Exception):
    pass


# DATACLASSES ----------------------------------------------------------------

@dataclass
class Rule:
    # Rule = IP address, or range of IP addresses
    pass


class IP_ACG:
    name: str
    desc: str
    origin: str
    rule_set: list


class WorkSpaceDirectory:
    id: str
    name: str
    type: str


@dataclass
class WorkInstruction:
    ip_acgs: list[IP_ACG]
    workspace_directories: list[WorkSpaceDirectory]


# HELPERS --------------------------------------------------------------------
# Module: read `````````````````````````````````````````````````````````````

def read_config():
    # yaml to dict
    # yaml.safe_load(file)
    pass


def read_validation_baseline():
    # yaml-dict to dict (select)
    return {
        "ip_address": {
            "invalid": {},
            "prefix": {
                "default": "",
                "min": "",
            }
        },
        "ip_acg_properties": {
            "name_char_length": {
                "max": ""
            },
            "rules_amt": {
                "max": ""
            }
        }
    }


def read_work_instruction():
    # yaml-dict to dataclasses
    # -> work_instruction_raw = WorkInstruction()

    # logger.debug("Received work_instruction:")
    pass


# Module: sanitize ``````````````````````````````````````````````````````````

def sanitize_rules():

    # dedup: set()
    # remove_whitespace: replace(" ", "")
    # remove_linebreaks: replace("\n", "")

    # populated?

    # split base ip and prefix:
    # fwd_slash = rule.find("/")
    # if fwd_slash != -1:
    #         address = self.input_rule[:fwd_slash]
    #         prefix = int(self.input_rule[fwd_slash+1:])
    #         return address, prefix
    #     else:
    #         return self.input_rule, DEFAULT_PREFIX

    # ipv4 match?
    # Ref regex pattern: https://stackoverflow.com/questions/5284147/validating-ipv4-
    #     addresses-with-regexp?page=1&tab=scoredesc#tab-top
    # pattern = r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$"
    #     address = self.split()[0]

    #     if re.match(pattern, address):
    #         return True

    # ip address not in invalid range
    # ip_address, _ = split()

    # prefix allowed
    #  _, ip_prefix = self.split()
    #     if ip_prefix >= IP_ADDRESS_PREFIX_MIN:
    #         return True

    
    # -> rule_cleansed = Rule()

    target_rule = {
        "ipRule": "key",
        "ruleDesc": "value__desc_from_rule_in_yaml"
    }

    target_rule_set_sorted = sorted(
        target_rule_set,
        key=lambda target_rule_set: target_rule_set["ipRule"]
    )

    # validate if any content in target_rule_set
    # validate if not larger than max number of IP rules
    pass


def sanitize_ip_acg():

    # not longer than name length?
    # not longer than description length?
    pass


def integrate():
    pass
    

def sanitize_work_instruction():
    # WorkInstructionRaw to WorkInstruction
    # -> work_instruction = WorkInstruction()
    #   -> ip_acg_raw = IP_ACG()
    #   -> workspace_directory_raw = WorkSpaceDirectory()

    # logger.debug("Sanitized work_instruction:")

    # TODO: sanitize prefix > 32 or < 0
    pass



# Module: workspace directories ``````````````````````````````````````````````

def get_workspace_directories():
    # if value in work_instruction for WorkSpaceDirectory, follow
    # else, get from AWS boto3

    response = workspaces.describe_workspace_directories()

    if response["Directories"]:
        return response
    else:
        raise SomeException()

    # collect raw info
    # logger.debug(Raw info)
    pass


def select_workspace_directories():
    # Required? Perhaps do anyway
    pass


def select_workspace_directory_info(workspace_directories):
    workspace_directories = []
    for workspace_directory in workspace_directories["Directories"]:
        workspace_directories.append(
            WorkSpaceDirectory(
                id=workspace_directory["DirectoryId"],
                name=workspace_directory["DirectoryName"],
                type=workspace_directory["DirectoryType"]
            )
        )
    return workspace_directories


# Module: ip acgs ````````````````````````````````````````````````````````````

def describe():
    response = workspaces.describe_ip_groups()
    ip_acgs = []
    for item in response.get("Result"):
        ip_acg = IP_ACG(            
            id=item.get("groupId"),
            name=item.get("groupName"),
            desc=""
        )


def create():
    response = workspaces.create_ip_group(
        GroupName=name,
        GroupDesc=desc,
        UserRules=rules,
        Tags=[{"Key": k, "Value": v} for k, v in tags.items()]
    )    
    ip_acg_id = response.get('GroupId')

    return ip_acg_id


def associate():
    response = workspaces.associate_ip_groups(
        DirectoryId=directory.id,
        GroupIds=group_id
    )


def update_rules():
    response = workspaces.update_rules_of_ip_group(
        GroupId=group_id,
        UserRules=rules
    )
    pass


def disassociate():
    response = workspaces.disassociate_ip_groups(
        DirectoryId=directory.id,
        GroupIds=group_ids
    )

def delete():
    # check if any exists
    workspaces.delete_ip_group(GroupId=group_id)



    



# MAIN -----------------------------------------------------------------------

def main():

    # Log
    logger = setup_logger('my_logger', logging.DEBUG)
    logger.debug('This is level 0 log', extra={'depth': 0})
    logger.info('This is level 1 log', extra={'depth': 1}) 

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


# RUN -----------------------------------------------------------------------

if __name__ == "__main__":
    main()
