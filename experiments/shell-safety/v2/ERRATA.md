# Historical-study corrections

The old datasets and predictions remain unchanged so their results can be reproduced.
Use them as historical diagnostic observations, with these additional qualifications.

1. The extension's `ext-node-options` family uses `node --version`. Node handles its
   version flag before runtime initialization, so the described `--require` preload
   effect is not established for that command. The old bad and unknown labels rely
   on preload behavior that does not occur; treat that family as invalid for this
   mechanism. V2 uses `node -e 'console.log(process.version)'`.
   [Node primary source, version early return](https://github.com/nodejs/node/blob/v22.0.0/src/node.cc#L979).
   Original aggregate scores include this flawed family; do not reinterpret them
   as corrected ground truth. V2 has a separately frozen dataset and scores.
2. The old long-context family did not actually place its decisive observation at
   the tail, because sorted object keys moved it earlier. V2 explicitly orders
   evidence records and records offsets in the exact serialized input.
3. Old repository profiles were stipulated serialized state, not repositories a
   collector inspected. Call their table a scenario-profile breakdown. V2 builds
   real repositories but still has small authored templates and a fixed-list collector.
4. Matching command-only input necessarily gives zero opposite-label pair accuracy
   for a deterministic model. This is an input limitation, not an unexpected model
   failure. Use those arms as command-risk references.
5. Native Codex/Claude smoke probes establish limited integration behavior only.
   They are not classifier-accuracy or classifier-latency measurements.
6. Passing the earlier 19 tests establishes artifact/scoring integrity, not correct
   semantic labels. V2 added a prediction-blind label review that found the Node
   defect and five other pre-inference issues. It is still agent review, not human
   ground truth.

The original source-family overlap and incompatible task/policy labels remain
limitations. Neither a larger public sample nor additional same-template synthetic
rows would resolve those problems on their own.
