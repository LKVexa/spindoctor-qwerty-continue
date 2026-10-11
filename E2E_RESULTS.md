# End-to-end results: spindoctor-qwerty-continue 1.1.0

Run on 2026-10-10 (PT) in a clean-room copy (empty folder, empty HOME, PATH=/usr/bin:/bin, no access to engine development
folders), following only this README: `tools/install_continue.py` (workspace and global), then `tests/continue_host_check.py`.

**Mode:** real host CLI with a stand-in model. **Continue CLI `cn` 1.5.47** was installed from npm (`npm i @continuedev/cli`) on a
Linux test machine and used with no account, no sign-in and no API key. No LLM was called: `tests/stub_llm.py` is a local scripted
OpenAI-compatible endpoint (127.0.0.1) that returns fixed tool calls. Driven by it, `cn -p --config <cfg> --auto` loaded the installed
block through `uses:`, started the SpinDoctor MCP server, offered the six `spindoctor_*` tools, put the workspace rule in the system
message, and **executed** four MCP tool calls itself (function table, Bell script, preset qc-001, chat-history theory test with
verdict *supported*), returning the results to the model and writing the PDFs. `--prompt <installed prompt>` passed the slash-command
text through. The `--global` install loaded through `~/.continue/config.yaml` (`uses: ./mcpServers/spindoctor-qwerty.yaml`) from
another folder, with the global rule applied.

**Format check:** Continue's docs (docs.continue.dev reference, MCP, rules and prompts pages, read 2026-10-10) still describe
`mcpServers` blocks (`name`, `version`, `schema: v1`; server `name`, `type`, `command`, `args`, `env`, `cwd`, `connectionTimeout`),
`.continue/mcpServers/`, Markdown rules (`name`, `description`, `globs`, `alwaysApply`) and prompts (`invokable: true`).

**Host behaviour found while testing (cn 1.5.47):**
- `cn` doesn't read `.continue/mcpServers/` blocks from the workspace. MCP servers must be in the config (`uses:` works).
- A rule with `alwaysApply: false` and no globs is not sent at all, so the rule is always-on (with `--no-rule` to skip it).
- Headless `cn -p "/name"` doesn't expand prompts. `--prompt FILE` does.

**Parity target:** the updated SpinDoctor 3.1.2. Publishing was approved by Russell on the basis of the updated 3.1.2 passing its
own suite 18/18, with the three 29-qubit test checks adapted to the 298-qubit limit.

## Host check (clean room, real `cn`)

```
PASS rule: front matter name + description, always applied (no globs, no alwaysApply:false), honesty rules, 298/59 qubits, chat-theory confirmation
PASS 4 prompts: name = file name, description, invokable: true
PASS engine bundled (MCP launcher, CLI, presets data, theory samples)
PASS examples/config.yaml: schema v1 config whose mcpServers entry is uses: ./mcpServers/spindoctor-qwerty.yaml, no keys
PASS installer --dry-run lists the plan and writes nothing
PASS installer --workspace: block (name/version/schema v1, stdio, absolute python + script + cwd, UTF-8 env), rule, 4 prompts, engine, INSTALLED.json
PASS reinstall is idempotent
PASS foreign file is not overwritten (exit 3, untouched); unsafe --python refused (exit 2)
PASS --no-rule installs prompts + server without the rule
PASS --global into $CONTINUE_GLOBAL_DIR (no cwd: the server runs where Continue/cn runs); prints the uses: ./mcpServers/... line
PASS --uninstall removes every installed file, keeps the one the user edited
PASS cn 1.5.47: -p --config (uses: installed block) starts the server; model is offered the 6 spindoctor_* tools; workspace rule in the system message
PASS cn executed 4 MCP tool calls: function table, Bell script, preset qc-001, chat-history theory test (verdict supported) -> results back to the model, PDFs on disk
PASS cn --prompt <installed spindoctor-preset prompt>: the prompt text reaches the model with the user's argument
PASS --global install: ~/.continue/config.yaml with uses: ./mcpServers/spindoctor-qwerty.yaml -> cn offers the 6 tools and applies the global rule in another folder
PASS --uninstall --global
PASS initialize (server spindoctor-qwerty 1.1.0)
PASS tools/list exposes the 6 tools
PASS function table (Markdown, 19 sections, 298-qubit limits listed)
PASS 241 presets listed
PASS one script per command family (16 families, every table example)
PASS 298-qubit circuit with mcx7 (prepared-factor-Born-Z)
PASS q.folder on mixed .txt/.csv/.json/.qasm folder (+ .md skipped)
PASS theory from a file -> supported, TXT+PDF report
PASS theory from a chat summary + quoted excerpts -> supported
PASS theory from an exported chat transcript -> supported
PASS presets qc-001..qc-025 match the updated 3.1.2 reference (20 identical, 5 documented differences)
PASS TXT+PDF reports valid (255 PDFs, 255 TXT twins)
SUMMARY 12/12 passed in 14.0s
PASS end-to-end through the installed block's server (command, args, cwd, env as Continue starts it)
HOST-CHECK (real Continue CLI cn (model = local scripted stub)) PASS
```

The same check without `cn` (`python3 tests/continue_host_check.py`): 12/12 checks, end-to-end 12/12.

## Notes

- **Preset differences (5 of qc-001..qc-025):** CPU-only reference instead of OpenCL GPU fields, tranche checkpoint text, state
  file name. They're documented in `tests/e2e_mcp.py` and are the same in every spindoctor-qwerty repo.
- **Not tested:** the VS Code and JetBrains extensions (their loading of workspace `.continue/mcpServers` blocks is documented but
  wasn't run), interactive `cn` slash commands, and any real model.
