from importlib.resources import files

from lambdaq.handle_event import handle_event
from lambdaq.metadata import Metadata

if __package__:
    with files(__package__).joinpath("VERSION").open("r") as t:
        __version__ = t.readline().strip()

__all__ = [
    "Metadata",
    "handle_event",
]
