#!/usr/bin/env python3
"""Instala a skill por symlinks globais; preserva qualquer instalação alheia."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

NAME = "web-search-openrouter-agent-skill"
SOURCE = Path(__file__).resolve().parents[1] / "skills" / NAME
CORE_ROOTS = (".agents/skills", ".claude/skills", ".codex/skills", ".dsh/skills")
EXTRA_ROOTS = (
    ".claude-deepseek/skills", ".claude-fred/skills", ".jcode/skills",
    ".pi/agent/skills", ".config/opencode/skill", ".config/opencode/skills", ".config/agents/skills",
)


def skill_roots(home: Path, all_roots: bool = False) -> list[Path]:
    """Raízes centrais + ferramentas existentes e contas Claude descobertas."""
    roots = [home / relative for relative in CORE_ROOTS]
    for relative in EXTRA_ROOTS:
        root = home / relative
        if all_roots or root.parent.exists():
            roots.append(root)
    for account in sorted(home.glob(".claude-*")):
        if account.is_dir():
            roots.append(account / "skills")
    unique = {}
    for root in roots:
        unique[os.path.normcase(str(root.absolute()))] = root
    return list(unique.values())


def install(source: Path, roots: list[Path], *, check: bool = False,
            dry_run: bool = False) -> list[dict]:
    source = source.resolve(strict=True)
    if not (source / "SKILL.md").is_file():
        raise ValueError("a origem não contém SKILL.md")
    results = []
    for root in roots:
        link = root.absolute() / NAME
        row = {"path": str(link), "target": str(source)}
        exists = os.path.lexists(link)
        if exists:
            if link.is_symlink() and link.resolve() == source:
                row["status"] = "ok"
            else:
                row["status"] = "conflict"
                row["error"] = "destino existente preservado; escolha outra raiz"
        elif check:
            row["status"] = "missing"
        elif dry_run:
            row["status"] = "would-link"
        else:
            try:
                root.mkdir(parents=True, exist_ok=True)
                os.symlink(source, link, target_is_directory=True)
                if not link.is_symlink() or link.resolve() != source:
                    raise OSError("não foi possível verificar o symlink criado")
                row["status"] = "linked"
            except OSError as error:
                row["status"] = "error"
                row["error"] = str(error)
        results.append(row)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--root", type=Path, action="append", help="raiz personalizada; repetível")
    parser.add_argument("--all", action="store_true", help="criar também as raízes opcionais conhecidas")
    parser.add_argument("--check", action="store_true", help="verificar sem modificar")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        rows = install(SOURCE, args.root or skill_roots(args.home, args.all),
                       check=args.check, dry_run=args.dry_run)
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            for row in rows:
                print(f"{row['status']}: {row['path']} -> {row['target']}")
                if row.get("error"):
                    print(f"Erro: {row['error']} — Solução: no Windows ative o Modo de Desenvolvedor para symlinks; nunca substitua uma pasta existente.", file=sys.stderr)
        return int(any(row["status"] in ("conflict", "error", "missing") for row in rows))
    except (OSError, ValueError) as error:
        print(f"Erro: {error} — Solução: confira a pasta da skill e as permissões dos symlinks.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
