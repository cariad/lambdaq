from typing import Any

from boto3 import Session

from lambdaq.event_handler import EventHandler
from lambdaq.types import MessageHandler, TMessage, TResponse


def handle_event(
    event: Any,
    handler: MessageHandler[TMessage, TResponse],
    task_token_key: str,
    session: Session | None = None,
) -> TResponse | None:
    """
    Handles a Lambda function event.

    Arguments:
        event: Function event.

        handler: Reference to a message-handling function.

        task_token_key: Key of the task token in each message.

        session: Optional Boto3 session. A new session will be created by
        default.

    Returns:
        Message handling response if the function was invoked directly, or
        `None` if the function was invoked by an SQS queue.
    """

    event_handler = EventHandler(
        event,
        handler,
        task_token_key,
        session=session,
    )

    return event_handler.handle_messages()
