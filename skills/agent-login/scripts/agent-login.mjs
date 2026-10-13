#!/usr/bin/env node
import { readFile, stat, mkdir, open, unlink } from 'node:fs/promises';
import { execFile } from 'node:child_process';
import { createHash } from 'node:crypto';
import { homedir } from 'node:os';
import { join, dirname } from 'node:path';

class Failure extends Error {
  constructor(code) { super(code); this.code = code; }
}
function need(value, code) { if (!value) throw new Failure(code); }
function parse(argv) {
  const args = [...argv], command = args.shift() || 'help', options = {};
  let alias;
  if (command === 'fill') {
    alias = args.shift();
    need(alias && !alias.startsWith('--'), 'invalid_arguments');
  }
  while (args.length) {
    const key = args.shift();
    need(['--config', '--cdp', '--target', '--submit'].includes(key) && !(key in options), 'invalid_arguments');
    options[key] = key === '--submit' ? true : args.shift();
    need(options[key] && (options[key] === true || !options[key].startsWith('--')), 'invalid_arguments');
  }
  need(['help', '--help', 'list', 'tabs', 'fill'].includes(command), 'invalid_arguments');
  return { command, alias, options };
}
function origin(value) {
  let url;
  try { url = new URL(value); } catch { throw new Failure('invalid_origin'); }
  const local = ['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname);
  need(url.protocol === 'https:' || (url.protocol === 'http:' && local), 'invalid_origin');
  need(!url.username && !url.password && !url.search && !url.hash && url.pathname === '/', 'invalid_origin');
  return url.origin;
}
function reference(value) {
  need(typeof value === 'string' && /^op:\/\/[A-Za-z0-9]{26}\/[A-Za-z0-9]{26}\/[^/?#]+$/.test(value), 'invalid_reference');
  return value;
}
async function loadConfig(file) {
  let info, data;
  try {
    info = await stat(file);
    need(info.isFile() && info.size < 1024 * 1024, 'invalid_config');
    need((info.mode & 0o077) === 0 && (!process.getuid || info.uid === process.getuid()), 'config_permissions');
    data = JSON.parse(await readFile(file, 'utf8'));
  } catch (error) { if (error instanceof Failure) throw error; throw new Failure('config_unavailable'); }
  need(data.version === 1 && typeof data.serviceAccountId === 'string' && /^[A-Za-z0-9]{26}$/.test(data.serviceAccountId), 'invalid_config');
  need(data.accounts && typeof data.accounts === 'object' && !Array.isArray(data.accounts), 'invalid_config');
  for (const [alias, account] of Object.entries(data.accounts)) {
    need(/^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/.test(alias) && account && typeof account === 'object', 'invalid_config');
    account.origin = origin(account.origin);
    reference(account.username); reference(account.password);
    need(account.selectors && ['username', 'password'].every(key => typeof account.selectors[key] === 'string' && account.selectors[key].length > 0), 'invalid_config');
    need(account.selectors.submit === undefined || typeof account.selectors.submit === 'string', 'invalid_config');
    need(account.allowedOrigins === undefined || Array.isArray(account.allowedOrigins), 'invalid_config');
    account.allowedOrigins = [...new Set([account.origin, ...(account.allowedOrigins || []).map(origin)])];
    for (const key of ['purpose', 'role']) need(account[key] === undefined || (typeof account[key] === 'string' && account[key].length <= 512), 'invalid_config');
  }
  return data;
}

function endpoint(value) {
  let url;
  try { url = new URL(value); } catch { throw new Failure('invalid_endpoint'); }
  need(url.protocol === 'http:' && ['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname), 'invalid_endpoint');
  need(url.port && !url.username && !url.password && !url.search && !url.hash && url.pathname === '/', 'invalid_endpoint');
  return url;
}
async function connect(value) {
  const url = endpoint(value);
  let response, info;
  try {
    response = await fetch(new URL('/json/version', url), { redirect: 'error', signal: AbortSignal.timeout(5000) });
    need(response.ok, 'connection_failed');
    info = await response.json();
  } catch { throw new Failure('connection_failed'); }
  let ws;
  try { ws = new URL(info.webSocketDebuggerUrl); } catch { throw new Failure('invalid_endpoint'); }
  need(ws.protocol === 'ws:' && ['127.0.0.1', 'localhost', '[::1]'].includes(ws.hostname) && ws.port === url.port && !ws.username && !ws.password && !ws.search && !ws.hash, 'invalid_endpoint');
  // Playwright debug logging can echo input values; suppress it in this consumer.
  delete process.env.DEBUG;
  delete process.env.PWDEBUG;
  const { chromium } = await import('playwright-core');
  return chromium.connectOverCDP(ws.href, { noDefaults: true, timeout: 5000 });
}
async function pages(browser) {
  const results = [];
  for (const context of browser.contexts()) for (const page of context.pages()) {
    const session = await context.newCDPSession(page);
    try { const { targetInfo } = await session.send('Target.getTargetInfo'); results.push({ page, id: targetInfo.targetId }); }
    finally { await session.detach(); }
  }
  return results;
}
function op(args) {
  const env = { ...process.env, OP_BIOMETRIC_UNLOCK_ENABLED: 'false' };
  for (const key of Object.keys(env)) if (['OP_CONNECT_HOST', 'OP_CONNECT_TOKEN', 'OP_ACCOUNT'].includes(key) || key.startsWith('OP_SESSION_')) delete env[key];
  return new Promise((resolve, reject) => {
    execFile('op', args, { env, timeout: 15000, maxBuffer: 1024 * 1024, encoding: 'utf8' }, (error, stdout) => error ? reject(new Failure('credential_access_failed')) : resolve(stdout));
  });
}
async function lease(file, target) {
  const directory = join(dirname(file), '.agent-login-leases');
  await mkdir(directory, { recursive: true, mode: 0o700 });
  const info = await stat(directory);
  need(info.isDirectory() && (info.mode & 0o077) === 0 && (!process.getuid || info.uid === process.getuid()), 'lease_permissions');
  const key = createHash('sha256').update(target).digest('hex');
  const path = join(directory, key);
  let handle;
  try { handle = await open(path, 'wx', 0o600); }
  catch (error) { throw new Failure(error.code === 'EEXIST' ? 'target_busy' : 'lease_unavailable'); }
  try { await handle.writeFile(JSON.stringify({ pid: process.pid, targetId: target, startedAt: new Date().toISOString() }) + '\n'); }
  catch {
    await Promise.allSettled([handle.close(), unlink(path)]);
    throw new Failure('lease_unavailable');
  }
  return async () => { await handle.close(); await unlink(path); };
}
async function input(page, selector, password) {
  const locator = page.locator(selector);
  need(await locator.count() === 1, 'invalid_fields');
  need(await locator.isVisible() && await locator.isEditable(), 'invalid_fields');
  const handle = await locator.elementHandle();
  need(handle && await handle.ownerFrame() === page.mainFrame(), 'invalid_fields');
  need(await handle.evaluate((element, isPassword) => element instanceof HTMLInputElement && !element.disabled && !element.readOnly && element.value === '' && (isPassword ? element.type === 'password' : !['password', 'hidden', 'file', 'checkbox', 'radio', 'submit', 'button'].includes(element.type)), password), 'invalid_fields');
  return handle;
}
async function fill(browser, config, account, target, submit) {
  const selected = (await pages(browser)).find(entry => entry.id === target);
  need(selected, 'target_not_found');
  const page = selected.page;
  need(new URL(page.url()).origin === account.origin, 'origin_mismatch');
  need(!await page.evaluate(() => !!navigator.serviceWorker?.controller), 'service_worker_unsupported');
  const username = await input(page, account.selectors.username, false);
  const password = await input(page, account.selectors.password, true);
  need(await username.evaluate((element, other) => element !== other, password), 'invalid_fields');
  let button;
  if (submit) {
    need(account.selectors.submit, 'submit_selector_required');
    const locator = page.locator(account.selectors.submit);
    need(await locator.count() === 1 && await locator.isVisible(), 'invalid_submit');
    button = await locator.elementHandle();
    need(button && await button.ownerFrame() === page.mainFrame(), 'invalid_submit');
    need(await button.evaluate((element, fields) => element !== fields.username && element !== fields.password && (element instanceof HTMLButtonElement || (element instanceof HTMLInputElement && ['button', 'submit'].includes(element.type)) || (!(element instanceof HTMLInputElement) && element.getAttribute('role') === 'button')), { username, password }), 'invalid_submit');
  }
  const document = await page.evaluateHandle(() => document);
  async function bound(handle, value, passwordField = false) {
    try {
      need(await handle.evaluate((element, args) => element.isConnected && element.ownerDocument === args.document && location.origin === args.origin && !navigator.serviceWorker?.controller && element.value === args.value && !element.disabled && !element.readOnly && (!args.passwordField || element.type === 'password'), { document, origin: account.origin, value, passwordField }), 'form_changed');
    } catch { throw new Failure('form_changed'); }
  }
  let userValue, passwordValue, inputMayHaveOccurred = false;
  const guard = await page.context().newCDPSession(page);
  let denied = false, guardError = false, blockedRequests = 0;
  const sensitive = new Set();
  const active = new Set(), operations = new Set();
  let lastNetworkActivity = Date.now();
  function credentialRequest(request) {
    if (request.hasPostData && request.postData === undefined) return true;
    const content = request.url + '\n' + (request.postData || '');
    return [userValue, passwordValue].filter(Boolean).some(value => [value, encodeURIComponent(value), encodeURIComponent(value).replace(/%20/g, '+'), JSON.stringify(value).slice(1, -1)].some(form => content.includes(form)));
  }
  guard.on('Network.requestWillBeSent', event => {
    active.add(event.requestId);
    if (event.type === 'Document' || credentialRequest(event.request) || sensitive.has(event.requestId)) {
      sensitive.add(event.requestId); lastNetworkActivity = Date.now();
    }
  });
  for (const name of ['Network.loadingFinished', 'Network.loadingFailed']) guard.on(name, event => { active.delete(event.requestId);
    if (sensitive.delete(event.requestId)) lastNetworkActivity = Date.now(); });
  guard.on('Fetch.requestPaused', event => {
    const operation = (async () => {
      let allowed = false;
      try { allowed = account.allowedOrigins.includes(new URL(event.request.url).origin); } catch {}
      const carriesCredentials = event.resourceType === 'Document' || credentialRequest(event.request) || sensitive.has(event.networkId);
      if (carriesCredentials && event.networkId) { sensitive.add(event.networkId); lastNetworkActivity = Date.now(); }
      if (!allowed) { blockedRequests++; if (carriesCredentials) denied = true; }
      try { await guard.send(allowed ? 'Fetch.continueRequest' : 'Fetch.failRequest', allowed ? { requestId: event.requestId } : { requestId: event.requestId, errorReason: 'BlockedByClient' }); }
      catch { guardError = true; }
    })();
    operations.add(operation); operation.finally(() => operations.delete(operation));
  });
  async function guardStatus() {
    if (denied) throw new Failure('destination_denied');
    if (guardError) throw new Failure('destination_guard_failed');
  }
  async function settle() {
    const deadline = Date.now() + 5000;
    lastNetworkActivity = Date.now();
    while ([...sensitive].some(id => active.has(id)) || operations.size || Date.now() - lastNetworkActivity < 300) {
      await guardStatus();
      need(Date.now() < deadline, 'submission_pending');
      await new Promise(resolve => setTimeout(resolve, 25));
    }
    await guardStatus();
  }
  try {
    await guard.send('Network.enable');
    await guard.send('Fetch.enable', { patterns: [{ urlPattern: '*', requestStage: 'Request' }] });
    need(process.env.OP_SERVICE_ACCOUNT_TOKEN, 'service_account_required');
    let identity;
    try { identity = JSON.parse(await op(['whoami', '--format=json'])); } catch (error) { if (error instanceof Failure) throw error; throw new Failure('credential_access_failed'); }
    need(identity.user_uuid === config.serviceAccountId, 'service_account_mismatch');
    userValue = await op(['read', '--no-newline', account.username]);
    passwordValue = await op(['read', '--no-newline', account.password]);
    need(userValue.length > 0 && passwordValue.length > 0, 'empty_credentials');
    await bound(username, ''); await bound(password, '', true);
    inputMayHaveOccurred = true;
    await username.fill(userValue, { timeout: 5000 });
    await bound(username, userValue); await bound(password, '', true);
    await password.fill(passwordValue, { timeout: 5000 });
    await bound(username, userValue); await bound(password, passwordValue, true);
    if (submit) {
      need(await button.evaluate((element, args) => element.isConnected && element.ownerDocument === args.document && location.origin === args.origin, { document, origin: account.origin }), 'form_changed');
      need(await button.isEnabled(), 'invalid_submit');
      try { await button.click({ timeout: 5000 }); }
      catch (error) { if (error.name === 'TimeoutError') throw new Failure('submission_pending'); throw error; }
      await settle();
    }
    await guardStatus();
    return { status: submit ? 'submitted' : 'filled', targetId: target, blockedRequests };
  } catch (error) {
    if (inputMayHaveOccurred) {
      for (const [handle, value] of [[username, userValue], [password, passwordValue]]) {
        try { await handle.evaluate((element, args) => {
          if (element.isConnected && element.ownerDocument === args.document && element.value === args.value) {
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
            setter.call(element, ''); element.dispatchEvent(new Event('input', { bubbles: true })); element.dispatchEvent(new Event('change', { bubbles: true }));
          }
        }, { document, value }); } catch {}
      }
    }
    const failure = denied ? new Failure('destination_denied') : error instanceof Failure ? error : new Failure('operation_failed');
    failure.inputMayHaveOccurred = inputMayHaveOccurred;
    throw failure;
  } finally {
    // Cancel outstanding sensitive chains before detaching interception.
    if ([...sensitive].some(id => active.has(id))) {
      await Promise.allSettled([guard.send('Page.stopLoading')]);
    }
    await Promise.allSettled([...operations]);
    // Cleanup must never replace a controlled failure or its partial-input flag.
    await Promise.allSettled([guard.send('Fetch.disable')]);
    await Promise.allSettled([guard.detach(), document.dispose()]);
  }
}
async function main() {
  const { command, alias, options } = parse(process.argv.slice(2));
  if (command === 'help' || command === '--help') {
    return { usage: ['agent-login list [--config FILE]', 'agent-login tabs --cdp http://127.0.0.1:PORT', 'agent-login fill ALIAS --cdp http://127.0.0.1:PORT --target ID [--submit] [--config FILE]'], config: '~/.config/agents/accounts.json', adapter: 'existing local Chromium CDP tab' };
  }
  const file = options['--config'] || join(homedir(), '.config', 'agents', 'accounts.json');
  if (command === 'list') {
    const config = await loadConfig(file);
    return { accounts: Object.entries(config.accounts).map(([alias, account]) => ({ alias, origin: account.origin, purpose: account.purpose, role: account.role })) };
  }
  if (command === 'tabs') {
    const browser = await connect(options['--cdp']);
    try { return { tabs: (await pages(browser)).map(({ page, id }) => { let pageOrigin = null; try { pageOrigin = new URL(page.url()).origin; } catch {} return { targetId: id, origin: pageOrigin }; }) }; }
    finally { await browser.close(); }
  }
  const config = await loadConfig(file);
  need(Object.hasOwn(config.accounts, alias), 'account_not_found');
  need(typeof options['--target'] === 'string' && /^[A-Za-z0-9_-]+$/.test(options['--target']), 'invalid_target');
  const url = endpoint(options['--cdp']);
  const release = await lease(file, options['--target']);
  let browser;
  try { browser = await connect(url.href); return await fill(browser, config, config.accounts[alias], options['--target'], options['--submit']); }
  finally {
    // Disconnect only; externally owned contexts and pages remain running.
    if (browser) await Promise.allSettled([browser.close()]);
    await Promise.allSettled([release()]);
  }
}

main().then(value => console.log(JSON.stringify(value))).catch(error => {
  console.log(JSON.stringify({ status: 'error', code: error instanceof Failure ? error.code : 'operation_failed', inputMayHaveOccurred: error.inputMayHaveOccurred || false }));
  process.exitCode = 1;
});
