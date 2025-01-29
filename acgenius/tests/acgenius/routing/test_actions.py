import pytest
from unittest.mock import Mock, patch
from acgenius.routing.actions import status, create, update, delete
from acgenius.resources.models import AppInput, Settings, WorkInstruction, Inventory, IP_ACG, Directory

@pytest.mark.parametrize("app_input", [
    # Basic status check
    (AppInput(cli={}, settings=Settings(work_instruction=WorkInstruction(ip_acgs=[], directories=[], tags={}), validation=True), inventory=Inventory(ip_acgs=[], directories=[]))),
])
def test_status(app_input, caplog):
    with caplog.at_level("INFO"):
        status(app_input)
    assert "✅ Completed display of status." in caplog.text

@pytest.mark.parametrize("app_input,expected_calls", [
    # Dryrun mode - no actual creation
    (AppInput(
        cli={"dryrun": True},
        settings=Settings(work_instruction=WorkInstruction(
            ip_acgs=[IP_ACG(id="test-id", name="Test ACG", desc="Test description", rules=[])],
            tags={},
            directories=[]
        ), validation=True),
        inventory=Inventory(ip_acgs=[], directories=[])
    ), 0),
    # Create with directories specified in work instruction
    (AppInput(
        cli={"dryrun": False},
        settings=Settings(work_instruction=WorkInstruction(
            ip_acgs=[IP_ACG(id="test-id", name="Test ACG", desc="Test description", rules=[])],
            directories=[Directory(id="dir-1", name="Directory 1")],
            tags={} 
        ), validation=True),
        inventory=Inventory(ip_acgs=[], directories=[])
    ), 1),
    # Create with directories from inventory
    (AppInput(
        cli={"dryrun": False},
        settings=Settings(work_instruction=WorkInstruction(
            ip_acgs=[IP_ACG(id="test-id", name="Test ACG", desc="Test description", rules=[])],
            tags={"env": "test"},
            directories=[]
        ), validation=True),
        inventory=Inventory(ip_acgs=[], directories=[Directory(id="dir-1", name="Directory 1")])
    ), 1),
])
def test_create(app_input, expected_calls):
    with patch('acgenius.routing.actions.create_ip_acg') as mock_create, \
         patch('acgenius.routing.actions.associate_ip_acg') as mock_associate, \
         patch('acgenius.routing.actions.create_report') as mock_report:
        
        mock_create.return_value = IP_ACG(id="created-id", name="Created ACG", desc="Created description", rules=[])
        app_input.settings.work_instruction.directories = [Directory(id="dir-1", name="Directory 1")]
        app_input.settings.work_instruction.tags = {"env": "test"}
        create(app_input)
        assert mock_create.call_count == expected_calls

@pytest.mark.parametrize("app_input,should_raise", [
    # No IP ACGs in inventory - should raise error
    (AppInput(
        cli={"dryrun": False},
        settings=Settings(work_instruction=WorkInstruction(
            ip_acgs=[IP_ACG(id="test-id", name="Test ACG", desc="Test description", rules=[])],
            tags={},
            directories=[]
        ), validation=True),
        inventory=Inventory(ip_acgs=[], directories=[])
    ), True),
    # IP ACGs exist - should update
    (AppInput(
        cli={"dryrun": False},
        settings=Settings(work_instruction=WorkInstruction(
            ip_acgs=[IP_ACG(id="test-id", name="Test ACG", desc="Test description", rules=[])],
            tags={},
            directories=[]
        ), validation=True),
        inventory=Inventory(ip_acgs=[IP_ACG(id="test-id", name="Test ACG", desc="Test description", rules=[])], directories=[])
    ), False),
    # Dryrun mode - no actual updates
    (AppInput(
        cli={"dryrun": True},
        settings=Settings(work_instruction=WorkInstruction(
            ip_acgs=[IP_ACG(id="test-id", name="Test ACG", desc="Test description", rules=[])],
            tags={},
            directories=[]
        ), validation=True),
        inventory=Inventory(ip_acgs=[IP_ACG(id="test-id", name="Test ACG", desc="Test description", rules=[])], directories=[])
    ), False),
])
def test_update(app_input, should_raise):
    with patch('acgenius.routing.actions.match_ip_acgs') as mock_match, \
         patch('acgenius.routing.actions.update_rules') as mock_update, \
         patch('acgenius.routing.actions.create_report') as mock_report:
        
        if should_raise:
            with pytest.raises(SystemExit):
                update(app_input)
        else:
            update(app_input)
            if not app_input.cli["dryrun"]:
                mock_update.assert_called_once()

@pytest.mark.parametrize("app_input,should_raise", [
    # No IP ACGs specified for deletion - should raise error
    (AppInput(
        cli={"dryrun": False, "ip_acg_ids_to_delete": []},
        settings=Settings(work_instruction=WorkInstruction(ip_acgs=[], tags={}, directories=[]), validation=True),
        inventory=Inventory(ip_acgs=[], directories=[])
    ), True),
    # Valid IP ACG specified for deletion
    (AppInput(
        cli={"dryrun": False, "ip_acg_ids_to_delete": ["test-id"]},
        settings=Settings(work_instruction=WorkInstruction(ip_acgs=[], tags={}, directories=[]), validation=True),
        inventory=Inventory(ip_acgs=[], directories=[Directory(id="dir-1", name="Directory 1")])
    ), False),
    # Dryrun mode - no actual deletion
    (AppInput(
        cli={"dryrun": True, "ip_acg_ids_to_delete": ["test-id"]},
        settings=Settings(work_instruction=WorkInstruction(ip_acgs=[], tags={}, directories=[]), validation=True),
        inventory=Inventory(ip_acgs=[], directories=[Directory(id="dir-1", name="Directory 1")])
    ), False),
])
def test_delete(app_input, should_raise):
    with patch('acgenius.routing.actions.disassociate_ip_acg') as mock_disassociate, \
         patch('acgenius.routing.actions.delete_ip_acg') as mock_delete:
        
        if should_raise:
            with pytest.raises(SystemExit):
                delete(app_input)
        else:
            delete(app_input)
            if not app_input.cli["dryrun"]:
                assert mock_disassociate.call_count == len(app_input.inventory.directories)
                assert mock_delete.call_count == len(app_input.cli["ip_acg_ids_to_delete"])

