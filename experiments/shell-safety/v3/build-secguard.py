"""Build the pinned native guard; sole upstream logic edit is model location."""
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
source = ROOT / ".experiments/upstream/secguard"
pin = "d45bbb55c30c767bb0c1fb07885a69bb11365836"
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip() == pin
brain_path = source / "crates/secguard-brain/src/lib.rs"
original = subprocess.check_output(["git", "show", "HEAD:crates/secguard-brain/src/lib.rs"], cwd=source, text=True)
old = 'let path = dirs::home_dir()?\n            .join(".secguard")\n            .join("models")\n            .join(format!("{name}.gguf"));'
new = 'let path = std::path::PathBuf::from(std::env::var("SECGUARD_STUDY_MODEL").ok()?);'
assert original.count(old) == 1
brain_path.write_text(original.replace(old, new))
driver = source / "crates/secguard-guard/examples/study.rs"
driver.parent.mkdir(exist_ok=True)
shutil.copy2(HERE / "secguard-driver.rs", driver)
env = os.environ.copy()
env["PATH"] = str(ROOT / ".experiments/rust/bin") + os.pathsep + env["PATH"]
env["CARGO_HOME"] = str(ROOT / ".experiments/cargo")
env["CARGO_TARGET_DIR"] = str(ROOT / ".experiments/secguard-target")
env["CARGO_BUILD_JOBS"] = "4"
log = ROOT / '.experiments/secguard-build.log'
with log.open('w') as stream:
    result = subprocess.run([str(ROOT / ".experiments/rust/bin/cargo"), "build", "--locked", "--release",
                    "-p", "secguard-guard", "--example", "study", "--features", "ml,secguard-brain/metal"],
                   cwd=source, env=env, stdout=stream, stderr=subprocess.STDOUT)
if result.returncode:
    print('\n'.join(log.read_text().splitlines()[-35:]))
    raise SystemExit(result.returncode)
binary = ROOT / ".experiments/secguard-target/release/examples/study"
(HERE / "secguard-build.json").write_text(json.dumps({"revision": pin,
    "patch": {"old": old, "new": new},
    "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
    "driver_sha256": hashlib.sha256(driver.read_bytes()).hexdigest(),
    "lock_sha256": hashlib.sha256((source / "Cargo.lock").read_bytes()).hexdigest()}, indent=2) + "\n")
