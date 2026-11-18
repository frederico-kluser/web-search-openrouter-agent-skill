#!/usr/bin/env python3
"""Valida sintaxe, formato básico, links locais e actions fixadas, sem dependências."""
import ast
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def check() -> list[str]:
    errors = []
    files = []
    for folder in ("scripts", "tests", "skills", ".github"):
        files.extend(path for path in (ROOT / folder).rglob("*")
                     if path.is_file() and path.suffix in (".py", ".md", ".yml", ".yaml"))
    files.extend(ROOT.glob("*.md"))
    for path in sorted(set(files)):
        relative = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            errors.append(f"{relative}: falta newline final")
        for number, line in enumerate(text.splitlines(), 1):
            if line.rstrip() != line:
                errors.append(f"{relative}:{number}: whitespace final")
            if path.suffix == ".py" and "\t" in line:
                errors.append(f"{relative}:{number}: tab em código Python")
        if path.suffix == ".py":
            try:
                ast.parse(text, filename=str(relative))
            except SyntaxError as error:
                errors.append(f"{relative}: {error}")
        if path.suffix in (".yml", ".yaml"):
            for action in re.findall(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)", text, re.M):
                if not re.fullmatch(r"[\w.-]+/[\w./-]+@[a-f0-9]{40}", action):
                    errors.append(f"{relative}: action não fixada por SHA: {action}")
            if "<PIN_SHA>" in text:
                errors.append(f"{relative}: placeholder de SHA")
        if path.suffix == ".md":
            visible = re.sub(r"```.*?```", "", text, flags=re.S)
            for target in re.findall(r"\]\(([^)]+)\)", visible):
                target = target.split(' "', 1)[0].strip("<>").split("#", 1)[0]
                if not target or re.match(r"[\w+.-]+:", target):
                    continue
                if not (path.parent / target).exists():
                    errors.append(f"{relative}: link inexistente: {target}")
    for required in ("LICENSE", "README.md", "CONTRIBUTING.md", "SECURITY.md",
                     "CODEOWNERS", "CHANGELOG.md", "AGENTS.md",
                     "skills/web-search-openrouter-agent-skill/SKILL.md"):
        if not (ROOT / required).is_file():
            errors.append(f"falta {required}")
    json_files = list((ROOT / ".github/rulesets").glob("*.json"))
    json_files.extend((ROOT / ".claude-plugin").glob("*.json"))
    json_files.extend(ROOT.glob("*.json"))
    objects = {}
    for path in json_files:
        try:
            objects[path.relative_to(ROOT).as_posix()] = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError) as error:
            errors.append(f"{path.relative_to(ROOT)}: JSON inválido: {error}")
    version_file = ROOT / "version.txt"
    if version_file.exists():
        version = version_file.read_text(encoding="utf-8").strip()
        if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[\w.-]+)?", version):
            errors.append("version.txt: SemVer inválido")
        plugin = objects.get(".claude-plugin/plugin.json", {})
        manifest = objects.get(".release-please-manifest.json", {})
        if plugin.get("version") != version or manifest.get(".") != version:
            errors.append("version.txt, plugin.json e release manifest divergem")
    return errors


if __name__ == "__main__":
    issues = check()
    for issue in issues:
        print(f"Erro: {issue} — Solução: corrija o arquivo antes do commit.", file=sys.stderr)
    if not issues:
        print("OK: sintaxe, formato, links, fundação e actions SHA-pinned")
    raise SystemExit(bool(issues))
