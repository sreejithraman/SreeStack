import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, rm, readFile, mkdir, readdir } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import http from 'node:http';
import { chromium } from 'playwright-core';

const folder = dirname(fileURLToPath(import.meta.url));
const cli = join(folder, 'agent-login.mjs');
const vault = 'a'.repeat(26), item = 'b'.repeat(26), identity = 'C'.repeat(26);
function account(origin = 'https://example.com') {
  return { origin, username: `op://${vault}/${item}/username`, password: `op://${vault}/${item}/password`, selectors: { username: '#email', password: '#password', submit: '#submit' }, purpose: 'Test login', role: 'BUYER' };
}
async function fixture(t, accounts = { demo: account() }) {
  const root = await mkdtemp(join(tmpdir(), 'agent-login-test-'));
  const closers = [];
  t.after(async () => { for (const close of closers) await close(); await rm(root, { recursive: true, force: true }); });
  const config = join(root, 'accounts.json');
  await writeFile(config, JSON.stringify({ version: 1, serviceAccountId: identity, accounts }), { mode: 0o600 });
  return { root, config, closers };
}
function run(args, env = {}) {
  return new Promise(resolve => {
    const child = spawn(process.execPath, [cli, ...args], { env: { ...process.env, ...env } });
    let stdout = '', stderr = '';
    child.stdout.on('data', data => { stdout += data; });
    child.stderr.on('data', data => { stderr += data; });
    const timer = setTimeout(() => child.kill('SIGKILL'), 30000);
    child.on('close', status => { clearTimeout(timer); resolve({ status, stdout, stderr }); });
  });
}

async function browserFixture(t, options = {}) {
  const f = await fixture(t);
  const server = http.createServer(async (req, res) => {
    if (req.url === '/poll' && options.backgroundDelay) {
      await new Promise(resolve => setTimeout(resolve, options.backgroundDelay));
      return res.end('background');
    }
    if (req.method === 'POST') {
      let body = ''; for await (const chunk of req) body += chunk;
      const fields = new URLSearchParams(body);
      const valid = fields.get('email') === 'fixture@example.invalid' && fields.get('password') === 'FIXTURE_password_never_echo';
      if (options.responseDelay) await new Promise(resolve => setTimeout(resolve, options.responseDelay));
      if (options.loginRedirect) { res.writeHead(307, { Location: options.loginRedirect }); return res.end(); }
      res.writeHead(valid ? 200 : 403, { 'Content-Type': 'text/html' });
      return res.end(`<h1>${valid ? 'Signed in' : 'Invalid credentials'}</h1>`);
    }
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end((req.url === '/' && options.html) || '<form method="POST" action="/login"><label>Email<input id="email" name="email" type="email"></label><label>Password<input id="password" name="password" type="password"></label><button id="submit">Log In</button></form>');
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  const browserEnv = Object.fromEntries(Object.entries(process.env).filter(([key]) => !key.startsWith('OP_')));
  const owner = await chromium.launchPersistentContext(join(f.root, 'browser-profile'), {
    headless: true, executablePath: process.env.TEST_BROWSER_EXECUTABLE || chromium.executablePath(),
    args: ['--remote-debugging-port=0', '--remote-debugging-address=127.0.0.1'], env: browserEnv,
  });
  f.closers.push(() => owner.close(), () => new Promise(resolve => server.close(resolve)));
  const port = (await readFile(join(f.root, 'browser-profile', 'DevToolsActivePort'), 'utf8')).split('\n')[0];
  const page = owner.pages()[0]; await page.goto(origin);
  const session = await owner.newCDPSession(page);
  const { targetInfo } = await session.send('Target.getTargetInfo'); await session.detach();
  await writeFile(f.config, JSON.stringify({ version: 1, serviceAccountId: identity, accounts: { demo: account(origin) } }), { mode: 0o600 });
  const bin = join(f.root, 'bin'); await mkdir(bin);
  await writeFile(join(bin, 'op'), `#!/usr/bin/env node\nconst fs=require('node:fs');const args=process.argv.slice(2);fs.appendFileSync(process.env.FAKE_OP_LOG,args[0]+'\\n');if(args[0]==='whoami')console.log(JSON.stringify({user_uuid:process.env.FAKE_OP_ID || '${identity}'}));else if(args[0]==='read'){if(process.env.FAKE_OP_FAIL){console.error('FIXTURE_password_never_echo');process.exit(1);}const ref=args.find(x=>x.startsWith('op://'));setTimeout(()=>process.stdout.write(ref.endsWith('/username')?'fixture@example.invalid':'FIXTURE_password_never_echo'),Number(process.env.FAKE_OP_DELAY || 0));}else process.exit(1);\n`, { mode: 0o700 });
  return { ...f, owner, page, origin, endpoint: `http://127.0.0.1:${port}`, target: targetInfo.targetId, env: { PATH: `${bin}:${process.env.PATH}`, FAKE_OP_LOG: join(f.root, 'op-log'), OP_SERVICE_ACCOUNT_TOKEN: 'fixture-service-token' } };
}

test('list discovers user aliases without resolving or printing credentials', async t => {
  const { config } = await fixture(t);
  const result = await run(['list', '--config', config], { OP_SERVICE_ACCOUNT_TOKEN: '' });
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(JSON.parse(result.stdout), { accounts: [{ alias: 'demo', origin: 'https://example.com', purpose: 'Test login', role: 'BUYER' }] });
  assert.equal(result.stderr, '');
  assert.ok(!result.stdout.includes('op://'));
});

test('fill requires a positional alias before loading any configuration', async () => {
  for (const args of [['fill'], ['fill', '--submit']]) {
    const result = await run(args);
    assert.equal(result.status, 1);
    assert.equal(JSON.parse(result.stdout).code, 'invalid_arguments');
  }
});

async function operations(f) {
  try { return (await readFile(f.env.FAKE_OP_LOG, 'utf8')).trim().split('\n'); }
  catch (error) { if (error.code === 'ENOENT') return []; throw error; }
}

test('tabs discovers existing targets without exposing credentials and leaves owner tabs usable', async t => {
  const f = await browserFixture(t);
  const sibling = await f.owner.newPage();
  const username = 'fixture@example.invalid', password = 'FIXTURE_password_never_echo';
  const origins = [f.origin, f.origin.replace('127.0.0.1', 'localhost')];
  const tabs = [f.page, sibling];
  const expected = [];
  const urls = [];
  for (const [index, page] of tabs.entries()) {
    const url = `${origins[index]}/?username=${encodeURIComponent(username)}#${password}`;
    await page.goto(url);
    await page.evaluate(value => { document.title = value; }, `${username} ${password}`);
    await page.locator('#email').fill(username);
    await page.locator('#password').fill(password);
    const session = await f.owner.newCDPSession(page);
    try {
      const { targetInfo } = await session.send('Target.getTargetInfo');
      expected.push({ targetId: targetInfo.targetId, origin: origins[index] });
    } finally { await session.detach(); }
    urls.push(page.url());
  }

  const result = await run(['tabs', '--cdp', f.endpoint], f.env);
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.equal(result.stderr, '');
  const output = JSON.parse(result.stdout);
  const byTarget = (a, b) => a.targetId.localeCompare(b.targetId);
  assert.deepEqual({ ...output, tabs: output.tabs.toSorted(byTarget) }, { tabs: expected.toSorted(byTarget) });
  for (const value of [username, encodeURIComponent(username), password, f.env.OP_SERVICE_ACCOUNT_TOKEN, 'op://']) {
    assert.ok(!(result.stdout + result.stderr).includes(value));
  }
  assert.deepEqual(await operations(f), []);
  assert.equal(f.owner.pages().length, tabs.length);
  for (const [index, page] of tabs.entries()) {
    assert.equal(page.isClosed(), false);
    assert.equal(page.url(), urls[index]);
    assert.equal(await page.locator('#email').inputValue(), username);
    assert.equal(await page.locator('#password').inputValue(), password);
    await page.locator('#email').fill('owner@example.invalid');
    assert.equal(await page.locator('#email').inputValue(), 'owner@example.invalid');
    await page.goto(`${origins[index]}/owner`);
    assert.equal(await page.locator('#password').inputValue(), '');
  }
});

test('wrong destination, target, and missing token fail before credential reads', async t => {
  const f = await browserFixture(t);
  const args = ['fill', 'demo', '--config', f.config, '--cdp', f.endpoint, '--target', f.target];
  const missing = await run(args, { ...f.env, OP_SERVICE_ACCOUNT_TOKEN: '' });
  assert.equal(JSON.parse(missing.stdout).code, 'service_account_required');
  const target = await run([...args.slice(0, -1), 'nonexistent-target'], f.env);
  assert.equal(JSON.parse(target.stdout).code, 'target_not_found');
  await writeFile(f.config, JSON.stringify({ version: 1, serviceAccountId: identity, accounts: { demo: account('https://example.com') } }));
  const wrongOrigin = await run(args, f.env);
  assert.equal(JSON.parse(wrongOrigin.stdout).code, 'origin_mismatch');
  assert.deepEqual(await operations(f), []);
  assert.equal(await f.page.locator('#password').inputValue(), '');
});

test('wrong service identity and private credential errors expose no values', async t => {
  const f = await browserFixture(t);
  const args = ['fill', 'demo', '--config', f.config, '--cdp', f.endpoint, '--target', f.target];
  const mismatch = await run(args, { ...f.env, FAKE_OP_ID: 'D'.repeat(26) });
  assert.equal(JSON.parse(mismatch.stdout).code, 'service_account_mismatch');
  assert.deepEqual(await operations(f), ['whoami']);
  const failure = await run(args, { ...f.env, FAKE_OP_FAIL: '1' });
  assert.equal(JSON.parse(failure.stdout).code, 'credential_access_failed');
  assert.ok(!(failure.stdout + failure.stderr).includes('FIXTURE_password_never_echo'));
  assert.equal(await f.page.locator('#password').inputValue(), '');
});

test('iframe fields are rejected before any credential retrieval', async t => {
  const f = await browserFixture(t, { html: '<iframe src="/frame"></iframe>' });
  // Replace the frame with a form inside the same-origin frame.
  const frame = f.page.frames().find(frame => frame !== f.page.mainFrame());
  await frame.setContent('<input id="email" type="email"><input id="password" type="password">');
  const mapped = account(f.origin);
  mapped.selectors.username = 'iframe >> internal:control=enter-frame >> #email';
  mapped.selectors.password = 'iframe >> internal:control=enter-frame >> #password';
  await writeFile(f.config, JSON.stringify({ version: 1, serviceAccountId: identity, accounts: { demo: mapped } }));
  const result = await run(['fill', 'demo', '--config', f.config, '--cdp', f.endpoint, '--target', f.target], f.env);
  assert.equal(result.status, 1);
  assert.deepEqual(await operations(f), []);
  assert.equal(await frame.locator('#password').inputValue(), '');
});

test('a credential input cannot double as the submit control', async t => {
  const f = await browserFixture(t);
  const mapped = account(f.origin); mapped.selectors.submit = '#password';
  await writeFile(f.config, JSON.stringify({ version: 1, serviceAccountId: identity, accounts: { demo: mapped } }));
  const result = await run(['fill', 'demo', '--config', f.config, '--cdp', f.endpoint, '--target', f.target, '--submit'], f.env);
  assert.equal(result.status, 1);
  assert.equal(JSON.parse(result.stdout).code, 'invalid_submit');
  assert.deepEqual(await operations(f), []);
});

test('fill submits the exact existing tab and leaves it usable by its owner', async t => {
  const f = await browserFixture(t);
  await f.page.locator('#submit').evaluate(button => {
    button.disabled = true;
    document.querySelector('form').addEventListener('input', () => {
      button.disabled = !(document.querySelector('#email').value && document.querySelector('#password').value);
    });
  });
  const sibling = await f.owner.newPage(); await sibling.goto(f.origin);
  const result = await run(['fill', 'demo', '--config', f.config, '--cdp', f.endpoint, '--target', f.target, '--submit'], f.env);
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.equal(JSON.parse(result.stdout).status, 'submitted');
  await f.page.getByRole('heading', { name: 'Signed in' }).waitFor();
  assert.equal(await sibling.locator('#email').inputValue(), '');
  assert.equal(await sibling.locator('#password').inputValue(), '');
  assert.equal(f.page.isClosed(), false);
  assert.ok(!(result.stdout + result.stderr).includes('FIXTURE_password_never_echo'));
  assert.ok(!(result.stdout + result.stderr).includes('fixture@example.invalid'));
});

test('a login redirect cannot forward credentials to an unapproved origin', async t => {
  let foreignPosts = 0;
  const foreign = http.createServer(async (req, res) => {
    if (req.method === 'POST') foreignPosts++;
    for await (const chunk of req) { /* Drain dummy input without retaining it. */ }
    res.end('<h1>Foreign destination</h1>');
  });
  await new Promise(resolve => foreign.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise(resolve => foreign.close(resolve)));
  const f = await browserFixture(t, { loginRedirect: `http://127.0.0.1:${foreign.address().port}/receive` });
  const result = await run(['fill', 'demo', '--config', f.config, '--cdp', f.endpoint, '--target', f.target, '--submit'], f.env);
  assert.equal(foreignPosts, 0, 'The external origin received a credential submission');
  assert.equal(result.status, 1);
  assert.equal(JSON.parse(result.stdout).code, 'destination_denied');
});

test('partial input fails safely when the original password field is replaced', async t => {
  const f = await browserFixture(t);
  await f.page.locator('#email').evaluate(element => element.addEventListener('input', () => {
    const password = document.querySelector('#password'); password.replaceWith(password.cloneNode());
  }));
  const result = await run(['fill', 'demo', '--config', f.config, '--cdp', f.endpoint, '--target', f.target], f.env);
  assert.equal(result.status, 1);
  assert.equal(JSON.parse(result.stdout).code, 'form_changed');
  assert.equal(JSON.parse(result.stdout).inputMayHaveOccurred, true);
  assert.equal(await f.page.locator('#email').inputValue(), '');
  assert.equal(await f.page.locator('#password').inputValue(), '');
});

test('a second consumer is rejected while credential retrieval owns the target', async t => {
  const f = await browserFixture(t);
  const args = ['fill', 'demo', '--config', f.config, '--cdp', f.endpoint, '--target', f.target];
  const first = run(args, { ...f.env, FAKE_OP_DELAY: '600' });
  for (let attempts = 0; !(await operations(f)).includes('read'); attempts++) {
    assert.ok(attempts < 100, 'First consumer never reached credential retrieval');
    await new Promise(resolve => setTimeout(resolve, 25));
  }
  const leaseDirectory = join(f.root, '.agent-login-leases');
  const leases = await readdir(leaseDirectory);
  assert.equal(leases.length, 1);
  const lease = JSON.parse(await readFile(join(leaseDirectory, leases[0]), 'utf8'));
  assert.equal(lease.targetId, f.target);
  assert.ok(Number.isInteger(lease.pid) && lease.pid > 0);
  assert.ok(Number.isFinite(Date.parse(lease.startedAt)));
  const aliasArgs = args.map(arg => arg === f.endpoint ? arg.replace('127.0.0.1', 'localhost') : arg);
  const second = await run(aliasArgs, f.env);
  assert.equal(JSON.parse(second.stdout).code, 'target_busy');
  const filled = await first;
  assert.equal(filled.status, 0);
  assert.equal(JSON.parse(filled.stdout).status, 'filled');
  assert.equal(await f.page.locator('#email').inputValue(), 'fixture@example.invalid');
  assert.equal(await f.page.locator('#password').inputValue(), 'FIXTURE_password_never_echo');
});

test('insecure mapping permissions and remote CDP endpoints are refused', async t => {
  const { config } = await fixture(t);
  const { chmod } = await import('node:fs/promises');
  await chmod(config, 0o644);
  const permissions = await run(['list', '--config', config]);
  assert.equal(JSON.parse(permissions.stdout).code, 'config_permissions');
  const remote = await run(['tabs', '--cdp', 'http://example.com:9222']);
  assert.equal(JSON.parse(remote.stdout).code, 'invalid_endpoint');
});

test('blocked background telemetry does not misreport an otherwise submitted login', async t => {
  let foreignPosts = 0;
  const foreign = http.createServer((req, res) => { foreignPosts++; res.end('ok'); });
  await new Promise(resolve => foreign.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise(resolve => foreign.close(resolve)));
  const f = await browserFixture(t);
  await f.page.locator('form').evaluate((form, endpoint) => form.addEventListener('submit', () => {
    fetch(endpoint, { method: 'POST', body: JSON.stringify({ event: 'login-clicked' }), keepalive: true }).catch(() => {});
  }), `http://127.0.0.1:${foreign.address().port}/telemetry`);
  const result = await run(['fill', 'demo', '--config', f.config, '--cdp', f.endpoint, '--target', f.target, '--submit'], f.env);
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.equal(JSON.parse(result.stdout).status, 'submitted');
  assert.ok(JSON.parse(result.stdout).blockedRequests > 0);
  assert.equal(foreignPosts, 0);
  await f.page.getByRole('heading', { name: 'Signed in' }).waitFor();
});

test('a pending asynchronous credential request stays guarded through its redirect', async t => {
  let foreignPosts = 0;
  const foreign = http.createServer(async (req, res) => {
    if (req.method === 'POST') foreignPosts++;
    for await (const chunk of req) { /* Drain dummy input. */ }
    res.end('ok');
  });
  await new Promise(resolve => foreign.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise(resolve => foreign.close(resolve)));
  const f = await browserFixture(t, { responseDelay: 600, loginRedirect: `http://127.0.0.1:${foreign.address().port}/receive` });
  await f.page.locator('form').evaluate(form => form.addEventListener('submit', event => {
    event.preventDefault();
    fetch('/login', { method: 'POST', body: new URLSearchParams(new FormData(form)) }).catch(() => {});
  }));
  const result = await run(['fill', 'demo', '--config', f.config, '--cdp', f.endpoint, '--target', f.target, '--submit'], f.env);
  assert.equal(foreignPosts, 0);
  assert.equal(JSON.parse(result.stdout).code, 'destination_denied');
});

test('a submission timeout cancels pending credential redirects before disconnecting', async t => {
  let foreignPosts = 0;
  const foreign = http.createServer(async (req, res) => {
    if (req.method === 'POST') foreignPosts++;
    for await (const chunk of req) { /* Drain dummy input. */ }
    res.end('ok');
  });
  await new Promise(resolve => foreign.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise(resolve => foreign.close(resolve)));
  const f = await browserFixture(t, { responseDelay: 6500, loginRedirect: `http://127.0.0.1:${foreign.address().port}/receive` });
  await f.page.locator('form').evaluate(form => form.addEventListener('submit', event => {
    event.preventDefault();
    fetch('/login', { method: 'POST', body: new URLSearchParams(new FormData(form)) }).catch(() => {});
  }));
  const result = await run(['fill', 'demo', '--config', f.config, '--cdp', f.endpoint, '--target', f.target, '--submit'], f.env);
  assert.equal(result.status, 1);
  assert.equal(JSON.parse(result.stdout).code, 'submission_pending');
  await new Promise(resolve => setTimeout(resolve, 1800));
  assert.equal(foreignPosts, 0, 'Pending credential redirect escaped after consumer disconnected');
  assert.equal(f.page.isClosed(), false);
});

test('a slow unrelated request does not hold up a completed credential submission', async t => {
  const f = await browserFixture(t, { backgroundDelay: 6500 });
  await f.page.locator('form').evaluate(form => form.addEventListener('submit', event => {
    event.preventDefault();
    fetch('/poll').catch(() => {});
    fetch('/login', { method: 'POST', body: new URLSearchParams(new FormData(form)) })
      .then(response => response.text()).then(html => document.body.innerHTML = html).catch(() => {});
  }));
  const result = await run(['fill', 'demo', '--config', f.config, '--cdp', f.endpoint, '--target', f.target, '--submit'], f.env);
  assert.equal(result.status, 0, result.stdout + result.stderr);
  assert.equal(JSON.parse(result.stdout).status, 'submitted');
  await f.page.getByRole('heading', { name: 'Signed in' }).waitFor();
});

test('a slow document submission reports the same controlled pending status', async t => {
  const f = await browserFixture(t, { responseDelay: 6500 });
  const result = await run(['fill', 'demo', '--config', f.config, '--cdp', f.endpoint, '--target', f.target, '--submit'], f.env);
  assert.equal(result.status, 1);
  assert.equal(JSON.parse(result.stdout).code, 'submission_pending');
  assert.equal(JSON.parse(result.stdout).inputMayHaveOccurred, true);
  assert.equal(f.page.isClosed(), false);
});

test('a replaced document produces form_changed before credential input', async t => {
  const f = await browserFixture(t);
  const pending = run(['fill', 'demo', '--config', f.config, '--cdp', f.endpoint, '--target', f.target], { ...f.env, FAKE_OP_DELAY: '600' });
  for (let attempts = 0; !(await operations(f)).includes('read'); attempts++) {
    assert.ok(attempts < 100, 'Consumer never reached credential retrieval');
    await new Promise(resolve => setTimeout(resolve, 25));
  }
  await f.page.goto(f.origin + '/changed');
  const result = await pending;
  assert.equal(result.status, 1);
  assert.equal(JSON.parse(result.stdout).code, 'form_changed');
  assert.equal(JSON.parse(result.stdout).inputMayHaveOccurred, false);
  assert.equal(await f.page.locator('#email').inputValue(), '');
  assert.equal(await f.page.locator('#password').inputValue(), '');
});
