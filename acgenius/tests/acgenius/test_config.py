import pytest
import logging
from acgenius.config import DepthFormatter


@pytest.mark.parametrize("depth, expected", [
    (0, "Test message"),
    (1, " | Test message"),
    (2, " | | Test message"),
])
def test_depth_formatter(depth, expected):
    formatter = DepthFormatter()
    record = logging.LogRecord("test", logging.INFO, "", 0, "Test message", None, None)
    setattr(record, "depth", depth)
    formatted_message = formatter.format(record)
    assert formatted_message == expected