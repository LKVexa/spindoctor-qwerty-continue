# SpinDoctor Qwerty 1.1.0 - Continue installer
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""Install SpinDoctor Qwerty into Continue (VS Code / JetBrains extension and the `cn` CLI). Standard library only.

  python3 tools/install_continue.py --workspace PATH     # into PATH/.continue (that project only)
  python3 tools/install_continue.py --global             # into ~/.continue (or $CONTINUE_GLOBAL_DIR)
  python3 tools/install_continue.py --uninstall --workspace PATH | --global

Options: --python CMD (default: the Python running this script, as an absolute path), --reports DIR (where reports go;
default: the engine's ~/spindoctor-workspace), --no-rule (skip the always-on rule, about 1,200 tokens per request), --dry-run (print the plan, change nothing), --force (replace files this
installer didn't write).

It copies, under the chosen .continue folder:
  spindoctor-qwerty/engine/          the bundled engine (Python 3.8+, no packages)
  mcpServers/spindoctor-qwerty.yaml  a config block that starts the MCP server with ABSOLUTE paths
  rules/spindoctor-qwerty.md         the agent rule (honesty rules, q.* grammar, function table, theory testing)
  prompts/spindoctor-*.md            4 slash commands (/spindoctor-functions, -run, -preset, -theory)
  spindoctor-qwerty/INSTALLED.json   the list of files it wrote (used by --uninstall)
Nothing else is touched: it never edits config.yaml. Absolute paths are used because Continue starts MCP servers from
its own working directory, so a relative script path would break."""
import argparse, hashlib, json, os, shutil, sys

VERSION = "1.1.0"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCK = "mcpServers/spindoctor-qwerty.yaml"


def q(s):  # a JSON string is a valid YAML double-quoted scalar
    return json.dumps(s, ensure_ascii=False)


def block_text(python, script, cwd, reports):
    lines = ["# SpinDoctor Qwerty %s - written by tools/install_continue.py (SPDX-License-Identifier: GPL-3.0-or-later)" % VERSION,
             "name: SpinDoctor Qwerty", "version: %s" % VERSION, "schema: v1", "mcpServers:",
             "  - name: SpinDoctor Qwerty", "    type: stdio", "    command: %s" % q(python), "    args:", "      - %s" % q(script)]
    if cwd: lines.append("    cwd: %s" % q(cwd))
    lines += ["    env:", '      PYTHONUTF8: "1"', '      PYTHONDONTWRITEBYTECODE: "1"']
    if reports: lines.append("      SPINDOCTOR_WORKSPACE: %s" % q(reports))
    lines.append("    connectionTimeout: 60000")
    return "\n".join(lines) + "\n"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def plan(target, args, workspace):
    """[(relative path, bytes)] for every file to write."""
    out = []
    eng = os.path.join(ROOT, "engine")
    for r, ds, fs in os.walk(eng):
        ds[:] = sorted(d for d in ds if d != "__pycache__")
        for f in sorted(fs):
            if f.endswith(".pyc"): continue
            p = os.path.join(r, f)
            out.append(("spindoctor-qwerty/engine/" + os.path.relpath(p, eng).replace(os.sep, "/"), open(p, "rb").read()))
    for sub in (("prompts",) if args.no_rule else ("rules", "prompts")):
        d = os.path.join(ROOT, "continue", sub)
        for f in sorted(os.listdir(d)):
            out.append(("%s/%s" % (sub, f), open(os.path.join(d, f), "rb").read()))
    script = os.path.join(target, "spindoctor-qwerty", "engine", "scripts", "spindoctor_mcp.py").replace("\\", "/")
    python = (args.python or sys.executable or "python3").replace("\\", "/")
    reports = os.path.abspath(os.path.expanduser(args.reports)).replace("\\", "/") if args.reports else None
    out.append((BLOCK, block_text(python, script, workspace.replace("\\", "/") if workspace else None, reports).encode("utf-8")))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Install SpinDoctor Qwerty %s into Continue" % VERSION)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--workspace", metavar="PATH"); g.add_argument("--global", dest="glob", action="store_true")
    ap.add_argument("--uninstall", action="store_true"); ap.add_argument("--python"); ap.add_argument("--reports")
    ap.add_argument("--no-rule", action="store_true"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    if a.python and any(c in a.python for c in '"\'`$;&|<>\n'):
        print("refusing: --python must be a plain program name or path"); return 2
    if a.glob:
        g_ = os.environ.get("CONTINUE_GLOBAL_DIR")
        target = os.path.abspath(g_) if g_ else os.path.join(os.path.expanduser("~"), ".continue"); workspace = None
    else:
        workspace = os.path.abspath(os.path.expanduser(a.workspace))
        if not os.path.isdir(workspace): print("no such folder: %s" % workspace); return 2
        target = os.path.join(workspace, ".continue")
    manifest_p = os.path.join(target, "spindoctor-qwerty", "INSTALLED.json")
    old = json.load(open(manifest_p, encoding="utf-8")) if os.path.isfile(manifest_p) else {"files": {}}

    if a.uninstall:
        n = 0
        for rel, h in sorted(old.get("files", {}).items()):
            p = os.path.join(target, rel)
            if os.path.isfile(p) and (sha(p) == h or a.force):
                if not a.dry_run: os.remove(p)
                n += 1
            elif os.path.isfile(p): print("kept (changed since install, use --force): %s" % p)
        if not a.dry_run:
            if os.path.isfile(manifest_p): os.remove(manifest_p)
            for r, ds, fs in sorted(os.walk(os.path.join(target, "spindoctor-qwerty")), reverse=True):
                if not os.listdir(r): os.rmdir(r)
        print("%s %d files from %s" % ("would remove" if a.dry_run else "removed", n, target)); return 0

    files = plan(target, a, workspace)
    clash = [rel for rel, data in files if os.path.isfile(os.path.join(target, rel)) and rel not in old["files"]
             and open(os.path.join(target, rel), "rb").read() != data]
    if clash and not a.force:
        print("refusing to replace files this installer didn't write (use --force):"); [print("  " + os.path.join(target, c)) for c in clash]; return 3
    if a.dry_run:
        for rel, data in files: print("would write %s (%d bytes)" % (os.path.join(target, rel), len(data)))
        return 0
    rec = {}
    for rel, data in files:
        p = os.path.join(target, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = p + ".tmp"; open(tmp, "wb").write(data); os.replace(tmp, p); rec[rel] = hashlib.sha256(data).hexdigest()
    for rel in set(old["files"]) - set(rec):  # files from an older install that this version no longer ships
        p = os.path.join(target, rel)
        if os.path.isfile(p) and sha(p) == old["files"][rel]: os.remove(p)
    json.dump({"name": "spindoctor-qwerty-continue", "version": VERSION, "files": rec}, open(manifest_p, "w", encoding="utf-8"), indent=1)
    blk = os.path.join(target, BLOCK)
    print("installed SpinDoctor Qwerty %s into %s (%d files)" % (VERSION, target, len(rec)))
    print("  MCP block: %s" % blk)
    if workspace:
        print("Continue (VS Code / JetBrains) loads .continue/mcpServers, rules and prompts from this workspace: reload the window, open Agent mode.")
    print("For the cn CLI (and if your Continue doesn't pick the block up), add this to the mcpServers list of your config.yaml:")
    print("  mcpServers:\n    - uses: %s" % (("./" + BLOCK) if not workspace else blk.replace("\\", "/")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
