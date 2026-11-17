"""Independent MCP client process for the fitness gate's JSON-line protocol."""

import asyncio
import json
from pathlib import Path
import sys


async def main():
    from fastmcp import Client
    from fastmcp.client.transports import StdioTransport

    runtime, state = map(Path, sys.argv[1:3])
    contract = sys.argv[3:4]
    transport = StdioTransport(
        command=str(runtime / 'bin/agent-task-queue'),
        args=['--data-dir', str(state), '--queue-capacity', 'heavy=1']
             + (['--ownership-contract', contract[0]] if contract else []),
        env={'TASK_QUEUE_POLL_WAITING': '.05', 'PYTHONUNBUFFERED': '1',
             'FASTMCP_CHECK_FOR_UPDATES': 'off'},
        keep_alive=False,
    )
    async with Client(transport) as client:
        print(json.dumps({'ready': True}), flush=True)
        while line := await asyncio.to_thread(sys.stdin.readline):
            request = json.loads(line)
            if request['tool'] == 'close':
                break
            try:
                result = await client.call_tool(request['tool'], request['arguments'])
                print(json.dumps({'result': result.structured_content['result']}), flush=True)
            except Exception as error:
                print(json.dumps({'error': str(error)}), flush=True)


if __name__ == '__main__':
    asyncio.run(main())
