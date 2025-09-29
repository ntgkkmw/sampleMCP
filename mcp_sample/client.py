"""Minimal MCP client implementation for demonstration purposes."""

from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any, Dict

from .protocol import build_handshake, decode_message, encode_message, is_handshake


async def read_message(reader: asyncio.StreamReader) -> Dict[str, Any]:
    raw = await reader.readline()
    if not raw:
        raise ConnectionError("Connection closed by server")
    return decode_message(raw)


async def run_client(host: str = "127.0.0.1", port: int = 8765, *, message: str = "Hello, MCP!") -> Dict[str, Any]:
    reader, writer = await asyncio.open_connection(host, port)

    writer.write(encode_message(build_handshake("client")))
    await writer.drain()
    response = await read_message(reader)
    if not is_handshake(response):
        raise RuntimeError(f"Invalid handshake response: {json.dumps(response)}")

    writer.write(encode_message({
        "type": "request",
        "id": 1,
        "method": "list_tools",
    }))
    await writer.drain()
    tools_response = await read_message(reader)

    writer.write(encode_message({
        "type": "request",
        "id": 2,
        "method": "call_tool",
        "params": {"name": "echo", "arguments": {"message": message}},
    }))
    await writer.drain()
    echo_response = await read_message(reader)

    writer.write(encode_message({
        "type": "request",
        "id": 3,
        "method": "call_tool",
        "params": {"name": "uppercase", "arguments": {"message": message}},
    }))
    await writer.drain()
    upper_response = await read_message(reader)

    writer.close()
    await writer.wait_closed()

    return {
        "tools": tools_response,
        "echo": echo_response,
        "uppercase": upper_response,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the sample MCP client")
    parser.add_argument("--host", default="127.0.0.1", help="Hostname of the MCP server")
    parser.add_argument("--port", type=int, default=8765, help="Port of the MCP server")
    parser.add_argument(
        "--message",
        default="Hello, MCP!",
        help="Message to send to the echo and uppercase tools",
    )
    args = parser.parse_args()

    responses = asyncio.run(run_client(args.host, args.port, message=args.message))
    print(json.dumps(responses, indent=2))


if __name__ == "__main__":
    main()
