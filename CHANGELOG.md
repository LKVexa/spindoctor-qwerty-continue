# Changelog

## 1.1.0 - 2026-10-10

- Engine 1.1.0 at parity with the updated SpinDoctor 3.1.2: 1-298 logical qubits (59 per entangled factor), the `mcx7` gate,
  wide-register Born-Z sampling, `q.folder` with 3.1.2 semantics, CSV report copies and measurement-CSV fitting equations. All 241
  presets replayed.
- New tools `spindoctor_functions` (function table) and `spindoctor_test_theory` (theory testing from a file, pasted text or the
  chat history, with TXT+JSON+PDF theory reports).
- New `tools/install_continue.py`: installs per project (`--workspace`) or per user (`--global`) with absolute paths, records what
  it wrote, refuses to overwrite foreign files, uninstalls cleanly. Replaces the 1.0 blocks, which hard-coded one PC's path and
  `python`.
- New always-on rule (`rules/spindoctor-qwerty.md`) and four slash-command prompts (`/spindoctor-functions`, `-run`, `-preset`,
  `-theory`). 1.0 shipped only the MCP block.
- MCP block: `type: stdio`, UTF-8 and no-bytecode env, `cwd` set to the project for workspace installs, 60 s connection timeout.
- Documented that `cn` loads MCP servers only from its config file (`uses:` line), and added `examples/config.yaml`.
- Tests: real `cn` CLI with a local scripted model stand-in (no account or key) executing MCP tool calls, plus the full end-to-end
  suite.
- License GPL-3.0-or-later. Author RUSSELL PHILIP SMITHSON. README, NOTICE, COPYRIGHT and SPDX headers added.

## 1.0.0

- First release: `config.yaml` and `.continue/mcpServers/spindoctor-qwerty.yaml` blocks pointing at a fixed local path.
