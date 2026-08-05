import importlib
from collections.abc import Iterable
from typing import Any, cast

from mersal.exceptions import MissingDependencyExceptionError

try:
    import msgspec
except ImportError as e:
    raise MissingDependencyExceptionError("msgspec") from e
from mersal.messages.message_headers import MessageHeaders
from mersal.serialization import Serializer

__all__ = ("MsgspecSerializer",)


def _fully_qualified_name(object_type: type) -> str:
    return f"{object_type.__module__}.{object_type.__qualname__}"


def _import_fully_qualified_type(dotted_path: str) -> type:
    module_path, _, qualname = dotted_path.rpartition(".")
    resolved: Any = importlib.import_module(module_path)
    for attr in qualname.split("."):
        resolved = getattr(resolved, attr)
    return cast("type", resolved)


class MsgspecSerializer(Serializer):
    class ObjectWrapper(msgspec.Struct):
        type: str
        object: msgspec.Raw | dict[Any, Any]

    def __init__(self, object_types: Iterable[type] = ()) -> None:
        self._name_to_type: dict[str, type] = {}
        self._type_to_name: dict[type, str] = {}
        for object_type in object_types:
            name = object_type.__name__
            self._name_to_type[name] = object_type
            self._type_to_name[object_type] = name
        self._resolved_dotted_paths: dict[str, type] = {}
        self._encoder = msgspec.json.Encoder()
        self._decoder = msgspec.json.Decoder(type=self.ObjectWrapper)

    def serialize(self, obj: Any) -> Any:
        if isinstance(obj, dict | MessageHeaders):
            _type = "dict"
            _object = dict(obj)
        else:
            object_type = type(obj)
            _type = self._type_to_name.get(object_type) or _fully_qualified_name(object_type)
            _object = obj

        encoded_object = self._encoder.encode(_object)
        return self._encoder.encode(self.ObjectWrapper(type=_type, object=msgspec.Raw(encoded_object)))

    def deserialize(self, data: Any) -> Any:
        unwrapped = self._decoder.decode(data)

        if unwrapped.type == "dict":
            _data = cast("dict", unwrapped.object)
            return msgspec.to_builtins(_data)  # pyright: ignore[reportCallIssue, reportArgumentType]

        object_type = self._name_to_type.get(unwrapped.type) or self._resolve_dotted_path(unwrapped.type)
        return msgspec.convert(unwrapped.object, type=object_type)  # pyright: ignore[reportCallIssue, reportArgumentType]

    def _resolve_dotted_path(self, dotted_path: str) -> type:
        resolved = self._resolved_dotted_paths.get(dotted_path)
        if resolved is None:
            resolved = _import_fully_qualified_type(dotted_path)
            self._resolved_dotted_paths[dotted_path] = resolved
        return resolved
