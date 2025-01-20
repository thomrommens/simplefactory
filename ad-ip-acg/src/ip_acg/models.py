from dataclasses import dataclass
from typing import Optional


@dataclass
class Rule:
    """Rule = IP address, or range of IP addresses"""
    ip: str
    desc: str


@dataclass
class IP_ACG:
    name: str
    desc: str
    rules: list[Rule]
    id: Optional[str] = None  # TODO keep?
    origin: Optional[str] = None # TODO keep?


@dataclass
class Directory:
    id: str
    name: str
    ip_acgs: Optional[list[IP_ACG]] = None
    type: Optional[str] = None
    state: Optional[str] = None


@dataclass
class Validation:
    invalid_rules: list[Rule]
    prefix_default: str 
    prefix_min: str


@dataclass
class WorkInstruction:
    directories: list[Directory]
    ip_acgs: list[IP_ACG]
    tags: dict
    