from typing import Callable

from lambdaq.types.message import TMessage
from lambdaq.types.response import TResponse

MessageHandler = Callable[[TMessage], TResponse]
