import asyncio
import json

from mcp_sample.client import run_client
from mcp_sample.server import run_server


def test_client_server_roundtrip():
    async def runner():
        host = "127.0.0.1"
        port = 8765

        server_task = asyncio.create_task(run_server(host, port))
        try:
            await asyncio.sleep(0.1)
            responses = await run_client(host, port, message="test message")
        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass

        assert responses["tools"]["type"] == "response"
        tools_payload = responses["tools"]["result"]
        assert any(tool["name"] == "echo" for tool in tools_payload["tools"])

        echo_payload = responses["echo"]["result"]
        assert echo_payload["output"] == "test message"

        uppercase_payload = responses["uppercase"]["result"]
        assert uppercase_payload["output"] == "TEST MESSAGE"

        json.dumps(responses)

    asyncio.run(runner())
