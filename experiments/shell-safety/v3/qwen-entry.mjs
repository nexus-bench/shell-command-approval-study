import {classifyAction} from 'upstream-classifier';
import {calls} from './qwen-transport.mjs';
import readline from 'node:readline';

// Shell projection retains the exact candidate command; there are no executable
// tools in this registry. No host config, credentials, or agent loop is loaded.
const shell = {name: 'run_shell_command', toAutoClassifierInput: p => ({command: p.command})};
const config = {
  getAutoModeSettings: () => ({}),
  getToolRegistry: () => ({getTool: name => name === shell.name ? shell : undefined}),
  getFastModel: () => 'qwen35-4b-q4', getModel: () => 'qwen35-4b-q4',
};
for await (const line of readline.createInterface({input: process.stdin})) {
  if (!line.trim()) continue;
  const input = JSON.parse(line);
  calls.length = 0;
  const result = await classifyAction({
    toolName: shell.name, toolParams: {command: input.command},
    messages: [{role: 'user', parts: [{text: input.userRequest}]}],
    config, signal: new AbortController().signal,
  });
  process.stdout.write(JSON.stringify({result, calls}) + '\n');
}
