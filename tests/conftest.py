from unittest.mock import Mock

from pytest import fixture


@fixture
def send_task_failure() -> Mock:
    return Mock()


@fixture
def send_task_success() -> Mock:
    return Mock()


@fixture
def session(
    step_functions: Mock,
) -> Mock:
    s = Mock()
    s.client = Mock(return_value=step_functions)
    return s


@fixture
def step_functions(
    send_task_failure: Mock,
    send_task_success: Mock,
) -> Mock:
    client = Mock()
    client.send_task_failure = send_task_failure
    client.send_task_success = send_task_success
    return client
