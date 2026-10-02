# Cursor SDK approval experiment — setup only

Status: not run. SDK 1.0.35 is pinned. The current session has neither a
CURSOR_API_KEY nor a stored Cursor SDK login. Docker 27.4.0 is available.

Install with `npm ci --ignore-scripts`. Configure CURSOR_API_KEY outside the
repository, then run `node preflight.mjs`. This only authenticates and inspects
the model catalog; it does not start an agent. Do not commit credentials.

Intended configuration: local Cursor agent runtime, composer-2.5 with explicit
fast=true, autoReview=true. Local runtime still uses hosted inference. Discover
the account catalog before assuming that model variant is available.

## Gates before measurement

1. Run in a disposable container/VM without host filesystem or Docker socket
   mounts. Supply synthetic fixtures only. Protect the inference credential
   from candidate commands; enforce outbound restrictions independently of
   the SDK. Container isolation alone does not protect an injected API key.
2. Verify Auto-review is available and observable with harmless control cases.
   Setting autoReview=true is insufficient: the documented backend-unavailable
   fallback executes tools without review. Stop if routing cannot be verified.
3. Capture exact proposed commands, review routing and outcome, agent revisions,
   execution results, run errors, model/catalog information, SDK version and
   usage. Agent refusals and sandbox denials are not classifier blocks.
4. Use a fresh fixture and agent per case. Compare matching cases with the
   native product tracks; report non-proposal and changed-command cases separately.

Headless classifier denials do not produce desktop approval prompts. Label
the result Cursor SDK + Auto-review, not desktop UI parity. Cursor manages the
reviewer model separately from the selected coding model.

Do not use SDK customTools as a shell-classifier substitute. The installed
1.0.35 LocalAgentOptions declaration explicitly says in-process custom tool
callbacks bypass interactive approval, even on autoReview runs. This differs
from the broad June changelog wording and needs runtime verification if used.

Sources checked 2026-10-02:
- https://cursor.com/docs/sdk/typescript#auto-review
- https://cursor.com/docs/agent/security/run-modes
- https://cursor.com/docs/models/cursor-composer-2-5
- Installed @cursor/sdk 1.0.35 dist/esm/options.d.ts
