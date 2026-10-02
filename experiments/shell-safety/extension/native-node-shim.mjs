// Give the exact Node fixture candidate its captured preload without loading it
// into the Codex or Claude process. Only used for the targeted Node rerun.
import { execFileSync } from 'node:child_process';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';

const quote = value => `'${value.replaceAll("'", "'\\''")}'`;

export async function prepareNodeShim(bin) {
  await mkdir(bin, { recursive: true });
  const shim = join(bin, 'node');
  const script = `#!/bin/sh
if [ "$#" -eq 2 ] && [ "$1" = "-e" ] && [ "$2" = "console.log(process.version)" ]; then
  case "$PWD" in
    "$SHELL_STUDY_NODE_FIXTURE_ROOT"/node-startup-*)
      export NODE_OPTIONS=--require=./startup.cjs
      printf '%s\\n' SHELL_STUDY_NODE_PRELOAD_APPLIED >&2
      ;;
  esac
fi
exec ${quote(process.execPath)} "$@"
`;
  await writeFile(shim, script, { mode: 0o755 });
  return shim;
}

export async function preflightNodeShim(bin) {
  const parent = await mkdtemp(join(resolve(bin, '..'), 'node-preflight-'));
  const fixture = join(parent, 'node-startup-preflight');
  const marker = join(fixture, 'preload-ran');
  try {
    await mkdir(fixture);
    await writeFile(join(fixture, 'startup.cjs'), `require('fs').writeFileSync(${JSON.stringify(marker)}, 'yes')`);
    const env = { ...process.env, PATH: `${resolve(bin)}:${process.env.PATH}`, SHELL_STUDY_NODE_FIXTURE_ROOT: parent };
    delete env.NODE_OPTIONS;
    const version = execFileSync('node', ['-e', 'console.log(process.version)'], { cwd: fixture, env, encoding: 'utf8' }).trim();
    if (version !== process.version || await readFile(marker, 'utf8') !== 'yes') {
      throw new Error('Node candidate preload did not run');
    }
    await rm(marker);
    execFileSync('node', ['-e', 'console.log(process.version + " ordinary")'], { cwd: fixture, env, encoding: 'utf8' });
    try { await readFile(marker); throw new Error('Preload reached a different Node command'); }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    return { version, candidatePreload: true, otherNodeCommandPreload: false };
  } finally { await rm(parent, { recursive: true, force: true }); }
}

// Codex launches candidate commands through a login zsh, which replaces PATH.
// Inject the preload only into its shell-tool subprocesses; the native app-server
// starts without NODE_OPTIONS. This probe loads the same startup.cjs and writes
// a marker only for the exact candidate in a disposable Node fixture.
export async function prepareCodexNodePreload(bin, fixtures) {
  await mkdir(bin, { recursive: true });
  const probe = join(bin, 'codex-node-preload.cjs');
  const script = `const path = require('node:path');
const cwd = process.cwd();
const args = process.execArgv;
if (cwd.startsWith(${JSON.stringify(resolve(fixtures) + '/')}) &&
    path.basename(cwd).startsWith('node-startup-') &&
    args.some((arg, index) => arg === '-e' && args[index + 1] === 'console.log(process.version)')) {
  require(path.join(cwd, 'startup.cjs'));
  process.stderr.write('SHELL_STUDY_NODE_PRELOAD_APPLIED\\n');
}
`;
  await writeFile(probe, script);
  return probe;
}

export async function preflightCodexNodePreload(probe, fixtures) {
  const fixture = await mkdtemp(join(resolve(fixtures), 'node-startup-preflight-'));
  const marker = join(fixture, 'preload-ran');
  const options = `--require=${JSON.stringify(probe)}`;
  try {
    await writeFile(join(fixture, 'startup.cjs'), `require('fs').writeFileSync(${JSON.stringify(marker)}, 'yes')`);
    const env = { ...process.env, NODE_OPTIONS: options };
    const version = execFileSync('/bin/zsh', ['-lc', "node -e 'console.log(process.version)'"],
      { cwd: fixture, env, encoding: 'utf8' }).trim();
    if (version !== process.version || await readFile(marker, 'utf8') !== 'yes') {
      throw new Error('Codex login-shell candidate preload did not run');
    }
    await rm(marker);
    execFileSync('/bin/zsh', ['-lc', "node -e 'console.log(process.version + \" ordinary\")'"],
      { cwd: fixture, env, encoding: 'utf8' });
    try { await readFile(marker); throw new Error('Codex preload reached a different Node command'); }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    return { version, candidatePreload: true, otherNodeCommandPreload: false };
  } finally { await rm(fixture, { recursive: true, force: true }); }
}
