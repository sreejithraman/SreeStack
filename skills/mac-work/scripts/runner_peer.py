"""Private test client for the canonical MCP facade; never a production route."""

import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys


async def main():
    from fastmcp import Client
    from fastmcp.client.transports import StdioTransport
    root = Path(sys.argv[1])
    transport = StdioTransport(command=str(root / 'bin/mac-work'), args=['mcp'],
        env={'FASTMCP_CHECK_FOR_UPDATES': 'off'}, keep_alive=False)
    async with Client(transport) as client:
        children = []
        for line in subprocess.check_output(['/bin/ps', '-axo', 'pid=,ppid=,args='], text=True).splitlines():
            pid, parent, command = line.strip().split(None, 2)
            if int(parent) == os.getpid() and str(root) in command and ' mcp' in command:
                children.append(int(pid))
        if len(children) != 1:
            raise RuntimeError('Could not identify the exact owned MCP server')
        print(json.dumps({'ready': True, 'server_pid': children[0]}), flush=True)
        while line := await asyncio.to_thread(sys.stdin.readline):
            request = json.loads(line)
            if request['tool'] == 'close':
                break
            try:
                value = await client.call_tool(request['tool'], request['arguments'])
                print(json.dumps({'result': value.structured_content}), flush=True)
            except Exception as error:
                print(json.dumps({'error': str(error)}), flush=True)


if __name__ == '__main__':
    asyncio.run(main())
