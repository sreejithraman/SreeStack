# HTTP requests

Use this parent-side helper with the owned server described in
[SKILL.md](../SKILL.md#create-the-session). Set `server_url`, `server_password`,
and `workspace` from that process. It discovers operation paths from the live
OpenAPI contract, uses authenticated loopback HTTP without proxies, and sends
complete request bodies without command-argument limits.

```python
import base64, json, re, urllib.parse, urllib.request

auth = base64.b64encode(("opencode:" + server_password).encode()).decode()
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def request(method, path, payload=None, timeout=45):
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(server_url + path, data=body, method=method,
        headers={"Authorization": "Basic " + auth,
                 "Content-Type": "application/json"})
    with opener.open(req, timeout=timeout) as response:
        raw = response.read()
    return json.loads(raw) if raw else None

spec = request("GET", "/openapi.json")
operations = {entry["operationId"]: (method.upper(), path)
    for path, methods in spec["paths"].items()
    for method, entry in methods.items()
    if isinstance(entry, dict) and "operationId" in entry}

def api(operation, *, payload=None, params=None, timeout=45):
    method, path = operations[operation]
    query = dict(params or {})
    for name in re.findall(r"\{([^}]+)\}", path):
        path = path.replace("{" + name + "}",
            urllib.parse.quote(str(query.pop(name)), safe=""))
    if query:
        path += "?" + urllib.parse.urlencode(query)
    return request(method, path, payload, timeout)
```
