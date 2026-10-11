# SpinDoctor Qwerty 1.1.0 - Continue host check
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""Continue host check. Standard library only (Python 3.8+); no Continue account, no sign-in, no API key, no model.

1. Static: rule front matter (name, description; always on), 4 prompt files (name, description, invokable: true), engine.
2. tools/install_continue.py: --dry-run writes nothing; --workspace install (block with absolute command/script/cwd parses
   as YAML); reinstall is idempotent; a foreign file is not overwritten (exit 3); unsafe --python refused; --no-rule;
   --global into $CONTINUE_GLOBAL_DIR; --uninstall removes exactly what was installed and keeps a file the user edited.
3. With the REAL Continue CLI (CN=/path/to/cn, or `cn` on PATH) in a throw-away HOME: tests/stub_llm.py stands in for
   the model (a local scripted OpenAI-compatible endpoint, not an LLM; no key). `cn -p --config cfg.yaml --auto` with
   `mcpServers: - uses: <installed block>`: cn starts the server, the 6 spindoctor_* tools are offered to the model, the
   workspace rule is in the system message, and the scripted tool calls (function table, Bell script, preset qc-001,
   chat-history theory test) are executed BY cn through MCP, with results returned to the model and reports on disk.
   `--prompt <installed prompt>` delivers the slash-command text. The global install is loaded the same way through
   ~/.continue/config.yaml (`uses: ./mcpServers/spindoctor-qwerty.yaml`).
4. End-to-end: tests/e2e_mcp.py through the server exactly as the installed block declares it (command, args, cwd, env).

usage: python3 tests/continue_host_check.py [REPO_DIR]"""
import json, os, re, shutil, socket, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = ["spindoctor_run_script", "spindoctor_run_preset", "spindoctor_list_presets", "spindoctor_report", "spindoctor_functions", "spindoctor_test_theory"]


def frontmatter(path):
    m = re.match(r"^---\n(.*?)\n---\n", open(path, encoding="utf-8").read(), re.S)
    return dict(re.findall(r"^([A-Za-z_-]+):\s*(.+)$", m.group(1), re.M)) if m else None


def read_block(path):
    """Parse the installer's block (simple YAML subset whose scalars are JSON strings) without third-party modules."""
    t = open(path, encoding="utf-8").read(); val = lambda k: json.loads(re.search(r"^\s+%s: (.+)$" % k, t, re.M).group(1))
    env = dict((k, json.loads(v)) for k, v in re.findall(r"^      ([A-Z0-9_]+): (.+)$", t, re.M))
    cwd = re.search(r"^    cwd: (.+)$", t, re.M)
    return {"command": val("command"), "args": [json.loads(re.search(r"^      - (.+)$", t, re.M).group(1))],
            "cwd": json.loads(cwd.group(1)) if cwd else None, "env": env, "text": t}


def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def snapshot(root):
    return {os.path.relpath(os.path.join(r, f), root): open(os.path.join(r, f), "rb").read() for r, ds, fs in os.walk(root) for f in fs}


def main():
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    repo = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(HERE)
    ok = True; mode = "host-simulated"

    def T(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond); print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -- " + str(detail)[:700])); sys.stdout.flush()

    inst = os.path.join(repo, "tools", "install_continue.py")
    I = lambda *a, **k: subprocess.run([sys.executable, inst] + list(a), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, **k)
    rule = os.path.join(repo, "continue", "rules", "spindoctor-qwerty.md"); fr = frontmatter(rule); rt = open(rule, encoding="utf-8").read()
    T("rule: front matter name + description, always applied (no globs, no alwaysApply:false), honesty rules, 298/59 qubits, chat-theory confirmation",
      fr and fr.get("name") and fr.get("description") and "globs" not in fr and "alwaysApply" not in fr and "not a" in rt and "quantum computer" in rt
      and "298" in rt and "59" in rt and "confirm" in rt, fr)
    pd = os.path.join(repo, "continue", "prompts"); pf = sorted(os.listdir(pd)); fms = {f: frontmatter(os.path.join(pd, f)) for f in pf}
    T("4 prompts: name = file name, description, invokable: true", pf == ["spindoctor-functions.md", "spindoctor-preset.md", "spindoctor-run.md", "spindoctor-theory.md"]
      and all(m and m.get("name") == f[:-3] and m.get("description") and m.get("invokable") == "true" for f, m in fms.items()), fms)
    T("engine bundled (MCP launcher, CLI, presets data, theory samples)", all(os.path.isfile(os.path.join(repo, "engine", p)) for p in (
      "scripts/spindoctor_mcp.py", "scripts/spindoctor_cli.py", "spindoctor/terminal.py", "spindoctor/data/SPINDOCTOR_PRESETS.json", "examples/theory/bell_theory.md")))

    ex_cfg = open(os.path.join(repo, "examples", "config.yaml"), encoding="utf-8").read()
    T("examples/config.yaml: schema v1 config whose mcpServers entry is uses: ./mcpServers/spindoctor-qwerty.yaml, no keys",
      "schema: v1" in ex_cfg and re.search(r"^mcpServers:\n  - uses: \./mcpServers/spindoctor-qwerty\.yaml$", ex_cfg, re.M) and "apiKey" not in ex_cfg)
    tmp = tempfile.mkdtemp(prefix="sdq_cont_"); ws = os.path.join(tmp, "project"); os.makedirs(ws)
    r = I("--dry-run", "--workspace", ws)
    T("installer --dry-run lists the plan and writes nothing", r.returncode == 0 and "would write" in r.stdout and not os.path.exists(os.path.join(ws, ".continue")), r.stdout[-300:])
    r = I("--workspace", ws); cont = os.path.join(ws, ".continue"); bp = os.path.join(cont, "mcpServers", "spindoctor-qwerty.yaml")
    b = read_block(bp) if os.path.isfile(bp) else {}
    try:
        import yaml  # optional cross-check with a real YAML parser
        y = yaml.safe_load(open(bp, encoding="utf-8")); yok = y["schema"] == "v1" and y["mcpServers"][0]["args"] == b["args"] and y["version"] == "1.1.0"
    except ImportError: yok = True
    T("installer --workspace: block (name/version/schema v1, stdio, absolute python + script + cwd, UTF-8 env), rule, 4 prompts, engine, INSTALLED.json",
      r.returncode == 0 and yok and os.path.isabs(b["command"]) and os.path.isfile(b["args"][0]) and b["cwd"] == ws.replace("\\", "/") and b["env"].get("PYTHONUTF8") == "1"
      and "schema: v1" in b["text"] and "type: stdio" in b["text"] and os.path.isfile(os.path.join(cont, "rules", "spindoctor-qwerty.md"))
      and len(os.listdir(os.path.join(cont, "prompts"))) == 4 and os.path.isfile(os.path.join(cont, "spindoctor-qwerty", "INSTALLED.json")), (r.stdout, b))
    s1 = snapshot(cont); r2 = I("--workspace", ws)
    T("reinstall is idempotent", r2.returncode == 0 and {k: v for k, v in snapshot(cont).items() if not k.endswith("INSTALLED.json")} == {k: v for k, v in s1.items() if not k.endswith("INSTALLED.json")})
    ws2 = os.path.join(tmp, "p2"); os.makedirs(os.path.join(ws2, ".continue", "rules"))
    open(os.path.join(ws2, ".continue", "rules", "spindoctor-qwerty.md"), "w").write("my own rule\n")
    r3 = I("--workspace", ws2); r4 = I("--workspace", ws, "--python", "python; rm -rf ~")
    T("foreign file is not overwritten (exit 3, untouched); unsafe --python refused (exit 2)",
      r3.returncode == 3 and open(os.path.join(ws2, ".continue", "rules", "spindoctor-qwerty.md")).read() == "my own rule\n" and r4.returncode == 2, (r3.stdout, r4.stdout))
    ws3 = os.path.join(tmp, "p3"); os.makedirs(ws3); r5 = I("--workspace", ws3, "--no-rule")
    T("--no-rule installs prompts + server without the rule", r5.returncode == 0 and not os.path.exists(os.path.join(ws3, ".continue", "rules")) and len(os.listdir(os.path.join(ws3, ".continue", "prompts"))) == 4)
    gdir = os.path.join(tmp, "gcontinue"); r6 = I("--global", env=dict(os.environ, CONTINUE_GLOBAL_DIR=gdir))
    gb = read_block(os.path.join(gdir, "mcpServers", "spindoctor-qwerty.yaml")) if r6.returncode == 0 else {}
    T("--global into $CONTINUE_GLOBAL_DIR (no cwd: the server runs where Continue/cn runs); prints the uses: ./mcpServers/... line",
      r6.returncode == 0 and gb.get("cwd") is None and os.path.isfile(gb["args"][0]) and "uses: ./mcpServers/spindoctor-qwerty.yaml" in r6.stdout, r6.stdout)
    # uninstall on a scratch copy; keeps a user-edited file
    ws4 = os.path.join(tmp, "p4"); os.makedirs(ws4); I("--workspace", ws4)
    ed = os.path.join(ws4, ".continue", "prompts", "spindoctor-run.md"); open(ed, "a").write("\nmy note\n")
    r7 = I("--uninstall", "--workspace", ws4); left = [os.path.relpath(os.path.join(a, f), ws4) for a, d, fs in os.walk(ws4) for f in fs]
    T("--uninstall removes every installed file, keeps the one the user edited", r7.returncode == 0 and left == [os.path.join(".continue", "prompts", "spindoctor-run.md")], (r7.stdout, left))

    cn = os.environ.get("CN") or shutil.which("cn")
    data = os.path.join(tmp, "reports")
    if cn:
        mode = "real Continue CLI cn (model = local scripted stub)"
        home = os.path.join(tmp, "home"); os.makedirs(home); port = free_port(); log = os.path.join(tmp, "stub.jsonl"); script = os.path.join(tmp, "script.json")
        env = dict(os.environ, HOME=home); env.pop("CONTINUE_GLOBAL_DIR", None)
        v = subprocess.run([cn, "--version"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120).stdout.strip().splitlines()[-1]
        cfg = os.path.join(tmp, "cn-config.yaml")
        model = "models:\n  - name: stub\n    provider: openai\n    model: stub\n    apiBase: http://127.0.0.1:%d/v1\n    roles: [chat]\n" % port
        open(cfg, "w").write("name: SpinDoctor test\nversion: 0.0.1\nschema: v1\n" + model + "mcpServers:\n  - uses: %s\n" % json.dumps(bp.replace("\\", "/")))
        steps = [{"tool": "spindoctor_functions", "args": {"section": "commands"}},
                 {"tool": "spindoctor_run_script", "args": {"script": "q.circuit new bell 2\nq.circuit add h 0\nq.circuit add cx 0 1\nq.circuit run shots 1000 basis z"}},
                 {"tool": "spindoctor_run_preset", "args": {"preset_id": "qc-001"}},
                 {"tool": "spindoctor_test_theory", "args": {"action": "run", "source": "chat", "text": "Claim: H then CX gives a Bell state; P(00)=P(11)=0.5.",
                  "excerpts": ["User: so H then CX should split 00 and 11 evenly?", "Assistant: yes, about half each"],
                  "hypothesis": "H on qubit 0 then CX(0,1) prepares a Bell state.", "prediction": "P(11) = 0.5 within shot noise.",
                  "script": "q.circuit new t 2\nq.circuit add h 0\nq.circuit add cx 0 1\nq.circuit run shots 2000 basis z",
                  "checks": [{"kind": "probability", "outcome": "11", "expected": 0.5, "tolerance": 0.05}]}},
                 {"text": "FINAL-DONE"}]
        json.dump(steps, open(script, "w"))
        stub = subprocess.Popen([sys.executable, os.path.join(HERE, "stub_llm.py"), str(port), log, script])
        try:
            time.sleep(1.0)
            r = subprocess.run([cn, "-p", "--config", cfg, "--auto", "show the SpinDoctor functions, run a Bell pair, preset qc-001 and test our theory"],
                               env=env, cwd=ws, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=600)
            recs = [json.loads(l) for l in open(log)] if os.path.isfile(log) else []
            agent = [x for x in recs if x["tools"]]
            res = agent[-1]["tool_results"] if agent else []
            flat = lambda x: x if isinstance(x, str) else json.dumps(x)
            T("cn %s: -p --config (uses: installed block) starts the server; model is offered the 6 spindoctor_* tools; workspace rule in the system message" % v,
              r.returncode == 0 and "FINAL-DONE" in r.stdout and agent and all(t in agent[0]["tools"] for t in TOOLS) and "Honesty rules" in (agent[0]["system"] or ""), (r.stdout[-500:], [x["tools"] for x in agent[:1]]))
            pdfs = [p for p in re.findall(r"[^\"\s\\]+?\.pdf", " ".join(flat(x) for x in res)) if os.path.isabs(p)]
            theory_pdf = [p for p in pdfs if "theory" in p.lower()]
            T("cn executed 4 MCP tool calls: function table, Bell script, preset qc-001, chat-history theory test (verdict supported) -> results back to the model, PDFs on disk",
              len(res) == 4 and "| Function | What it does | Command to type |" in flat(res[0]) and "q.circuit" in flat(res[1]) and "qc-001" in flat(res[2])
              and "chat" in flat(res[3]) and "supported" in flat(res[3]) and "not found" not in " ".join(flat(x) for x in res) and len(pdfs) >= 6 and theory_pdf and all(os.path.isfile(p) for p in pdfs),
              {"n": len(res), "parts": ["| Function | What it does | Command to type |" in flat(res[0]) if res else None, "supported" in flat(res[3]) if len(res) > 3 else None,
               "not found" in " ".join(flat(x) for x in res)], "pdfs": pdfs[:6], "missing": [p for p in pdfs[:6] if not os.path.isfile(p)]})
            open(log, "w").close(); json.dump([{"text": "FINAL-DONE"}], open(script, "w"))
            stub.kill(); stub = subprocess.Popen([sys.executable, os.path.join(HERE, "stub_llm.py"), str(port), log, script]); time.sleep(1.0)
            pp = os.path.join(cont, "prompts", "spindoctor-preset.md")
            r = subprocess.run([cn, "-p", "--config", cfg, "--auto", "--prompt", pp, "qc-001"], env=env, cwd=ws, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=300)
            recs = [json.loads(l) for l in open(log)]; um = " ".join(flat(u) for x in recs for u in x["user"])
            T("cn --prompt <installed spindoctor-preset prompt>: the prompt text reaches the model with the user's argument", r.returncode == 0 and "spindoctor_run_preset" in um and "qc-001" in um, um[:300])
            # global install, loaded through ~/.continue/config.yaml
            open(log, "w").close()
            genv = dict(env); I("--global", env=genv)
            gcfg = os.path.join(home, ".continue", "config.yaml")
            open(gcfg, "w").write("name: Local\nversion: 0.0.1\nschema: v1\n" + model + "mcpServers:\n  - uses: ./mcpServers/spindoctor-qwerty.yaml\n")
            other = os.path.join(tmp, "elsewhere"); os.makedirs(other)
            r = subprocess.run([cn, "-p", "--config", gcfg, "--auto", "hi"], env=genv, cwd=other, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=300)
            recs = [json.loads(l) for l in open(log) if l.strip()]; ag = [x for x in recs if x["tools"]]
            T("--global install: ~/.continue/config.yaml with uses: ./mcpServers/spindoctor-qwerty.yaml -> cn offers the 6 tools and applies the global rule in another folder",
              r.returncode == 0 and ag and all(t in ag[0]["tools"] for t in TOOLS) and "Honesty rules" in (ag[0]["system"] or ""), (r.stdout[-300:], [x["tools"] for x in ag[:1]]))
            rr = I("--uninstall", "--global", env=genv)
            T("--uninstall --global", rr.returncode == 0 and not os.path.exists(os.path.join(home, ".continue", "spindoctor-qwerty")), rr.stdout)
        finally:
            stub.kill()
    else:
        print("SKIP real Continue CLI not found (set CN=/path/to/cn)")
    env2 = dict(os.environ, **b["env"]); env2["SPINDOCTOR_WORKSPACE"] = os.path.join(tmp, "e2e_ws")
    ex = os.path.join(cont, "spindoctor-qwerty", "engine", "examples", "theory")
    r = subprocess.run([sys.executable, os.path.join(HERE, "e2e_mcp.py"), "--server", b["command"]] + b["args"] + ["--examples", ex, "--out", os.path.join(tmp, "e2e_results.json")], env=env2, cwd=b["cwd"])
    T("end-to-end through the installed block's server (command, args, cwd, env as Continue starts it)", r.returncode == 0)
    print("HOST-CHECK (%s)" % mode, "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
