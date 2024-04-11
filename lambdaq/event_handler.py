from json import dumps, loads
from typing import Any, Generic, cast

from boto3 import Session

from lambdaq.logging import logger
from lambdaq.metadata import Metadata
from lambdaq.types import MessageHandler, TMessage, TResponse


class EventHandler(Generic[TMessage, TResponse]):
    def __init__(
        self,
        event: Any,
        handler: MessageHandler[TMessage, TResponse],
        task_token_key: str,
        session: Session | None = None,
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
            message = cast(TMessage, body)
            token = str(message[self.task_token_key])  # type: ignore

            try:
                response = self.handler(
                    message,
                    self.metadata,
                )

            except Exception as ex:
                self._send_task_state(
                    token,
                    exception=ex,
                )

                continue

            self._send_task_state(
                token,
                response=response,
            )

        return None
