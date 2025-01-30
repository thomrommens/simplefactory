import pytest
from unittest.mock import patch, MagicMock
from acgenius.resources.models import AppInput, Settings, Inventory
from acgenius.routing.routes import run_common_route, run_selected_route


@pytest.mark.parametrize("directories,ip_acgs,validation,work_instruction", [
    # Happy path - all data present
    ([{"dir": "test"}], [{"acg": "test"}], {"val": "test"}, "WI-123"),
    # Empty directories
    ([], [{"acg": "test"}], {"val": "test"}, "WI-123"),
    # Empty ip_acgs
    ([{"dir": "test"}], [], {"val": "test"}, "WI-123"),
    # Empty validation
    ([{"dir": "test"}], [{"acg": "test"}], {}, "WI-123"),
    # Empty work instruction
    ([{"dir": "test"}], [{"acg": "test"}], {"val": "test"}, ""),
])
def test_run_common_route(directories, ip_acgs, validation, work_instruction):
    with patch('acgenius.routing.routes.show_directories') as mock_dirs, \
         patch('acgenius.routing.routes.show_ip_acgs') as mock_ip_acgs, \
         patch('acgenius.routing.routes.parse_settings') as mock_settings, \
         patch('acgenius.routing.routes.val_work_instruction') as mock_wi:
        
        mock_dirs.return_value = directories
        mock_ip_acgs.return_value = ip_acgs
        mock_settings.return_value = Settings(validation=validation, work_instruction="")
        mock_wi.return_value = work_instruction

        settings, inventory = run_common_route()

        assert isinstance(settings, Settings)
        assert isinstance(inventory, Inventory)
        assert settings.validation == validation
        assert settings.work_instruction == work_instruction
        assert inventory.directories == directories
        assert inventory.ip_acgs == ip_acgs


@pytest.mark.parametrize("action,dryrun,expected_log", [
    # Status action
    ("status", True, ""),
    # Create action with dryrun
    ("create", True, "These IP ACGs would be attempted to create"),
    # Create action without dryrun
    ("create", False, "These IP ACGs will be attempted to create"),
    # Update action with dryrun
    ("update", True, "These IP ACGs would be attempted to update"),
    # Delete action without dryrun
    ("delete", False, "These IP ACGs will be attempted to delete"),
])
def test_run_selected_route_valid_actions(action, dryrun, expected_log):
    app_input = AppInput(cli={"action": action, "dryrun": dryrun}, settings=None, inventory=None)
    
    with patch('acgenius.routing.routes.status') as mock_status, \
         patch('acgenius.routing.routes.create') as mock_create, \
         patch('acgenius.routing.routes.update') as mock_update, \
         patch('acgenius.routing.routes.delete') as mock_delete, \
         patch('acgenius.routing.routes.logger') as mock_logger:

        run_selected_route(app_input)

        action_map = {
            "status": mock_status,
            "create": mock_create,
            "update": mock_update,
            "delete": mock_delete
        }

        action_map[action].assert_called_once_with(app_input)
        if action != "status":
            mock_logger.info.assert_called_once()
            assert expected_log in mock_logger.info.call_args[0][0]


@pytest.mark.parametrize("invalid_input,expected_error", [
    # Missing action key
    ({"dryrun": True}, KeyError),
    # None as action
    ({"action": None, "dryrun": True}, KeyError),
    # Invalid action type
    ({"action": 123, "dryrun": True}, KeyError),
])
def test_run_selected_route_invalid_inputs(invalid_input, expected_error):
    app_input = AppInput(cli=invalid_input, settings=None, inventory=None)
    
    with patch('acgenius.routing.routes.process_error') as mock_process_error, \
         pytest.raises(expected_error):
        run_selected_route(app_input)
        mock_process_error.assert_called_once()


@pytest.mark.parametrize("action", [
    # Invalid action string
    "invalid_action",
    # Empty string action
    "",
    # Special characters action
    "@#$%",
])
def test_run_selected_route_invalid_actions(action):
    app_input = AppInput(cli={"action": action, "dryrun": True}, settings=None, inventory=None)
    
    with patch('acgenius.routing.routes.process_error') as mock_process_error, \
         pytest.raises(KeyError):
        run_selected_route(app_input)
        mock_process_error.assert_called_once()
