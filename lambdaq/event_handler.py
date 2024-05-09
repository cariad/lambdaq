from json import dumps, loads
from typing import Any, Generic, cast

from boto3 import Session

from lambdaq.logging import logger
from lambdaq.metadata import Metadata
from lambdaq.types import MessageHandler, TMessage, TResponse


class EventHandler(Generic[TMessage, TResponse]):
    """
    Event handler.

    Arguments:
        event: Function event.

        handler: Reference to a message-handling function.

        session: Optional Boto3 session. A new session will be created by
        default.

        task_token_key: Key of the Step Functions task token in each message.
        Step Functions state will not be published if this is omitted.
    """

    def __init__(
        self,
        event: Any,
        handler: MessageHandler[TMessage, TResponse],
        session: Session | None = None,
        task_token_key: str | None = None,
    ) -> None:
        self.event = event
        self.handler = handler

        self.metadata = Metadata(
            session or Session(),
        )

        self.task_token_key = task_token_key

    def _send_task_state(
        self,
        token: str,
        exception: Exception | None = None,
        response: TResponse | None = None,
    ) -> None:
        sf = self.metadata.session.client("stepfunctions")

        try:
            if exception:
                sf.send_task_failure(
                    taskToken=token,
                    error=exception.__class__.__name__,
                    cause=str(exception),
                )

            else:
                sf.send_task_success(
                    output=dumps(response),
                    taskToken=token,
                )

        except sf.exceptions.TaskTimedOut:
            # We intentionally swallow this exception, otherwise SQS will
            # redrive the message for another go and we'll land right back here
            # again.
            #
            # We can safely ignore it because the state machine doesn't care.

            logger.warning(
                "State machine timed-out waiting for this message to be handled",
            )

    def handle_messages(
        self,
    ) -> TResponse | None:
        if "Records" not in self.event:
            logger.info("Received a single direct invocation")
            return self.handler(
                cast(TMessage, self.event),
                self.metadata,
            )

        records = self.event["Records"]

        for index, record in enumerate(records):
            logger.info(
                "Processing enqueued message %s/%s",
                index + 1,
                len(records),
            )

            body = loads(record["body"])
            token = body[self.task_token_key] if self.task_token_key else None
            message = cast(TMessage, body)

            try:
                response = self.handler(
                    message,
                    self.metadata,
                )

            except Exception as ex:
                if token:
                    self._send_task_state(
                        token,
                        exception=ex,
                    )

                continue

            if token:
                self._send_task_state(
                    token,
                    response=response,
                )

        return None
