from importlib.metadata import version

from .msgspec_serializer import MsgspecSerializer

__all__ = [
    "MsgspecSerializer",
]


def __getattr__(name: str) -> str:
    if name != "__version__":
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)

    return version("mersal_msgspec")
