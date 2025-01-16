from dataclasses import dataclass


@dataclass
class Rule:
    """Rule = IP address, or range of IP addresses"""
    pass


@dataclass
class IP_ACG:
    name: str
    desc: str
    origin: str
    rules: list[Rule]


@dataclass
class Directory:
    id: str
    name: str
    type: str


@dataclass
class WorkInstruction:
    ip_acgs: list[IP_ACG]
    directories: list[Directory]
