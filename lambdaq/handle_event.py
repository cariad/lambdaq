from typing import Any

from boto3 import Session

from lambdaq.event_handler import EventHandler
from lambdaq.types import MessageHandler, TMessage, TResponse


def handle_event(
    event: Any,
    handler: MessageHandler[TMessage, TResponse],
    session: Session | None = None,
    task_token_key: str | None = None,
) -> TResponse | None:
    """
    Handles a Lambda function event.

    Arguments:
        event: Function event.

        handler: Reference to a message-handling function.

        session: Optional Boto3 session. A new session will be created by
        default.

        task_token_key: Key of the Step Functions task token in each message.
        Step Functions state will not be submitted if this is omitted.

    Returns:
        Message handling response if the function was invoked directly, or
        `None` if the function was invoked by an SQS queue.
    """

    event_handler = EventHandler(
        event,
        handler,
        session=session,
        task_token_key=task_token_key,
    )

    return event_handler.handle_messages()
