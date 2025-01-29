import pytest
from pathlib import Path
import yaml
import sys
from dataclasses import asdict

from acgenius.validation.utils import (
    get_settings,
    val_settings_main_structure,
    val_settings_ip_acg_structure,
    get_validation_baseline,
    get_work_instruction,
    parse_settings,
    split_ip_and_prefix,
    remove_whitespaces
)
from acgenius.resources.models import Rule, IP_ACG, Directory, WorkInstruction, Validation, Settings

@pytest.fixture
def valid_settings():
    return {
        "ip_acgs": [],
        "tags": {},
        "directories": [],
        "user_input_validation": {
            "ip_address": {
                "invalid": [{"192.168.1.1": "test"}],
                "prefix": {"default": 32, "min": 24}
            },
            "ip_acg": {
                "rules_amt": {"max": 100},
                "rules_desc_length": {"max": 50},
                "name_length": {"max": 30}
            }
        }
    }

@pytest.mark.parametrize("settings_content,expected_exception", [
    # Valid YAML
    ({"key": "value"}, None),
    # Invalid YAML syntax
    ("invalid: yaml: content:", yaml.parser.ParserError),
])
def test_get_settings(tmp_path, monkeypatch, settings_content, expected_exception):
    settings_file = tmp_path / "settings.yaml"
    
    if isinstance(settings_content, dict):
        yaml.dump(settings_content, settings_file.open('w'))
    else:
        settings_file.write_text(settings_content)
    
    monkeypatch.setattr('acgenius.validation.utils.SETTINGS_FILE_PATH', str(settings_file))
    
    if expected_exception:
        with pytest.raises(SystemExit):
            get_settings()
    else:
        result = get_settings()
        assert result == settings_content

@pytest.mark.parametrize("settings,should_raise", [
    # All valid types
    ({"ip_acgs": [], "tags": {}, "directories": [], "user_input_validation": {}}, False),
    # Invalid ip_acgs type
    ({"ip_acgs": {}, "tags": {}, "directories": [], "user_input_validation": {}}, True),
    # Invalid tags type
    ({"ip_acgs": [], "tags": [], "directories": [], "user_input_validation": {}}, True),
    # Invalid directories type
    ({"ip_acgs": [], "tags": {}, "directories": {}, "user_input_validation": {}}, True),
    # Invalid user_input_validation type
    ({"ip_acgs": [], "tags": {}, "directories": [], "user_input_validation": []}, True),
])
def test_val_settings_main_structure(settings, should_raise):
    if should_raise:
        with pytest.raises(SystemExit):
            val_settings_main_structure(settings)
    else:
        val_settings_main_structure(settings)

@pytest.mark.parametrize("ip_acgs,should_raise", [
    # Valid structure
    ([{"name": "test", "desc": "test", "origin": "test", "rules": []}], False),
    # Missing name
    ([{"desc": "test", "origin": "test", "rules": []}], True),
    # Missing desc
    ([{"name": "test", "origin": "test", "rules": []}], True),
    # Missing origin
    ([{"name": "test", "desc": "test", "rules": []}], True),
    # Missing rules
    ([{"name": "test", "desc": "test", "origin": "test"}], True),
])
def test_val_settings_ip_acg_structure(valid_settings, ip_acgs, should_raise):
    valid_settings["ip_acgs"] = ip_acgs
    if should_raise:
        with pytest.raises(SystemExit):
            val_settings_ip_acg_structure(valid_settings)
    else:
        val_settings_ip_acg_structure(valid_settings)

def test_get_validation_baseline(valid_settings):
    result = get_validation_baseline(valid_settings)
    assert isinstance(result, Validation)
    assert len(result.invalid_rules) == 1
    assert result.rules_amt_max == 100
    assert result.rules_desc_length_max == 50
    assert result.prefix_default == 32
    assert result.prefix_min == 24
    assert result.ip_acg_name_length_max == 30

@pytest.mark.parametrize("settings_input,expected_result", [
    # Empty lists and dicts
    (
        {"directories": [], "ip_acgs": [], "tags": {}},
        WorkInstruction(directories=[], ip_acgs=[], tags={})
    ),
    # Valid directory and IP ACG
    (
        {
            "directories": [{"id": "1", "name": "test"}],
            "ip_acgs": [{
                "name": "test",
                "desc": "test",
                "origin": "test",
                "rules": [{"192.168.1.1": "test"}]
            }],
            "tags": {"key": "value"}
        },
        WorkInstruction(
            directories=[Directory(id="1", name="test")],
            ip_acgs=[IP_ACG(
                name="test",
                desc="test",
                origin="test",
                rules=[Rule(ip="192.168.1.1", desc="test")]
            )],
            tags={"key": "value"}
        )
    ),
])
def test_get_work_instruction(settings_input, expected_result):
    result = get_work_instruction(settings_input)
    assert asdict(result) == asdict(expected_result)

def test_parse_settings(valid_settings, monkeypatch):
    def mock_get_settings():
        return valid_settings
    
    monkeypatch.setattr('acgenius.validation.utils.get_settings', mock_get_settings)
    
    result = parse_settings()
    assert isinstance(result, Settings)
    assert isinstance(result.validation, Validation)
    assert isinstance(result.work_instruction, WorkInstruction)

@pytest.mark.parametrize("rule,expected_ip,expected_prefix", [
    # IP with prefix
    (Rule(ip="192.168.1.1/24", desc="test"), "192.168.1.1", 24),
    # IP without prefix
    (Rule(ip="192.168.1.1", desc="test"), "192.168.1.1", 32),
])
def test_split_ip_and_prefix(rule, expected_ip, expected_prefix):
    ip, prefix = split_ip_and_prefix(rule)
    assert ip == expected_ip
    assert prefix == expected_prefix

@pytest.mark.parametrize("input_ip,expected_ip", [
    # No whitespace
    ("192.168.1.1", "192.168.1.1"),
    # Single whitespace
    ("192.168.1.1 ", "192.168.1.1"),
    # Multiple whitespaces
    ("192. 168. 1. 1", "192.168.1.1"),
])
def test_remove_whitespaces(input_ip, expected_ip):
    rule = Rule(ip=input_ip, desc="test")
    result = remove_whitespaces(rule)
    assert result == expected_ip
