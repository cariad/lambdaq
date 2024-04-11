from json import dumps
from typing import TypedDict
from unittest.mock import Mock, call

from pytest import raises

from lambdaq import handle_event


class Message(TypedDict):
    magic_word: str


class QueuedMessage(Message):
    task_token: str


class Response(TypedDict):
    status: str


def handle_message(
    message: Message,
) -> Response:
    if message["magic_word"] == "clown":
        raise ValueError("Clowns are too cool for nerds")

    return Response(
        status=f'The magic word is "{message["magic_word"]}"',
    )


def test_direct_event(
    send_task_failure: Mock,
    send_task_success: Mock,
    session: Mock,
) -> None:
    event = Message(
        magic_word="cat",
    )

    response = handle_event(
        event,
        handle_message,
        "task_token",
        session=session,
    )

    send_task_failure.assert_not_called()
    send_task_success.assert_not_called()

    assert response == Response(
        status='The magic word is "cat"',
    )


def test_direct_event_with_failure(
    send_task_failure: Mock,
    send_task_success: Mock,
    session: Mock,
) -> None:
    event = Message(
        magic_word="clown",
    )

    with raises(ValueError) as ex:
        _ = handle_event(
            event,
            handle_message,
            "task_token",
            session=session,
        )

    assert str(ex.value) == "Clowns are too cool for nerds"

    send_task_failure.assert_not_called()
    send_task_success.assert_not_called()


def test_single_enqueued_event(
    send_task_failure: Mock,
    send_task_success: Mock,
    session: Mock,
) -> None:
    event = {
        "Records": [
            {
                "body": dumps(
                    QueuedMessage(
                        magic_word="dog",
                        task_token="dog_token",
                    ),
                )
            }
        ],
    }

    response = handle_event(
        event,
        handle_message,
        "task_token",
        session=session,
    )

    send_task_failure.assert_not_called()
    send_task_success.assert_called_once_with(
        output=dumps(
            Response(
                status='The magic word is "dog"',
            )
        ),
        taskToken="dog_token",
    )

    assert response is None


def test_multiple_enqueued_events(
    send_task_failure: Mock,
    send_task_success: Mock,
    session: Mock,
) -> None:
    event = {
        "Records": [
            {
                "body": dumps(
                    QueuedMessage(
                        magic_word="wolf",
                        task_token="wolf_token",
                    ),
                )
            },
            {
                "body": dumps(
                    QueuedMessage(
                        magic_word="tardigrade",
                        task_token="tardigrade_token",
                    ),
                )
            },
        ],
    }

    response = handle_event(
        event,
        handle_message,
        "task_token",
        session=session,
    )

    send_task_failure.assert_not_called()

    assert send_task_success.call_count == 2

    send_task_success.assert_has_calls(
        [
            call(
                output=dumps(
                    Response(
                        status='The magic word is "wolf"',
                    )
                ),
                taskToken="wolf_token",
            ),
            call(
                output=dumps(
                    Response(
                        status='The magic word is "tardigrade"',
                    )
                ),
                taskToken="tardigrade_token",
            ),
        ]
    )

    assert response is None


def test_multiple_enqueued_events_with_failures(
    send_task_failure: Mock,
    send_task_success: Mock,
    session: Mock,
) -> None:
    event = {
        "Records": [
            {
                "body": dumps(
                    QueuedMessage(
                        magic_word="wolf",
                        task_token="wolf_token",
                    ),
                )
            },
            {
                "body": dumps(
                    QueuedMessage(
                        magic_word="clown",
                        task_token="clown_token_0",
                    ),
                )
            },
            {
                "body": dumps(
                    QueuedMessage(
                        magic_word="tardigrade",
                        task_token="tardigrade_token",
                    ),
                )
            },
            {
                "body": dumps(
                    QueuedMessage(
                        magic_word="clown",
                        task_token="clown_token_1",
                    ),
                )
            },
        ],
    }

    response = handle_event(
        event,
        handle_message,
        "task_token",
        session=session,
    )

    assert send_task_failure.call_count == 2

    send_task_failure.assert_has_calls(
        [
            call(
                taskToken="clown_token_0",
                error="ValueError",
                cause="Clowns are too cool for nerds",
            ),
            call(
                taskToken="clown_token_1",
                error="ValueError",
                cause="Clowns are too cool for nerds",
            ),
        ]
    )

    assert send_task_success.call_count == 2

    send_task_success.assert_has_calls(
        [
            call(
                output=dumps(
                    Response(
                        status='The magic word is "wolf"',
                    )
                ),
                taskToken="wolf_token",
            ),
            call(
                output=dumps(
                    Response(
                        status='The magic word is "tardigrade"',
                    )
                ),
                taskToken="tardigrade_token",
            ),
        ]
    )

    assert response is None


def test_state_machine_time_out(
    send_task_failure: Mock,
    send_task_success: Mock,
    session: Mock,
    step_functions: Mock,
) -> None:
    event = {
        "Records": [
            {
                "body": dumps(
                    QueuedMessage(
                        magic_word="turtle",
                        task_token="turtle_token",
                    ),
                )
            }
        ],
    }

    step_functions.exceptions = Mock()
    step_functions.exceptions.TaskTimedOut = ValueError
    send_task_success.side_effect = ValueError

    response = handle_event(
        event,
        handle_message,
        "task_token",
        session=session,
    )

    send_task_failure.assert_not_called()

    send_task_success.assert_has_calls(
        [
            call(
                output=dumps(
                    Response(
                        status='The magic word is "turtle"',
                    )
                ),
                taskToken="turtle_token",
            ),
        ]
    )

    assert response is None
