import pytest
from datetime import datetime
from dataclasses import dataclass

from acgenius.resources.models import IP_ACG, Rule, Inventory, WorkInstruction
from acgenius.resources.ip_acgs.utils import match_ip_acgs, format_rules, extend_tags, format_tags


# @pytest.mark.parametrize("inventory_ip_acgs,work_instruction_ip_acgs,expected_ids", [
#     # Single match
#     ([IP_ACG(id="123", name="test1", desc="description1", rules=[])], 
#      [IP_ACG(id=None, name="test1", desc="description1", rules=[])],
#      ["123"]),
    
#     # Multiple matches
#     ([IP_ACG(id="123", name="test1", desc="description1", rules=[]), 
#       IP_ACG(id="456", name="test2", desc="description2", rules=[])],
#      [IP_ACG(id=None, name="test1", desc="description1", rules=[]),
#       IP_ACG(id=None, name="test2", desc="description2", rules=[])],
#      ["123", "456"]),
    
#     # No matches
#     ([IP_ACG(id="123", name="test1", desc="description1", rules=[])],
#      [IP_ACG(id=None, name="test2", desc="description2", rules=[])],
#      [None]),
    
#     # Empty lists
#     ([], [], []),
# ])
# def test_match_ip_acgs(inventory_ip_acgs, work_instruction_ip_acgs, expected_ids):
#     inventory = Inventory(ip_acgs=inventory_ip_acgs, directories=[])
#     work_instruction = WorkInstruction(ip_acgs=work_instruction_ip_acgs, directories=[], tags=[])

#     if len(work_instruction_ip_acgs) > 0:
#         with pytest.raises(SystemExit):
#             match_ip_acgs(inventory, work_instruction)

#     if len(inventory_ip_acgs) > 0:
#         result = match_ip_acgs(inventory, work_instruction)
#         for ip_acg, expected_id in zip(result.ip_acgs, expected_ids):
#             assert ip_acg.id == expected_id


@pytest.mark.parametrize("rules,expected", [
    # Single rule
    ([Rule(ip="192.168.1.0/24", desc="Test rule")],
     [{"ipRule": "192.168.1.0/24", "ruleDesc": "Test rule"}]),
    
    # Multiple rules, verify sorting
    ([Rule(ip="192.168.2.0/24", desc="Second rule"),
      Rule(ip="192.168.1.0/24", desc="First rule")],
     [{"ipRule": "192.168.1.0/24", "ruleDesc": "First rule"},
      {"ipRule": "192.168.2.0/24", "ruleDesc": "Second rule"}]),
    
    # Empty rules
    ([], []),
])
def test_format_rules(rules, expected):
    ip_acg = IP_ACG(id="123", name="test", desc="description", rules=rules)
    result = format_rules(ip_acg)
    assert result == expected


@pytest.mark.parametrize("initial_tags,ip_acg_name,expected_keys", [
    # Empty initial tags
    ({}, "test-acg", ["IPACGName", "Created"]),
    
    # Existing tags
    ({"Environment": "prod"}, "test-acg", ["Environment", "IPACGName", "Created"]),
])
def test_extend_tags(initial_tags, ip_acg_name, expected_keys):
    ip_acg = IP_ACG(id="123", name=ip_acg_name, desc="description", rules=[])
    result = extend_tags(initial_tags, ip_acg)
    
    assert set(result.keys()) == set(expected_keys)
    assert result["IPACGName"] == ip_acg_name
    assert datetime.fromisoformat(result["Created"])


@pytest.mark.parametrize("input_tags,expected", [
    # Single tag
    ({"key1": "value1"},
     [{"Key": "key1", "Value": "value1"}]),
    
    # Multiple tags
    ({"key1": "value1", "key2": "value2"},
     [{"Key": "key1", "Value": "value1"},
      {"Key": "key2", "Value": "value2"}]),
    
    # Empty tags
    ({}, []),
])
def test_format_tags(input_tags, expected):
    result = format_tags(input_tags)
    assert sorted(result, key=lambda x: x["Key"]) == sorted(expected, key=lambda x: x["Key"])
