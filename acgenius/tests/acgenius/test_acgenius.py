import pytest
from click.testing import CliRunner
from unittest.mock import patch

from acgenius.acgenius import main
from acgenius.resources.models import AppInput, Settings, Inventory


@pytest.mark.parametrize(
    "action,ip_acg_ids,dryrun,debug,expected_app_input,mock_settings,mock_inventory", [
        # Basic status check
        ("status", (), False, False, 
         AppInput(cli={"action": "status", "dryrun": False, "ip_acg_ids_to_delete": ()}, 
                 settings=Settings(validation=None), 
                 inventory=Inventory(directories=[], ip_acgs=[])),
         Settings(validation=None),
         Inventory(directories=[], ip_acgs=[])),
        
        # Create with dryrun
        ("create", (), True, False,
         AppInput(cli={"action": "create", "dryrun": True, "ip_acg_ids_to_delete": ()},
                 settings=Settings(validation=None),
                 inventory=Inventory(directories=[], ip_acgs=[])),
         Settings(validation=None),
         Inventory(directories=[], ip_acgs=[])),
        
        # Update with debug
        ("update", (), False, True,
         AppInput(cli={"action": "update", "dryrun": False, "ip_acg_ids_to_delete": ()},
                 settings=Settings(validation=None),
                 inventory=Inventory(directories=[], ip_acgs=[])),
         Settings(validation=None),
         Inventory(directories=[], ip_acgs=[])),
        
        # Delete with IP ACG IDs
        ("delete", ("acg1", "acg2"), False, False,
         AppInput(cli={"action": "delete", "dryrun": False, "ip_acg_ids_to_delete": ("acg1", "acg2")},
                 settings=Settings(validation=None),
                 inventory=Inventory(directories=[], ip_acgs=[])),
         Settings(validation=None),
         Inventory(directories=[], ip_acgs=[])),
        
        # All options enabled with delete
        ("delete", ("acg1",), True, True,
         AppInput(cli={"action": "delete", "dryrun": True, "ip_acg_ids_to_delete": ("acg1",)},
                 settings=Settings(validation=None),
                 inventory=Inventory(directories=[], ip_acgs=[])),
         Settings(validation=None),
         Inventory(directories=[], ip_acgs=[]))
    ]
)
def test_main_valid_inputs(action, ip_acg_ids, dryrun, debug, expected_app_input, 
                          mock_settings, mock_inventory):
    runner = CliRunner()
    
    with patch('acgenius.acgenius.run_common_route') as mock_common_route, \
         patch('acgenius.acgenius.run_selected_route') as mock_selected_route:
        
        mock_common_route.return_value = (mock_settings, mock_inventory)
        
        args = [action]
        if ip_acg_ids:
            args.extend(ip_acg_ids)
        if dryrun:
            args.append('--dryrun')
        if debug:
            args.append('--debug')
            
        result = runner.invoke(main, args)
        
        assert result.exit_code == 0
        mock_common_route.assert_called_once()
        mock_selected_route.assert_called_once_with(expected_app_input)


@pytest.mark.parametrize(
    "action,exception_class,exception_msg", [
        # Common route failure
        ("status", ValueError, "Common route failed"),
        # Selected route failure
        ("create", RuntimeError, "Selected route failed"),
        # Generic exception
        ("update", Exception, "Unexpected error")
    ]
)
def test_main_error_handling(action, exception_class, exception_msg):
    runner = CliRunner()
    
    with patch('acgenius.acgenius.run_common_route') as mock_common_route:
        mock_common_route.side_effect = exception_class(exception_msg)
        
        result = runner.invoke(main, [action])
        
        assert result.exit_code != 0
        mock_common_route.assert_called_once()
