import pytest
from botocore.exceptions import ClientError
import sys
from acgenius.routing.errors import get_error_code, process_error, set_app_response
from acgenius.config import EXC_UNEXPECTED_GENERIC, EXIT_APP


@pytest.mark.parametrize("exception,expected", [
    (ValueError(), "ValueError"),
    (TypeError(), "TypeError"),
    (ClientError({"Error": {"Code": "ResourceNotFoundException"}}, "operation"), "ClientError"),
])
def test_get_error_code(exception, expected):
    assert get_error_code(exception) == expected


# import logging

# @pytest.mark.parametrize("error_map,code,msg_generic,exception,expected_msg", [
#     ({"ValueError": {"crash": False, "msg": "Custom message"}}, "ValueError", "Base message", ValueError(), "Base message Custom message"),
#     ({}, "KeyError", "Base message", KeyError(), f"Base message An unexpected exception occurred."),
#     ({"TypeError": {"crash": False, "msg": "Type error occurred"}}, "TypeError", "Base message", TypeError(), "Base message Type error occurred"),
# ])
# def test_process_error_logging(error_map, code, msg_generic, exception, expected_msg, caplog):
#     with caplog.at_level(logging.WARNING):
#         process_error(error_map, code, msg_generic, exception)
#     assert expected_msg in caplog.text


@pytest.mark.parametrize("error_map,code,crash", [
    ({"ValueError": {"crash": True}}, "ValueError", True),
    ({"KeyError": {"crash": False}}, "KeyError", False),
    ({}, "UnknownError", True),
])
def test_process_error_crash_behavior(error_map, code, crash):
    if crash:
        with pytest.raises(SystemExit):
            process_error(error_map, code, "Test message")
    else:
        process_error(error_map, code, "Test message")

import logging

# @pytest.mark.parametrize("exception,crash,expected_log_level", [
#     (ValueError(), True, "ERROR"),
#     (ValueError(), False, "WARNING"),
#     (None, True, "INFO"),
# ])
# def test_set_app_response_logging(exception, crash, expected_log_level, caplog):
#     if crash:
#         with caplog.at_level(logging.ERROR):  # Capture ERROR level logs
#             with pytest.raises(SystemExit):
#                 set_app_response(exception, crash)
#     else:
#         with caplog.at_level(logging.WARNING):  # Capture WARNING level logs
#             set_app_response(exception, crash)
    
#     # Check if the log level is captured correctly
#     log_levels = [record.levelname for record in caplog.records]
#     if exception is None:
#         assert "INFO" in log_levels, f"Expected log level 'INFO' not found in logs: {log_levels}"
#     else:
#         assert expected_log_level in log_levels, f"Expected log level '{expected_log_level}' not found in logs: {log_levels}"


@pytest.mark.parametrize("exception,crash", [
    (ValueError(), True),
    (None, True),
])
def test_set_app_response_exit(exception, crash):
    with pytest.raises(SystemExit):
        set_app_response(exception, crash)


@pytest.mark.parametrize("exception,crash", [
    (ValueError(), False),
])
def test_set_app_response_no_exit(exception, crash):
    set_app_response(exception, crash)
