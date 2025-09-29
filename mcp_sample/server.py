"""Minimal MCP server implementation for demonstration purposes."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Callable

from .protocol import build_handshake, decode_message, encode_message, is_handshake

LOGGER = logging.getLogger(__name__)


class ToolRegistry:
    """Simple in-memory collection of callable tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}

    def register(self, name: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        self._tools[name] = handler

    def describe(self) -> Dict[str, Any]:
        return {
            "tools": [
                {"name": name, "description": handler.__doc__ or ""}
                for name, handler in sorted(self._tools.items())
            ]
        }

    def call(self, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")
        return self._tools[name](params)


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()

    def echo_tool(params: Dict[str, Any]) -> Dict[str, Any]:
        """Echo the provided message back to the caller."""

        return {"output": params.get("message", "")}

    def uppercase_tool(params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert the provided message to uppercase."""

        message = params.get("message", "")
        return {"output": str(message).upper()}

    registry.register("echo", echo_tool)
    registry.register("uppercase", uppercase_tool)
    return registry


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, registry: ToolRegistry) -> None:
    peer = writer.get_extra_info("peername")
    LOGGER.info("Client connected: %s", peer)
    try:
        raw = await reader.readline()
        if not raw:
            LOGGER.warning("Connection closed before handshake from %s", peer)
            return
        message = decode_message(raw)
        if not is_handshake(message):
            LOGGER.error("Invalid handshake from %s: %s", peer, message)
            writer.write(encode_message({
                "type": "error",
                "error": {"code": 400, "message": "Handshake required"},
            }))
            await writer.drain()
            return
        writer.write(encode_message(build_handshake("server")))
        await writer.drain()

        while not reader.at_eof():
            raw = await reader.readline()
            if not raw:
                break
            message = decode_message(raw)
            LOGGER.debug("Received message from %s: %s", peer, message)
            response = await dispatch(message, registry)
            if response is None:
                continue
            writer.write(encode_message(response))
            await writer.drain()
    except asyncio.CancelledError:
        raise
    except Exception as exc:  # pragma: no cover - defensive logging
        LOGGER.exception("Error handling client %s: %s", peer, exc)
    finally:
        LOGGER.info("Client disconnected: %s", peer)
        writer.close()
        await writer.wait_closed()


async def dispatch(message: Dict[str, Any], registry: ToolRegistry) -> Dict[str, Any] | None:
    if message.get("type") != "request":
        return {
            "type": "error",
            "error": {"code": 400, "message": "Only request messages are supported"},
        }

    request_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}

    try:
        if method == "list_tools":
            result = registry.describe()
        elif method == "call_tool":
            name = params.get("name")
            if not name:
                raise ValueError("Missing tool name")
            tool_params = params.get("arguments") or {}
            result = registry.call(name, tool_params)
        else:
            raise ValueError(f"Unknown method: {method}")
    except Exception as exc:
        return {
            "type": "error",
            "id": request_id,
            "error": {"code": 400, "message": str(exc)},
        }

    return {"type": "response", "id": request_id, "result": result}


async def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    registry = build_default_registry()
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, registry), host, port
    )
    addresses = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])
    LOGGER.info("Serving on %s", addresses)
    try:
        async with server:
            await server.serve_forever()
    except asyncio.CancelledError:
        LOGGER.info("Server shutdown requested")
        raise


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
