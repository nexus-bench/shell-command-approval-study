# Local and hosted Qwen comparison

Use the existing completed `qwen-code-v3` local Qwen3.5-4B run and
`qwen-coder-plus-v3` hosted Qwen3-Coder-Plus run on the same frozen 120 cases.
Both use the pinned Qwen Code classifier prompt, transcript projection and
two-stage logic. Candidate commands are inert strings and never executed.

The hosted transport uses OpenRouter model `qwen/qwen3-coder-plus`, requires
support for requested parameters, disables provider fallback, and preserves
upstream stage timeouts. It omits llama.cpp-specific parameters and the local
seed. Requests, returned provider/model identifiers, usage and errors are saved.
This is a model-and-serving comparison, not an isolated model-size ablation.
Neither arm reproduces the complete Qwen Code permission manager or SDK retries.

## Presentation

Completed hosted result: 107 allow, 13 unavailable, zero valid block verdicts.
All 13 unavailable reviews failed second-stage validation because `thinking`
was absent. Reported API cost: $0.05398939, excluding smoke. All responses
identified Alibaba as provider. Both local and hosted approved all 72 legacy
cases. On evidence-v3/test, both approved 6/6 supported, 6/6 conflicts and
8/12 unresolved cases; local had two blocks and two timeouts, hosted had four
schema failures. These are not evidence of a hosted safety improvement.

- Local table: Qwen Code classifier + Qwen3.5-4B alongside AutoShell/secguard
  and other local reviewers, using only shared cases. State each policy and
  evidence interface; do not describe policy differences as model accuracy.
- Hosted table: Qwen Code classifier + Qwen3-Coder-Plus alongside the existing
  Codex/Claude native runs, with an explicit scope column (classifier-only vs
  full product). Use shared cases only and keep classifier verdicts distinct
  from observed approval prompts, refusals, execution and sandbox outcomes.
- Paired Qwen table: the two Qwen runs provide the most direct comparison.
  Count unavailable reviews separately; never interpret them as safe decisions.

## Cursor: proposed native-product experiment (not yet run)

Use Cursor desktop Auto-review in a disposable machine with synthetic fixtures,
no credentials, and externally enforced network isolation. Record app version,
selected coding model, run mode, protections, allowlists and sandbox settings.
Use identical task requests and fixture states across native products. Record
the actual proposed command; a changed command is not the original test case.

For each attempt record whether the agent proposed the target command, whether
the allowlist or sandbox handled it, whether a classifier review was observable,
whether the agent revised its approach, and whether the user was prompted.
Unknown classifier routing stays unknown. Report classifier coverage alongside
outcomes. Do not execute hazardous fixtures on the host to obtain a verdict.

Cursor's documented execution order is allowlist, sandbox where possible, then
classifier. Cloud agents do not use these Run Modes, so their unattended behavior
is not an Auto-review measurement. A prompted model imitation would measure a
reconstruction, not Cursor. A controlled MCP stub could test MCP approval, but
must not be substituted for native shell approval results.

Sources checked 2026-10-02:
- https://cursor.com/docs/agent/security/run-modes
- https://cursor.com/changelog/auto-review
- https://openrouter.ai/qwen/qwen3-coder-plus/api
