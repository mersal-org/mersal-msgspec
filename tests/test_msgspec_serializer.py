import uuid
from dataclasses import dataclass

import pytest

from mersal.msgspec import MsgspecSerializer

__all__ = (
    "Message1",
    "test_msgspec_dict_serialization",
    "test_msgspec_object_serialization",
    "test_msgspec_object_serialization_without_object_types",
)


pytestmark = pytest.mark.anyio


@dataclass
class Message1:
    name: str


async def test_msgspec_object_serialization():
    subject = MsgspecSerializer(
        object_types={
            Message1,
        }
    )

    message = Message1(name="A")

    encoded_message = subject.serialize(message)

    decoded_message = subject.deserialize(encoded_message)

    assert decoded_message == message


async def test_msgspec_object_serialization_without_object_types():
    """`object_types` is optional - a type left out of it falls back to being tagged
    with its fully-qualified dotted path and resolved on demand via
    `importlib.import_module`, so two independently-constructed serializers (e.g. a
    publisher and a subscriber in different processes) can round trip a message
    neither was ever told about upfront.
    """
    publisher = MsgspecSerializer()
    subscriber = MsgspecSerializer()

    message = Message1(name="A")

    encoded_message = publisher.serialize(message)

    expected_tag = f"{Message1.__module__}.{Message1.__qualname__}".encode()
    assert expected_tag in encoded_message  # sanity: tag is the dotted path, not "Message1"

    decoded_message = subscriber.deserialize(encoded_message)

    assert decoded_message == message


@pytest.mark.skip
async def test_msgspec_dict_serialization():
    subject = MsgspecSerializer(object_types=set())

    data = {"a": 10, "b": uuid.uuid4()}
    encoded_message = subject.serialize(data)

    decoded_data = subject.deserialize(encoded_message)

    assert decoded_data == data
