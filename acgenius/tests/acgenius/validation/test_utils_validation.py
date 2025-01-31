import pytest
import yaml
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
from acgenius.resources.models import (
    Rule, IP_ACG, Directory, WorkInstruction, Validation, Settings
)


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
                "name_length": {"max": 30},
                "groups_per_directory_amt": {"max": 25}
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


@pytest.mark.parametrize("settings", [
    # All valid types
    {"ip_acgs": [], "tags": {}, "directories": [], "user_input_validation": {}},
    # All valid types with content
    {"ip_acgs": [{"name": "test"}], "tags": {"env": "prod"}, "directories": [{"id": 1}], "user_input_validation": {"key": "val"}},
])
def test_val_settings_main_structure_valid(settings):
    val_settings_main_structure(settings)

@pytest.mark.parametrize("settings, invalid_key", [
    # ip_acgs wrong type
    ({"ip_acgs": {}, "tags": {}, "directories": [], "user_input_validation": {}}, "ip_acgs"),
    ({"ip_acgs": None, "tags": {}, "directories": [], "user_input_validation": {}}, "ip_acgs"),
    ({"ip_acgs": "wrong", "tags": {}, "directories": [], "user_input_validation": {}}, "ip_acgs"),
    # tags wrong type
    ({"ip_acgs": [], "tags": [], "directories": [], "user_input_validation": {}}, "tags"),
    ({"ip_acgs": [], "tags": None, "directories": [], "user_input_validation": {}}, "tags"),
    ({"ip_acgs": [], "tags": "wrong", "directories": [], "user_input_validation": {}}, "tags"),
    # directories wrong type
    ({"ip_acgs": [], "tags": {}, "directories": {}, "user_input_validation": {}}, "directories"),
    ({"ip_acgs": [], "tags": {}, "directories": None, "user_input_validation": {}}, "directories"),
    ({"ip_acgs": [], "tags": {}, "directories": "wrong", "user_input_validation": {}}, "directories"),
    # user_input_validation wrong type
    ({"ip_acgs": [], "tags": {}, "directories": [], "user_input_validation": []}, "user_input_validation"),
    ({"ip_acgs": [], "tags": {}, "directories": [], "user_input_validation": None}, "user_input_validation"),
    ({"ip_acgs": [], "tags": {}, "directories": [], "user_input_validation": "wrong"}, "user_input_validation"),
])
def test_val_settings_main_structure_invalid_types(settings, invalid_key):
    with pytest.raises(SystemExit):
        val_settings_main_structure(settings)

@pytest.mark.parametrize("settings, missing_key", [
    # Missing ip_acgs
    ({"tags": {}, "directories": [], "user_input_validation": {}}, "ip_acgs"),
    # Missing tags
    ({"ip_acgs": [], "directories": [], "user_input_validation": {}}, "tags"),
    # Missing directories
    ({"ip_acgs": [], "tags": {}, "user_input_validation": {}}, "directories"),
    # Missing user_input_validation
    ({"ip_acgs": [], "tags": {}, "directories": []}, "user_input_validation"),
    # Empty dict
    ({}, "ip_acgs"),
])
def test_val_settings_main_structure_missing_keys(settings, missing_key):
    with pytest.raises(SystemExit):
        val_settings_main_structure(settings)


@pytest.mark.parametrize("settings", [
    # Valid case with single IP ACG containing all required keys
    {"ip_acgs": [{"name": "test", "desc": "test", "origin": "test", "rules": []}]},
    # Valid case with multiple IP ACGs
    {"ip_acgs": [
        {"name": "test1", "desc": "test1", "origin": "test1", "rules": []},
        {"name": "test2", "desc": "test2", "origin": "test2", "rules": []}
    ]},
])
def test_val_settings_ip_acg_structure_valid(settings):
    val_settings_ip_acg_structure(settings)

@pytest.mark.parametrize("settings, expected_error", [
    # Empty IP ACGs list with None
    ({"ip_acgs": [None]}, "SettingsYAMLIPACGNoKeysException"),
    # Missing name key
    ({"ip_acgs": [{"desc": "test", "origin": "test", "rules": []}]}, "SettingsYAMLIPACGExpectedKeyException"),
    # Missing desc key
    ({"ip_acgs": [{"name": "test", "origin": "test", "rules": []}]}, "SettingsYAMLIPACGExpectedKeyException"),
    # Missing origin key
    ({"ip_acgs": [{"name": "test", "desc": "test", "rules": []}]}, "SettingsYAMLIPACGExpectedKeyException"),
    # Missing rules key
    ({"ip_acgs": [{"name": "test", "desc": "test", "origin": "test"}]}, "SettingsYAMLIPACGExpectedKeyException"),
    # Multiple IP ACGs with one missing key
    ({"ip_acgs": [
        {"name": "test1", "desc": "test1", "origin": "test1", "rules": []},
        {"name": "test2", "desc": "test2", "rules": []}
    ]}, "SettingsYAMLIPACGExpectedKeyException"),
])
def test_val_settings_ip_acg_structure_invalid(settings, expected_error):
    with pytest.raises(SystemExit):
        val_settings_ip_acg_structure(settings)


def test_get_validation_baseline(valid_settings):
    result = get_validation_baseline(valid_settings)
    assert isinstance(result, Validation)
    assert len(result.invalid_rules) == 1
    assert result.rules_amt_max == 100
    assert result.rules_desc_length_max == 50
    assert result.prefix_default == 32
    assert result.prefix_min == 24
    assert result.ip_acg_name_length_max == 30
    assert result.groups_per_directory_amt_max == 25

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
        return {
            **valid_settings,
            "groups_per_directory_amt_max": 25
        }
    
    monkeypatch.setattr('acgenius.validation.utils.get_settings', mock_get_settings)
    
    result = parse_settings()
    assert isinstance(result, Settings)
    assert isinstance(result.validation, Validation)
    assert isinstance(result.work_instruction, WorkInstruction)


def test_split_ip_and_prefix_with_prefix(valid_settings):
    # Test IP address with explicit prefix
    rule = Rule(ip="192.168.1.0/24", desc="Test rule")
    ip, prefix = split_ip_and_prefix(rule, parse_settings())
    
    assert ip == "192.168.1.0"
    assert prefix == 24


def test_split_ip_and_prefix_without_prefix(valid_settings):
    # Test IP address without prefix (should use default)
    rule = Rule(ip="192.168.1.1", desc="Test rule")
    ip, prefix = split_ip_and_prefix(rule, parse_settings())
    
    assert ip == "192.168.1.1"
    assert prefix == valid_settings["user_input_validation"]["ip_address"]["prefix"]["default"]


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
