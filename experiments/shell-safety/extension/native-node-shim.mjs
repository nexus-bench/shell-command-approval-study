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
