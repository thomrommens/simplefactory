import pytest
from botocore.exceptions import ClientError
from unittest.mock import patch

from acgenius.config import EXC_ACCESS_DENIED, EXC_INVALID_PARAM, STD_INSTR_README
from acgenius.resources.ip_acgs.inventory import get_ip_acgs, sel_ip_acgs, show_ip_acgs
from acgenius.resources.models import IP_ACG, Rule


@pytest.mark.parametrize("aws_response,expected", [
    # Empty response
    ({}, None),
    # No Result key
    ({"SomeOtherKey": []}, None),
    # Valid response with data
    ({"Result": [{"groupId": "1", "groupName": "test"}]}, [{"groupId": "1", "groupName": "test"}]),
])
def test_get_ip_acgs_response_handling(aws_response, expected):
    with patch("acgenius.resources.ip_acgs.inventory.workspaces") as mock_ws:
        mock_ws.describe_ip_groups.return_value = aws_response
        result = get_ip_acgs()
        assert result == expected

@pytest.mark.parametrize("exception,error_code,expected_msg", [
    # Invalid parameter exception
    (ClientError({"Error": {"Code": "InvalidParameterValuesException"}}, "operation"), 
     "InvalidParameterValuesException", EXC_INVALID_PARAM),
    # Access denied exception
    (ClientError({"Error": {"Code": "AccessDeniedException"}}, "operation"),
     "AccessDeniedException", f"{EXC_ACCESS_DENIED} {STD_INSTR_README}"),
    # Generic exception
    (Exception("Generic error"), None, "Could not get IP ACGs from AWS."),
])
def test_get_ip_acgs_error_handling(exception, error_code, expected_msg):
    with patch("acgenius.resources.ip_acgs.inventory.workspaces") as mock_ws:
        mock_ws.describe_ip_groups.side_effect = exception
        with pytest.raises(SystemExit) as pytest_exit:
            get_ip_acgs()
        assert pytest_exit.value.code == 1

@pytest.mark.parametrize("input_data,expected", [
    # Empty input
    ([], []),
    # Single IP ACG without rules
    ([{
        "groupId": "1",
        "groupName": "test1",
        "groupDesc": "desc1",
        "userRules": []
    }], [IP_ACG(id="1", name="test1", desc="desc1", rules=[])]),
    # Multiple IP ACGs with rules, testing sort by name
    ([{
        "groupId": "2",
        "groupName": "testB",
        "groupDesc": "descB",
        "userRules": [{"ipRule": "10.0.0.0/16", "ruleDesc": "rule1"}]
    }, {
        "groupId": "1",
        "groupName": "testA",
        "groupDesc": "descA",
        "userRules": [{"ipRule": "192.168.0.0/16", "ruleDesc": "rule2"}]
    }], [
        IP_ACG(id="1", name="testA", desc="descA", 
               rules=[Rule(ip="192.168.0.0/16", desc="rule2")]),
        IP_ACG(id="2", name="testB", desc="descB", 
               rules=[Rule(ip="10.0.0.0/16", desc="rule1")])
    ]),
])
def test_sel_ip_acgs_processing(input_data, expected):
    result = sel_ip_acgs(input_data)
    assert result == expected

@pytest.mark.parametrize("get_response,expected", [
    # No IP ACGs found
    (None, None),
    # Valid IP ACGs found
    ([{
        "groupId": "1",
        "groupName": "test1",
        "groupDesc": "desc1",
        "userRules": [{"ipRule": "10.0.0.0/16", "ruleDesc": "rule1"}]
    }], [
        IP_ACG(id="1", name="test1", desc="desc1",
               rules=[Rule(ip="10.0.0.0/16", desc="rule1")])
    ]),
])
def test_show_ip_acgs_integration(get_response, expected):
    with patch("acgenius.resources.ip_acgs.inventory.get_ip_acgs") as mock_get, \
         patch("acgenius.resources.ip_acgs.inventory.create_report") as mock_report:
        mock_get.return_value = get_response
        result = show_ip_acgs()
        assert result == expected
        if expected is not None:
            mock_report.assert_called_once_with(subject=expected, origin="inventory")
        else:
            mock_report.assert_not_called()
