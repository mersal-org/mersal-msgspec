from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from mersal.msgspec.msgspec_serializer import MsgspecSerializer
from mersal.plugins import Plugin
from mersal.serialization import (
    Serializer,
)

if TYPE_CHECKING:
    from mersal.configuration import StandardConfigurator

__all__ = (
    "MsgspecSerializerConfig",
    "MsgspecSerializerPlugin",
)


@dataclass
class MsgspecSerializerConfig:
    message_types: set[type]

    @property
    def plugin(self) -> MsgspecSerializerPlugin:
        return MsgspecSerializerPlugin(self)


class MsgspecSerializerPlugin(Plugin):
    def __init__(self, config: MsgspecSerializerConfig) -> None:
        self._config = config

    def __call__(self, configurator: StandardConfigurator) -> None:
        def register(_: StandardConfigurator) -> MsgspecSerializer:
            return MsgspecSerializer(self._config.message_types)

        configurator.register(Serializer, register)
