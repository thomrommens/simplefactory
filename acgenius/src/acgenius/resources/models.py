from dataclasses import dataclass
from typing import Optional


@dataclass
class Rule:
    """Rule = IP address + prefix"""
    ip: str
    desc: str


@dataclass
class IP_ACG:
    """
    Represent an IP Access Control Group for AWS WorkSpaces.
    
    Attributes:
        name: Name of the IP ACG
        desc: Description of the IP ACG
        rules: List of Rule objects containing IP addresses and descriptions
        id: Optional AWS resource ID of the IP ACG
        origin: Optional source/origin of the IP ACG configuration
    """
    name: str
    desc: str
    rules: list[Rule]
    id: Optional[str] = None
    origin: Optional[str] = None


@dataclass
class Directory:
    """
    Represent an AWS Directory Service directory.
    
    Attributes:
        id: AWS resource ID of the directory
        name: Name of the directory
        ip_acgs: Optional list of associated IP ACGs
        type: Optional directory type (e.g. Simple AD, AD Connector)
        state: Optional current state of the directory
    """
    id: str
    name: str
    ip_acgs: Optional[list[IP_ACG]] = None
    type: Optional[str] = None
    state: Optional[str] = None


@dataclass
class Validation:
    """
    Represent validation rules and constraints for IP ACG configuration.
    
    Attributes:
        invalid_rules: List of Rule objects that failed validation
        prefix_default: Default CIDR prefix length to use
        prefix_min: Minimum allowed CIDR prefix length
    """
    invalid_rules: list[Rule]
    prefix_default: str 
    prefix_min: str
    rules_amt_max: int
    rules_desc_length_max: int
    ip_acg_name_length_max: int
    # TODO: consistent order throughout code base


@dataclass
class WorkInstruction:
    """
    Represent desired configuration state for directories and IP ACGs.
    
    Attributes:
        directories: List of Directory objects to configure
        ip_acgs: List of IP_ACG objects to configure
        tags: Dictionary of tags to apply to resources
    """
    directories: list[Directory]
    ip_acgs: list[IP_ACG]
    tags: dict


@dataclass
class Inventory:
    """
    Represent current state of directories and IP ACGs in AWS.
    
    Attributes:
        directories: List of existing Directory objects
        ip_acgs: List of existing IP_ACG objects
    """
    directories: list[Directory]
    ip_acgs: list[IP_ACG]


@dataclass
class Settings:
    """
    Represent application settings and configuration.
    
    Attributes:
        validation: Validation rules and constraints
        work_instruction: Optional WorkInstruction for desired state
    """
    validation: Validation
    work_instruction: Optional[WorkInstruction] = None


@dataclass
class AppInput:
    """
    Represent all inputs needed to run the application.
    
    Attributes:
        cli: Dictionary of command line arguments
        settings: Settings object with validation and work instructions
        inventory: Inventory object with current AWS state
    """
    cli: dict
    settings: Settings
    inventory: Inventory
