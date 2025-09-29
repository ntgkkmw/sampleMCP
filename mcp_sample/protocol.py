"""Utility helpers for the sample MCP implementation."""

from __future__ import annotations

import json
from typing import Any, Dict

from . import PROTOCOL_VERSION


def encode_message(message: Dict[str, Any]) -> bytes:
    """Serialize a message to a JSON line for transport."""
    return (json.dumps(message, separators=(",", ":")) + "\n").encode("utf-8")


def decode_message(raw: bytes) -> Dict[str, Any]:
    """Deserialize a message from a JSON line."""
    return json.loads(raw.decode("utf-8"))


def build_handshake(role: str) -> Dict[str, Any]:
    """Create a handshake payload for the given role."""
    return {"type": "handshake", "protocol": PROTOCOL_VERSION, "role": role}


def is_handshake(message: Dict[str, Any]) -> bool:
    """Return True when the message represents a MCP handshake."""
    return (
        message.get("type") == "handshake"
        and message.get("protocol") == PROTOCOL_VERSION
    )
