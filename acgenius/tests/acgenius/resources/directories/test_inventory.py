from unittest.mock import Mock, patch
import pytest
from botocore.exceptions import ClientError

from acgenius.resources.directories.inventory import get_directories, sel_directories, show_directories
from acgenius.resources.models import Directory



@pytest.mark.parametrize(
    "mock_response,expected_result",
    [
        # Happy path - directories exist
        ({"Directories": [{"dir": "data"}]}, [{"dir": "data"}]),
        # Empty directories list
        ({"Directories": []}, None),
    ]
)
def test_get_directories_success(mock_response, expected_result):
    with patch("acgenius.resources.directories.inventory.workspaces") as mock_workspaces:
        mock_workspaces.describe_workspace_directories.return_value = mock_response
        result = get_directories()
        assert result == expected_result


# @pytest.mark.parametrize(
#     "exception,expected_crash",
#     [
#         # Invalid parameter exception
#         (ClientError({"Error": {"Code": "InvalidParameterValuesException"}}, "operation"), True),
#         # Generic client error
#         (ClientError({"Error": {"Code": "GenericError"}}, "operation"), False),
#         # Unknown exception
#         (Exception("Unknown error"), False),
#     ]
# )
# def test_get_directories_exceptions(exception, expected_crash):
#     with patch("acgenius.resources.directories.inventory.workspaces") as mock_workspaces:
#         mock_workspaces.describe_workspace_directories.side_effect = exception
#         if expected_crash:
#             with pytest.raises(Exception):
#                 get_directories()
#         else:
#             assert get_directories() is None


# @pytest.mark.parametrize(
#     "input_data,expected_output",
#     [
#         # Complete directory data
#         ([{
#             "DirectoryId": "d-123",
#             "DirectoryName": "test-dir",
#             "DirectoryType": "SimpleAD",
#             "State": "Active",
#             "ipGroupIds": ["ip-1"]
#         }], [Directory(
#             id="d-123",
#             name="test-dir",
#             type="SimpleAD",
#             state="Active",
#             ip_acgs=["ip-1"]
#         )]),
#         # Missing optional fields
#         ([{
#             "DirectoryId": "d-123",
#             "DirectoryName": "test-dir",
#             "DirectoryType": "SimpleAD",
#             "State": "Active"
#         }], [Directory(
#             id="d-123",
#             name="test-dir",
#             type="SimpleAD",
#             state="Active",
#             ip_acgs=None
#         )]),
#         # Empty input
#         ([], []),
#     ]
# )
# def test_sel_directories(input_data, expected_output):
#     result = sel_directories(input_data)
#     assert len(result) == len(expected_output)
#     for res, exp in zip(result, expected_output):
#         assert res.id == exp.id
#         assert res.name == exp.name
#         assert res.type == exp.type
#         assert res.state == exp.state
#         assert res.ip_acgs == exp.ip_acgs


# @pytest.mark.parametrize(
#     "mock_directories,expected_result",
#     [
#         # Happy path with directories
#         ([{"DirectoryId": "d-123"}], [Directory(id="d-123", name=None, type=None, state=None, ip_acgs=None)]),
#         # Empty directories list
#         ([], []),
#     ]
# )
# def test_show_directories(mock_directories, expected_result):
#     with patch("acgenius.resources.directories.inventory.get_directories") as mock_get:
#         with patch("acgenius.resources.directories.inventory.create_report") as mock_report:
#             mock_get.return_value = mock_directories
#             result = show_directories()
#             assert len(result) == len(expected_result)
#             for res, exp in zip(result, expected_result):
#                 assert res.id == exp.id
#             mock_report.assert_called_once() 