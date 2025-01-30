import pytest
from botocore.exceptions import ClientError
from acgenius.routing.errors import get_error_code, process_error, set_app_response


@pytest.mark.parametrize("exception,expected", [
    (ValueError(), "ValueError"),
    (TypeError(), "TypeError"),
    (ClientError({"Error": {"Code": "ResourceNotFoundException"}}, "operation"), "ClientError"),
])
def test_get_error_code(exception, expected):
    assert get_error_code(exception) == expected


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
