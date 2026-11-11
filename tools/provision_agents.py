#!/usr/bin/env python3
"""Provision /opt/agents from the tracked agents/ source tree.

Creates the layout, installs helpers, records a provisioning manifest, and locks
bin/ with chflags on macOS. It never edits shell profiles, installs LaunchAgents,
or installs a retention LaunchAgent — those stay deliberate human actions.
"""

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "agents"
DEFAULT_TARGET = Path("/opt/agents")
VERSION = "1"

DIRECTORIES = ["", "bin", "data", "data/.trash", "state", "state/locks", "logs", "tmp", "tools"]


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def chflags(path, flag):
    result = subprocess.run(["chflags", flag, str(path)],
                            capture_output=True, text=True, check=False)
    return result.returncode == 0, (result.stderr or result.stdout).strip()


def locked(path):
    result = subprocess.run(["stat", "-f", "%f", str(path)],
                            capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return None
    try:
        return bool(int(result.stdout.strip(), 0) & 0x2)
    except ValueError:
        return None


def source_commit():
    result = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                            capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="provision_agents.py", description=__doc__)
    parser.add_argument("--target", default=str(DEFAULT_TARGET),
                        help="installation root (default /opt/agents)")
    parser.add_argument("--dry-run", action="store_true", help="show the plan only")
    parser.add_argument("--force", action="store_true", help="replace differing files after unlocking")
    parser.add_argument("--no-lock", action="store_true", help="do not chflags-lock bin/")
    args = parser.parse_args(argv)

    target = Path(args.target).expanduser()
    if not target.is_absolute():
        parser.error("--target must be absolute")
    if not SOURCE.is_dir() or not (SOURCE / "bin").is_dir():
        parser.error(f"source tree missing: {SOURCE}")
    if not (SOURCE / "README.md").is_file():
        parser.error(f"source README missing: {SOURCE / 'README.md'}")

    helpers = sorted(path for path in (SOURCE / "bin").iterdir()
                     if path.is_file() and not path.name.startswith("."))
    if not helpers:
        parser.error("no helpers found in agents/bin")

    for helper in helpers:
        first = helper.read_text(encoding="utf-8", errors="replace").splitlines()[:1]
        if not first or not first[0].startswith("#!"):
            parser.error(f"{helper.name} does not start with a shebang")

    files = [("README.md", SOURCE / "README.md", 0o600)]
    files += [(helper.name, helper, 0o700) for helper in helpers]

    conflicts = []
    if target.exists() and not target.is_dir():
        parser.error(f"{target} exists and is not a directory")
    for name, source, _mode in files:
        destination = (target / name) if name == "README.md" else (target / "bin" / name)
        if destination.is_file() and destination.read_bytes() != source.read_bytes():
            if not args.force:
                conflicts.append(str(destination))
    if conflicts:
        print("conflict: installed files differ (re-run with --force to replace):", file=sys.stderr)
        for path in conflicts:
            print(f"  {path}", file=sys.stderr)
        return 1

    print(f"provisioning {target} from {SOURCE}")
    if args.dry_run:
        print("dry run: no changes")

    darwin = platform.system() == "Darwin"
    if args.force and darwin and (target / "bin").is_dir():
        chflags(target / "bin", "nouchg")
        for name, _source, _mode in files:
            chflags(target / "bin" / name, "nouchg")
    if not args.dry_run:
        for relative in DIRECTORIES:
            directory = target / relative
            directory.mkdir(parents=True, exist_ok=True)
            os.chmod(directory, 0o700)
        print(f"  layout    {len(DIRECTORIES)} directories at 0700")

        installed = 0
        unchanged = 0
        for name, source, mode in files:
            destination = (target / name) if name == "README.md" else (target / "bin" / name)
            if destination.is_file() and destination.read_bytes() == source.read_bytes():
                unchanged += 1
                os.chmod(destination, mode)
                print(f"  unchanged {name}")
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_name(destination.name + ".tmp")
            temporary.write_bytes(source.read_bytes())
            os.chmod(temporary, mode)
            os.replace(temporary, destination)
            installed += 1
            print(f"  install   {name}")
        print(f"  files     {installed} installed, {unchanged} unchanged")

        provisioned = {
            "schema": VERSION,
            "provisionedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "source": str(SOURCE),
            "sourceCommit": source_commit(),
            "target": str(target),
            "helpers": {helper.name: sha256(helper) for helper in helpers},
            "readme": sha256(SOURCE / "README.md"),
        }
        state = target / "state" / "provision.json"
        with open(state, "w", encoding="utf-8") as handle:
            json.dump(provisioned, handle, indent=2)
            handle.write("\n")
        os.chmod(state, 0o600)
        print(f"  record    {state}")

        if args.no_lock:
            print("  lock      skipped (--no-lock); preflight will FAIL")
        elif not darwin:
            print("  lock      skipped: chflags is macOS-only")
        else:
            failures = []
            for helper in helpers:
                okay, error = chflags(target / "bin" / helper.name, "uchg")
                if not okay:
                    failures.append(f"{helper.name}: {error}")
            okay, error = chflags(target / "bin", "uchg")
            if not okay:
                failures.append(f"bin/: {error}")
            if failures:
                print("  lock      FAILED", file=sys.stderr)
                for failure in failures:
                    print(f"            {failure}", file=sys.stderr)
                return 1
            print(f"  lock      {len(helpers)} helpers + bin/ with chflags uchg")

        if not darwin:
            print("  note      chflags locks are macOS-only; verify permissions manually")

        print("")
        print("next steps (deliberate, not automated):")
        print('  export PATH="/opt/agents/bin:$PATH"   # add to your shell profile')
        print("  install the retention LaunchAgent after reviewing agents/README.md")
        print("  /opt/agents/bin/preflight")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
