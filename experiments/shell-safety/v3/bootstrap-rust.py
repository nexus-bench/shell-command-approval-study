"""Install verified Rust components under the ignored workspace cache only."""
import hashlib
import json
import subprocess
import shutil
import tarfile
import tomllib
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parents[3]
cache = root / ".experiments"
manifest = tomllib.loads((cache / "rust-channel.toml").read_text())
installed = []
for name in ("cargo", "rustc", "rust-std"):
    entry = manifest["pkg"][name]["target"]["aarch64-apple-darwin"]
    destination = cache / entry["xz_url"].rsplit("/", 1)[-1]
    if not destination.exists():
        with urllib.request.urlopen(entry["xz_url"], timeout=120) as response, destination.open("wb") as out:
            while chunk := response.read(1024 * 1024):
                out.write(chunk)
    assert hashlib.sha256(destination.read_bytes()).hexdigest() == entry["xz_hash"]
    with tarfile.open(destination) as archive:
        archive.extractall(cache / "rust-install", filter="data")
    source = cache / "rust-install" / destination.name.removesuffix(".tar.xz")
    # rust-installer's option parser does not support prefixes with spaces.
    # Copy the relocatable component layout directly; do not alter system paths.
    component = source / (name if name != "rust-std" else "rust-std-aarch64-apple-darwin")
    for item in component.iterdir():
        if item.name == "manifest.in":
            continue
        target = cache / "rust" / item.name
        target.parent.mkdir(parents=True, exist_ok=True)
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)
    installed.append({"name": name, "url": entry["xz_url"], "sha256": entry["xz_hash"]})
(cache / "rust-install.json").write_text(json.dumps(installed, indent=2) + "\n")
