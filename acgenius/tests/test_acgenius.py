import pytest
from acgenius import main
from unittest.mock import patch


@pytest.mark.parametrize("action, ip_acg_ids_to_delete, dryrun, debug", [
    # Test for status action with no IPs to delete
    ("status", (), False, False),
])
def test_main_status(action, ip_acg_ids_to_delete, dryrun, debug):
    with patch('acgenius.setup_logger') as mock_logger:
        main(action, ip_acg_ids_to_delete, dryrun, debug)
        mock_logger().info.assert_any_call(f"Selected action:        [{action}]")

@pytest.mark.parametrize("action, ip_acg_ids_to_delete, dryrun, debug", [
    # Test for create action with no IPs to delete
    ("create", (), False, False),
])
def test_main_create(action, ip_acg_ids_to_delete, dryrun, debug):
    with patch('acgenius.setup_logger') as mock_logger:
        main(action, ip_acg_ids_to_delete, dryrun, debug)
        mock_logger().info.assert_any_call(f"Selected action:        [{action}]")

@pytest.mark.parametrize("action, ip_acg_ids_to_delete, dryrun, debug", [
    # Test for update action with no IPs to delete
    ("update", (), False, False),
])
def test_main_update(action, ip_acg_ids_to_delete, dryrun, debug):
    with patch('acgenius.setup_logger') as mock_logger:
        main(action, ip_acg_ids_to_delete, dryrun, debug)
        mock_logger().info.assert_any_call(f"Selected action:        [{action}]")

@pytest.mark.parametrize("action, ip_acg_ids_to_delete, dryrun, debug", [
    # Test for delete action with one IP to delete
    ("delete", ("192.168.1.1",), False, False),
])
def test_main_delete(action, ip_acg_ids_to_delete, dryrun, debug):
    with patch('acgenius.setup_logger') as mock_logger:
        main(action, ip_acg_ids_to_delete, dryrun, debug)
        mock_logger().info.assert_any_call(f"Delete list of IP ACGs: [{ip_acg_ids_to_delete}]")

@pytest.mark.parametrize("action, ip_acg_ids_to_delete, dryrun, debug", [
    # Test for dry run mode enabled
    ("create", (), True, False),
])
def test_main_dryrun(action, ip_acg_ids_to_delete, dryrun, debug):
    with patch('acgenius.setup_logger') as mock_logger:
        main(action, ip_acg_ids_to_delete, dryrun, debug)
        mock_logger().info.assert_any_call(f"Dry run mode enabled:   [True]")

@pytest.mark.parametrize("action, ip_acg_ids_to_delete, dryrun, debug", [
    # Test for debug mode enabled
    ("update", (), False, True),
])
def test_main_debug(action, ip_acg_ids_to_delete, dryrun, debug):
    with patch('acgenius.setup_logger') as mock_logger:
        main(action, ip_acg_ids_to_delete, dryrun, debug)
        mock_logger().info.assert_any_call(f"Debug mode enabled:     [True]")