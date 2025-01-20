from dataclasses import asdict
import json
import re

from exceptions import (
    IPACGAmtRulesException, 
    IPACGDescriptionLengthException, 
    IPACGDuplicateRulesException, 
    IPACGNameLengthException, 
    RulePrefixInvalidException, 
    RuleIPV4FormatInvalidException, 
    RuleLinebreakException
)
from models import IP_ACG, Directory, Rule, WorkInstruction


# ****************************************************************************
# Input
# ****************************************************************************

work_instruction_raw = WorkInstruction(
    
    directories=[Directory(id='None', name='None', ip_acgs=None, type=None, state=None)], 
    
    ip_acgs=[
        IP_ACG(
            name='Domain A', 
            desc='Allowed inbound IP addresses from Domain A', 
            rules=[
                Rule(
                    ip='222.204.240.123', 
                    desc='This trusted single host'
                ), 
                Rule(ip='254.254.253.251/27', desc='That trusted series of hosts'), Rule(ip='1.1.1.1/30', desc='This trusted series of hosts'), Rule(ip='2.2.2.2', desc='That trusted host'), Rule(ip='3.4.5.6', desc='Yet another trusted host')], 
            id=None, origin='This Department'), 
        IP_ACG(
            name='Domain B', desc='Allowed inbound IP addresses from Domain B', rules=[Rule(ip='5.6.7.8', desc='This trusted single host'), Rule(ip='99.77.66.55/27', desc='That trusted series of hosts'), Rule(ip='12.34.56.78/30', desc='This trusted series of hosts'), Rule(ip='77.88.99.67', desc='That trusted host'), Rule(ip='2.3.4.5', desc='Yet another trusted host')], id=None, origin='That Department')], 
    
    tags={'IPACGName': 'placeholder', 'Application': 'WorkSpacesEnv', 'Environment': 'test', 'Department': 'ThatDepartment', 'CostCenter': 'ThatCostCenter', 'CreatedBy': 'IP ACG module', 'ModifiedBy': 'IP ACG module', 'Created': 'placeholder', 'RuleSetLastApplied': 'placeholder'})


print("Work instruction before:")
print(json.dumps(asdict(work_instruction_raw), indent=4))


# ****************************************************************************
# Validate RULE level
# ****************************************************************************

def split_base_ip_and_prefix(rule: str):

    fwd_slash = rule.ip.find("/")

    if fwd_slash != -1:
        base_ip = rule.ip[:fwd_slash]
        prefix = int(rule.ip[fwd_slash+1:])

    else:
        base_ip = rule.ip
        prefix = 32  # TODO replace with dynamic value

    return base_ip, prefix


def remove_whitespaces(rule):
    print(f"| | | | Remove whitespaces if any...")
    return rule.ip.replace(" ", "")


def validate_linebreaks_absent(rule) -> bool:

    print(f"| | | | Validate if no linebreaks are found...")
    if "\n" in rule.ip:
        raise RuleLinebreakException("Line break found in IP rule [{rule}].")
    

def validate_ipv4_format(base_ip: str) -> bool:
    """
    Ref regex pattern: https://stackoverflow.com/questions/5284147/validating-ipv4-addresses-with-regexp?page=1&tab=scoredesc#tab-top
    Checks for population?
    """       
    print(f"| | | | Validate IPv4 format for base_ip [{base_ip}]...")
    
    pattern = r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$"

    if not re.match(pattern, base_ip):
        raise RuleIPV4FormatInvalidException(
            f"Base IP address is invalid. Please revise settings.yaml."
        )
        # TODO: check if populated included?


def validate_prefix(prefix) -> bool:
    print(f"| | | | Validate prefix [{prefix}]...")
    if not 27 <= prefix <= 32:  # TODO replace with dynamic values
        raise RulePrefixInvalidException(
            f"Prefix [{prefix}] is invalid. Please revise settings.yaml."
        )
    
# TODO: limit of rule description length?

# ----------------------------------------------------------------------------

def validate_rules(work_instruction: WorkInstruction) -> WorkInstruction:
    """
    """
    print(f"| Start: validate IP rules of settings.yaml...")
    for ip_acg in work_instruction.ip_acgs: 
        
        print(f"| | Start: IP ACG [{ip_acg.name}]...")
        for rule in ip_acg.rules: 
            print(f"| | | Start: Rule: IP address [{rule.ip}]; description [{rule.desc}]...")
            
            rule.ip = remove_whitespaces(rule)

            validate_linebreaks_absent(rule)

            base_ip, _ = split_base_ip_and_prefix(rule)
            _, prefix = split_base_ip_and_prefix(rule)

            validate_ipv4_format(base_ip)
            validate_prefix(prefix)
            print(f"| | Finish: IP ACG [{ip_acg.name}]...")

    print(f"| Finish: validate IP rules of settings.yaml...")
    return work_instruction
  

# ****************************************************************************
# Validate IP ACG level
# ****************************************************************************

def validate_no_dup_rules(ip_acg):
    """
    Validate no duplicate rules in rule list per IP ACG.
    """
    print(f"| | | Validate that there are no duplicate rules within the IP ACG...")
    # if not len(ip_acg.rules) == len(set(ip_acg.rules)):  # TODO update walk through for set
    #     raise IPACGDuplicateRulesException("XX")


def validate_amt_rules(ip_acg):
    """
    Validate if not larger than max number of IP rules.
    """
    print(f"| | | Validate that the maximum number of IP rules is 10 or less...")  # TODO dynamic
    if not len(ip_acg.rules) <= 10:
        raise IPACGAmtRulesException("XX")


def validate_group_name(ip_acg):
    """
    Validate if IP ACG name not longer than name length.
    """
    print(f"| | | Validate that the IP ACG name length is not longer than 50 characters...") # TODO dynamic
    if not len(ip_acg.name) <= 50:
        raise IPACGNameLengthException("XX")


def validate_group_desc(ip_acg):
    """
    Validate if IP ACG description not longer than description length.
    """
    print(f"| | | Validate that the IP ACG description is not longer than 255 characters...") # TODO check + include in settings.json + dynamic
    if not len(ip_acg.name) <= 255:
        raise IPACGDescriptionLengthException("XX")

# ----------------------------------------------------------------------------

def validate_ip_acgs(work_instruction_raw):
    print(f"| Start: validate IP ACG properties of settings.yaml...")
    
    for ip_acg in work_instruction_raw.ip_acgs: 
        print(f"| | Start: IP ACG [{ip_acg.name}]...")

        validate_no_dup_rules(ip_acg)
        validate_amt_rules(ip_acg)
        validate_group_name(ip_acg)
        validate_group_desc(ip_acg)

    return work_instruction_raw
    

# ****************************************************************************

def validate_work_instruction(work_instruction_raw):
    work_instruction_rules_validated = validate_rules(work_instruction_raw)
    work_instruction_ip_acgs_validated = validate_ip_acgs(work_instruction_rules_validated)

    return work_instruction_ip_acgs_validated


# TODO: update work_instruction vs. work_instruction_raw
# TODO: replace prints with logger
