import { spawn } from 'node:child_process';
import { createInterface } from 'node:readline';
import { once } from 'node:events';

// Small JSONL transport for the version-pinned Codex probe, not an app adapter.
export class Rpc {
  pending = new Map(); events = []; serial = 0; waiters = [];
  constructor(command, args, options = {}) {
    this.process = spawn(command, args, { ...options, stdio: ['pipe', 'pipe', 'pipe'] });
    this.process.stderr.on('data', () => {}); // Deliberately discard potentially sensitive diagnostics.
    this.process.on('error', error => this.fail(error));
    this.process.on('exit', () => this.fail(new Error('Backend exited')));
    this.lines = createInterface({ input: this.process.stdout });
    this.lines.on('line', line => {
      let message;
      try { message = JSON.parse(line); } catch { this.fail(new Error('Invalid JSONL')); return; }
      if (message.method) {
        this.events.push(message);
        this.onEvent?.(message);
        for (const waiter of [...this.waiters]) if (waiter.predicate(message)) waiter.resolve(message);
      } else {
        const pending = this.pending.get(message.id);
        if (!pending) return;
        this.pending.delete(message.id);
        clearTimeout(pending.timer);
        if (message.error) pending.reject(Object.assign(new Error(message.error.message), { code: message.error.code }));
        else pending.resolve(message.result);
      }
    });
  }
  send(message) { this.process.stdin.write(JSON.stringify(message) + '\n'); }
  request(method, params = {}, timeout = 90000) {
    const id = ++this.serial;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { this.pending.delete(id); reject(new Error(`${method} timeout`)); }, timeout);
      this.pending.set(id, { resolve, reject, timer });
      this.send({ id, method, params });
    });
  }
  wait(predicate, after = 0, timeout = 120000) {
    const found = this.events.slice(after).find(predicate);
    if (found) return Promise.resolve(found);
    return new Promise((resolve, reject) => {
      const remove = () => { clearTimeout(timer); this.waiters = this.waiters.filter(x => x !== waiter); };
      const waiter = { predicate, resolve: message => { remove(); resolve(message); }, reject: error => { remove(); reject(error); } };
      const timer = setTimeout(() => waiter.reject(new Error('Event timeout')), timeout);
      this.waiters.push(waiter);
    });
  }
  fail(error) {
    for (const p of this.pending.values()) { clearTimeout(p.timer); p.reject(error); }
    this.pending.clear();
    for (const w of [...this.waiters]) w.reject(error);
  }
  async close() {
    if (this.process.exitCode !== null || this.process.signalCode) return;
    const exit = once(this.process, 'exit');
    this.process.stdin.end();
    const timer = setTimeout(() => this.process.kill('SIGTERM'), 1500);
    await exit; clearTimeout(timer); this.lines.close();
  }
}
