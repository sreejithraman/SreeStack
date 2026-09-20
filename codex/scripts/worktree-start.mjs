#!/usr/bin/env node

import path from 'node:path';
import { spawnSync } from 'node:child_process';

const BASE_BRANCH = 'main';
const REMOTE = 'origin';
const HOOK_EVENT_NAME = 'SessionStart';

function readStdin() {
  return new Promise((resolve) => {
    if (process.stdin.isTTY) {
      resolve('');
      return;
    }

    let input = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (chunk) => {
      input += chunk;
    });
    process.stdin.on('end', () => resolve(input));
    process.stdin.on('error', () => resolve(''));
  });
}

function parseInput(text) {
  if (!text.trim()) {
    return {};
  }

  try {
    return JSON.parse(text);
  } catch {
    return {};
  }
}

function git(cwd, args) {
  const result = spawnSync('git', args, {
    cwd,
    encoding: 'utf8',
    env: { ...process.env, GIT_TERMINAL_PROMPT: '0' },
    stdio: ['ignore', 'pipe', 'pipe'],
    timeout: 30_000,
  });

  return {
    ok: !result.error && result.status === 0,
    status: result.status ?? 1,
    stdout: (result.stdout ?? '').trim(),
    stderr: (result.stderr ?? result.error?.message ?? '').trim(),
  };
}

function commit(cwd, ref) {
  const result = git(cwd, ['rev-parse', '--verify', `${ref}^{commit}`]);
  return result.ok ? result.stdout : null;
}

function branch(cwd) {
  const result = git(cwd, ['symbolic-ref', '--quiet', '--short', 'HEAD']);
  return result.ok ? result.stdout : null;
}

function isAncestor(cwd, ancestor, descendant) {
  return git(cwd, ['merge-base', '--is-ancestor', ancestor, descendant]).status === 0;
}

function short(value) {
  return value?.slice(0, 12) ?? 'unknown';
}

function oneLine(value) {
  return value.replace(/\s+/g, ' ').trim().slice(0, 500);
}

function output({ continueSession, message, context }) {
  const result = {
    continue: continueSession,
    hookSpecificOutput: {
      hookEventName: HOOK_EVENT_NAME,
    },
  };

  if (!continueSession) {
    result.stopReason = message;
  }
  if (message) {
    result.systemMessage = message;
  }
  if (context) {
    result.hookSpecificOutput.additionalContext = context;
  }

  console.log(JSON.stringify(result));
}

function allow(context) {
  output({ continueSession: true, context });
}

function block(message) {
  output({ continueSession: false, message, context: message });
}

function isPrimaryCheckout(root) {
  const gitDir = git(root, ['rev-parse', '--absolute-git-dir']);
  const commonDir = git(root, ['rev-parse', '--git-common-dir']);
  if (!gitDir.ok || !commonDir.ok) {
    throw new Error('Could not find the Git worktree paths.');
  }

  return path.resolve(gitDir.stdout) === path.resolve(root, commonDir.stdout);
}

async function main() {
  const input = parseInput(await readStdin());
  if (input.source && input.source !== 'startup') {
    return;
  }

  const cwd = input.cwd || process.cwd();
  const rootResult = git(cwd, ['rev-parse', '--show-toplevel']);
  if (!rootResult.ok) {
    return;
  }

  const root = rootResult.stdout;
  const currentBranch = branch(root);
  const primary = isPrimaryCheckout(root);

  if (primary) {
    if (currentBranch === BASE_BRANCH) {
      block(
        'Codex opened the primary checkout on main. Start this task in Worktree mode so the primary checkout stays clean.',
      );
    }
    return;
  }

  if (currentBranch) {
    return;
  }

  const initialHead = commit(root, 'HEAD');
  const localMain = commit(root, `refs/heads/${BASE_BRANCH}`);
  if (!initialHead || !localMain || initialHead !== localMain) {
    return;
  }

  const trackedState = git(root, ['status', '--porcelain', '--untracked-files=no']);
  if (!trackedState.ok) {
    block('Could not check the new worktree for tracked changes. The worktree was left unchanged.');
    return;
  }
  if (trackedState.stdout) {
    block('The new main-based worktree has tracked or staged changes. The worktree was left unchanged.');
    return;
  }

  const origin = git(root, ['remote', 'get-url', REMOTE]);
  if (!origin.ok) {
    allow('This repository has no origin remote. The new worktree uses local main.');
    return;
  }

  const fetch = git(root, [
    'fetch',
    '--quiet',
    '--no-prune',
    '--no-tags',
    '--no-recurse-submodules',
    REMOTE,
    `+refs/heads/${BASE_BRANCH}:refs/remotes/${REMOTE}/${BASE_BRANCH}`,
  ]);
  if (!fetch.ok) {
    const detail = oneLine(fetch.stderr || fetch.stdout || 'unknown Git error');
    block(`Could not fetch origin/main: ${detail}. The worktree was left unchanged.`);
    return;
  }

  const remoteMain = commit(root, `refs/remotes/${REMOTE}/${BASE_BRANCH}`);
  if (!remoteMain) {
    block('The origin remote has no origin/main ref. The worktree was left unchanged.');
    return;
  }

  if (initialHead === remoteMain) {
    allow(`The new worktree already matches origin/main at ${short(remoteMain)}.`);
    return;
  }

  if (isAncestor(root, initialHead, remoteMain)) {
    const move = git(root, [
      '-c',
      'core.hooksPath=/dev/null',
      'switch',
      '--detach',
      '--quiet',
      '--no-overwrite-ignore',
      '--no-recurse-submodules',
      remoteMain,
    ]);
    if (!move.ok) {
      const detail = oneLine(move.stderr || move.stdout || 'unknown Git error');
      block(`Could not move the new worktree to origin/main: ${detail}.`);
      return;
    }

    allow(
      `Moved the new worktree from local main ${short(initialHead)} to origin/main ${short(remoteMain)}.`,
    );
    return;
  }

  if (isAncestor(root, remoteMain, initialHead)) {
    block(
      `Local main ${short(initialHead)} is ahead of origin/main ${short(remoteMain)}. The worktree was left unchanged. Push or reconcile main, then start a new worktree.`,
    );
    return;
  }

  block(
    `Local main ${short(initialHead)} and origin/main ${short(remoteMain)} have split. The worktree was left unchanged. Reconcile main, then start a new worktree.`,
  );
}

main().catch((error) => {
  block(`The worktree preflight failed: ${oneLine(error.message)}.`);
});
