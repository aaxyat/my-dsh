#!/usr/bin/env python3
"""Provision the machine-local Playwright MCP server used by DSH.

Installs @playwright/mcp into /opt/agents/tools/playwright-mcp with the DSH
runtime Node and pnpm, then downloads Playwright's Chromium into that directory.
The DSH profile row in harness/plugins/playwright-mcp/ points at these paths.

No credentials are read or written. The script is idempotent: a matching
package version and an installed Chromium are left in place.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_TARGET = Path("/opt/agents/tools/playwright-mcp")
PACKAGE = "@playwright/mcp"
VERSION = "0.0.85"
BROWSERS = ".browsers"


def die(message):
    print(f"provision_playwright_mcp: {message}", file=sys.stderr)
    return 1


def runtime_paths():
    home = Path.home()
    root = home / ".dsh" / "dsh-runtimes"
    nodes = sorted(root.glob("*/dependencies/node/bin/node"),
                   key=lambda path: path.stat().st_mtime, reverse=True)
    pnpms = sorted(root.glob("*/dependencies/pnpm/bin/pnpm.mjs"),
                   key=lambda path: path.stat().st_mtime, reverse=True)
    if not nodes:
        raise SystemExit(die(f"no DSH runtime Node under {root}"))
    if not pnpms:
        raise SystemExit(die(f"no DSH runtime pnpm under {root}"))
    return nodes[0], pnpms[0]


def run(command, env=None, cwd=None):
    result = subprocess.run(command, cwd=cwd, env=env, text=True)
    if result.returncode != 0:
        raise SystemExit(die(f"command failed ({result.returncode}): {' '.join(map(str, command))}"))
    return result


def package_matches(target):
    manifest = target / "node_modules" / PACKAGE.replace("/", os.sep) / "package.json"
    if not manifest.is_file():
        return False
    try:
        return json.loads(manifest.read_text()).get("version") == VERSION
    except (OSError, json.JSONDecodeError):
        return False


def chromium_installed(target):
    root = target / BROWSERS
    return any(path.is_dir() and path.name.startswith("chromium-") for path in root.glob("chromium-*"))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="provision_playwright_mcp.py", description=__doc__)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET,
                        help=f"installation directory (default: {DEFAULT_TARGET})")
    parser.add_argument("--dry-run", action="store_true", help="print actions without installing")
    args = parser.parse_args(argv)

    target = args.target.expanduser().resolve()
    node, pnpm = runtime_paths()
    manifest = {
        "name": "dsh-playwright-mcp-tool",
        "private": True,
        "version": "1.0.0",
        "description": "Machine-local install of @playwright/mcp used by the DSH playwright MCP row.",
        "dependencies": {PACKAGE: VERSION},
    }

    print(f"target   {target}")
    print(f"node     {node}")
    print(f"pnpm     {pnpm}")
    print(f"package  {PACKAGE}@{VERSION}")

    if args.dry_run:
        print("would write package.json, run pnpm install, and install Chromium")
        return 0

    target.mkdir(parents=True, exist_ok=True)
    package_json = target / "package.json"
    package_json.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    env = os.environ.copy()
    env["PATH"] = f"{node.parent}{os.pathsep}{env.get('PATH', '')}"
    if not package_matches(target):
        print("installing package")
        run([str(node), str(pnpm), "install"], cwd=target, env=env)
    else:
        print("package already installed")

    browser_root = target / BROWSERS
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(browser_root)
    if not chromium_installed(target):
        playwright_cli = next(target.glob("node_modules/.pnpm/playwright@*/node_modules/playwright/cli.js"), None)
        if playwright_cli is None:
            raise SystemExit(die("playwright CLI not found after install"))
        print("installing Chromium")
        run([str(node), str(playwright_cli), "install", "chromium"], env=env)
    else:
        print("Chromium already installed")

    cli = target / "node_modules" / PACKAGE.replace("/", os.sep) / "cli.js"
    if not cli.is_file():
        raise SystemExit(die(f"MCP CLI missing: {cli}"))
    print(f"ready    {cli}")
    print("restart DSH or reinstall the playwright bundle to load the row")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
