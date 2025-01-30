import pytest
from botocore.exceptions import ClientError
from unittest.mock import patch

from acgenius.resources.directories.inventory import (
    get_directories, sel_directories, show_directories
)
from acgenius.resources.models import Directory


@pytest.mark.parametrize("aws_response, expected_result", [
    # Happy path - returns directories
    ({"Directories": [{"dir": "data"}]}, [{"dir": "data"}]),
    # Empty directories list
    ({"Directories": []}, None),
])
def test_get_directories_success(aws_response, expected_result):
    with patch('acgenius.resources.directories.inventory.workspaces') as mock_workspaces:
        mock_workspaces.describe_workspace_directories.return_value = aws_response
        assert get_directories() == expected_result

@pytest.mark.parametrize("exception, expected_crash", [
    # Invalid parameter exception
    (ClientError({"Error": {"Code": "InvalidParameterValuesException"}}, "operation"), True),
    # Generic client error
    (ClientError({"Error": {"Code": "SomeOtherError"}}, "operation"), True),
    # Generic exception
    (Exception("Generic error"), True),
])
def test_get_directories_exceptions(exception, expected_crash):
    with patch('acgenius.resources.directories.inventory.workspaces') as mock_workspaces:
        mock_workspaces.describe_workspace_directories.side_effect = exception
        if expected_crash:
            with pytest.raises(SystemExit) as pytest_exit:
                get_directories()
            assert pytest_exit.value.code == 1
        else:
            assert get_directories() is None

@pytest.mark.parametrize("input_directory,expected_directory", [
    # Complete directory data
    (
        {
            "DirectoryId": "d-123",
            "DirectoryName": "test-dir",
            "DirectoryType": "SimpleAD",
            "State": "Active",
            "ipGroupIds": ["ip-1", "ip-2"]
        },
        Directory(
            id="d-123",
            name="test-dir",
            type="SimpleAD",
            state="Active",
            ip_acgs=["ip-1", "ip-2"]
        )
    ),
    # Missing optional fields
    (
        {
            "DirectoryId": "d-123",
            "DirectoryName": "test-dir",
            "DirectoryType": "SimpleAD",
            "State": "Active"
        },
        Directory(
            id="d-123",
            name="test-dir",
            type="SimpleAD",
            state="Active",
            ip_acgs=None
        )
    ),
])
def test_sel_directories_single(input_directory, expected_directory):
    result = sel_directories([input_directory])
    assert len(result) == 1
    assert result[0].id == expected_directory.id
    assert result[0].name == expected_directory.name
    assert result[0].type == expected_directory.type
    assert result[0].state == expected_directory.state
    assert result[0].ip_acgs == expected_directory.ip_acgs

@pytest.mark.parametrize("directories,expected_count", [
    # Multiple directories
    ([
        {
            "DirectoryId": "d-123",
            "DirectoryName": "test-dir-1",
            "DirectoryType": "SimpleAD",
            "State": "Active"
        },
        {
            "DirectoryId": "d-456",
            "DirectoryName": "test-dir-2",
            "DirectoryType": "MicrosoftAD",
            "State": "Active"
        }
    ], 2),
    # Empty directory list
    ([], 0),
])
def test_sel_directories_multiple(directories, expected_count):
    result = sel_directories(directories)
    assert len(result) == expected_count

@pytest.mark.parametrize("mock_directories,expected_count", [
    # Happy path with directories
    ([{"DirectoryId": "d-123"}], 1),
    # No directories
    ([], 0),
])
def test_show_directories(mock_directories, expected_count):
    with patch('acgenius.resources.directories.inventory.get_directories') as mock_get_dirs, \
         patch('acgenius.resources.directories.inventory.create_report') as mock_report:
        mock_get_dirs.return_value = mock_directories
        result = show_directories()
        assert len(result) == expected_count
        mock_report.assert_called_once()
