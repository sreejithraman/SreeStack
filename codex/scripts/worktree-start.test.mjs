import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { chmodSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import test, { after } from 'node:test';
import { fileURLToPath } from 'node:url';

const hook = path.join(path.dirname(fileURLToPath(import.meta.url)), 'worktree-start.mjs');
const tempRoots = new Set();

after(() => {
  for (const root of tempRoots) {
    rmSync(root, { force: true, recursive: true });
  }
});

function git(cwd, ...args) {
  return execFileSync('git', args, {
    cwd,
    encoding: 'utf8',
    env: { ...process.env, GIT_CONFIG_NOSYSTEM: '1' },
    stdio: ['ignore', 'pipe', 'pipe'],
  }).trim();
}

function initRepo() {
  const root = mkdtempSync(path.join(tmpdir(), 'codex-worktree-hook-'));
  tempRoots.add(root);
  const repo = path.join(root, 'repo');
  mkdirSync(repo);
  git(repo, 'init', '--initial-branch=main');
  git(repo, 'config', 'user.name', 'Codex Hook Test');
  git(repo, 'config', 'user.email', 'codex-hook@example.test');
  writeFileSync(path.join(repo, 'file.txt'), 'one\n');
  git(repo, 'add', 'file.txt');
  git(repo, 'commit', '-m', 'initial');
  return { root, repo };
}

function addOrigin(fixture) {
  const remote = path.join(fixture.root, 'remote.git');
  git(fixture.root, 'init', '--bare', '--initial-branch=main', remote);
  git(fixture.repo, 'remote', 'add', 'origin', remote);
  git(fixture.repo, 'push', '-u', 'origin', 'main');
  return remote;
}

function addDetachedWorktree(fixture, ref = 'main') {
  const worktree = path.join(fixture.root, `worktree-${Math.random().toString(16).slice(2)}`);
  git(fixture.repo, 'worktree', 'add', '--detach', worktree, ref);
  return worktree;
}

function commitFile(repo, text) {
  writeFileSync(path.join(repo, 'file.txt'), `${text}\n`);
  git(repo, 'add', 'file.txt');
  git(repo, 'commit', '-m', text);
  return git(repo, 'rev-parse', 'HEAD');
}

function runHook(cwd, source = 'startup') {
  const result = spawnSync('node', [hook], {
    cwd,
    encoding: 'utf8',
    input: JSON.stringify({ cwd, hook_event_name: 'SessionStart', source }),
    env: { ...process.env, GIT_CONFIG_NOSYSTEM: '1' },
  });
  assert.equal(result.status, 0, result.stderr);
  return result.stdout.trim() ? JSON.parse(result.stdout) : null;
}

test('moves a new detached main worktree to a newer origin/main', () => {
  const fixture = initRepo();
  const remote = addOrigin(fixture);
  const worktree = addDetachedWorktree(fixture);
  const peer = path.join(fixture.root, 'peer');
  git(fixture.root, 'clone', remote, peer);
  git(peer, 'config', 'user.name', 'Codex Hook Test');
  git(peer, 'config', 'user.email', 'codex-hook@example.test');
  const latest = commitFile(peer, 'remote-ahead');
  git(peer, 'push', 'origin', 'main');

  const output = runHook(worktree);

  assert.equal(output.continue, true);
  assert.equal(git(worktree, 'rev-parse', 'HEAD'), latest);
  assert.match(output.hookSpecificOutput.additionalContext, /Moved the new worktree/);
});

test('allows a detached main worktree that already matches origin/main', () => {
  const fixture = initRepo();
  addOrigin(fixture);
  const worktree = addDetachedWorktree(fixture);

  const output = runHook(worktree);

  assert.equal(output.continue, true);
  assert.match(output.hookSpecificOutput.additionalContext, /already matches/);
});

test('preserves unrelated remote refs while fetching origin/main', () => {
  const fixture = initRepo();
  addOrigin(fixture);
  git(fixture.repo, 'config', 'fetch.prune', 'true');
  git(fixture.repo, 'config', 'remote.origin.prune', 'true');
  const stale = git(fixture.repo, 'rev-parse', 'HEAD');
  git(fixture.repo, 'update-ref', 'refs/remotes/origin/stale', stale);
  const worktree = addDetachedWorktree(fixture);

  const output = runHook(worktree);

  assert.equal(output.continue, true);
  assert.equal(git(fixture.repo, 'rev-parse', 'refs/remotes/origin/stale'), stale);
});

test('uses local main when the repository has no origin', () => {
  const fixture = initRepo();
  const worktree = addDetachedWorktree(fixture);
  const before = git(worktree, 'rev-parse', 'HEAD');

  const output = runHook(worktree);

  assert.equal(output.continue, true);
  assert.equal(git(worktree, 'rev-parse', 'HEAD'), before);
  assert.match(output.hookSpecificOutput.additionalContext, /no origin remote/);
});

test('blocks the primary checkout on main', () => {
  const fixture = initRepo();

  const output = runHook(fixture.repo);

  assert.equal(output.continue, false);
  assert.match(output.stopReason, /Worktree mode/);
});

test('leaves the primary checkout on a feature branch alone', () => {
  const fixture = initRepo();
  git(fixture.repo, 'switch', '-c', 'feature');

  assert.equal(runHook(fixture.repo), null);
});

test('honors a detached worktree created from a feature branch', () => {
  const fixture = initRepo();
  addOrigin(fixture);
  git(fixture.repo, 'switch', '-c', 'feature');
  const featureHead = commitFile(fixture.repo, 'feature-work');
  git(fixture.repo, 'switch', 'main');
  const worktree = addDetachedWorktree(fixture, 'feature');

  assert.equal(runHook(worktree), null);
  assert.equal(git(worktree, 'rev-parse', 'HEAD'), featureHead);
});

test('leaves a branch-attached worktree alone', () => {
  const fixture = initRepo();
  const worktree = path.join(fixture.root, 'feature-worktree');
  git(fixture.repo, 'worktree', 'add', '-b', 'feature', worktree, 'main');

  assert.equal(runHook(worktree), null);
});

test('blocks a dirty detached main worktree', () => {
  const fixture = initRepo();
  addOrigin(fixture);
  const worktree = addDetachedWorktree(fixture);
  writeFileSync(path.join(worktree, 'file.txt'), 'dirty\n');

  const output = runHook(worktree);

  assert.equal(output.continue, false);
  assert.match(output.stopReason, /tracked or staged changes/);
});

test('blocks when local main is ahead of origin/main', () => {
  const fixture = initRepo();
  addOrigin(fixture);
  commitFile(fixture.repo, 'local-ahead');
  const worktree = addDetachedWorktree(fixture);

  const output = runHook(worktree);

  assert.equal(output.continue, false);
  assert.match(output.stopReason, /is ahead of origin\/main/);
});

test('blocks when local main and origin/main have split', () => {
  const fixture = initRepo();
  const remote = addOrigin(fixture);
  const peer = path.join(fixture.root, 'peer');
  git(fixture.root, 'clone', remote, peer);
  git(peer, 'config', 'user.name', 'Codex Hook Test');
  git(peer, 'config', 'user.email', 'codex-hook@example.test');
  commitFile(peer, 'remote-change');
  git(peer, 'push', 'origin', 'main');
  commitFile(fixture.repo, 'local-change');
  const worktree = addDetachedWorktree(fixture);

  const output = runHook(worktree);

  assert.equal(output.continue, false);
  assert.match(output.stopReason, /have split/);
});

test('updates origin/main after a safe force-push', () => {
  const fixture = initRepo();
  const initial = git(fixture.repo, 'rev-parse', 'HEAD');
  const remote = addOrigin(fixture);
  const worktree = addDetachedWorktree(fixture);
  const peer = path.join(fixture.root, 'peer');
  git(fixture.root, 'clone', remote, peer);
  git(peer, 'config', 'user.name', 'Codex Hook Test');
  git(peer, 'config', 'user.email', 'codex-hook@example.test');
  const replaced = commitFile(peer, 'replaced-remote-change');
  git(peer, 'push', 'origin', 'main');
  git(fixture.repo, 'fetch', 'origin');
  assert.equal(git(fixture.repo, 'rev-parse', 'refs/remotes/origin/main'), replaced);
  git(peer, 'reset', '--hard', initial);
  const replacement = commitFile(peer, 'replacement-remote-change');
  git(peer, 'push', '--force', 'origin', 'main');

  const output = runHook(worktree);

  assert.equal(output.continue, true);
  assert.equal(git(fixture.repo, 'rev-parse', 'refs/remotes/origin/main'), replacement);
  assert.equal(git(worktree, 'rev-parse', 'HEAD'), replacement);
});

test('does not fetch tags while updating origin/main', () => {
  const fixture = initRepo();
  const remote = addOrigin(fixture);
  const worktree = addDetachedWorktree(fixture);
  const peer = path.join(fixture.root, 'peer');
  git(fixture.root, 'clone', remote, peer);
  git(peer, 'config', 'user.name', 'Codex Hook Test');
  git(peer, 'config', 'user.email', 'codex-hook@example.test');
  const latest = commitFile(peer, 'tagged-remote-change');
  git(peer, 'tag', 'fetched-by-accident');
  git(peer, 'push', 'origin', 'main');
  git(peer, 'push', 'origin', 'fetched-by-accident');
  assert.throws(() => git(fixture.repo, 'rev-parse', '--verify', 'refs/tags/fetched-by-accident'));

  const output = runHook(worktree);

  assert.equal(output.continue, true);
  assert.equal(git(worktree, 'rev-parse', 'HEAD'), latest);
  assert.throws(() => git(fixture.repo, 'rev-parse', '--verify', 'refs/tags/fetched-by-accident'));
});

test('blocks when fetch fails', () => {
  const fixture = initRepo();
  addOrigin(fixture);
  const worktree = addDetachedWorktree(fixture);
  git(fixture.repo, 'remote', 'set-url', 'origin', path.join(fixture.root, 'missing.git'));

  const output = runHook(worktree);

  assert.equal(output.continue, false);
  assert.match(output.stopReason, /Could not fetch origin\/main/);
});

test('blocks when origin has no main branch', () => {
  const fixture = initRepo();
  const remote = path.join(fixture.root, 'remote.git');
  git(fixture.root, 'init', '--bare', '--initial-branch=master', remote);
  git(fixture.repo, 'remote', 'add', 'origin', remote);
  git(fixture.repo, 'push', 'origin', 'main:master');
  const worktree = addDetachedWorktree(fixture);

  const output = runHook(worktree);

  assert.equal(output.continue, false);
  assert.match(output.stopReason, /Could not fetch origin\/main/);
  assert.match(output.stopReason, /couldn't find remote ref refs\/heads\/main/);
});

test('allows untracked setup files while moving to origin/main', () => {
  const fixture = initRepo();
  const remote = addOrigin(fixture);
  const worktree = addDetachedWorktree(fixture);
  writeFileSync(path.join(worktree, 'local.env'), 'local=true\n');
  const peer = path.join(fixture.root, 'peer');
  git(fixture.root, 'clone', remote, peer);
  git(peer, 'config', 'user.name', 'Codex Hook Test');
  git(peer, 'config', 'user.email', 'codex-hook@example.test');
  const latest = commitFile(peer, 'remote-ahead');
  git(peer, 'push', 'origin', 'main');

  const output = runHook(worktree);

  assert.equal(output.continue, true);
  assert.equal(git(worktree, 'rev-parse', 'HEAD'), latest);
});

test('preserves an untracked file when origin/main starts tracking its path', () => {
  const fixture = initRepo();
  const remote = addOrigin(fixture);
  const worktree = addDetachedWorktree(fixture);
  const before = git(worktree, 'rev-parse', 'HEAD');
  writeFileSync(path.join(worktree, 'local.env'), 'local setup\n');
  const peer = path.join(fixture.root, 'peer');
  git(fixture.root, 'clone', remote, peer);
  git(peer, 'config', 'user.name', 'Codex Hook Test');
  git(peer, 'config', 'user.email', 'codex-hook@example.test');
  writeFileSync(path.join(peer, 'local.env'), 'remote setup\n');
  git(peer, 'add', 'local.env');
  git(peer, 'commit', '-m', 'track setup path');
  git(peer, 'push', 'origin', 'main');

  const output = runHook(worktree);

  assert.equal(output.continue, false);
  assert.equal(git(worktree, 'rev-parse', 'HEAD'), before);
  assert.equal(readFileSync(path.join(worktree, 'local.env'), 'utf8'), 'local setup\n');
});

test('does not run post-checkout hooks while moving the worktree', () => {
  const fixture = initRepo();
  const remote = addOrigin(fixture);
  const worktree = addDetachedWorktree(fixture);
  writeFileSync(path.join(worktree, 'local.env'), 'keep me\n');
  const peer = path.join(fixture.root, 'peer');
  git(fixture.root, 'clone', remote, peer);
  git(peer, 'config', 'user.name', 'Codex Hook Test');
  git(peer, 'config', 'user.email', 'codex-hook@example.test');
  commitFile(peer, 'remote-ahead');
  git(peer, 'push', 'origin', 'main');
  const hook = git(worktree, 'rev-parse', '--git-path', 'hooks/post-checkout');
  writeFileSync(hook, '#!/bin/sh\nprintf "changed by hook\\n" > "$PWD/local.env"\n');
  chmodSync(hook, 0o755);

  const output = runHook(worktree);

  assert.equal(output.continue, true);
  assert.equal(readFileSync(path.join(worktree, 'local.env'), 'utf8'), 'keep me\n');
});

test('preserves an unrelated nested Git checkout while moving the worktree', () => {
  const fixture = initRepo();
  const remote = addOrigin(fixture);
  const worktree = addDetachedWorktree(fixture);
  const nested = path.join(worktree, 'nested');
  mkdirSync(nested);
  git(nested, 'init', '--initial-branch=main');
  git(nested, 'config', 'user.name', 'Codex Hook Test');
  git(nested, 'config', 'user.email', 'codex-hook@example.test');
  writeFileSync(path.join(nested, 'local.txt'), 'keep me\n');
  git(nested, 'add', 'local.txt');
  git(nested, 'commit', '-m', 'nested local');
  const nestedHead = git(nested, 'rev-parse', 'HEAD');
  const peer = path.join(fixture.root, 'peer');
  git(fixture.root, 'clone', remote, peer);
  git(peer, 'config', 'user.name', 'Codex Hook Test');
  git(peer, 'config', 'user.email', 'codex-hook@example.test');
  const latest = commitFile(peer, 'remote-ahead');
  git(peer, 'push', 'origin', 'main');

  const output = runHook(worktree);

  assert.equal(output.continue, true);
  assert.equal(git(worktree, 'rev-parse', 'HEAD'), latest);
  assert.equal(git(nested, 'rev-parse', 'HEAD'), nestedHead);
  assert.equal(readFileSync(path.join(nested, 'local.txt'), 'utf8'), 'keep me\n');
});

test('preserves a nested Git checkout when origin/main collides with its file', () => {
  const fixture = initRepo();
  const remote = addOrigin(fixture);
  const worktree = addDetachedWorktree(fixture);
  const before = git(worktree, 'rev-parse', 'HEAD');
  const nested = path.join(worktree, 'nested');
  mkdirSync(nested);
  git(nested, 'init', '--initial-branch=main');
  git(nested, 'config', 'user.name', 'Codex Hook Test');
  git(nested, 'config', 'user.email', 'codex-hook@example.test');
  writeFileSync(path.join(nested, 'local.txt'), 'keep me\n');
  git(nested, 'add', 'local.txt');
  git(nested, 'commit', '-m', 'nested local');
  const nestedHead = git(nested, 'rev-parse', 'HEAD');
  const peer = path.join(fixture.root, 'peer');
  git(fixture.root, 'clone', remote, peer);
  git(peer, 'config', 'user.name', 'Codex Hook Test');
  git(peer, 'config', 'user.email', 'codex-hook@example.test');
  mkdirSync(path.join(peer, 'nested'));
  writeFileSync(path.join(peer, 'nested/local.txt'), 'remote content\n');
  git(peer, 'add', 'nested/local.txt');
  git(peer, 'commit', '-m', 'track nested path');
  git(peer, 'push', 'origin', 'main');

  const output = runHook(worktree);

  assert.equal(output.continue, false);
  assert.equal(git(worktree, 'rev-parse', 'HEAD'), before);
  assert.equal(git(nested, 'rev-parse', 'HEAD'), nestedHead);
  assert.equal(readFileSync(path.join(nested, 'local.txt'), 'utf8'), 'keep me\n');
});

test('does not recurse into submodules while moving the worktree', () => {
  const fixture = initRepo();
  const submodule = path.join(fixture.root, 'submodule');
  mkdirSync(submodule);
  git(submodule, 'init', '--initial-branch=main');
  git(submodule, 'config', 'user.name', 'Codex Hook Test');
  git(submodule, 'config', 'user.email', 'codex-hook@example.test');
  writeFileSync(path.join(submodule, 'sub.txt'), 'one\n');
  git(submodule, 'add', 'sub.txt');
  git(submodule, 'commit', '-m', 'submodule-one');
  const firstSubmoduleHead = git(submodule, 'rev-parse', 'HEAD');
  git(
    fixture.repo,
    '-c',
    'protocol.file.allow=always',
    'submodule',
    'add',
    submodule,
    'vendor/sub',
  );
  git(fixture.repo, 'commit', '-am', 'add submodule');
  const remote = addOrigin(fixture);
  const worktree = addDetachedWorktree(fixture);
  git(
    worktree,
    '-c',
    'protocol.file.allow=always',
    'submodule',
    'update',
    '--init',
  );
  git(worktree, 'config', 'submodule.recurse', 'true');
  const worktreeSubmodule = path.join(worktree, 'vendor/sub');
  writeFileSync(path.join(worktreeSubmodule, 'local.txt'), 'keep me\n');
  writeFileSync(path.join(submodule, 'sub.txt'), 'two\n');
  git(submodule, 'add', 'sub.txt');
  git(submodule, 'commit', '-m', 'submodule-two');
  const secondSubmoduleHead = git(submodule, 'rev-parse', 'HEAD');
  const peer = path.join(fixture.root, 'peer');
  git(fixture.root, 'clone', remote, peer);
  git(peer, 'config', 'user.name', 'Codex Hook Test');
  git(peer, 'config', 'user.email', 'codex-hook@example.test');
  git(
    peer,
    '-c',
    'protocol.file.allow=always',
    'submodule',
    'update',
    '--init',
  );
  const peerSubmodule = path.join(peer, 'vendor/sub');
  git(peerSubmodule, 'fetch', 'origin');
  git(peerSubmodule, 'checkout', secondSubmoduleHead);
  git(peer, 'add', 'vendor/sub');
  git(peer, 'commit', '-m', 'update submodule');
  const latest = git(peer, 'rev-parse', 'HEAD');
  git(peer, 'push', 'origin', 'main');

  const output = runHook(worktree);

  assert.equal(output.continue, true);
  assert.equal(git(worktree, 'rev-parse', 'HEAD'), latest);
  assert.equal(git(worktreeSubmodule, 'rev-parse', 'HEAD'), firstSubmoduleHead);
  assert.equal(readFileSync(path.join(worktreeSubmodule, 'local.txt'), 'utf8'), 'keep me\n');
});

test('does nothing for resume and non-Git starts', () => {
  const fixture = initRepo();
  const plain = path.join(fixture.root, 'plain');
  mkdirSync(plain);

  assert.equal(runHook(fixture.repo, 'resume'), null);
  assert.equal(runHook(plain), null);
});

test('preserves ignored setup files when origin/main starts tracking their path', () => {
  const fixture = initRepo();
  writeFileSync(path.join(fixture.repo, '.gitignore'), 'local.env\n');
  git(fixture.repo, 'add', '.gitignore');
  git(fixture.repo, 'commit', '-m', 'ignore local setup');
  const remote = addOrigin(fixture);
  const worktree = addDetachedWorktree(fixture);
  const before = git(worktree, 'rev-parse', 'HEAD');
  writeFileSync(path.join(worktree, 'local.env'), 'local setup\n');
  const peer = path.join(fixture.root, 'peer');
  git(fixture.root, 'clone', remote, peer);
  git(peer, 'config', 'user.name', 'Codex Hook Test');
  git(peer, 'config', 'user.email', 'codex-hook@example.test');
  writeFileSync(path.join(peer, 'local.env'), 'remote setup\n');
  git(peer, 'add', '--force', 'local.env');
  git(peer, 'commit', '-m', 'track setup path');
  git(peer, 'push', 'origin', 'main');

  const output = runHook(worktree);

  assert.equal(output.continue, false);
  assert.equal(git(worktree, 'rev-parse', 'HEAD'), before);
  assert.equal(readFileSync(path.join(worktree, 'local.env'), 'utf8'), 'local setup\n');
});
