import pytest
from unittest.mock import patch
from acgenius.resources.ip_acgs.work_instruction import delete_ip_acg


@pytest.mark.parametrize("ip_acg_id,expected_msg", [
    # Valid deletion
    ("valid_id", "☑ Deleted IP ACG [valid_id]."),
])
def test_delete_ip_acg_success(ip_acg_id, expected_msg):
    with patch("acgenius.resources.ip_acgs.work_instruction.workspaces.delete_ip_group") as mock_delete:
        mock_delete.return_value = {}
        with patch("acgenius.resources.ip_acgs.work_instruction.logger.info") as mock_info:
            delete_ip_acg(ip_acg_id)
            mock_info.assert_called_once_with(expected_msg, extra={"depth": 1})

@pytest.mark.parametrize("ip_acg_id,exception,expected_msg", [
    # Invalid parameter exception
    ("invalid_id", Exception("InvalidParameterValuesException"), "Could not delete IP ACG [invalid_id] in AWS."),
])
def test_delete_ip_acg_invalid_parameter(ip_acg_id, exception, expected_msg):
    with patch("acgenius.resources.ip_acgs.work_instruction.workspaces.delete_ip_group") as mock_delete:
        mock_delete.side_effect = exception
        with pytest.raises(SystemExit):
            delete_ip_acg(ip_acg_id)

@pytest.mark.parametrize("ip_acg_id,exception,expected_msg", [
    # Resource not found exception
    ("not_found_id", Exception("ResourceNotFoundException"), "Could not find IP ACG in AWS. Double check if it is created, and if not, do a 'create' run of this app."),
])
def test_delete_ip_acg_resource_not_found(ip_acg_id, exception, expected_msg):
    with patch("acgenius.resources.ip_acgs.work_instruction.workspaces.delete_ip_group") as mock_delete:
        mock_delete.side_effect = exception
        with pytest.raises(SystemExit):
            delete_ip_acg(ip_acg_id)

@pytest.mark.parametrize("ip_acg_id,exception,expected_msg", [
    # Resource associated exception
    ("associated_id", Exception("ResourceAssociatedException"), "The IP ACG is still associated with a directory in AWS. Please retry a 'delete' run first. Otherwise, please inspect in the AWS console."),
])
def test_delete_ip_acg_resource_associated(ip_acg_id, exception, expected_msg):
    with patch("acgenius.resources.ip_acgs.work_instruction.workspaces.delete_ip_group") as mock_delete:
        mock_delete.side_effect = exception
        with pytest.raises(SystemExit):
            delete_ip_acg(ip_acg_id)
