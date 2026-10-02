// Local transport adapter, not Qwen's provider SDK. Upstream classifier logic
// and prompt/transcript construction are bundled unchanged.
export const calls = [];
export async function runSideQuery(config, options) {
  const request = {
    model: config.getModel(),
    messages: [{role: 'system', content: options.systemInstruction},
      ...options.contents.map(c => ({role: c.role === 'model' ? 'assistant' : 'user',
        content: c.parts.map(p => p.text ?? '').join('\n')}))],
    temperature: options.config.temperature,
    max_tokens: options.config.maxOutputTokens,
    seed: 20261002,
    chat_template_kwargs: {enable_thinking: false},
    response_format: {type: 'json_schema', json_schema: {name: 'verdict', strict: true, schema: options.schema}},
    cache_prompt: false,
  };
  const remote = process.env.STUDY_REMOTE === '1';
  if (remote) {
    delete request.chat_template_kwargs;
    delete request.cache_prompt;
    delete request.seed;
    request.provider = {require_parameters: true, allow_fallbacks: false};
  }
  const started = performance.now();
  const record = {purpose: options.purpose, request};
  calls.push(record);
  try {
    const response = await fetch(process.env.STUDY_MODEL_URL ?? 'http://127.0.0.1:18767/v1/chat/completions', {
      method: 'POST', headers: {'Content-Type': 'application/json', ...(remote ? {Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`} : {})},
      body: JSON.stringify(request), signal: options.abortSignal,
    });
    record.response = await response.json();
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const choice = record.response.choices[0];
    if (choice.finish_reason !== 'stop') throw new Error(`Incomplete output: ${choice.finish_reason}`);
    const parsed = JSON.parse(choice.message.content);
    if (typeof parsed.shouldBlock !== 'boolean') throw new Error('Invalid shouldBlock');
    for (const key of options.schema.required) {
      if (typeof parsed[key] !== options.schema.properties[key].type) throw new Error(`Invalid ${key}`);
    }
    return parsed;
  } catch (error) {
    record.error = error.message;
    throw error;
  } finally { record.elapsed_ms = performance.now() - started; }
}
