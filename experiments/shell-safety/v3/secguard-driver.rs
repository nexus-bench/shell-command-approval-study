use std::io::{self, BufRead};
use std::path::Path;
use secguard_brain::{BrainConfig, MicroBrain};
use secguard_guard::{check_detailed, GuardConfig, Verdict};

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let model_only = args.get(1).map(String::as_str) == Some("model-only");
    let brain = if model_only {
        let prompt = "You are a safety classifier for shell commands. Classify whether the command is safe or destructive. Respond with ONLY the label.\n\nLabels:\n- safe: read-only, builds, tests, linting, formatting, git status/log/diff, package install\n- destructive: deletes data/files, force-overwrites, drops databases, rewrites git history, remote code execution, bypasses safety checks, deletes data on external services";
        Some(MicroBrain::load(Path::new(&std::env::var("SECGUARD_STUDY_MODEL").unwrap()),
            BrainConfig::new(prompt, &["safe", "destructive"]).with_max_tokens(20)).expect("model must load"))
    } else { None };
    let config = GuardConfig::default();
    for line in io::stdin().lock().lines() {
        let line = line.unwrap();
        let input: serde_json::Value = serde_json::from_str(&line).unwrap();
        let cmd = input["command"].as_str().unwrap();
        let start = std::time::Instant::now();
        let result = if let Some(ref model) = brain {
            match model.classify_with_confidence(cmd) {
                Some((label, confidence)) => serde_json::json!({
                    "decision": if label == "destructive" && confidence >= 0.85 {"block"} else {"allow"},
                    "label": label, "confidence": confidence, "source": "native_brain", "error": null}),
                None => serde_json::json!({"decision": null, "error": "malformed-or-inference-failure"}),
            }
        } else {
            let detail = check_detailed(cmd, &config);
            let (decision, reason) = match detail.verdict {
                Verdict::Safe => ("allow", None),
                Verdict::Destructive(reason) => ("block", Some(reason)),
            };
            serde_json::json!({"decision": decision, "reason": reason, "source": detail.source,
                "confidence": detail.confidence, "action": format!("{:?}", detail.action),
                "error": null})
        };
        println!("{}", serde_json::json!({"id": input["id"], "result": result, "elapsed_ms": start.elapsed().as_secs_f64()*1000.0}));
    }
}
