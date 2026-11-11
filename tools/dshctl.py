#!/usr/bin/env python3
"""my-dsh control CLI: capture, apply, link, check and doctor.

Standard library only, so it runs on a fresh Mac and on a bare CI runner.
The repository is the source of truth; ~/.dsh and ~/.agents are deploy targets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import plistlib
import re
import shutil
import struct
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

VERSION = "0.1.0"
ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "harness" / "manifest.json"
INVENTORY_PATH = ROOT / "machine" / "inventory.json"

REQUIRED_DOCS = [
    "README.md",
    "AGENTS.md",
    "HANDOFF.md",
    "CHANGELOG.md",
    "docs/architecture.md",
    "docs/layout.md",
    "docs/workflow.md",
    "docs/restore.md",
    "docs/secrets.md",
    "docs/inventory.md",
    "docs/troubleshooting.md",
    "docs/decisions/README.md",
    "harness/profile/README.md",
    "harness/skills/README.md",
    "harness/plugins/README.md",
    "harness/mcp/servers.yaml",
    "harness/tools/README.md",
    "harness/instructions/RULES.md",
    "agents/README.md",
    "docs/host-readiness.md",
]

SECRET_PATTERNS = [
    (
        "private key block",
        re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----[\s\S]{0,200}?[A-Za-z0-9+/=]{40,}"),
    ),
    ("openai-style key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    (
        "github token",
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    ),
    ("aws access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("google api key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("credentialed url", re.compile(r"https?://[^\s/:@]+:[^\s/@]+@")),
    (
        "assigned secret value",
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret|token|password|passwd)\b\s*[:=]\s*[\"']?"
            r"([A-Za-z0-9_\-./+=]{20,})"
        ),
    ),
]

BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz",
    ".tgz", ".woff", ".woff2", ".ttf", ".otf", ".mp4", ".mov", ".asar",
}


# --------------------------------------------------------------------------
# generic helpers
# --------------------------------------------------------------------------

def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def expand(value) -> Path:
    return Path(os.path.expanduser(str(value)))


def display(path) -> str:
    p = Path(path)
    home = Path.home()
    try:
        return "~/" + str(p.relative_to(home))
    except ValueError:
        return str(p)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 256), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    os.replace(tmp, path)


def run(cmd, cwd=None):
    return subprocess.run(
        cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True, check=False
    )


class Findings:
    def __init__(self, title: str):
        self.title = title
        self.errors = []
        self.warnings = []
        print(f"{self.title}")

    def error(self, message: str) -> None:
        self.errors.append(message)
        print(f"  ERROR     {message}")

    def warn(self, message: str) -> None:
        self.warnings.append(message)
        print(f"  WARN      {message}")

    def note(self, message: str) -> None:
        print(f"  {message}")

    def finish(self, ok_message: str = "all checks passed") -> int:
        print("")
        if self.errors:
            print(f"  {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
            return 1
        if self.warnings:
            print(f"  OK with warnings: {len(self.warnings)} warning(s) — {ok_message}")
        else:
            print(f"  OK: {ok_message}")
        return 0


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        raise SystemExit("error: harness/manifest.json is missing")
    try:
        manifest = read_json(MANIFEST_PATH)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"error: cannot parse harness/manifest.json: {exc}")
    if not isinstance(manifest, dict):
        raise SystemExit("error: harness/manifest.json must contain a JSON object")
    return manifest


def copy_artifacts(manifest: dict):
    return [a for a in manifest.get("artifacts", []) if a.get("mode") == "copy"]


def link_artifacts(manifest: dict):
    return [a for a in manifest.get("artifacts", []) if a.get("mode") in ("symlink", "symlink-tree")]


def profile_dir(manifest: dict) -> Path:
    return expand(manifest["homes"]["dsh"]) / "profiles" / manifest["profile"]


# --------------------------------------------------------------------------
# check
# --------------------------------------------------------------------------

def tracked_files():
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            capture_output=True, check=True,
        )
        found = []
        for raw in result.stdout.split(b"\0"):
            if not raw:
                continue
            path = ROOT / raw.decode("utf-8", "replace")
            if path.is_file():
                found.append(path)
        return found
    except (OSError, subprocess.CalledProcessError):
        ignored = {".git", "node_modules", "__pycache__", ".venv"}
        return [
            p for p in ROOT.rglob("*")
            if p.is_file() and not (set(p.relative_to(ROOT).parts) & ignored)
        ]


def parse_front_matter(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None, ""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            fields = {}
            for line in lines[1:index]:
                if not line.strip() or line.lstrip().startswith("#") or line.startswith(" "):
                    continue
                if ":" in line:
                    key, value = line.split(":", 1)
                    fields[key.strip()] = value.strip().strip("\"'")
            return fields, "\n".join(lines[index + 1:])
    return None, text


def check_front_matter(path: Path, findings: Findings, require_name=True) -> None:
    fields, _body = parse_front_matter(path)
    rel = path.relative_to(ROOT)
    if fields is None:
        findings.error(f"{rel}: missing YAML front matter (--- ... ---)")
        return
    name = fields.get("name", "")
    description = fields.get("description", "")
    if require_name:
        if not name:
            findings.error(f"{rel}: front matter is missing `name`")
        elif not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
            findings.error(f"{rel}: name '{name}' must be lower-case kebab-case")
        elif path.parent.name not in (name, "skills") and path.name != f"{name}.md":
            findings.warn(f"{rel}: name '{name}' does not match its directory '{path.parent.name}'")
    if not description:
        findings.error(f"{rel}: front matter is missing `description`")
    elif len(description) < 10:
        findings.warn(f"{rel}: description is very short; the model only sees this line")
    if path.stat().st_size > 32 * 1024:
        findings.warn(f"{rel}: larger than 32 KB; move detail into references/")


def validate_manifest(manifest: dict, findings: Findings) -> None:
    if manifest.get("version") != 1:
        findings.error("manifest: 'version' must be 1")
    profile = manifest.get("profile")
    if not isinstance(profile, str) or not profile:
        findings.error("manifest: 'profile' must be a non-empty string")
    elif not (ROOT / "harness" / "profile" / profile).is_dir():
        findings.error(f"manifest: harness/profile/{profile}/ does not exist")

    homes = manifest.get("homes")
    if not isinstance(homes, dict) or not homes.get("dsh") or not homes.get("agents"):
        findings.error("manifest: 'homes' must define 'dsh' and 'agents'")
    else:
        for key, value in homes.items():
            if not (str(value).startswith("~/") or str(value).startswith("/")):
                findings.error(f"manifest: homes.{key} must start with '~/' or '/'")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        findings.error("manifest: 'artifacts' must be a non-empty list")
        return

    seen = set()
    for index, artifact in enumerate(artifacts):
        label = f"manifest.artifacts[{index}]"
        if not isinstance(artifact, dict):
            findings.error(f"{label}: must be an object")
            continue
        artifact_id = artifact.get("id")
        if not artifact_id:
            findings.error(f"{label}: missing 'id'")
        elif artifact_id in seen:
            findings.error(f"{label}: duplicate id '{artifact_id}'")
        else:
            seen.add(artifact_id)
        mode = artifact.get("mode")
        if mode not in ("symlink", "symlink-tree", "copy"):
            findings.error(f"{label}: mode must be symlink, symlink-tree or copy")
        target = artifact.get("target")
        if not isinstance(target, str) or not (
            target.startswith("~/") or target.startswith("/")
        ):
            findings.error(f"{label}: target must start with '~/' or '/'")
        source = artifact.get("source")
        if not isinstance(source, str) or source.startswith("/") or ".." in Path(source).parts:
            findings.error(f"{label}: source must be a repo-relative path")
        elif not (ROOT / source).exists():
            findings.error(f"{label}: source '{source}' does not exist")
        elif mode == "copy" and not (ROOT / source).is_file():
            findings.error(f"{label}: copy source '{source}' must be a file")

    plugins = manifest.get("plugins", [])
    if not isinstance(plugins, list):
        findings.error("manifest: 'plugins' must be a list")
        return
    for index, plugin in enumerate(plugins):
        label = f"manifest.plugins[{index}]"
        if not isinstance(plugin, dict):
            findings.error(f"{label}: must be an object")
            continue
        source = plugin.get("source")
        if not source or not (ROOT / source).is_dir():
            findings.error(f"{label}: source directory '{source}' does not exist")
            continue
        pkg_path = ROOT / source / "package.json"
        if not pkg_path.is_file():
            findings.error(f"{source}/package.json is missing")
            continue
        try:
            pkg = read_json(pkg_path)
        except ValueError as exc:
            findings.error(f"{source}/package.json is invalid JSON: {exc}")
            continue
        if plugin.get("package") and pkg.get("name") != plugin.get("package"):
            findings.error(
                f"{source}/package.json name '{pkg.get('name')}' != manifest package '{plugin.get('package')}'"
            )
        bundle = (pkg.get("dsh") or {}).get("bundle") or {}
        patch = bundle.get("patch")
        if not patch:
            findings.error(f"{source}/package.json does not declare dsh.bundle.patch")
        elif not (ROOT / source / patch).is_file():
            findings.error(f"{source}: bundle patch '{patch}' does not exist")
        if patch and (ROOT / source / patch).is_file():
            patch_text = (ROOT / source / patch).read_text(encoding="utf-8", errors="replace")
            if "insert:" not in patch_text:
                findings.warn(f"{source}/{patch}: no 'insert:' entry; is the row declared elsewhere?")
        entry = pkg.get("dsh", {}).get("client", {})
        if not entry.get("platform"):
            findings.warn(f"{source}: no dsh.client.platform (host-only bundle)")

    mcp = manifest.get("mcp") or {}
    if mcp.get("source") and not (ROOT / mcp["source"]).is_file():
        findings.error(f"manifest.mcp.source '{mcp['source']}' does not exist")

    workspace = manifest.get("agentWorkspace")
    if not isinstance(workspace, dict):
        findings.error("manifest: 'agentWorkspace' must be an object")
    else:
        source = workspace.get("source")
        if not source or not (ROOT / source).is_dir():
            findings.error(f"manifest.agentWorkspace.source '{source}' is not a directory")
        target = workspace.get("target")
        if not isinstance(target, str) or not (target.startswith("/") or target.startswith("~/")):
            findings.error("manifest.agentWorkspace.target must be an absolute path")
        provisioner = workspace.get("provisionedBy")
        if not provisioner or not (ROOT / provisioner).is_file():
            findings.error(f"manifest.agentWorkspace.provisionedBy '{provisioner}' is missing")


def check_profile(manifest: dict, findings: Findings) -> None:
    directory = ROOT / "harness" / "profile" / manifest["profile"]
    if not directory.is_dir():
        findings.error(f"harness/profile/{manifest['profile']}/ is missing")
        return

    patch = directory / "cordis.patch.yml"
    if not patch.is_file():
        findings.error(f"{patch.relative_to(ROOT)} is missing")
    else:
        text = patch.read_text(encoding="utf-8", errors="replace")
        if not text.strip():
            findings.error(f"{patch.relative_to(ROOT)} is empty")
        if "\t" in text:
            findings.error(f"{patch.relative_to(ROOT)} contains tab characters (invalid YAML)")
        if text.lstrip().startswith("{") or text.lstrip().startswith("["):
            findings.warn(f"{patch.relative_to(ROOT)} is JSON-style YAML; DSH normally uses a block list")

    package_path = directory / "package.json"
    package = {}
    if not package_path.is_file():
        findings.error(f"{package_path.relative_to(ROOT)} is missing")
    else:
        try:
            package = read_json(package_path)
        except ValueError as exc:
            findings.error(f"{package_path.relative_to(ROOT)} is invalid JSON: {exc}")
    bundles = ((package.get("dsh") or {}).get("profile") or {}).get("bundles")
    if not isinstance(bundles, list) or not bundles:
        findings.error(f"{package_path.relative_to(ROOT)} lacks dsh.profile.bundles")
    else:
        if "@deepseek-ai/dsh-base" not in bundles:
            findings.warn("profile bundles do not include @deepseek-ai/dsh-base")
    dependencies = package.get("dependencies", {})
    if not isinstance(dependencies, dict):
        findings.error(f"{package_path.relative_to(ROOT)}: dependencies must be an object")
    else:
        for name, spec in dependencies.items():
            if isinstance(spec, str) and spec.startswith("link:/"):
                linked = Path(spec[len("link:"):])
                try:
                    linked.relative_to(ROOT)
                except ValueError:
                    findings.warn(
                        f"profile dependency {name} links outside this repo ({spec}); "
                        "run ./bin/dsh apply --with-plugins to point it at harness/plugins/ on this machine"
                    )

    workspace = directory / "pnpm-workspace.yaml"
    if not workspace.is_file():
        findings.error(f"{workspace.relative_to(ROOT)} is missing")
    elif "\t" in workspace.read_text(encoding="utf-8", errors="replace"):
        findings.error(f"{workspace.relative_to(ROOT)} contains tabs")


def check_skills(findings: Findings) -> None:
    root = ROOT / "harness" / "skills"
    if not root.is_dir():
        findings.error("harness/skills/ is missing")
        return
    count = 0
    for child in sorted(root.iterdir()):
        if child.name.startswith((".", "_")) or child.name == "README.md":
            continue
        if child.is_dir():
            skill_file = child / "SKILL.md"
            if not skill_file.is_file():
                findings.error(f"harness/skills/{child.name}/SKILL.md is missing")
                continue
            check_front_matter(skill_file, findings)
            count += 1
        elif child.suffix == ".md":
            check_front_matter(child, findings)
            count += 1
    findings.note(f"skills: {count} personal skill(s)")


def check_secrets(findings: Findings) -> None:
    files = tracked_files()
    scanned = 0
    for path in files:
        if path.name == ".credentials.yaml" or path.suffix.lower() in BINARY_SUFFIXES:
            if path.name == ".credentials.yaml":
                findings.error(f"{display(path)} is tracked — remove it from Git immediately")
            continue
        try:
            if path.stat().st_size > 1024 * 1024:
                continue
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        scanned += 1
        for name, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                value = match.group(1) if match.groups() else ""
                if name == "assigned secret value" and re.fullmatch(r"[A-Z][A-Z0-9_]{3,}", value):
                    continue  # an environment-variable name, not a value
                line_no = text.count("\n", 0, match.start()) + 1
                findings.error(
                    f"possible {name} in {display(path)}:{line_no} — do not commit; see docs/secrets.md"
                )
    findings.note(f"secret scan: {scanned} text file(s)")


def check_markdown_links(findings: Findings) -> None:
    link_pattern = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
    checked = 0
    for path in tracked_files():
        if path.suffix.lower() != ".md":
            continue
        rel = path.relative_to(ROOT)
        if rel.parts[:2] == ("docs", "templates"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        in_fence = False
        for line_no, line in enumerate(text.splitlines(), start=1):
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for match in link_pattern.finditer(line):
                target = match.group(1).strip()
                if target.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
                    continue
                target = target.strip("<>")
                if not target or any(ch in target for ch in "{}<>*"):
                    continue
                target = unquote(target.split("#", 1)[0])
                if not target:
                    continue
                if target.startswith("/"):
                    findings.error(f"{rel}:{line_no}: absolute link '{match.group(1)}'")
                    continue
                checked += 1
                resolved = (path.parent / target).resolve()
                try:
                    resolved.relative_to(ROOT)
                except ValueError:
                    findings.error(f"{rel}:{line_no}: link escapes the repository: '{target}'")
                    continue
                if not resolved.exists():
                    findings.error(f"{rel}:{line_no}: broken link '{target}'")
    findings.note(f"markdown links: {checked} internal link(s)")


def check_inventory(manifest: dict, findings: Findings) -> None:
    if not INVENTORY_PATH.is_file():
        findings.warn("machine/inventory.json is missing — run ./bin/dsh capture")
        return
    try:
        inventory = read_json(INVENTORY_PATH)
    except ValueError as exc:
        findings.error(f"machine/inventory.json is invalid JSON: {exc}")
        return
    if inventory.get("schema") != 1:
        findings.warn("machine/inventory.json schema is not 1")
    managed = inventory.get("managedFiles") or {}
    stale = []
    for artifact in copy_artifacts(manifest):
        source = artifact["source"]
        entry = managed.get(source)
        if not entry:
            stale.append(f"{source} (not recorded)")
            continue
        path = ROOT / source
        if not path.is_file():
            continue
        if sha256_file(path) != entry.get("sha256"):
            stale.append(source)
    if stale:
        findings.warn(
            "profile files changed since the last capture: "
            + ", ".join(stale)
            + " — run ./bin/dsh capture"
        )
    findings.note(f"inventory: captured {inventory.get('capturedAt', 'unknown')}")


def cmd_check(_args) -> int:
    findings = Findings(f"my-dsh check — {ROOT}")
    manifest = load_manifest()
    validate_manifest(manifest, findings)
    check_profile(manifest, findings)
    check_skills(findings)
    for doc in REQUIRED_DOCS:
        if not (ROOT / doc).is_file():
            findings.error(f"required document missing: {doc}")
    if not os.access(str(ROOT / "bin" / "dsh"), os.X_OK):
        findings.error("bin/dsh is not executable (chmod +x bin/dsh)")
    check_secrets(findings)
    check_markdown_links(findings)
    check_inventory(manifest, findings)
    return findings.finish()


# --------------------------------------------------------------------------
# capture
# --------------------------------------------------------------------------

def build_inventory(manifest: dict) -> dict:
    dsh_home = expand(manifest["homes"]["dsh"])
    agents_home = expand(manifest["homes"]["agents"])
    profile = manifest["profile"]
    profile_path = dsh_home / "profiles" / profile

    package = {}
    package_path = profile_path / "package.json"
    if package_path.is_file():
        try:
            package = read_json(package_path)
        except ValueError:
            package = {}
    bundles = ((package.get("dsh") or {}).get("profile") or {}).get("bundles") or []
    dependencies = package.get("dependencies") or {}

    runtime = {}
    runtime_path = None
    runtime_root = dsh_home / "dsh-runtimes"
    if runtime_root.is_dir():
        candidates = sorted(
            runtime_root.glob("*/runtime.json"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        if candidates:
            runtime_path = candidates[0]
            try:
                runtime = read_json(runtime_path)
            except ValueError:
                runtime = {}

    version = runtime.get("desktopVersion", "")
    app_path = Path(os.environ.get("DSH_APP", "/Applications/DeepSeek Harness.app"))
    if not version:
        info = app_path / "Contents" / "Info.plist"
        if info.is_file():
            try:
                with open(info, "rb") as handle:
                    version = plistlib.load(handle).get("CFBundleShortVersionString", "")
            except Exception:
                version = ""

    personal_skills = []
    skills_root = ROOT / "harness" / "skills"
    if skills_root.is_dir():
        personal_skills = sorted(
            child.name for child in skills_root.iterdir()
            if child.is_dir() and not child.name.startswith((".", "_"))
        )

    bundled = []
    asar = app_path / "Contents" / "Resources" / "app.asar"
    if asar.is_file():
        bundled = asar_skill_names(asar)

    refs = []
    credentials = dsh_home / ".credentials.yaml"
    if credentials.is_file():
        in_refs = False
        try:
            for line in credentials.read_text(encoding="utf-8", errors="replace").splitlines():
                if re.match(r"^refs:\s*$", line):
                    in_refs = True
                    continue
                if in_refs:
                    if re.match(r"^\S", line):
                        break
                    match = re.match(r"^\s+([A-Z][A-Z0-9_]*):", line)
                    if match:
                        refs.append(match.group(1))
        except OSError:
            refs = []

    managed = {}
    for artifact in copy_artifacts(manifest):
        path = ROOT / artifact["source"]
        if path.is_file():
            managed[artifact["source"]] = {
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
    instructions = []
    for artifact in link_artifacts(manifest):
        if artifact.get("kind") != "instructions":
            continue
        path = ROOT / artifact["source"]
        if path.is_file():
            managed[artifact["source"]] = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
        target = expand(artifact["target"])
        instructions.append(
            {
                "source": artifact["source"],
                "target": artifact["target"],
                "deployed": target.is_symlink() or target.exists(),
            }
        )

    workspace = manifest.get("agentWorkspace") or {}
    workspace_target = expand(workspace.get("target", "/opt/agents"))
    workspace_bin = workspace_target / "bin"
    helpers = sorted(
        path.name for path in workspace_bin.iterdir() if path.is_file()
    ) if workspace_bin.is_dir() else []
    provisioned = {}
    state_path = workspace_target / "state" / "provision.json"
    if state_path.is_file():
        try:
            provisioned = read_json(state_path)
        except ValueError:
            provisioned = {}
    if skills_root.is_dir():
        for child in sorted(skills_root.glob("*/SKILL.md")):
            rel = str(child.relative_to(ROOT))
            managed[rel] = {"sha256": sha256_file(child), "bytes": child.stat().st_size}

    personal_plugins = []
    for plugin in manifest.get("plugins", []):
        name = plugin.get("package")
        personal_plugins.append(
            {
                "id": plugin.get("id"),
                "package": name,
                "installed": name in dependencies,
                "enabled": bool(plugin.get("enabled")),
                "install": plugin.get("install", "link"),
                "deployed": (expand(plugin["target"]).exists() if plugin.get("target") else False),
            }
        )

    return {
        "schema": 1,
        "generatedBy": "bin/dsh capture",
        "capturedAt": iso_now(),
        "host": {
            "system": platform.system(),
            "release": platform.release(),
            "arch": platform.machine(),
            "model": apple_model(),
            "python": platform.python_version(),
        },
        "dsh": {
            "version": version,
            "profile": profile,
            "home": display(dsh_home),
            "agentsHome": display(agents_home),
            "app": str(app_path) if app_path.exists() else None,
        },
        "runtime": {
            "platform": runtime.get("platform"),
            "arch": runtime.get("arch"),
            "node": runtime.get("node"),
            "pnpm": runtime.get("pnpm"),
            "python": runtime.get("python"),
        } if runtime else None,
        "profile": {
            "bundles": bundles,
            "dependencies": dependencies,
        },
        "plugins": {
            "installedDependencies": sorted(dependencies),
            "thirdParty": sorted(name for name in dependencies if not name.startswith("@local/")),
            "personal": personal_plugins,
        },
        "skills": {
            "personal": personal_skills,
            "bundled": bundled,
            "userRoot": display(agents_home / "skills"),
        },
        "instructions": instructions,
        "agentWorkspace": {
            "source": workspace.get("source"),
            "target": str(workspace_target),
            "exists": workspace_target.is_dir(),
            "helpers": helpers,
            "provisionedAt": provisioned.get("provisionedAt"),
            "sourceCommit": provisioned.get("sourceCommit"),
        },
        "credentials": {
            "store": display(credentials),
            "refs": sorted(refs),
            "note": "names only; values are never captured or committed",
        },
        "managedFiles": managed,
    }


def apple_model() -> str:
    try:
        result = subprocess.run(
            ["sysctl", "-n", "hw.model"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except OSError:
        pass
    return ""


def asar_skill_names(asar_path: Path):
    try:
        with open(asar_path, "rb") as handle:
            handle.read(4)
            handle.read(4)
            handle.read(4)
            json_size = struct.unpack("<I", handle.read(4))[0]
            header = json.loads(handle.read(json_size))
    except Exception:
        return []

    names = set()

    def walk(node, prefix):
        for name, value in node.get("files", {}).items():
            path = prefix + "/" + name
            if "files" in value:
                walk(value, path)
            elif name == "SKILL.md":
                parts = path.split("/")
                if "skills" in parts or "assets" in parts:
                    names.add(parts[-2])

    walk(header, "")
    return sorted(names)


def cmd_capture(args) -> int:
    manifest = load_manifest()
    dry = args.dry_run
    print(f"my-dsh capture — {'dry run' if dry else 'live -> repo'}")
    changes = 0
    missing = 0

    for artifact in copy_artifacts(manifest):
        live = expand(artifact["target"])
        source = ROOT / artifact["source"]
        if not live.exists():
            print(f"  MISSING   {display(live)}")
            missing += 1
            continue
        new_bytes = live.read_bytes()
        old_bytes = source.read_bytes() if source.is_file() else None
        if old_bytes == new_bytes:
            print(f"  unchanged {artifact['source']}")
            continue
        changes += 1
        if dry:
            print(f"  would update {artifact['source']}  <-  {display(live)}")
        else:
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(new_bytes)
            print(f"  updated   {artifact['source']}  <-  {display(live)}")

    for artifact in link_artifacts(manifest):
        state = link_state(artifact, expand(artifact["target"]))
        if state == "ok":
            print(f"  linked    {artifact['target']}")
        else:
            print(f"  DEPLOY?   {artifact['target']} ({state}) — run ./bin/dsh link")

    if not dry:
        write_json(INVENTORY_PATH, build_inventory(manifest))
        print(f"  written   machine/inventory.json")
    print("")
    if missing:
        print(f"  {changes} change(s), {missing} missing live file(s)")
    else:
        print(f"  {changes} change(s) captured")
    return 0


# --------------------------------------------------------------------------
# apply / link
# --------------------------------------------------------------------------

class Deployer:
    def __init__(self, manifest: dict, dry_run: bool, force: bool):
        self.manifest = manifest
        self.dry_run = dry_run
        self.force = force
        self.conflicts = 0
        self.changes = 0
        self.backup_root = expand(manifest["homes"]["dsh"]) / "backups" / f"my-dsh-{utc_stamp()}"

    def backup(self, target: Path) -> Path:
        home = Path.home()
        try:
            rel = target.relative_to(home)
        except ValueError:
            rel = Path("external") / target.name
        destination = self.backup_root / rel
        if destination.exists():
            destination = destination.with_name(destination.name + ".1")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink() or target.is_file():
            shutil.copy2(str(target), str(destination), follow_symlinks=False)
            target.unlink()
        else:
            shutil.move(str(target), str(destination))
        print(f"  backup    {display(target)} -> {display(destination)}")
        return destination

    def copy_artifact(self, artifact: dict) -> None:
        source = ROOT / artifact["source"]
        target = expand(artifact["target"])
        label = artifact["source"]
        if not source.is_file():
            print(f"  MISSING   {label} (run ./bin/dsh capture?)")
            self.conflicts += 1
            return
        new_bytes = source.read_bytes()
        if target.exists() and target.is_file():
            if target.read_bytes() == new_bytes:
                print(f"  unchanged {display(target)}")
                return
            if not self.force:
                print(f"  CONFLICT  {display(target)} differs — capture it or use --force")
                self.conflicts += 1
                return
            self.changes += 1
            if self.dry_run:
                print(f"  would replace {display(target)}")
                return
            self.backup(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(new_bytes)
            print(f"  updated   {display(target)}")
            return
        if target.is_symlink():
            print(f"  CONFLICT  {display(target)} is a symlink — use --force to replace")
            self.conflicts += 1
            return
        self.changes += 1
        if artifact.get("id") == "profile-package-json":
            try:
                dependencies = json.loads(new_bytes.decode("utf-8")).get("dependencies", {})
            except ValueError:
                dependencies = {}
            for name, spec in dependencies.items():
                if isinstance(spec, str) and spec.startswith("link:"):
                    linked = Path(spec[len("link:"):])
                    if not linked.exists():
                        print(
                            f"  WARN      {name} links to a missing path ({linked}); "
                            "run apply --with-plugins to relink personal plugins"
                        )
        if self.dry_run:
            print(f"  would create {display(target)}")
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(new_bytes)
        print(f"  created   {display(target)}")

    def symlink(self, source: Path, target: Path, label: str) -> None:
        if target.is_symlink():
            if os.path.realpath(str(target)) == os.path.realpath(str(source)):
                print(f"  linked    {display(target)}")
                return
            if not self.force:
                print(f"  CONFLICT  {display(target)} points elsewhere — use --force")
                self.conflicts += 1
                return
            self.changes += 1
            if self.dry_run:
                print(f"  would relink {display(target)}")
                return
            target.unlink()
            target.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(str(source), str(target))
            print(f"  relinked  {display(target)}")
            return
        if target.exists():
            if not self.force:
                print(f"  CONFLICT  {display(target)} exists — use --force (it will be backed up)")
                self.conflicts += 1
                return
            self.changes += 1
            if self.dry_run:
                print(f"  would replace {display(target)} with a symlink")
                return
            self.backup(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(str(source), str(target))
            print(f"  linked    {display(target)}")
            return
        self.changes += 1
        if self.dry_run:
            print(f"  would link {display(target)} -> {label}")
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(str(source), str(target))
        print(f"  linked    {display(target)} -> {label}")

    def link_artifact(self, artifact: dict) -> None:
        source = ROOT / artifact["source"]
        target = expand(artifact["target"])
        if not source.exists():
            print(f"  MISSING   {artifact['source']}")
            self.conflicts += 1
            return
        if artifact["mode"] == "symlink":
            self.symlink(source, target, artifact["source"])
            return
        if target.is_symlink() or (target.exists() and not target.is_dir()):
            if not self.force:
                print(f"  CONFLICT  {display(target)} is not a plain directory — use --force")
                self.conflicts += 1
                return
            self.changes += 1
            if self.dry_run:
                print(f"  would replace {display(target)} with a directory")
                return
            self.backup(target)
        if not target.exists():
            self.changes += 1
            if self.dry_run:
                print(f"  would create {display(target)}/")
            else:
                target.mkdir(parents=True, exist_ok=True)
                print(f"  created   {display(target)}/")
        for child in sorted(source.iterdir()):
            if child.name.startswith((".", "_")) or child.name == "README.md":
                continue
            if child.is_dir() or child.suffix == ".md":
                self.symlink(child, target / child.name, str(child.relative_to(ROOT)))

    def install_plugins(self) -> int:
        enabled = [
            plugin for plugin in self.manifest.get("plugins", [])
            if plugin.get("enabled") and plugin.get("install") == "link"
        ]
        if not enabled:
            print("  plugins: none enabled for install (manifest 'enabled: true')")
            return 0
        manager = find_package_manager(self.manifest)
        if manager is None:
            print("  ERROR     pnpm not found; expected ~/.dsh/dsh-runtimes/*/dependencies/pnpm")
            return 1
        profile = profile_dir(self.manifest)
        failures = 0
        for plugin in enabled:
            source = (ROOT / plugin["source"]).resolve()
            spec = f"link:{source}"
            command = manager + ["add", spec]
            print(f"  plugin    {plugin['package']}")
            if self.dry_run:
                print(f"            would run: {' '.join(command)} (cwd {display(profile)})")
                continue
            result = run(command, cwd=profile)
            if result.returncode != 0:
                print(f"  ERROR     pnpm failed for {plugin['package']}")
                tail = (result.stderr or result.stdout or "").strip().splitlines()[-5:]
                for line in tail:
                    print(f"            {line}")
                failures += 1
                continue
            add_bundle(self.manifest, plugin["package"])
            print(f"            installed and selected; restart DSH to load it")
        return failures


def add_bundle(manifest: dict, package_name: str) -> None:
    package_path = profile_dir(manifest) / "package.json"
    if not package_path.is_file():
        return
    package = read_json(package_path)
    profile = package.setdefault("dsh", {}).setdefault("profile", {})
    bundles = profile.setdefault("bundles", [])
    if package_name in bundles:
        return
    bundles.append(package_name)
    write_json(package_path, package)
    print(f"            added {package_name} to dsh.profile.bundles")


def find_package_manager(manifest: dict):
    dsh_home = expand(manifest["homes"]["dsh"])
    runtime = dsh_home / "dsh-runtimes"
    nodes = sorted(runtime.glob("*/dependencies/node/bin/node"), key=lambda p: p.stat().st_mtime, reverse=True)
    pnpms = sorted(runtime.glob("*/dependencies/pnpm/bin/pnpm.cjs"), key=lambda p: p.stat().st_mtime, reverse=True)
    if nodes and pnpms:
        return [str(nodes[0]), str(pnpms[0])]
    pnpm = shutil.which("pnpm")
    if pnpm:
        return [pnpm]
    return None


def link_state(artifact: dict, target: Path) -> str:
    if artifact["mode"] == "symlink":
        if target.is_symlink():
            expected = (ROOT / artifact["source"]).resolve()
            return "ok" if Path(os.path.realpath(str(target))) == expected else "wrong-target"
        if target.exists():
            return "regular-file"
        return "missing"
    if not target.exists():
        return "missing"
    for child in sorted((ROOT / artifact["source"]).iterdir()):
        if child.name.startswith((".", "_")) or child.name == "README.md":
            continue
        if not (child.is_dir() or child.suffix == ".md"):
            continue
        link = target / child.name
        if not link.is_symlink():
            return "missing-links"
        if Path(os.path.realpath(str(link))) != child.resolve():
            return "wrong-target"
    return "ok"


def cmd_apply(args) -> int:
    manifest = load_manifest()
    print(f"my-dsh apply — {'dry run' if args.dry_run else 'repo -> machine'}")
    deployer = Deployer(manifest, args.dry_run, args.force)
    for artifact in copy_artifacts(manifest):
        deployer.copy_artifact(artifact)
    if not args.no_link:
        for artifact in link_artifacts(manifest):
            deployer.link_artifact(artifact)
    failures = 0
    if args.with_plugins:
        failures = deployer.install_plugins()
    print("")
    if deployer.conflicts:
        print(f"  {deployer.conflicts} conflict(s); conflicting files were left untouched. Re-run with --force after reviewing.")
        return 1
    if failures:
        print(f"  {failures} plugin installation failure(s)")
        return 1
    if deployer.dry_run:
        print(f"  dry run: {deployer.changes} change(s) would be made")
    else:
        print(f"  applied: {deployer.changes} change(s)")
        if not args.with_plugins:
            print("  hint: restart DSH and run ./bin/dsh doctor")
    return 0


def cmd_link(args) -> int:
    manifest = load_manifest()
    print(f"my-dsh link — {'dry run' if args.dry_run else 'symlinks'}")
    deployer = Deployer(manifest, args.dry_run, args.force)
    for artifact in link_artifacts(manifest):
        deployer.link_artifact(artifact)
    print("")
    if deployer.conflicts:
        print(f"  {deployer.conflicts} conflict(s)")
        return 1
    print(f"  {'would link' if args.dry_run else 'linked'}: {deployer.changes} change(s)")
    return 0


# --------------------------------------------------------------------------
# doctor
# --------------------------------------------------------------------------

def cmd_doctor(_args) -> int:
    print(f"my-dsh doctor — {ROOT}")
    warnings = 0

    def warn(message):
        nonlocal warnings
        warnings += 1
        print(f"  WARN  {message}")

    print("\nrepository")
    branch = run(["git", "-C", str(ROOT), "rev-parse", "--abbrev-ref", "HEAD"])
    remote = run(["git", "-C", str(ROOT), "remote", "get-url", "origin"])
    status = run(["git", "-C", str(ROOT), "status", "--porcelain"])
    dirty = len([line for line in status.stdout.splitlines() if line.strip()])
    print(f"  branch  {branch.stdout.strip() or 'unknown'}")
    print(f"  remote  {remote.stdout.strip() or 'none'}")
    print(f"  changes {dirty} uncommitted file(s)")
    print(f"  python  {sys.executable} ({platform.python_version()})")

    manifest = load_manifest()
    dsh_home = expand(manifest["homes"]["dsh"])
    agents_home = expand(manifest["homes"]["agents"])
    profile = profile_dir(manifest)

    print("\ndsh")
    print(f"  home    {display(dsh_home)} {'ok' if dsh_home.is_dir() else 'MISSING'}")
    print(f"  agents  {display(agents_home)} {'ok' if agents_home.is_dir() else 'not created yet'}")
    print(f"  profile {display(profile)} {'ok' if profile.is_dir() else 'MISSING'}")
    if not profile.is_dir():
        warn("profile directory is missing; run apply after installing DSH")

    version = ""
    runtime_root = dsh_home / "dsh-runtimes"
    if runtime_root.is_dir():
        candidates = sorted(runtime_root.glob("*/runtime.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if candidates:
            try:
                version = read_json(candidates[0]).get("desktopVersion", "")
            except ValueError:
                version = ""
            print(f"  version {version or 'unknown'}")
    if not version:
        warn("could not determine the installed DSH version")

    print("\ndeployment")
    for artifact in copy_artifacts(manifest):
        source = ROOT / artifact["source"]
        target = expand(artifact["target"])
        if not source.is_file():
            warn(f"repo source missing: {artifact['source']}")
            continue
        if not target.is_file():
            print(f"  missing   {display(target)}")
            continue
        same = target.read_bytes() == source.read_bytes()
        print(f"  {'in sync ' if same else 'drifted '} {display(target)}")
        if not same:
            warn(f"{display(target)} differs from {artifact['source']} — capture or apply")

    for artifact in link_artifacts(manifest):
        state = link_state(artifact, expand(artifact["target"]))
        if state != "ok":
            warn(f"{display(expand(artifact['target']))}: {state} — run ./bin/dsh link")
    skills = sorted(
        child.name for child in (ROOT / "harness" / "skills").iterdir()
        if child.is_dir() and not child.name.startswith((".", "_"))
    ) if (ROOT / "harness" / "skills").is_dir() else []
    print(f"  skills  {len(skills)} personal: {', '.join(skills) if skills else 'none'}")

    print("\ninventory")
    if INVENTORY_PATH.is_file():
        try:
            inventory = read_json(INVENTORY_PATH)
            print(f"  captured {inventory.get('capturedAt', 'unknown')} on {inventory.get('host', {}).get('model', 'unknown')}")
            print(f"  dsh      {inventory.get('dsh', {}).get('version', 'unknown')} / profile {inventory.get('dsh', {}).get('profile', 'unknown')}")
            print(f"  refs     {', '.join(inventory.get('credentials', {}).get('refs', [])) or 'none'}")
        except ValueError:
            warn("machine/inventory.json is invalid; run capture")
    else:
        warn("machine/inventory.json is missing; run ./bin/dsh capture")

    print("\ntools")
    for name in ("git", "gh", "node"):
        found = shutil.which(name)
        print(f"  {name:<6} {found or 'not found'}")

    print("")
    print(f"  {'OK' if warnings == 0 else str(warnings) + ' warning(s)'}")
    return 0


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="bin/dsh",
        description="Capture, deploy and validate this DeepSeek Harness configuration.",
    )
    parser.add_argument("--version", action="version", version=f"my-dsh {VERSION}")
    subparsers = parser.add_subparsers(dest="command")

    check = subparsers.add_parser("check", help="validate the repository (no machine state needed)")
    check.set_defaults(func=cmd_check)

    capture = subparsers.add_parser("capture", help="copy live profile into the repo and refresh inventory")
    capture.add_argument("--dry-run", action="store_true", help="show what would change")
    capture.set_defaults(func=cmd_capture)

    apply_parser = subparsers.add_parser("apply", help="deploy the repo to this machine")
    apply_parser.add_argument("--dry-run", action="store_true", help="show what would change")
    apply_parser.add_argument("--force", action="store_true", help="back up and replace conflicting files")
    apply_parser.add_argument("--no-link", action="store_true", help="skip instruction and skill symlinks")
    apply_parser.add_argument("--with-plugins", action="store_true", help="install personal plugins marked enabled")
    apply_parser.set_defaults(func=cmd_apply)

    link = subparsers.add_parser("link", help="create instruction and skill symlinks")
    link.add_argument("--dry-run", action="store_true", help="show what would change")
    link.add_argument("--force", action="store_true", help="back up and replace conflicting paths")
    link.set_defaults(func=cmd_link)

    doctor = subparsers.add_parser("doctor", help="report environment, symlink and drift health")
    doctor.set_defaults(func=cmd_doctor)

    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        sys.exit(130)
