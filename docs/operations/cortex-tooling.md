# Prepare Cortex tooling without a Snowflake connection

This repository pins public Snowflake tooling so maintainers can inspect a reproducible snapshot before deciding whether to activate anything. Preparation does **not** install a CLI, authenticate, configure a connection, execute SQL, or activate a skill.

## Safe check

Run the offline validation first:

```bash
scripts/prepare_cortex_tooling.sh --check
```

The check validates `.cortex/tooling.lock.json`, exact commit SHA formats, allow-listed public repositories, archive URLs, selected paths, local Python availability, and any already-prepared destination markers. It performs no network or Snowflake action and does not inspect credential files.

## Explicit preparation

Only after approving the lock and the network download, run:

```bash
scripts/prepare_cortex_tooling.sh --prepare
```

Preparation downloads archives for the exact locked commits from public GitHub codeload URLs. It extracts them through path and entry-type checks into the deterministic external cache `$TMPDIR/finops-cortex-tooling-cache/`, then copies only the selected skill directories into `.cortex/skills/`.

The script creates `.cortex/skills/.gitignore` with a wildcard before copying. The generated ignore file ignores itself and every prepared artifact, keeping downloaded content out of source control without changing the repository `.gitignore`. Existing managed destinations with the same source marker are reused; unmanaged, incomplete, or differently pinned destinations cause a failure instead of being overwritten.

## Review before activation

The prepared files are inert copies. Review them before any later installation or use:

1. Compare each `.cortex/skills/<name>/.source-lock.json` with `.cortex/tooling.lock.json`.
2. Read every selected `SKILL.md` and all referenced files, especially bundled scripts, hooks, SQL, and external-service calls.
3. Review each skill's `LICENSE` or `LICENSE.txt`. For Snowflake AI Kit material, also review `.cortex/skills/_source-licenses/snowflake-ai-kit/<revision>/LICENSE` and `LICENSE-SKILLS.md`.
4. Confirm that the requested behavior and privileges are appropriate for the intended Snowflake role and environment.
5. Treat all downloaded instructions and executable content as untrusted until the review is complete.

`Snowflake-Labs/coco-skills` describes its collection as community-contributed educational and reference material. Snowflake reviews contributions but explicitly does not guarantee correctness, completeness, or security. A public repository and a pinned commit improve reproducibility; they do not establish trust or fitness for production.

## Compatibility boundary

Snowflake AI Kit officially documents routing from **Claude Code** and **OpenAI Codex** to Cortex Code. Its repository also documents a different Devin integration. It does not document a native OpenCode plugin integration. Therefore, these files do not connect OpenCode to Cortex Code and must not be represented as an OpenCode integration.

The selected `cortex-router`, `cortex-run`, and `cortex-setup` files are preserved for source review of the officially documented Claude Code/Codex path. Copying them into this repository does not make that path available to OpenCode.

The following remain later-only operations and require a separate, explicit authorization:

- installing or invoking `cortex`, `snow`, Claude Code, Codex, Devin, plugins, or package managers;
- adding, selecting, testing, or changing a Snowflake connection;
- authenticating or inspecting local credential stores;
- compiling or running SQL, checking privileges, or executing the Task Graph;
- checking Cortex model availability or Account Usage freshness;
- installing, registering, syncing, or activating any prepared skill;
- validating email delivery or any other live Snowflake behavior.

No current artifact proves Snowflake compilation, privileges, Account Usage freshness, graph execution, email delivery, Cortex authentication, model access, or runtime compatibility.

## Pinned sources

| Source | Commit | Resolution record |
|---|---|---|
| `Snowflake-Labs/snowflake-ai-kit` | `9259a3b67def2ced6d67e96dc65637d12c3cf40f` | Public GitHub `commits/main` metadata, resolved 2026-11-17 |
| `Snowflake-Labs/coco-skills` | `f5aa17340a3423e300b9efe8f07d5e00617ef4b6` | Public GitHub `commits/main` metadata, resolved 2026-11-17 |

The lock records the exact public metadata endpoint and immutable codeload URL for each source. Updating a pin is a reviewable lock change, not an automatic update.

## What the script cannot do

The script intentionally has no connection setup, SQL execution, model check, skill activation, CLI installation, package-manager call, coding-agent invocation, or shell-profile mutation path. Those omissions are safety boundaries, not missing setup steps.
