import pytest

from acgenius.resources.utils import specify_report, create_report
from acgenius.resources.models import Directory, IP_ACG, Rule


@pytest.mark.parametrize(
    "input_item, expected_output",
    [
        (IP_ACG(id="acg1", name="test_acg", desc="test description", rules=[]), 
         {"description": "test description"}),
        
        (Directory(
            id="dir1", 
            name="test_dir",
            type="group",
            state="active",
            ip_acgs=["acg1", "acg2"]
        ),
        {
            "ip_acgs_associated": ["acg1", "acg2"],
            "type": "group",
            "state": "active"
        }),
    ]
)
def test_specify_report_returns_correct_dict(input_item, expected_output):
    result = specify_report(input_item)
    assert result == expected_output

@pytest.mark.parametrize(
    "subject, origin",
    [
        ([], "work_instruction"),
        ([Directory(
            id="dir1",
            name="test_dir",
            type="group", 
            state="active",
            ip_acgs=["acg1"]
        )], "work_instruction"),
        ([IP_ACG(
            id="acg1",
            name="test_acg",
            desc="test description",
            rules=[
                Rule(
                    ip="10.0.0.0/24",
                    desc="test rule"
                )
            ]
        )], "work_instruction"),
        ([], "other"),
        ([Directory(
            id="dir1",
            name="test_dir", 
            type="group",
            state="active",
            ip_acgs=["acg1"]
        )], "other"),
        ([IP_ACG(
            id="acg1",
            name="test_acg", 
            desc="test description",
            rules=[
                Rule(
                    ip="10.0.0.0/24",
                    desc="test rule"
                )
            ]
        )], "other")
    ]
)
def test_create_report_prints_correctly(capsys, subject, origin):
    create_report(subject, origin)
    captured = capsys.readouterr()
    assert isinstance(captured.out, str)
    if not subject:
        assert captured.out == ""
    else:
        assert len(captured.out) > 0
        if isinstance(subject[0], IP_ACG):
            assert "rule" in captured.out
            assert "description" in captured.out
        else:
            assert "type" in captured.out
            assert "state" in captured.out

@pytest.mark.parametrize(
    "subject, origin",
    [
        ([IP_ACG(
            id="acg1",
            name="test_acg",
            desc="test description", 
            rules=[
                Rule(
                    ip="10.0.0.0/24",
                    desc="test rule 1"
                ),
                Rule(
                    ip="192.168.0.0/24",
                    desc="test rule 2"
                )
            ]
        )], "work_instruction"),
        ([IP_ACG(
            id="acg1",
            name="test_acg",
            desc="test description",
            rules=[
                Rule(
                    ip="10.0.0.0/24",
                    desc="test rule 1"
                ),
                Rule(
                    ip="192.168.0.0/24",
                    desc="test rule 2"
                )
            ]
        )], "other")
    ]
)
def test_create_report_multiple_rules(capsys, subject, origin):
    create_report(subject, origin)
    captured = capsys.readouterr()
    assert "test rule 1" in captured.out
    assert "test rule 2" in captured.out
    assert "10.0.0.0/24" in captured.out
    assert "192.168.0.0/24" in captured.out
