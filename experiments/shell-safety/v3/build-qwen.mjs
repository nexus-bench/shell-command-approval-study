import {build} from 'esbuild';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {readFileSync, writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const here = dirname(fileURLToPath(import.meta.url));
const upstream = resolve(here, '../../../.experiments/upstream/qwen-code');
const pin = 'a011f66944768e05b432a10548ffa4576f1d8ef8';
if (execFileSync('git', ['rev-parse', 'HEAD'], {cwd: upstream, encoding: 'utf8'}).trim() !== pin) throw new Error('Wrong Qwen revision');
const result = await build({
  entryPoints: [resolve(here, 'qwen-entry.mjs')],
  outfile: resolve(here, '../../../.experiments/qwen-classifier.mjs'),
  bundle: true, platform: 'node', format: 'esm', metafile: true,
  plugins: [{name: 'isolate-classifier', setup(b) {
    b.onResolve({filter: /^upstream-classifier$/}, () => ({path: resolve(upstream, 'packages/core/src/permissions/classifier.ts')}));
    b.onResolve({filter: /\/sideQuery\.js$/}, () => ({path: resolve(here, 'qwen-transport.mjs')}));
    b.onResolve({filter: /\/debugLogger\.js$/}, () => ({path: 'logger', namespace: 'shim'}));
    b.onResolve({filter: /\/contextLengthError\.js$/}, () => ({path: 'context', namespace: 'shim'}));
    b.onLoad({filter: /.*/, namespace: 'shim'}, a => ({contents: a.path === 'logger'
      ? 'export const createDebugLogger = () => ({debug(){}, warn(){}});'
      : 'export const isContextLengthExceededError = e => /context|token limit/i.test(String(e));', loader: 'js'}));
  }}],
});
const sources = Object.keys(result.metafile.inputs).filter(p => !p.startsWith('shim:')).map(p => ({path: p,
  sha256: createHash('sha256').update(readFileSync(p)).digest('hex')}));
writeFileSync(resolve(here, 'qwen-build.json'), JSON.stringify({revision: pin, sources,
  limitations: ['Local JSON-schema transport replaces runSideQuery; no SDK retry parity claim.',
    'No parent agent, allowlist, sandbox, or native permission manager.',
    'Stock transcript: user request and pending command only; no file evidence promoted to user messages.']}, null, 2) + '\n');
console.log('Built pinned source-isolated classifier');
