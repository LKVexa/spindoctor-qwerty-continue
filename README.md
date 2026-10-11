# SpinDoctor Qwerty for Continue

**Continue add-on for the SpinDoctor 3.1.2 quantum-circuit simulator.** It gives [Continue](https://continue.dev) (the VS Code and
JetBrains extensions, and the `cn` CLI) a local MCP server with six tools, an agent rule and four slash-command prompts. You can
build and run `q.*` circuits (1-298 logical qubits), run the 241 built-in presets, process folders of command files with `q.folder`,
test theories from files, pasted text or the conversation itself, and get TXT, PDF, JSON and CSV reports. Everything runs locally
in a bundled, standard-library-only Python engine.

> **Honest limits:** SpinDoctor is a **classical** FP64 simulator running on your computer. It is not a quantum computer, does not
> connect to quantum hardware and gives no quantum speed-up or advantage. Registers hold 1-298 logical qubits, but one entangled
> group (factor) is limited to 59 qubits and dense factors to the memory budget (2^n x 16 bytes); registers wider than 29 qubits
> sample in basis Z only. Histograms come from seeded Born sampling. Requires **Python 3.8+** (no packages). MCP tools work in
> Continue's **Agent** mode.

Version **1.1.0** (engine 1.1.0, "SpinDoctor 3.1.2 parity"). Author: RUSSELL PHILIP SMITHSON. License: GPL-3.0-or-later.

## Install

Continue has no plugin package format. It reads config blocks from `.continue/` folders, so this repo ships an installer that copies
the engine and writes the blocks with **absolute paths**. Continue starts MCP servers from its own working directory, so a relative
script path would break.

```sh
git clone https://github.com/LKVexa/spindoctor-qwerty-continue
cd spindoctor-qwerty-continue

# one project (VS Code / JetBrains pick it up from the workspace):
python3 tools/install_continue.py --workspace /path/to/your/project

# or for every project (your user-level ~/.continue):
python3 tools/install_continue.py --global
```

On Windows use `python` (or `py`) instead of `python3`. The block records the Python that ran the installer as an absolute path,
so the server keeps working even where `python3` doesn't exist. Use `--python CMD` to pick another one.

**What it writes** (under `<project>/.continue/` or `~/.continue/`):

| File | Purpose |
|---|---|
| `mcpServers/spindoctor-qwerty.yaml` | Config block (`name`/`version`/`schema: v1`) that starts `engine/scripts/spindoctor_mcp.py` over stdio |
| `rules/spindoctor-qwerty.md` | Always-on rule: honesty rules, q.* grammar, function table, theory testing (about 1,200 tokens; skip it with `--no-rule`, or toggle it in the rules toolbar) |
| `prompts/spindoctor-{functions,run,preset,theory}.md` | Slash commands (`invokable: true`) |
| `spindoctor-qwerty/engine/` | The bundled engine |
| `spindoctor-qwerty/INSTALLED.json` | The list of files it wrote |

It never edits your `config.yaml` and refuses to overwrite files it didn't write unless you pass `--force`. Other options:
`--reports DIR` (reports folder; default `~/spindoctor-workspace`), `--dry-run`. Remove it with
`python3 tools/install_continue.py --uninstall --workspace /path/to/your/project` (or `--uninstall --global`). Files you've edited
since the install are kept.

**VS Code / JetBrains:** after a `--workspace` install, reload the window, switch to **Agent** mode and ask *"show the SpinDoctor
functions"*. After a `--global` install, add the server to `~/.continue/config.yaml` as shown below. `cn` picks up the rule in
`~/.continue/rules/` on its own (tested). The extensions weren't tested with the global folders.

**`cn` CLI** (`npm i -g @continuedev/cli`): `cn` loads rules from the workspace and `~/.continue`, but MCP servers only from the config
file. Add the block to the `mcpServers` list of the config you use (see [examples/config.yaml](examples/config.yaml)):

```yaml
mcpServers:
  - uses: ./mcpServers/spindoctor-qwerty.yaml          # in ~/.continue/config.yaml after --global
  # - uses: /path/to/your/project/.continue/mcpServers/spindoctor-qwerty.yaml   # after --workspace
```

Then run `cn --config ~/.continue/config.yaml` (interactive, type `/` for the prompts) or, headless,
`cn -p --config ~/.continue/config.yaml --prompt ~/.continue/prompts/spindoctor-preset.md "qc-001"`.

## Slash commands

| Prompt | What it does |
|---|---|
| `/spindoctor-functions [section or filter]` | Shows the function table |
| `/spindoctor-run <q.* commands>` | Runs q.* commands and summarises probabilities, counts and report paths |
| `/spindoctor-preset <qc-NNN> [name=value ...]` | Runs one of the 241 presets |
| `/spindoctor-theory <file \| text \| "we discussed">` | Tests a theory and writes a theory test report |

## SpinDoctor Qwerty - plugin tools

| Function | What it does | Command to type |
|---|---|---|
| Function table (spindoctor_functions) | Show this table in chat | Ask: "show the SpinDoctor functions" or type `/spindoctor-functions` |
| Run a script (spindoctor_run_script) | Run any q.* lines above; returns results + TXT/JSON/CSV/PDF report paths | Ask: "run q.circuit new bell 2 / q.circuit add h 0 / ..." |
| Run a preset (spindoctor_run_preset) | Run qc-001..qc-241 with overrides | Ask: "run preset qc-067 with shots=64" or type `/spindoctor-preset qc-067 shots=64` |
| List presets (spindoctor_list_presets) | Search the 241 presets | Ask: "list presets about Grover" |
| Read a report (spindoctor_report) | List/read TXT reports (PDF/JSON paths alongside) | Ask: "show the newest SpinDoctor report" |
| Test a theory from a file (spindoctor_test_theory source=file) | Read a .txt/.md/.pdf/.py/.json/.csv/.q attachment, then hypothesis -> prediction -> q.* script -> run -> verdict + TXT/PDF theory report | Ask: "test the theory in C:/notes/theory.md" (the host must pass the file path/content) |
| Test a theory from text (spindoctor_test_theory source=text) | Same pipeline for pasted text | Ask: "test this theory: a Hadamard on \|0> gives 50/50" |
| Test the theory we discussed (spindoctor_test_theory source=chat) | The AI summarises the theory from the conversation (claims, assumptions, variables, prediction), you confirm, then it is tested; quoted excerpts go in the report under 'Source: chat history'. An exported chat transcript (.txt/.md/.json/.html) also works | Ask: "test the theory we discussed" (or `/spindoctor-theory`) or "test the theory in my exported chat C:/chats/conversation.json" |

Every command family is listed with a runnable example in **[FUNCTIONS.md](FUNCTIONS.md)** (the exact table the tool shows):
circuits (`q.circuit`, including 298-qubit wide registers and the `mcx7` gate), queries (`q.query`), the tranche register
(`q.tranche`), the procedural grid, presets and sequences, resource planning, math calculators, physics models, lessons, noise, error
correction, compilation, algorithms, inputs/folders/history (`q.input`, `q.folder`, `q.history`) and the cartridge commands.

## Theory testing

`spindoctor_test_theory` turns a claim into a test: hypothesis -> measurable prediction -> `q.*` script -> run -> compare -> a TXT +
JSON + PDF **theory test report** with the hypothesis, script, raw results, verdict (*supported*, *not supported* or *inconclusive*)
and limits.

- **From a file:** .txt, .md, .pdf, .py, .json, .csv or .q. In Continue, @-mention the file or give its path; relative paths are resolved against the project folder (for a `--workspace` install).
- **From pasted text.**
- **From the chat history:** say *"test the theory we discussed"*. The model writes a short summary (claims, assumptions, variables,
  measurable prediction), shows it to you to confirm or correct, then passes it with optional quoted excerpts; the report records them
  under *Source: chat history*. Exported chat transcripts (.txt/.md/.json/.html from ChatGPT, Claude and others) also work.
- The plugin cannot read your conversation or attachments by itself: only the model sees them, and very long conversations may already
  be truncated by the context window.

Sample theory files and chat transcripts are in `engine/examples/theory/`. The two sample
PDFs are stored as text; run `python3 engine/examples/theory/make_sample_pdfs.py` to
recreate them.

## Folder ingestion (`q.folder`)

`q.folder run path="<folder>"` runs every supported file at the top level of a folder (.txt, .csv, .json, .qasm, .qasm2, .circuit,
.pdf) in ordinal name order: 1-128 supported files, at most 4 MiB per file, 1-128 commands per file and 4096 characters per command,
strict UTF-8. Other files (for example .md) are skipped and listed. The first failing file stops the job.

## Testing

| Test | Command | Result for 1.1.0 |
|---|---|---|
| Host check with the **real `cn` CLI** | `CN=$(command -v cn) python3 tests/continue_host_check.py` | 17/17 checks, end-to-end 12/12 |
| Same without `cn` | `python3 tests/continue_host_check.py` | 12/12 checks, end-to-end 12/12 |

**Real host:** Continue CLI `cn` 1.5.47 (npm `@continuedev/cli`) ran on a Linux test machine with **no account, no sign-in and no API
key**. A real model was not used: `tests/stub_llm.py` is a small local, scripted OpenAI-compatible endpoint that asks for fixed tool
calls. With that, cn started the installed MCP server, offered the six `spindoctor_*` tools to the "model", put the rule in the
system message, and **executed** the tool calls through MCP: the function table, a Bell circuit, preset qc-001 and a chat-history
theory test (verdict *supported*, PDFs written). `--prompt` passed the slash-command text through, and the `--global` install loaded
through `~/.continue/config.yaml`. The VS Code / JetBrains extensions weren't run. In headless `cn -p`, typing `/name` isn't expanded,
so use `--prompt FILE` there. Details are in [E2E_RESULTS.md](E2E_RESULTS.md).

## Repository layout

| Path | What |
|---|---|
| `continue/rules/`, `continue/prompts/` | The rule and the 4 prompts the installer copies |
| `engine/` | Bundled engine 1.1.0: `scripts/spindoctor_mcp.py` (MCP server), `scripts/spindoctor_cli.py` (CLI), `spindoctor/` (package), `examples/theory/` |
| `tools/install_continue.py` | Installer / uninstaller |
| `examples/config.yaml` | Example `~/.continue/config.yaml` |
| `tests/` | `continue_host_check.py`, `e2e_mcp.py`, `stub_llm.py`, reference outputs for qc-001..qc-025 |

## Author and license

Author: **RUSSELL PHILIP SMITHSON** <russellsmithson77@outlook.com>

Copyright (C) 2026 RUSSELL PHILIP SMITHSON. Licensed under the GNU General Public License v3.0 or later (`GPL-3.0-or-later`): see
[LICENSE](LICENSE), [NOTICE](NOTICE) and [COPYRIGHT](COPYRIGHT). Continue is a trademark of Continue Dev, Inc.; this project is not
affiliated with it.
