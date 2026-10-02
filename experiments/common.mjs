import { mkdtemp, mkdir, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const root = fileURLToPath(new URL('../', import.meta.url));
export const fixture = resolve(root, 'experiments/fixture.py');
export const python = process.env.EXPERIMENT_PYTHON || 'python3';
export async function workspace() {
  const cwd = await mkdtemp(resolve(tmpdir(), 'unit-ui-feasibility-'));
  const state = resolve(cwd, 'revision.txt');
  await writeFile(state, '1');
  return { cwd, state };
}

// Only caller-selected metadata enters traces. Never serialize raw SDK events,
// account responses, environments, request headers, stderr, or model reasoning.
export function recorder(name) {
  const rows = [];
  const record = (event, data = {}) => {
    const row = { event, ...data };
    rows.push(row);
    console.log(JSON.stringify(row));
  };
  record.save = async () => {
    const directory = resolve(root, '.experiments');
    await mkdir(directory, { recursive: true });
    await writeFile(resolve(directory, `${name}.json`), JSON.stringify(rows, null, 2) + '\n');
  };
  return record;
}

export function subscriptionEnv() {
  const env = { ...process.env };
  for (const key of Object.keys(env)) {
    if (/^(ANTHROPIC_|OPENAI_API_KEY$|CLAUDE_CODE_(OAUTH_TOKEN|USE_|API_KEY)|CODEX_API_KEY$)/.test(key)) delete env[key];
  }
  return env;
}

export const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
export function safeError(text, secrets = []) {
  let sanitized = String(text);
  for (const secret of secrets) if (secret) sanitized = sanitized.split(secret).join('<redacted>');
  return sanitized.replace(/(?:Bearer\s+\S+|sk-[\w-]+|[\w.+-]+@[\w.-]+\.[a-z]+)/gi, '<redacted>')
    .replace(/\/Users\/[^/\s]+/g, '<home>').replace(/https?:\/\/\S+/g, '<url>').slice(0, 600);
}
