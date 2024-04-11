from typing import Callable

from lambdaq.metadata import Metadata
from lambdaq.types.message import TMessage
from lambdaq.types.response import TResponse

MessageHandler = Callable[[TMessage, Metadata], TResponse]
