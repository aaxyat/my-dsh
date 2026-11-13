#!/usr/bin/env python3
"""Provision the machine-local mcp-remote bridge used by the Cloudflare MCP row.

Cloudflare's account API server (https://mcp.cloudflare.com/mcp) answers with an
OAuth challenge and DSH's MCP client has no OAuth flow, so the row is mounted as
a stdio server whose job is to speak OAuth on DSH's behalf. That bridge is
mcp-remote, installed into /opt/agents/tools/cloudflare-mcp-oauth with the DSH
runtime Node and pnpm. The DSH profile row in
harness/plugins/cloudflare-mcp/cordis.patch.yml points at these paths.

Install scripts are disabled: the pinned version declares none, and disabling
them keeps that true if a future resolve ever pulls one in. Tokens are not
handled here — mcp-remote stores them under ~/.mcp-auth after the first browser
login, which this script only prints the command for.

The script is idempotent: a matching installed version is left in place.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_TARGET = Path("/opt/agents/tools/cloudflare-mcp-oauth")
PACKAGE = "mcp-remote"
VERSION = "0.16.6"
SERVER_URL = "https://mcp.cloudflare.com/mcp"


def die(message):
    print(f"provision_cloudflare_mcp_oauth: {message}", file=sys.stderr)
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
    manifest = target / "node_modules" / PACKAGE / "package.json"
    if not manifest.is_file():
        return False
    try:
        return json.loads(manifest.read_text()).get("version") == VERSION
    except (OSError, json.JSONDecodeError):
        return False


def main(argv=None):
    parser = argparse.ArgumentParser(prog="provision_cloudflare_mcp_oauth.py", description=__doc__)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET,
                        help=f"installation directory (default: {DEFAULT_TARGET})")
    parser.add_argument("--dry-run", action="store_true", help="print actions without installing")
    args = parser.parse_args(argv)

    target = args.target.expanduser().resolve()
    node, pnpm = runtime_paths()
    manifest = {
        "name": "cloudflare-mcp-oauth",
        "private": True,
        "version": "1.0.0",
        "type": "module",
        "description": "Machine-local mcp-remote bridge for the DSH cloudflare MCP row.",
        "dependencies": {PACKAGE: VERSION},
    }

    print(f"target   {target}")
    print(f"node     {node}")
    print(f"pnpm     {pnpm}")
    print(f"package  {PACKAGE}@{VERSION}")

    if args.dry_run:
        print("would write package.json and run pnpm install --ignore-scripts")
        return 0

    target.mkdir(parents=True, exist_ok=True)
    (target / "package.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    env = os.environ.copy()
    env["PATH"] = f"{node.parent}{os.pathsep}{env.get('PATH', '')}"
    if not package_matches(target):
        print("installing package")
        run([str(node), str(pnpm), "install", "--ignore-scripts"], cwd=target, env=env)
    else:
        print("package already installed")

    proxy = target / "node_modules" / PACKAGE / "dist" / "proxy.js"
    client = target / "node_modules" / PACKAGE / "dist" / "client.js"
    for path in (proxy, client):
        if not path.is_file():
            raise SystemExit(die(f"bridge entry point missing: {path}"))

    print(f"ready    {proxy}")
    if (Path.home() / ".mcp-auth").is_dir():
        print("tokens   ~/.mcp-auth present; no login needed")
    else:
        print("tokens   none — run once, approve in the browser:")
        print(f"         {node} {client} {SERVER_URL}")
    print("restart DSH to load the row")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
