import pytest

from acgenius.validation.directories import val_directories_specified
from acgenius.resources.models import WorkInstruction, Directory


@pytest.mark.parametrize(
    "directories,expected",
    [
        # No directories specified
        ([], False),
        # Directory with empty id and name
        ([Directory(id="", name="")], False),
        # Directory with id but no name
        ([Directory(id="123", name="")], False),
        # Directory with name but no id
        ([Directory(id="", name="dir1")], False),
        # Directory with both id and name
        ([Directory(id="123", name="dir1")], True),
        # Multiple directories (only first one matters)
        (
            [
                Directory(id="123", name="dir1"),
                Directory(id="456", name="dir2")
            ],
            True
        ),
        # Multiple directories, first one invalid 
        (
            [
                Directory(id="", name=""),
                Directory(id="456", name="dir2")
            ],
            False
        ),
    ]
)
def test_val_directories_specified(directories, expected):
    work_instruction = WorkInstruction(directories=directories, ip_acgs=[], tags=[])
    result = val_directories_specified(work_instruction)
    assert result == expected
