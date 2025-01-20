from dataclasses import dataclass


@dataclass
class Rule:
    """Rule = IP address, or range of IP addresses"""
    ip: str
    desc: str


@dataclass
class IP_ACG:
    id: str
    name: str
    desc: str
    rules: list[Rule]
    origin: str = None # TODO keep?


@dataclass
class Directory:
    id: str
    name: str
    type: str
    state: str
    ip_acgs: list[IP_ACG]


@dataclass
class WorkInstruction:
    ip_acgs: list[IP_ACG]
    directories: list[Directory]
