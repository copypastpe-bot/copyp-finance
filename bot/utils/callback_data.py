import base64
import uuid


def encode_uuid(value: uuid.UUID | str) -> str:
    if isinstance(value, str):
        value = uuid.UUID(value)
    return base64.urlsafe_b64encode(value.bytes).decode("ascii").rstrip("=")


def decode_uuid(value: str) -> uuid.UUID:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return uuid.UUID(bytes=base64.urlsafe_b64decode(value + padding))
