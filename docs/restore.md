# Restore — rebuilding the harness on a new machine

Target: a fresh macOS machine with DSH installed. This procedure reproduces instructions, profile, skills, plugins and tool configuration. It does **not** reproduce conversations, credentials or DSH runtime binaries.

Time: ~10 minutes, plus app installation and sign-in.

## Before you start

Have ready:

- The **DSH desktop version** recorded in [`machine/inventory.json`](../machine/inventory.json) (`dsh.version`). Installing the same major/minor avoids schema drift; newer is usually fine but capture a diff afterwards.
- Access to the GitHub repository (`aaxyat/my-dsh`).
- Your API credentials (DeepSeek and/or the `opencode-go` relay key). They are **not** in the repo.
- Git, and (optional) the GitHub CLI for pushing updates back.

## 1. Install DSH

Install the desktop app (Apple Silicon build), launch it once, and complete sign-in. Let it create `~/.dsh` and a default profile. Close it before deploying configuration into its profile.

```sh
ls ~/.dsh/profiles/          # should list "desktop" (or the profile you will use)
```

If the profile name differs, adapt `harness/manifest.json` `profile` and the `harness/profile/<name>/` directory before applying.

## 2. Clone and inspect

```sh
git clone https://github.com/aaxyat/my-dsh.git ~/Documents/Projects/my-dsh
cd ~/Documents/Projects/my-dsh

./bin/dsh doctor             # repo, python, DSH home, profile, versions
./bin/dsh check              # repository integrity
./bin/dsh apply --dry-run    # exactly what will be written/linked
```

Read the dry-run output. On a clean machine every line should be `create`; anything marked `conflict` means the app already wrote that file — inspect before forcing.

## 3. Deploy

```sh
./bin/dsh apply
```

This:

- copies the three profile files into `~/.dsh/profiles/desktop/`, backing up any existing versions under `~/.dsh/backups/my-dsh-<timestamp>/`;
- creates `~/.agents/AGENTS.md` and `~/.agents/RULES.md` as symlinks to `harness/instructions/`;
- creates `~/.agents/skills/<name>` symlinks for every personal skill;
- refuses to overwrite a differing live file unless `--force`.

Optional personal plugins:

```sh
./bin/dsh apply --with-plugins     # pnpm add link:<repo>/harness/plugins/<name>
```

Provision the machine-level agent workspace required by `AGENTS.md` §7:

```sh
python3 tools/provision_agents.py --dry-run
python3 tools/provision_agents.py
/opt/agents/bin/preflight
```

Then add `/opt/agents/bin` to `PATH` in your shell profile. The root-level `/agents` alias and the retention LaunchAgent are deliberate human steps, not automated by the provisioner.

## 4. Restore credentials

Never copy `.credentials.yaml`. Instead:

1. Open DSH → **Settings → Account** (or the provider's model settings) and add the key named by the profile, e.g. `OPENCODE_GO_API_KEY`.
2. Alternatively, launch DSH from a shell that exports the variable, so the GUI process inherits it.
3. Confirm the models listed in `harness/profile/desktop/cordis.patch.yml` appear in the model picker.

The only credential **names** the repo knows are in [`.env.example`](../.env.example) and in the inventory as references. If a restore needs a name that is not there, the profile changed without a capture.

## 5. Restart and verify

Quit DSH completely and relaunch. Then check, in order:

| Check | Expected |
|---|---|
| New session in any project | Global `AGENTS.md` rules appear; check that `RULES.md` is present next to it. |
| This repo opened as a workspace | Root `AGENTS.md` is loaded in addition to global ones. |
| Skill catalog / `skill` tool | Every `harness/skills/*/SKILL.md` is listed. |
| Model picker | `opencode-go` models from the patch are present; default is `deepseek-v4.1-flash`. |
| UI settings | Chat transcript style / usage detail match the patch. |
| Plugins page | Selected bundles loaded without errors; personal plugins if installed. |
| `./bin/dsh doctor` | All green, symlinks point into this repo. |

If a check fails, see [troubleshooting.md](troubleshooting.md).

## 6. Post-restore housekeeping

```sh
cd ~/Documents/Projects/my-dsh
./bin/dsh capture        # inventory now records this machine
git diff                 # should be empty if nothing drifted
git commit -am "chore: capture restore on <machine>"   # only if inventory changed
git push
```

Record the new machine in `HANDOFF.md` (session log) and, if the OS/architecture differs, in `docs/inventory.md`.

## What is intentionally not restored

| Item | Why | How to get it back |
|---|---|---|
| API keys / OAuth tokens | Secret | Re-enter in DSH |
| Conversations and workspace index | Machine state, not config | Not restored |
| `node_modules`, lockfiles | Reproducible | Reinstalled by pnpm during plugin installation |
| DSH application and runtime | Reinstalled | Installer |
| Third-party plugin source | Upstream | Registry/version from `registry.yaml` |
| `.local.md` overlays | Deliberately machine-local | Recreate manually |

## Uninstall / rollback

`apply` keeps a timestamped backup per run. To roll back, copy the files from `~/.dsh/backups/my-dsh-<timestamp>/` to their original paths and restart. To remove only the symlinks, delete `~/.agents/AGENTS.md` and `~/.agents/skills/<name>`; the repo is unaffected.
