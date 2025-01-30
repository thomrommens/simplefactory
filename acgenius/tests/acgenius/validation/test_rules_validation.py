import pytest
from dataclasses import dataclass

from acgenius.resources.models import Rule, WorkInstruction, IP_ACG
from acgenius.validation.rules import (
    val_ip_linebreaks_absent,
    val_ip_format_correct,
    val_ip_allowed,
    val_prefix_allowed,
    val_rule_desc_length,
    val_rule_unique,
    val_amt_rules_allowed,
    val_rules
)

@dataclass
class MockValidation:
    invalid_rules: list
    prefix_min: int
    prefix_default: int
    rules_desc_length_max: int
    rules_amt_max: int
    groups_per_directory_amt_max: int

@dataclass
class MockSettings:
    validation: MockValidation

@pytest.mark.parametrize("ip,desc,expected", [
    # Valid IP without linebreaks
    ("192.168.1.1", "test", None),
    # IP with linebreak in middle
    ("192.168.1\n.1", "test", SystemExit),
    # IP with linebreak at end
    ("192.168.1.1\n", "test", SystemExit),
])
def test_val_ip_linebreaks_absent(ip, desc, expected):
    rule = Rule(ip=ip, desc=desc)
    if expected == SystemExit:
        with pytest.raises(SystemExit):
            val_ip_linebreaks_absent(rule)
    else:
        assert val_ip_linebreaks_absent(rule) == expected

@pytest.mark.parametrize("ip,expected", [
    # Valid IP address
    ("192.168.1.1", None),
    # Invalid format - extra digit
    ("192.168.1.256", SystemExit),
    # Invalid format - missing digit
    ("192.168.1", SystemExit),
    # Invalid format - letters
    ("192.168.1.abc", SystemExit),
    # Invalid format - special characters
    ("192.168.1.*", SystemExit),
])
def test_val_ip_format_correct(ip, expected):
    if expected == SystemExit:
        with pytest.raises(SystemExit):
            val_ip_format_correct(ip)
    else:
        assert val_ip_format_correct(ip) == expected

@pytest.mark.parametrize("ip,invalid_ips,expected", [
    # IP not in invalid list
    ("192.168.1.1", [], None),
    # IP in invalid list
    ("192.168.1.1", [Rule(ip="192.168.1.1", desc="invalid")], SystemExit),
])
def test_val_ip_allowed(ip, invalid_ips, expected):
    settings = MockSettings(
        validation=MockValidation(
            invalid_rules=invalid_ips,
            prefix_min=16,
            prefix_default=32,
            rules_desc_length_max=100,
            rules_amt_max=60,
            groups_per_directory_amt_max=25
        )
    )
    if expected == SystemExit:
        with pytest.raises(SystemExit):
            val_ip_allowed(ip, settings)
    else:
        assert val_ip_allowed(ip, settings) == expected

@pytest.mark.parametrize("prefix,prefix_min,prefix_default,expected", [
    # Valid prefix within range
    (24, 16, 32, None),
    # Prefix below minimum
    (8, 16, 32, SystemExit),
    # Prefix above maximum
    (48, 16, 32, SystemExit),
    # Prefix at minimum boundary
    (16, 16, 32, None),
    # Prefix at maximum boundary
    (32, 16, 32, None),
])
def test_val_prefix_allowed(prefix, prefix_min, prefix_default, expected):
    settings = MockSettings(
        validation=MockValidation(
            invalid_rules=[],
            prefix_min=prefix_min,
            prefix_default=prefix_default,
            rules_desc_length_max=100,
            rules_amt_max=60,
            groups_per_directory_amt_max=25
        )
    )
    if expected == SystemExit:
        with pytest.raises(SystemExit):
            val_prefix_allowed(prefix, settings)
    else:
        assert val_prefix_allowed(prefix, settings) == expected

@pytest.mark.parametrize("desc,max_length,expected", [
    # Description within limit
    ("Short description", 100, None),
    # Description at limit
    ("x" * 100, 100, None),
    # Description exceeding limit
    ("x" * 101, 100, SystemExit),
])
def test_val_rule_desc_length(desc, max_length, expected):
    rule = Rule(ip="192.168.1.1", desc=desc)
    settings = MockSettings(
        validation=MockValidation(
            invalid_rules=[],
            prefix_min=16,
            prefix_default=32,
            rules_desc_length_max=max_length,
            rules_amt_max=60,
            groups_per_directory_amt_max=25
        )
    )
    if expected == SystemExit:
        with pytest.raises(SystemExit):
            val_rule_desc_length(rule, settings)
    else:
        assert val_rule_desc_length(rule, settings) == expected

@pytest.mark.parametrize("rule_list,expected", [
    # No duplicates
    (["192.168.1.1/32", "192.168.1.2/32"], None),
    # Single duplicate
    (["192.168.1.1/32", "192.168.1.1/32"], SystemExit),
    # Multiple duplicates
    (["192.168.1.1/32", "192.168.1.1/32", "192.168.1.2/32", "192.168.1.2/32"], SystemExit),
    # Empty list
    ([], None),
])
def test_val_rule_unique(rule_list, expected):
    if expected == SystemExit:
        with pytest.raises(SystemExit):
            val_rule_unique(rule_list)
    else:
        assert val_rule_unique(rule_list) == expected

@pytest.mark.parametrize("rule_count,max_rules,expected", [
    # Valid number of rules
    (5, 60, None),
    # No rules
    (0, 60, SystemExit),
    # Maximum number of rules
    (60, 60, None),
    # Exceeding maximum
    (61, 60, SystemExit),
])
def test_val_amt_rules_allowed(rule_count, max_rules, expected):
    rule_list = ["192.168.1.1/32"] * rule_count
    settings = MockSettings(
        validation=MockValidation(
            invalid_rules=[],
            prefix_min=16,
            prefix_default=32,
            rules_desc_length_max=100,
            rules_amt_max=max_rules,
            groups_per_directory_amt_max=25
        )
    )
    if expected == SystemExit:
        with pytest.raises(SystemExit):
            val_amt_rules_allowed(rule_list, settings)
    else:
        assert val_amt_rules_allowed(rule_list, settings) == expected

@pytest.mark.parametrize("rules,expected", [
    # Valid work instruction
    ([Rule(ip="192.168.1.1", desc="test")], None),
    # Invalid IP format
    ([Rule(ip="192.168.1.256", desc="test")], SystemExit),
    # IP with linebreak
    ([Rule(ip="192.168.1\n.1", desc="test")], SystemExit),
])
def test_val_rules(rules, expected):
    settings = MockSettings(
        validation=MockValidation(
            invalid_rules=[],
            prefix_min=16,
            prefix_default=32,
            rules_desc_length_max=100,
            rules_amt_max=60,
            groups_per_directory_amt_max=25
        )
    )
    ip_acg = IP_ACG(name="test_acg", desc="test", rules=rules)
    work_instruction = WorkInstruction(ip_acgs=[ip_acg], directories=[], tags=[])
    
    if expected == SystemExit:
        with pytest.raises(SystemExit):
            val_rules(work_instruction, settings)
    else:
        result = val_rules(work_instruction, settings)
        assert isinstance(result, WorkInstruction)
        assert result.ip_acgs[0].desc == "test"
