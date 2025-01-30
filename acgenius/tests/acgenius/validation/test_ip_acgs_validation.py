import pytest

from acgenius.resources.models import (
    IP_ACG, Settings, WorkInstruction, Inventory, Validation
)
from acgenius.validation.ip_acgs import (
    val_amt_groups_per_directory_allowed,
    val_ip_acg_name_length_allowed,
    val_ip_acg_name_unique,
    val_ip_acg_description_length_allowed,
    val_ip_acgs,
    val_ip_acgs_match_inventory
)


@pytest.fixture
def settings():
    validation_settings = Validation(
        ip_acg_name_length_max=32,
        rules_desc_length_max=100,
        invalid_rules=[],
        rules_amt_max=10,
        prefix_default="default_prefix",
        prefix_min=1,
        groups_per_directory_amt_max=25
    )
    return Settings(validation=validation_settings)


@pytest.mark.parametrize(
    "ip_acg_name_list,max_groups,should_raise",
    [
        # Empty list - valid
        ([], 5, False),
        # Single group - valid
        (["group1"], 5, False),
        # Multiple groups within limit - valid
        (["group1", "group2", "group3"], 5, False),
        # Exact limit - valid
        (["group1", "group2", "group3", "group4", "group5"], 5, False),
        # Exceeds limit by 1 - invalid
        (["group1", "group2", "group3", "group4", "group5", "group6"], 5, True),
        # Significantly exceeds limit - invalid
        (["group1", "group2", "group3", "group4", "group5", "group6", "group7", "group8"], 5, True),
    ]
)
def test_val_amt_groups_per_directory_allowed(ip_acg_name_list, max_groups, should_raise, settings):
    settings.validation.groups_per_directory_amt_max = max_groups
    
    if should_raise:
        with pytest.raises(SystemExit):
            val_amt_groups_per_directory_allowed(ip_acg_name_list, settings)
    else:
        val_amt_groups_per_directory_allowed(ip_acg_name_list, settings)

@pytest.mark.parametrize(
    "max_groups",
    [
        # Zero limit
        0,
        # Small limit
        1,
        # Large limit
        100,
    ]
)
def test_val_amt_groups_per_directory_allowed_different_limits(max_groups, settings):
    settings.validation.groups_per_directory_amt_max = max_groups
    ip_acg_name_list = ["group1"] * (max_groups + 1)
    
    with pytest.raises(SystemExit):
        val_amt_groups_per_directory_allowed(ip_acg_name_list, settings)


@pytest.mark.parametrize("name, max_length, should_raise", [        
    ("valid_name", 32, False),
    ("", 32, True),
    (None, 32, True),
    ("a" * 33, 32, True),
    ("a" * 32, 32, False),
])
def test_val_ip_acg_name_length_allowed(name, max_length, should_raise, settings):
    ip_acg = IP_ACG(name=name, desc="test description", rules=[])
    settings.validation.ip_acg_name_length_max = max_length
    
    if should_raise:
        with pytest.raises(SystemExit):
            val_ip_acg_name_length_allowed(ip_acg, settings)
    else:
        val_ip_acg_name_length_allowed(ip_acg, settings)

@pytest.mark.parametrize("name_list, should_raise", [
    (["group1", "group2", "group3"], False),
    (["group1", "group1", "group2"], True),
    (["group1", "group2", "group2", "group3", "group3"], True),
    ([], False),
    (["single_group"], False),
])
def test_val_ip_acg_name_unique(name_list, should_raise):
    if should_raise:
        with pytest.raises(SystemExit):
            val_ip_acg_name_unique(name_list)
    else:
        val_ip_acg_name_unique(name_list)

@pytest.mark.parametrize("desc, max_length, should_raise", [
    ("Valid description", 100, False),
    ("", 100, True),
    (None, 100, True),
    ("a" * 101, 100, True),
    ("a" * 100, 100, False),
])
def test_val_ip_acg_description_length_allowed(desc, max_length, should_raise, settings):
    ip_acg = IP_ACG(name="test_group", desc=desc, rules=[])
    settings.validation.rules_desc_length_max = max_length
    
    if should_raise:
        with pytest.raises(SystemExit):
            val_ip_acg_description_length_allowed(ip_acg, settings)
    else:
        val_ip_acg_description_length_allowed(ip_acg, settings)

@pytest.mark.parametrize("ip_acgs_data, should_raise", [
    ([("group1", "desc1"), ("group2", "desc2")], False),
    ([("group1", "desc1"), ("group1", "desc2")], True),
    ([("group1", "a" * 101), ("group2", "desc2")], True),
    ([], False),
])
def test_val_ip_acgs(ip_acgs_data, should_raise, settings):
    ip_acgs = [IP_ACG(name=name, desc=desc, rules=[]) for name, desc in ip_acgs_data]
    work_instruction = WorkInstruction(ip_acgs=ip_acgs, directories=[], tags=[])
    
    if should_raise:
        with pytest.raises(SystemExit):
            val_ip_acgs(work_instruction, settings)
    else:
        result = val_ip_acgs(work_instruction, settings)
        assert result == work_instruction

@pytest.mark.parametrize("matches, inventory_length, should_raise", [
    (3, 3, False),
    (2, 3, True),
    (0, 0, False),
    (5, 3, True),
    (0, 1, True),
])
def test_val_ip_acgs_match_inventory(matches, inventory_length, should_raise):
    inventory = Inventory(
        ip_acgs=[IP_ACG(name=f"group{i}", desc=f"desc{i}", rules=[]) for i in range(inventory_length)],
        directories=[]
    )
    
    if should_raise:
        with pytest.raises(SystemExit):
            val_ip_acgs_match_inventory(matches, inventory)
    else:
        val_ip_acgs_match_inventory(matches, inventory)
